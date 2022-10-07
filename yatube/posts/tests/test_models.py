from django.test import TestCase
from django.urls import reverse

from ..models import Comment, Follow, Group, Post, User

USER = 'Vlad0n4uk'
FOLLOWER = 'follower'
FOLLOW_URL = reverse('posts:profile_follow', args=[USER])


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=FOLLOWER)
        cls.author = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовая пост',
            author=cls.user,
            group=cls.group
        )
        cls.comment = Comment.objects.create(
            text='comment',
            author=cls.author,
            post=cls.post
        )
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_post = (
            f'{self.post.text:.15}, '
            f'{self.post.pub_date}, '
            f'{self.post.group}'

        )
        str_comment = (
            f'text={self.comment.text:.15}, '
            f'pub_date={self.comment.pub_date}'
        )
        str_follow = (
            f'user={self.follow.user} '
            f'подписан на author={self.follow.author}'
        )
        cases = [
            [str_post, self.post],
            [self.group.title, self.group],
            [str_follow, self.follow],
            [str_comment, self.comment],
        ]
        for expected, model in cases:
            with self.subTest():
                self.assertEqual(expected, str(model))
