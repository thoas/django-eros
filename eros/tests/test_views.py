from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType

from eros.models import Like
from eros.tests.models import Poll


class ViewTests(TestCase):
    def setUp(self):
        self.poll = Poll.objects.create(
            question='What is my name?'
        )

        self.content_type = ContentType.objects.get_for_model(Poll)

    def test_like_view(self):
        response = self.client.get(reverse('eros_like', kwargs={
            'content_type': '%s.%s' % (Poll._meta.app_label, self.content_type),
            'object_pk': self.poll.pk
        }))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response,
                                'eros/like.html')

    def test_like_complete(self):
        like_url = reverse('eros_like', kwargs={
            'content_type': '%s.%s' % (Poll._meta.app_label, self.content_type),
            'object_pk': self.poll.pk
        })

        response = self.client.post(like_url)

        self.assertRedirects(response, like_url)

        self.assertEqual(Like.objects.get_count(obj=self.poll), 1)
