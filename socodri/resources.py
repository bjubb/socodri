from restless import dj
from restless.resources import skip_prepare
from django.db.models import Count
from django.conf import settings
from django.conf.urls import patterns, url
from socodri import authorization, models, preparers, insights, utils


class InsightsMixin(object):
    def __init__(self, *args, **kwargs):
        super(InsightsMixin, self).__init__(*args, **kwargs)

        self.http_methods.update({
            'insights_detail': {
                'GET': 'insights_detail',
            },
            'insights_list': {
                'GET': 'insights_list',
            }
        })

    @classmethod
    def urls(cls, name_prefix=None):
        "Add insights edge"
        urlpatterns = super(InsightsMixin, cls).urls(name_prefix=name_prefix)
        return urlpatterns + patterns('',
            url(r'^(?P<pk>\d+)/insights/$', cls.as_view('insights_detail'), name=cls.build_url_name('insights', name_prefix)),
            url(r'^(?P<slug>[\w-]+)/insights/$', cls.as_view('insights_detail'), name=cls.build_url_name('insights', name_prefix)),
            url(r'^insights/$', cls.as_view('insights_list'), name=cls.build_url_name('insights', name_prefix))
        )

    @skip_prepare
    def insights_detail(self, pk=None, slug=None):
        return {
            'data': {'spend': 0.00, 'conversions': 0, 'conversion_revenue': 0.00}
        }

    @skip_prepare
    def insights_list(self):
        return []


class GetCurrentUserMixin(object):
    def is_authenticated(self):
        self.request.user = utils.get_current_user(self.request.COOKIES)
        return self.request.user is not None


class AuthorizationMixin(object):
    def is_authorized(self):
        return authorization.is_request_authorized(self.request)

    def get_authorized_queryset(self):
        assert self.model
        using_whiltelist = {
            'pk__in': settings.WHITELISTED_INITIATIVES.get(self.request.user.get('id'), [])
        }
        return self.model.objects.all()


class InitiativeResource(GetCurrentUserMixin, AuthorizationMixin, InsightsMixin, dj.DjangoResource):
    name_prefix = 'initiative'
    model = models.Initiative
    preparer = preparers.LaxFieldsPreparer(fields={
        'id': 'id',
        'slug': 'slug',
        'name': 'name',
        'brand_id': 'brand_id',
        'brand_name': 'brand_name',
        'conversion_name': 'conversion_name'
    })

    @classmethod
    def urls(cls, name_prefix=None):
        "Add slug detail view"
        name_prefix = name_prefix or cls.name_prefix
        urlpatterns = super(InitiativeResource, cls).urls(name_prefix=name_prefix)
        return urlpatterns + patterns('',
            url(r'^(?P<slug>[\w-]+)/$', cls.as_detail(), name=cls.build_url_name('detail', name_prefix)),
        )

    def list(self):
        return self.get_authorized_queryset()

    def _get_lookup_filter(self, pk=None, slug=None):
        return pk and {'pk': pk} or {'slug': slug}

    def detail(self, pk=None, slug=None):
        return self.get_authorized_queryset().filter(**self._get_lookup_filter(pk, slug)).first()

    @skip_prepare
    def insights_detail(self, pk=None, slug=None):
        initiative = models.Initiative.objects.filter(**self._get_lookup_filter(pk, slug)).first()
        return {'data': insights.get_bimonthly_insights(initiative)}


class WindowResource(GetCurrentUserMixin, AuthorizationMixin, InsightsMixin, dj.DjangoResource):
    name_prefix = 'window'
    model = models.Window
    preparer = preparers.LaxFieldsPreparer(fields={
        'id': 'id',
        'slug': 'slug',
        'name': 'name',
        'adaccount': 'adaccount.name',
        'conversion_name': 'conversion_name'
    })

    @classmethod
    def urls(cls, name_prefix=None):
        "Add slug detail view"
        name_prefix = name_prefix or cls.name_prefix
        urlpatterns = super(WindowResource, cls).urls(name_prefix=name_prefix)
        return urlpatterns + patterns('',
            url(r'^(?P<slug>[\w-]+)/$', cls.as_detail(), name=cls.build_url_name('detail', name_prefix)),
        )

    def list(self):
        initiative = self.request.GET.get('initiative')
        all_windows = models.Window.objects.all()
        windows = all_windows.filter(initiative=initiative) if initiative else all_windows
        return windows

    def _get_lookup_filter(self, pk=None, slug=None):
        return pk and {'pk': pk} or {'slug': slug}

    def detail(self, pk=None, slug=None):
        return self.get_authorized_queryset().filter(**self._get_lookup_filter(pk, slug)).first()

    @skip_prepare
    def insights_detail(self, pk=None, slug=None):
        window = models.Window.objects.filter(**self._get_lookup_filter(pk, slug)).first()
        daily = self.request.GET.get('daily', False)
        return {'data': insights.get_daily_window_insights(window) if daily else insights.get_window_insights(window)}


class ActionResource(dj.DjangoResource):
    preparer = preparers.LaxFieldsPreparer(fields={
        'id': 'id',
        'pixel_id': 'pixel_id',
        'pixel_name': 'pixel.name',
        'name': 'name',
        'tag': 'tag'
    })

    def list(self):
        stage = self.request.GET.get('stage')
        all_actions = models.Action.objects.all()
        return all_actions.filter(stage=stage) if stage else all_actions

    def detail(self, pk):
        return models.Action.objects.get(id=pk)


class StageResource(InsightsMixin, dj.DjangoResource):
    preparer = preparers.LaxFieldsPreparer(fields={
        'id': 'id',
        'name': 'name',
        'number': 'number',
        'window_id': 'window_id',
    })

    def list(self):
        window = self.request.GET.get('window')
        all_stages = models.Stage.objects.all()
        stages = all_stages.filter(window=window) if window else all_stages
        return stages

    def detail(self, pk):
        return models.Stage.objects.get(pk=pk)

    @skip_prepare
    def insights_list(self):
        window = self.request.GET.get('window')
        return {'data': insights.get_stage_insights(models.Window.objects.get(id=window))}

class LabelResource(InsightsMixin, dj.DjangoResource):
    preparer = preparers.LaxFieldsPreparer(fields={
        'id': 'id',
        'window_id': 'window_id',
        'category': 'category',
        'text': 'text',
        'object_type': 'object_type',
        'object_id': 'object_id',
        'platform': 'platform'
    })

    def __init__(self, *args, **kwargs):
        super(LabelResource, self).__init__(*args, **kwargs)

        self.http_methods.update({
            'categories': {
                'GET': 'categories',
            }
        })

    @classmethod
    def urls(cls, name_prefix=None):
        urlpatterns = super(LabelResource, cls).urls(name_prefix=name_prefix)
        return urlpatterns + patterns('',
            url(r'^categories/$', cls.as_view('categories'), name=cls.build_url_name('categories', name_prefix))
        )

    def list(self):
        window = self.request.GET.get('window', 0)
        return models.Label.objects.all().filter(window=window)

    def detail(self, pk):
        return models.Label.objects.get(pk=pk)

    @skip_prepare
    def categories(self):
        window = self.request.GET.get('window', 0)
        categories = set(models.Label.objects.all().filter(window=window).values_list('category', flat=True))
        return {
            'data': tuple(sorted(categories))
        }

    @skip_prepare
    def insights_list(self):
        window = self.request.GET.get('window')
        category = self.request.GET.get('category')
        data = dict(
            insights.get_label_catgegory_insights(
                models.Window.objects.get(id=window),
                category
            )
        )
        return {'data': data}
