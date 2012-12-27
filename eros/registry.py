from .base import ErosModelBase


class ErosRegistry(dict):
    def __init__(self):
        self._models = {}

    def eros_for_model(self, model):
        try:
            return self._models[model]
        except KeyError:
            return

    def unregister(self, name):
        del self[name]

    def register(self, *args, **kwargs):
        from django.db import models

        eros = None
        model = None

        assert len(args) <= 2, 'register takes at most 2 args'
        assert len(args) > 0, 'register takes at least 1 arg'

        for arg in args:
            if issubclass(arg, models.Model):
                model = arg
            else:
                eros = arg

        if model:
            self._register_model_eros(model, eros, **kwargs)
        else:
            name = kwargs.get('name', eros.__name__)
            eros = type(name, (eros,), kwargs)
            self._register_eros(eros)

    def _register_model_eros(self, model, eros=None,
                             name=None, **kwargs):

        if name is not None:
            pass
        elif eros is not None:
            if eros.__name__.find(model.__name__) == 0:
                name = eros.__name__
            else:
                name = '%s%s' % (model.__name__, eros.__name__)
        else:
            name = '%sEros' % model.__name__

        if eros is None:
            base = ErosModelBase
        else:
            base = eros

        eros = type(name, (base,), kwargs)

        self._register_eros(eros)
        self._models[model] = eros

    def _register_eros(self, eros):
        self[eros.__name__] = eros


def _autodiscover(registry):
    import copy
    from django.conf import settings
    from django.utils.importlib import import_module
    from django.utils.module_loading import module_has_submodule

    for app in settings.INSTALLED_APPS:
        mod = import_module(app)
        # Attempt to import the app's admin module.
        try:
            before_import_registry = copy.copy(registry)
            import_module('%s.eros_registry' % app)
        except:
            # Reset the model registry to the state before the last import as
            # this import will have to reoccur on the next request and this
            # could raise NotRegistered and AlreadyRegistered exceptions
            # (see #8245).
            registry = before_import_registry

            # Decide whether to bubble up this error. If the app just
            # doesn't have an admin module, we can ignore the error
            # attempting to import it, otherwise we want it to bubble up.
            if module_has_submodule(mod, 'eros_registry'):
                raise

registry = ErosRegistry()


def autodiscover():
    _autodiscover(registry)


def register(*args, **kwargs):
    return registry.register(*args, **kwargs)
