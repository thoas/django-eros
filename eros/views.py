from django.db import models
from django.views import generic
from django.views.generic.base import TemplateResponseMixin
from django.core.exceptions import SuspiciousOperation
from django.utils.html import escape
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.shortcuts import redirect

from eros.models import like
from eros.util import get_ip


class LikeView(TemplateResponseMixin, generic.View):
    http_method_names = ['post', 'get']
    using = None
    context_object_name = 'resource'
    template_name = 'eros/like.html'

    def get_context_data(self, **kwargs):
        ctype = kwargs.get("content_type")
        object_pk = kwargs.get("object_pk")

        if ctype is None or object_pk is None:
            raise SuspiciousOperation("Missing content_type or object_pk field.")
        try:
            model = models.get_model(*ctype.split(".", 1))
            target = model._default_manager.using(self.using).get(pk=object_pk)
        except TypeError:
            raise SuspiciousOperation(
                "Invalid content_type value: %r" % escape(ctype))
        except AttributeError:
            raise SuspiciousOperation(
                "The given content-type %r does not resolve to a valid model." % escape(ctype))
        except ObjectDoesNotExist:
            raise Http404("No object matching content-type %r and object PK %r exists." % (escape(ctype), escape(object_pk)))
        except (ValueError, ValidationError), e:
            raise SuspiciousOperation(
                "Attempting go get content-type %r and object PK %r exists raised %s" % (escape(ctype),
                                                                                         escape(object_pk),
                                                                                         e.__class__.__name__))
        return {
            self.context_object_name: target
        }

    def get(self, request, *args, **kwargs):
        self.request = request

        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.request = request

        context = self.get_context_data(**kwargs)

        obj = like(context[self.context_object_name],
                   user_ip=get_ip(request),
                   user=request.user if request.user.is_authenticated() else None)

        return redirect(reverse('eros_like', kwargs=kwargs))
