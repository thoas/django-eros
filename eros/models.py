from django.db import models
from django.db.models import signals
from django.contrib.auth.models import User
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _
from django.contrib.contenttypes import generic


class Resource(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType)
    object_id = models.PositiveSmallIntegerField(_('object id'), db_index=True)
    like_count = models.PositiveIntegerField(default=0, db_index=True)
    content_object = generic.GenericForeignKey(ct_field='content_type', fk_field='object_id')

    class Meta:
        unique_together = (('content_type', 'object_id'))

    def compute(self, commit=True):
        self.like_count = self.likes.count()

        if commit:
            self.save()


class LikeManager(models.Manager):
    def contribute_to_class(self, cls, name):
        signals.post_save.connect(self.post_save, sender=cls)
        return super(LikeManager, self).contribute_to_class(cls, name)

    def post_save(self, instance, **kwargs):
        if kwargs['created']:
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
    user = models.ForeignKey(User, null=True, blank=True)
    ip_address = models.IPAddressField(_('IP Address'),
                                       help_text=_('The IP address'))
    created = models.DateTimeField(auto_now_add=True)

    resource = models.ForeignKey(Resource, related_name='likes')

    objects = LikeManager()


def like(obj, user_ip, user=None):
    content_type = ContentType.objects.get_for_model(obj)

    resource, created = Resource.objects.get_or_create(content_type=content_type,
                                                       object_id=obj.pk)

    return Like.objects.create(resource=resource,
                               ip_address=user_ip,
                               user=user)
