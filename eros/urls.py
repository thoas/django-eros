from django.conf.urls import patterns, url

from eros import views


urlpatterns = patterns(
    '',
    url(r'^like/$',
        views.LikeView.as_view(),
        name='eros_like'),
    url(r'^like/list/$',
        views.LikeListView.as_view(),
        name='eros_like_list'),
)
