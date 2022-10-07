import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Follow, Group, Post, User
from posts.settings import COUNT_POST_ON_PAGE

COUNT_LAST_PAGE_POSTS = 3
USER = 'Vlad0n4uk'
FOLLOWER = 'follower'
SLUG_1 = 'slugtest'
SLUG_2 = 'slugtest_2'
INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=['slugtest'])
NOT_GROUP_URL = reverse('posts:group_list', args=['slugtest_2'])
PROFILE_URL = reverse('posts:profile', args=[USER])
FOLLOW_INDEX_URL = reverse('posts:follow_index')
FOLLOW_URL = reverse('posts:profile_follow', args=[USER])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[USER])
GROUP_URL_LAST_PAGE = GROUP_URL + '?page=2'
PROFILE_URL_LAST_PAGE = PROFILE_URL + '?page=2'
INDEX_URL_LAST_PAGE = INDEX_URL + '?page=2'
FOLLOW_INDEX_URL_LAST_PAGE = FOLLOW_INDEX_URL + '?page=2'
NAME_GIF = 'posts/small.gif'
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Создаем пользователя
        cls.user = User.objects.create_user(username=USER)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG_1,
            description='Тестовое описание',
        )
        cls.image = SimpleUploadedFile(
            name=NAME_GIF,
            content=(
                b'\x47\x49\x46\x38\x39\x61\x02\x00'
                b'\x01\x00\x80\x00\x00\x00\x00\x00'
                b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
                b'\x00\x00\x00\x2C\x00\x00\x00\x00'
                b'\x02\x00\x01\x00\x00\x02\x02\x0C'
                b'\x0A\x00\x3B'
            ),
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
            slug=SLUG_2,
            description='Тестовое описание-2',
        )
        cls.POST_DETAIL_URL = reverse(
            'posts:post_detail', args=[cls.post.pk]
        )
        cls.follower = User.objects.create_user(username=FOLLOWER)
        cls.guest_client = Client()
        cls.authorized_client = Client()
        cls.auth_follower = Client()
        # Авторизуем пользователя
        cls.authorized_client.force_login(cls.user)
        cls.auth_follower.force_login(cls.follower)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_at_different_pages(self):
        self.auth_follower.get(FOLLOW_URL)
        pages_list = [
            [INDEX_URL, {'is_page_obj_in': True}],
            [GROUP_URL, {'is_page_obj_in': True}],
            [PROFILE_URL, {'is_page_obj_in': True}],
            [FOLLOW_INDEX_URL, {'is_page_obj_in': True}],
            [self.POST_DETAIL_URL, {'is_page_obj_in': False}],
        ]
        for url, flag in pages_list:
            with self.subTest(address=url):
                response = self.auth_follower.get(url)
                if flag['is_page_obj_in']:
                    self.assertEqual(len(response.context['page_obj']), 1)
                    post = response.context['page_obj'][0]
                else:
                    post = response.context.get('post')
                self.assertEqual(post.text, self.post.text)
                self.assertEqual(post.author, self.post.author)
                self.assertEqual(post.group, self.post.group)
                self.assertEqual(post.id, self.post.id)
                self.assertEqual(post.image, self.post.image)

    def test_post_in_correct_page(self):
        urls = [NOT_GROUP_URL, FOLLOW_INDEX_URL]
        for url in urls:
            self.assertNotIn(self.post, self.authorized_client.get(
                url).context['page_obj'])

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
        follows = Follow.objects.count()
        "Отправляем GET-запрос и проверяем нет ли повторной подписки"
        self.auth_follower.get(FOLLOW_URL)
        self.assertEqual(Follow.objects.count(), follows)
        "Проверяем наличие поста в ленте подписок у подписчика"
        self.assertIn(self.post, self.auth_follower.get(
            FOLLOW_INDEX_URL).context['page_obj'])

    def test_follow(self):
        "Проверим наличие не-подписки"
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            ).exists()
        )
        "Отправляем GET-запрос и проверяем наличие объекта модели Follow"
        self.auth_follower.get(
            FOLLOW_URL,
            follow=True
        )
        self.assertTrue(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            ).exists()
        )

    def test_unfollow(self):
        "Подпишем пользователя на автора"
        Follow.objects.create(user=self.follower,
                              author=self.user)
        "Отправляем GET-запрос и проверяем отсутствие объекта модели Follow"
        self.auth_follower.get(
            UNFOLLOW_URL,
            follow=True
        )
        self.assertFalse(
            Follow.objects.filter(
                author=self.user,
                user=self.follower,
            ).exists()
        )

    def test_count_posts_on_page(self):
        other_posts = len(Post.objects.all())
        Post.objects.bulk_create(Post(
            author=self.user,
            text=f'Тестовый пост {post_number}',
            group=self.group
        ) for post_number in range(
            COUNT_POST_ON_PAGE + COUNT_LAST_PAGE_POSTS)
        )
        self.auth_follower.get(FOLLOW_URL)
        url_and_count_list = [
            [FOLLOW_INDEX_URL, COUNT_POST_ON_PAGE],
            [INDEX_URL, COUNT_POST_ON_PAGE],
            [GROUP_URL, COUNT_POST_ON_PAGE],
            [PROFILE_URL, COUNT_POST_ON_PAGE],
            [INDEX_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS + other_posts],
            [GROUP_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS + other_posts],
            [PROFILE_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS + other_posts],
            [FOLLOW_INDEX_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS + other_posts],
        ]
        for url, count in url_and_count_list:
            with self.subTest(address=url, count_posts=count):
                self.assertEqual(
                    len(self.auth_follower.get(url).context['page_obj']),
                    count
                )
