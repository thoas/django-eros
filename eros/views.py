from django.db import models
from django.views import generic
from django.views.generic.base import TemplateResponseMixin
from django.core.exceptions import SuspiciousOperation
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.shortcuts import redirect

from eros.models import like, Resource
from eros.util import get_ip


class LikeView(TemplateResponseMixin, generic.View):
    http_method_names = ['post', 'get']
    using = None
    template_name = 'eros/like.html'

    def get_context_data(self, **kwargs):
        ctype = kwargs.get("content_type")
        object_pk = kwargs.get("object_pk")

        if ctype is None or object_pk is None:
            raise SuspiciousOperation("Missing content_type or object_pk field.")

        self.model = self.get_model(ctype)

        return {
            'count': Resource.objects.get_cache_count(ctype, object_pk)
        }

    def get_model(self, ctype):
        try:
            model = models.get_model(*ctype.split(".", 1))
        except TypeError:
            raise SuspiciousOperation(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            raise SuspiciousOperation(
                "The given content-type %r does not resolve to a valid model." % escape(ctype))
        return model

    def get_object(self, object_pk):
        try:
            obj = self.model._default_manager.using(self.using).get(pk=object_pk)
        except ObjectDoesNotExist:
            raise Http404("No object matching content-type %r and object PK %r exists." % (escape(self.model), escape(object_pk)))
        except (ValueError, ValidationError), e:
            raise SuspiciousOperation(
                "Attempting go get content-type %r and object PK %r exists raised %s" % (escape(self.model),
                                                                                         escape(object_pk),
                                                                                         e.__class__.__name__))
        return obj

    def get(self, request, *args, **kwargs):
        self.request = request

        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.request = request

        self.get_context_data(**kwargs)

        like(self.get_object(kwargs['object_pk']),
             user_ip=get_ip(request),
             user=request.user if request.user.is_authenticated() else None)

        return redirect(reverse('eros_like', kwargs=kwargs))
