from django.test import TestCase

from eros.models import like, Like, unlike, Resource

from .models import Poll


class LikeTests(TestCase):
    def setUp(self):
        from eros.compat import User

        self.poll = Poll.objects.create(
            question='What is my name?'
        )

        self.user = User.objects.create_user('newbie', 'newbie@localhost', '$ecret')

    def test_like(self):
        like(self.poll, user_ip='127.0.0.1', user=self.user)

        obj = Like.objects.get(user=self.user)

        self.assertEqual(obj.resource.like_count, 1)

        self.assertEqual(Like.objects.get_count(obj=self.poll, user_ip='127.0.0.1'), 1)

        self.assertEqual(Like.objects.get_count(obj=self.poll), 1)

    def test_unlike(self):
        like(self.poll, user_ip='127.0.0.1', user=self.user)

        obj = Like.objects.get(user=self.user)

        self.assertEqual(obj.resource.like_count, 1)

        unlike(self.poll, user=self.user)

        resource = Resource.objects.get(pk=obj.resource.pk)

        self.assertEqual(resource.like_count, 0)
