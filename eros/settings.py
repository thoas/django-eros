from django.conf import settings

from django.core.cache import DEFAULT_CACHE_ALIAS


EROS_CACHE_PREFIX = getattr(settings,
                            'EROS_CACHE_PREFIX',
                            'eros_')

EROS_CACHE_ALIAS = getattr(settings,
                           'EROS_CACHE_ALIAS',
                           DEFAULT_CACHE_ALIAS)
