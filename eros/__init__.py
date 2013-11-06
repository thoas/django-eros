version = (0, 2, 1)

__version__ = '.'.join(map(str, version))

from .registry import register, autodiscover

__all__ = ['register', 'autodiscover']
