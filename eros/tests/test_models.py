from django.test import TestCase
from django.contrib.auth.models import User

from eros.models import like, Like
from eros.tests.models import Poll


class LikeTests(TestCase):
    def test_like(self):
        poll = Poll.objects.create(
            question='What is my name?'
        )

        user = User.objects.create_user('newbie', 'newbie@localhost', '$ecret')

        obj = like(poll, user_ip='127.0.0.1', user=user)

        self.assertEqual(obj.resource.like_count, 1)

        self.assertEqual(Like.objects.get_count(obj=poll, user_ip='127.0.0.1'), 1)

        self.assertEqual(Like.objects.get_count(obj=poll), 1)
