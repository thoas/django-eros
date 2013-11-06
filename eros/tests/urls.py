from django.conf.urls import patterns, include

import eros

eros.autodiscover()


urlpatterns = patterns(
    '',
    (r'^', include('eros.urls')),
)
