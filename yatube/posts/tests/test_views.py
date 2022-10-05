import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User

INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=['slugtest'])
NOT_GROUP_URL = reverse('posts:group_list', args=['slugtest_2'])
PROFILE_URL = reverse('posts:profile', args=['Vlad0n4uk'])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=['Vlad0n4uk'])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=['Vlad0n4uk'])
NAME_GIF = 'posts/small.gif'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username='Vlad0n4uk')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slugtest',
            description='Тестовое описание',
        )
        cls.small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name=NAME_GIF,
            content=cls.small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
            image=cls.image
        )
        cls.group_2 = Group.objects.create(
            title='Тестовая группа-2',
            slug='slugtest_2',
            description='Тестовое описание-2',
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.pk]
        )
        cls.follower = User.objects.create_user(username='follower')

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.auth_follower = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.auth_follower.force_login(self.follower)
        self.POST_DETAIL_ARGS = reverse(
            'posts:post_detail', args=[self.post.pk]
        )
        cache.clear()

    def test_post_at_different_pages(self):
        pages_list = [
            [INDEX_URL, {'is_page_obj_in': True}],
            [GROUP_URL, {'is_page_obj_in': True}],
            [PROFILE_URL, {'is_page_obj_in': True}],
            [self.POST_DETAIL_URL, {'is_page_obj_in': False}],
        ]
        for url, flag in pages_list:
            with self.subTest(address=url):
                response = self.client.get(url)
                if flag['is_page_obj_in']:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context.get('post')
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.user)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.image, self.post.image)

    def test_post_in_correct_group(self):
        response = self.authorized_client.get(NOT_GROUP_URL)
        self.assertNotIn(self.post, response.context['page_obj'])

    def test_group_in_correct_group(self):
        group = self.authorized_client.get(GROUP_URL).context['group']
        self.assertEqual(self.group.id, group.id)
        self.assertEqual(self.group.title, group.title)
        self.assertEqual(self.group.slug, group.slug)
        self.assertEqual(self.group.description, group.description)

    def test_author_in_profile(self):
        response = self.authorized_client.get(PROFILE_URL)
        self.assertEqual(self.user, response.context['author'])

    def test_index_page_cache(self):
        first_content = self.authorized_client.get(INDEX_URL).content
        Post.objects.all().delete()
        self.assertEqual(
            first_content,
            (self.authorized_client.get(INDEX_URL).content)
        )
        cache.clear()
        self.assertNotEqual(
            first_content,
            (self.authorized_client.get(INDEX_URL).content)
        )

    def test_follow_posts(self):
        Follow.objects.create(user=self.follower,
                              author=self.user)
        self.assertEqual(Follow.objects.count(), 1)
        "Отправляем POST-запрос и проверяем нет ли повторной подписки"
        self.auth_follower.post(FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), 1)
        "Проверяем наличие поста в ленте подписок у подписчика"
        self.assertEqual(len(self.auth_follower.get(
            FOLLOW_INDEX_URL).context['page_obj']), 1)
        "Проверяем наличие поста в ленте подписок у не-подписчика"
        self.assertEqual(len(self.authorized_client.get(
            FOLLOW_INDEX_URL).context['page_obj']), 0)

    def test_follow_and_unfollow(self):
        form_data = {
            'author': self.user,
            'user': self.follower
        }
        # Отправляем POST-запрос
        self.auth_follower.post(
            FOLLOW_URL,
            data=form_data,
            follow=True
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            ).exists()
        )
        self.auth_follower.post(
            UNFOLLOW_URL,
            data=form_data,
            follow=True
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            ).exists()
        )
