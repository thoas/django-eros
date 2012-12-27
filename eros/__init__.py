version = (0, 1, 'alpha')

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover
