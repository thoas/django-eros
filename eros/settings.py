from django.conf import settings


EROS_CACHE_PREFIX = getattr(settings,
                            'EROS_CACHE_PREFIX',
                            'eros_')
