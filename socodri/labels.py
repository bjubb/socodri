from socodri import utils


def avon_jan(insights_data):
    ad_labels = lambda x: dict(Creative=utils.uncamel(x[0]), WCA=x[1][:-3], Placement=x[2])
    adset_labels = lambda x: dict(WCA=x[0][:-3], Placement=x[1].split(' |')[0]) if 'WCA' in x[0] else dict(CRM=utils.uncamel('-'.join(x[:-1])), Placement=x[-1].split(' |')[0])
    def _labels(ad_insight):
        l = adset_labels(ad_insight.get('adset_name').split('-'))
        l.update(ad_labels(ad_insight.get('ad_name').split('-')))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))


def solarcity_video(insights_data):
    ad_labels = lambda x: {'Page Post': x[2]}
    adset_labels = lambda x: {'Retargeting': utils.uncamel(x[2].split('|')[0])}
    def _labels(ad_insight):
        l = adset_labels(ad_insight.get('adset_name').split('_'))
        l.update(ad_labels(ad_insight.get('ad_name').split('_')))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))


def solarcity_instagram(insights_data):
    adset_labels = lambda x: {'Channel': utils.uncamel(x[2].split('|')[0])}
    def _labels(ad_insight):
        l = adset_labels(ad_insight.get('adset_name').split('_'))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))


def solarcity_bid(insights_data):
    campaign_labels = lambda x: {'Bid Type': x[2].split(' ')[0]}
    def _labels(ad_insight):
        l = campaign_labels(ad_insight.get('campaign_name').split('_'))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))


def solarcity_seed(insights_data):
    campaign_labels = lambda x: {'Seed': utils.uncamel(x[2])}
    def _labels(ad_insight):
        l = campaign_labels(ad_insight.get('campaign_name').split('_'))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))


def solarcity_adunit(insights_data):
    campaign_labels = lambda x: {'Ad Unit': utils.uncamel(x[2])}
    def _labels(ad_insight):
        l = campaign_labels(ad_insight.get('campaign_name').split('_'))
        return ad_insight.get('ad_id'), l
    return dict(map(_labels, insights_data))
