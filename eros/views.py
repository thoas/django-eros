from django.db import models
from django.views import generic
from django.views.generic.base import TemplateResponseMixin
from django.core.exceptions import SuspiciousOperation
from django.utils.html import escape
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.http import Http404
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

from eros.models import like, Resource, unlike, Like
from eros.util import get_ip
from eros.registry import registry


class LikeViewMixin(object):
    http_method_names = ['get', 'post']
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

    def get_eros(self, model):
        eros = registry.eros_for_model(model)

        if not eros:
            raise SuspiciousOperation(
                'The given model %r does not resolve to a register eros model.' % repr(model))

        return eros

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


class LikeView(TemplateResponseMixin, LikeViewMixin, generic.View):
    template_name = 'eros/like.html'

    def get_context_data(self, **kwargs):
        ctype = self.request.GET.get('ctype', '')
        object_pk = self.request.GET.get('object_pk', '')

        if ctype is None or object_pk is None:
            raise SuspiciousOperation('Missing content_type or object_pk field.')

        self.model = self.get_model(ctype)

        self.eros = self.get_eros(self.model)

        is_liker = False

        if self.request.user.is_authenticated():
            is_liker = Resource.cache.is_liker(ctype, object_pk, self.request.user)

        return {
            'count': Resource.cache.get_count(ctype, object_pk),
            'ctype': ctype,
            'object_pk': object_pk,
            'is_liker': is_liker
        }

    def get(self, request, *args, **kwargs):
        self.request = request

        context = self.get_context_data(**kwargs)

        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        self.request = request

        context = self.get_context_data(**kwargs)

        if request.user.is_authenticated():
            obj = self.get_object(context['object_pk'])

            result = like(obj,
                          user_ip=get_ip(request),
                          user=request.user,
                          author=self.eros().get_author(obj))

            if result is False:
                unlike(self.get_object(context['object_pk']),
                       user=request.user)

            context = self.get_context_data(**kwargs)

        return redirect(reverse('eros_like') + '?ctype=%s&object_pk=%s' % (context.get('ctype'),
                                                                           context.get('object_pk')))


class LikeListView(LikeViewMixin, generic.ListView):
    http_method_names = ['get']
    template_name = 'eros/like_list.html'
    context_object_name = 'likes'
    paginate_by = 5

    def get_queryset(self):
        self.ctype = self.request.GET.get('ctype', '')
        self.object_pk = self.request.GET.get('object_pk', '')

        if self.ctype is None or self.object_pk is None:
            raise SuspiciousOperation('Missing content_type or object_pk field.')

        self.model = self.get_model(self.ctype)

        self.object = self.get_object(self.object_pk)

        likes = (Like.objects.filter(resource__content_type=ContentType.objects.get_for_model(self.model),
                                     resource__object_id=self.object_pk)
                 .select_related('user')
                 .order_by('-created'))

        return likes

    def get_context_data(self, **kwargs):
        context = dict(super(LikeListView, self).get_context_data(**kwargs), **{
            'ctype': self.ctype,
            'object_pk': self.object_pk,
            'object': self.object,
        })

        return context
