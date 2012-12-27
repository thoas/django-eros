from django.conf.urls.defaults import patterns, include

import eros

eros.autodiscover()


urlpatterns = patterns(
    '',
    (r'^', include('eros.urls')),
)
