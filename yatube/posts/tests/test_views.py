import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

INDEX_URL = reverse('posts:index')
GROUP_URL = reverse('posts:group_list', args=['slugtest'])
NOT_GROUP_URL = reverse('posts:group_list', args=['slugtest_2'])
PROFILE_URL = reverse('posts:profile', args=['Vlad0n4uk'])
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        self.POST_DETAIL_ARGS = reverse(
            'posts:post_detail', args=[self.post.pk]
        )

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
