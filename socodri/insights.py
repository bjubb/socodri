import time
from copy import copy
from django.core.cache import cache
from facebookads.objects import AdAccount, Insights, AsyncJob
from socodri import utils


def _get_attr_window(view_window, click_window):
    return filter(lambda x: x, [
        getattr(Insights.ActionAttributionWindow, view_window, None),
        getattr(Insights.ActionAttributionWindow, click_window, None)
    ])


def get_attr_window(window):
    return _get_attr_window(window.view_window, window.click_window)


def _get_attr_multipliers(view_multiplier=None, click_multiplier=None):
    return filter(lambda x: x, [view_multiplier, click_multiplier])


def get_attr_multipliers(window):
    return _get_attr_multipliers(
        window.view_multiplier if window.view_window else None,
        window.click_multiplier if window.click_window else None
    )


def aggregate_insights_data(settings, actions, data):
    val = {'conversions': 0, 'conversion_revenue': 0.00}

    val['reach'] = data['reach']
    val['spend'] = data['spend']
    val['impressions'] = data['impressions']
    val['date_start'] = data['date_start']
    val['date_stop'] = data['date_stop']

    attr_window = _get_attr_window(settings.view_window, settings.click_window)
    attr_multipliers = _get_attr_multipliers(settings.view_multiplier, settings.click_multiplier)

    filtered_actions = set([(a.pixel.id, a.tag) for a in actions])
    create_action_tuple = lambda a: (long(a[Insights.ActionBreakdown.action_target_id]), unicode(a[Insights.ActionBreakdown.action_type]))

    for action in filter(lambda x: create_action_tuple(x) in filtered_actions, data.get('actions', [])):
        conversions = sum(
            map(lambda (window, multiplier): action.get(window, 0) * multiplier,
                zip(attr_window, attr_multipliers)
               )
        )
        val['conversions'] += conversions

    if settings.revenue_source == 'Facebook':
        for action_value in filter(lambda x: create_action_tuple(x) in filtered_actions, data.get('action_values', [])):
            conversion_revenue = sum(
                map(lambda (window, multiplier): action_value.get(window, 0.0) * multiplier,
                    zip(attr_window, attr_multipliers)
                   )
            )
            val['conversion_revenue'] += conversion_revenue
    return val


def aggregate_window_data(window, data):
    val = {'conversions': 0, 'conversion_revenue': 0.00}

    val['reach'] = data['reach']
    val['spend'] = data['spend']
    val['impressions'] = data['impressions']
    val['date_start'] = data['date_start']
    val['date_stop'] = data['date_stop']

    attr_window = get_attr_window(window)
    attr_multipliers = get_attr_multipliers(window)
    for action in data.get('actions', []):
        pixel_id = long(action[Insights.ActionBreakdown.action_target_id])
        tag = action[Insights.ActionBreakdown.action_type]
        if window.stage_set.filter(actions__pixel__id=pixel_id, actions__tag=tag).count():
            conversions = sum(
                map(lambda (w, m): action.get(w, 0) * m,
                    zip(attr_window, attr_multipliers)
                   )
            )
            val['conversions'] += conversions

    for action_value in data.get('action_values', []):
        pixel_id = long(action[Insights.ActionBreakdown.action_target_id])
        tag = action[Insights.ActionBreakdown.action_type]
        if window.stage_set.filter(actions__pixel__id=pixel_id, actions__tag=tag).count():
            conversion_revenue = sum(
                map(lambda (w, m): action_value.get(w, 0) * m,
                    zip(attr_window, attr_multipliers)
                   )
            )
            val['conversion_revenue'] += conversion_revenue

    return val


def aggregate_stage_data(window, data):
    stages = {}
    val = {'conversions': 0, 'conversion_revenue': 0.00}
    val['spend'] = data['spend']
    val['impressions'] = data['impressions']
    val['date_start'] = data['date_start']
    val['date_stop'] = data['date_stop']

    for stage_num in window.stage_set.values_list('number', flat=True):
        stages[stage_num] = copy(val)

    conversion_action_prefix = 'offsite_conversion.'
    attr_window = get_attr_window(window)
    attr_multipliers = get_attr_multipliers(window)
    for action in filter(lambda x: conversion_action_prefix in x[Insights.ActionBreakdown.action_type], data.get('actions', [])):
        pixel_id = long(action[Insights.ActionBreakdown.action_target_id])
        prefix, tag = action[Insights.ActionBreakdown.action_type].split(conversion_action_prefix)
        for stage in window.stage_set.filter(actions__pixel__id=pixel_id, actions__tag=tag):
            conversions = sum(
                map(lambda (window, multiplier): action.get(window, 0) * multiplier,
                    zip(attr_window, attr_multipliers)
                   )
            )
            stages[stage.number]['conversions'] += conversions

    for action_value in filter(lambda x: conversion_action_prefix in x[Insights.ActionBreakdown.action_type], data.get('action_values', [])):
        pixel_id = long(action_value[Insights.ActionBreakdown.action_target_id])
        prefix, tag = action_value[Insights.ActionBreakdown.action_type].split(conversion_action_prefix)
        for stage in window.stage_set.filter(actions__pixel__id=pixel_id, actions__tag=tag):
            conversion_revenue = sum(
                map(lambda (window, multiplier): action_value.get(window, 0.0) * multiplier,
                    zip(attr_window, attr_multipliers)
                   )
            )
            stages[stage.number]['conversion_revenue'] += conversion_revenue
    return stages

def _get_sync(account, params):
    return [data for data in account.get_insights(params=params)]

def _get_async(account, params):
    async_job = account.get_insights(params=params, async=True)
    while True:
        job = async_job.remote_read()
        time.sleep(1)
        if job:
            break
    return [data for data in async_job.get_result()]

def get_adaccount_insights(adaccount, attr_window, campaigns=[], adsets=[], ads=[], increment=Insights.Increment.all_days):
    object_filters = []
    if campaigns:
        object_filters.append({
                'field': 'campaign.id',
                'operator': Insights.Operator.in_.upper(),
                'value': campaigns
        })
    if adsets:
        object_filters.append({
                'field': 'adset.id',
                'operator': Insights.Operator.in_.upper(),
                'value': adsets
        })
    if ads:
        object_filters.append({
                'field': 'ad.id',
                'operator': Insights.Operator.in_.upper(),
                'value': ads
        })

    params = {
        'time_increment': increment,
        'sort': Insights.Field.date_start,
        'fields': [
            Insights.Field.reach,
            Insights.Field.impressions,
            Insights.Field.spend,
            Insights.Field.actions,
            Insights.Field.action_values,
        ],
        'action_breakdowns': [
            Insights.ActionBreakdown.action_destination,
            Insights.ActionBreakdown.action_type,
            Insights.ActionBreakdown.action_target_id
        ],
        'action_attribution_windows': attr_window,
        'filtering': [
            {
                'field': Insights.Field.impressions,
                'operator': Insights.Operator.greater_than_or_equal.upper(),
                'value': 0
            }
        ] + object_filters
    }

    cache_key = '%s_%s' % (adaccount.id, utils.hash_params(params))
    if not cache.get(cache_key):
        account = AdAccount('act_%s' % adaccount.id)
        # cache[cache_key] = _get_sync(account, params) if increment == Insights.Increment.all_days else _get_async(account, params)
        cache.set(cache_key, _get_async(account, params), 60*60*24*7)  # one week

    return cache.get(cache_key)[0] if increment == Insights.Increment.all_days else cache.get(cache_key)

def get_ad_insights(adaccount, attr_window, campaigns, daily=False):
    params = {
        'time_increment': 1 if daily else Insights.Increment.all_days,
        'level': Insights.Level.ad,
        'fields': [
            Insights.Field.ad_id,
            Insights.Field.ad_name,
            Insights.Field.adset_id,
            Insights.Field.adset_name,
            Insights.Field.campaign_id,
            Insights.Field.campaign_name,
            Insights.Field.spend,
            Insights.Field.actions,
            Insights.Field.action_values,
        ],
        'action_breakdowns': [
            Insights.ActionBreakdown.action_destination,
            Insights.ActionBreakdown.action_type,
            Insights.ActionBreakdown.action_target_id
        ],
        'action_attribution_windows': attr_window,
        'filtering': [
            {
                'field': Insights.Field.impressions,
                'operator': Insights.Operator.greater_than_or_equal.upper(),
                'value': 0
            },
            {
                'field': 'campaign.id',
                'operator': Insights.Operator.in_.upper(),
                'value': campaigns
            }
        ]
    }
    account = AdAccount('act_%s' % adaccount.id)
    return [d for d in account.get_insights(params=params)]


def get_bimonthly_insights(initiative):
    return [
        aggregate_insights_data(initiative.settings, initiative.actions.all(), data)
            for data in get_adaccount_insights(
                initiative.adaccount,
                _get_attr_window(initiative.settings.view_window, initiative.settings.click_window),
                campaigns=tuple(initiative.campaigns.all().values_list('id', flat=True)),
                increment=15
            )
    ]


def get_daily_window_insights(window):
    assert window
    return [
        aggregate_window_data(window, data)
            for data in get_adaccount_insights(
                window.adaccount,
                get_attr_window(window),
                campaigns=tuple(window.campaigns.all().values_list('id', flat=True)),
                increment=1
            )
    ]


def get_window_insights(window):
    assert window
    return aggregate_window_data(window,
        get_adaccount_insights(
            window.adaccount,
            get_attr_window(window),
            campaigns=tuple(window.campaigns.all().values_list('id', flat=True))
        )
    )


def get_stage_insights(window):
    assert window
    return aggregate_stage_data(window,
        get_adaccount_insights(
            window.adaccount,
            get_attr_window(window),
            campaigns=tuple(window.campaigns.all().values_list('id', flat=True))
        )
    )

def get_label_catgegory_insights(window, category):
    assert window
    label_ads_map = {}
    for text, ad_id in window.labels.all().filter(category=category, object_type='ad').values_list('text', 'object_id'):
        if text not in label_ads_map:
            label_ads_map[text] = [ad_id]
        else:
            label_ads_map[text].append(ad_id)

    for label_text, ads in label_ads_map.iteritems():
        yield label_text, aggregate_window_data(window,
            get_adaccount_insights(
                window.adaccount,
                get_attr_window(window),
                ads=tuple(ads)
            )
        )
