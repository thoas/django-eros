from django.db import models
from django.views import generic
from django.core.exceptions import SuspiciousOperation
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404

from eros.models import like, Resource
from eros.util import get_ip
from eros.http import JSONResponse


class BaseLikeView(generic.View):
    http_method_names = ['get']
    using = None

    def get_model(self, ctype):
        try:
            model = models.get_model(*ctype.split('.', 1))
        except TypeError:
            raise SuspiciousOperation(
                'Invalid content_type value: %r' % escape(ctype))
        except AttributeError:
            raise SuspiciousOperation(
                'The given content-type %r does not resolve to a valid model.' % escape(ctype))
        return model

    def get_object(self, object_pk):
        try:
            obj = self.model._default_manager.using(self.using).get(pk=object_pk)
        except ObjectDoesNotExist:
            raise Http404('No object matching content-type %r and object PK %r exists.' % (escape(self.model), escape(object_pk)))
        except (ValueError, ValidationError), e:
            raise SuspiciousOperation(
                'Attempting go get content-type %r and object PK %r exists raised %s' % (escape(self.model),
                                                                                         escape(object_pk),
                                                                                         e.__class__.__name__))
        return obj


class LikeView(BaseLikeView):
    def get_context_data(self, **kwargs):
        ctype = self.request.GET.get('ctype', '')
        object_pk = self.request.GET.get('object_pk', '')

        if ctype is None or object_pk is None:
            raise SuspiciousOperation('Missing content_type or object_pk field.')

        self.model = self.get_model(ctype)

        return {
            'count': Resource.cache.get_count(ctype, object_pk),
            'ctype': ctype,
            'object_pk': object_pk
        }

    def get(self, request, *args, **kwargs):
        self.request = request

        submit = self.request.GET.get('submit', False)

        context = self.get_context_data(**kwargs)

        if submit and request.user.is_authenticated():
            like(self.get_object(context['object_pk']),
                 user_ip=get_ip(request),
                 user=request.user)

            context = self.get_context_data(**kwargs)

        return JSONResponse(context, callback=request.GET.get('callback', ''))


class LikeListView(BaseLikeView):
    pass
