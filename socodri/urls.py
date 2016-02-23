from django.conf.urls import include, patterns
from socodri import views, resources


urlpatterns = patterns('',
    (r'^api/initiative/', include(resources.InitiativeResource.urls())),
    (r'^api/window/', include(resources.WindowResource.urls())),
    (r'^api/action/', include(resources.ActionResource.urls())),
    (r'^api/stage/', include(resources.StageResource.urls())),
    (r'^api/label/', include(resources.LabelResource.urls())),
    (r'^ping/$', views.ping),
    (r'^.*/$', views.show_app),
    (r'^$', views.show_app)
)
