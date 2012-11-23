from django.conf.urls.defaults import patterns, url

from eros import views


urlpatterns = patterns(
    '',
    url(r'^like/(?P<content_type>[a-z\.]+)/(?P<object_pk>[\d]+)/$',
        views.LikeView.as_view(),
        name='eros_like'),
)
