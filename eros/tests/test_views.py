from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User

from eros.models import Like
from eros.tests.models import Poll


class ViewTests(TestCase):
    def setUp(self):
        self.poll = Poll.objects.create(
            question='What is my name?'
        )

        self.content_type = ContentType.objects.get_for_model(Poll)

        self.user = User.objects.create_user('newbie', 'newbie@localhost', '$ecret')

    def test_like_view(self):
        querystring = '?ctype=%s&object_pk=%s' % ('%s.%s' % (Poll._meta.app_label, self.content_type), self.poll.pk)

        response = self.client.get(reverse('eros_like') + querystring)

        self.assertEqual(response.status_code, 200)

    def test_like_complete(self):

        self.client.login(username='newbie', password='$ecret')

        like_url = reverse('eros_like', )

        querystring = '?ctype=%s&object_pk=%s' % ('%s.%s' % (Poll._meta.app_label, self.content_type), self.poll.pk)

        response = self.client.post(like_url + querystring)

        self.assertEqual(response.status_code, 302)

        self.assertEqual(Like.objects.get_count(obj=self.poll), 1)
