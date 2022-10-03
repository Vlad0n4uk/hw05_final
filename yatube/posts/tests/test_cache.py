from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User

INDEX_URL = reverse('posts:index')


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
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
        cls.INDEX_URL = reverse('posts:index')

    def setUp(self):
        self.author = Client()
        self.author.force_login(self.user)

    def test_index_page_cache(self):
        first_content = self.author.get(reverse('posts:index')).content
        self.post.delete()
        self.assertEqual(
            first_content,
            (self.author.get(reverse('posts:index')).content)
        )
        cache.clear()
        self.assertNotEqual(
            first_content,
            (self.author.get(reverse('posts:index')).content)
        )
