from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic

from django.core.cache import get_cache

from eros.settings import EROS_CACHE_PREFIX, EROS_CACHE_ALIAS

cache = get_cache(EROS_CACHE_ALIAS)


def make_key_from_obj(obj, suffix=None):
    return make_key('.'.join(ContentType.objects.get_for_model(obj).natural_key()), obj.pk, suffix or '')


def make_key(ctype, object_pk, suffix=None):
    return EROS_CACHE_PREFIX + '%s:%s:%s' % (ctype,
                                             object_pk,
                                             suffix or '')


class ResourceManager(models.Manager):
    pass


class ResourceCacheManager(models.Manager):
    def get_count(self, ctype, object_pk):
        cache_key = make_key(ctype, object_pk, 'count')

        count = cache.get(cache_key, False) or False

        if count is False:
            try:
                resource = self.model.objects.get(content_type=self._get_ctype(ctype), object_id=object_pk)
            except self.model.DoesNotExist:
                count = 0
            else:
                count = resource.like_count

            cache.set(cache_key, count)

        return count

    def is_liker(self, ctype, object_pk, user):
        cache_key = make_key(ctype, object_pk, 'users')

        results = cache.get(cache_key, None)

        if results is None:
            count = self.get_count(ctype, object_pk)

            results = ''

            if count:
                content_type = self._get_ctype(ctype)

                likes = (Like.objects.filter(resource__content_type=content_type,
                                             resource__object_id=object_pk).values_list('user'))

                results = '|'.join([str(like[0]) for like in likes])

            cache.set(cache_key, results)

        return str(user.pk) in results.split('|')

    def _get_ctype(self, ctype):
        return ContentType.objects.get_for_model(models.get_model(*ctype.split('.')))


class Resource(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveIntegerField(_('object id'), db_index=True)
    like_count = models.PositiveIntegerField(default=0, db_index=True)
    content_object = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')
    user = models.ForeignKey(User, null=True, blank=True)

    objects = ResourceManager()
    cache = ResourceCacheManager()

    class Meta:
        unique_together = (('content_type', 'object_id'))

    def compute(self, commit=True):
        self.like_count = self.likes.count()

        self.sync_cache()

        if commit:
            self.save()

    def sync_count(self):
        ctype = '.'.join(self.content_type.natural_key())

        count_key = make_key(ctype, self.object_id, 'count')

        cache.set(count_key, self.like_count)

        return self.like_count

    def sync_users(self):
        ctype = '.'.join(self.content_type.natural_key())

        users_key = make_key(ctype, self.object_id, 'users')

        user_keys = '|'.join([str(like[0]) for like in self.likes.values_list('user')])

        cache.set(users_key, user_keys)

        return user_keys

    def sync_cache(self):
        self.sync_count()
        self.sync_users()


class LikeManager(models.Manager):
    def contribute_to_class(self, cls, name):
        signals.post_save.connect(self.post_save, sender=cls)
        signals.post_delete.connect(self.post_delete, sender=cls)
        return super(LikeManager, self).contribute_to_class(cls, name)

    def post_save(self, instance, **kwargs):
        if kwargs['created']:
            instance.resource.compute()

    def post_delete(self, instance, **kwargs):
        instance.resource.compute()

    def get_count(self, obj, user=None, user_ip=None):
        content_type = ContentType.objects.get_for_model(obj)

        if not user and not user_ip:
            return Resource.objects.get(content_type=content_type,
                                        object_id=obj.pk).like_count

        filters = {
            'resource__content_type': content_type,
            'resource__object_id': obj.pk
        }

        if user:
            filters['user'] = user

        if user_ip:
            filters['ip_address'] = user_ip

        return self.filter(**filters).count()


class Like(models.Model):
    user = models.ForeignKey(User)
    ip_address = models.IPAddressField(_('IP Address'),
                                       help_text=_('The IP address'),
                                       null=True,
                                       blank=True)
    created = models.DateTimeField(auto_now_add=True)

    resource = models.ForeignKey(Resource, related_name='likes')

    objects = LikeManager()


def like(obj, user_ip, user, author=None):
    content_type = ContentType.objects.get_for_model(obj)

    resource, created = Resource.objects.get_or_create(content_type=content_type, object_id=obj.pk)

    if created and author:
        resource.user = author
        resource.save()

    like, created = Like.objects.get_or_create(resource=resource,
                                               user=user)

    if created:
        like.ip_address = user_ip
        like.save()

    return created


def unlike(obj, user):
    return (Like.objects.filter(resource__content_type=ContentType.objects.get_for_model(obj),
                                resource__object_id=obj.pk,
                                user=user).delete())
