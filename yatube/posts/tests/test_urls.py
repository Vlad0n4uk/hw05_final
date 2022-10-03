from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.settings import (POST_CREATE_HTML, POST_DETAIL_HTML,
                            POST_EDIT_HTML, POST_GROUP_LIST_HTML,
                            POST_INDEX_HTML, POST_PROFILE_HTML)

AUTHOR = 'author'
SLUG = 'slugtest'
OK = HTTPStatus.OK
REDIRECT = HTTPStatus.FOUND
ERROR = HTTPStatus.NOT_FOUND
LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
POST_CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_URL_LAST_PAGE = f'{GROUP_URL}?page=2'
PROFILE_URL_LAST_PAGE = f'{PROFILE_URL}?page=2'
INDEX_URL_LAST_PAGE = f'{INDEX_URL}?page=2'
ERROR_URL = f'{INDEX_URL}unexisting_page'
GUEST_CREATE_URL = f'{LOGIN_URL}?next={POST_CREATE_URL}'


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='slugtest',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.user_2 = User.objects.create_user(username='Vlad0n')
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.GUEST_EDIT_URL = f'{LOGIN_URL}?next={cls.EDIT_URL}'
        cls.ADD_COMMENT = reverse('posts:add_comment', args=[cls.post.pk])
        cls.GUEST_ADD_COMMENT = f'{LOGIN_URL}?next={cls.ADD_COMMENT}'

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest = Client()
        # Создаем второй клиент
        self.author = Client()
        self.another = Client()
        # Авторизуем пользователя
        self.author.force_login(self.user)
        self.another.force_login(self.user_2)

    def test_status_code(self):
        test_status_code_urls = [
            [self.EDIT_URL, self.author, OK],
            [PROFILE_URL, self.guest, OK],
            [self.DETAIL_URL, self.guest, OK],
            [INDEX_URL, self.guest, OK],
            [POST_CREATE_URL, self.guest, REDIRECT],
            [self.EDIT_URL, self.author, OK],
            [self.EDIT_URL, self.another, REDIRECT],
            [self.EDIT_URL, self.guest, REDIRECT],
            [POST_CREATE_URL, self.author, OK],
            [ERROR_URL, self.guest, ERROR],
            [self.ADD_COMMENT, self.author, REDIRECT],
            [self.ADD_COMMENT, self.another, REDIRECT],
            [self.ADD_COMMENT, self.guest, REDIRECT]
        ]
        for address, client, status in test_status_code_urls:
            with self.subTest(url=address, status_code=status, user=client):
                self.assertEqual(status, client.get(address).status_code)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            INDEX_URL: POST_INDEX_HTML,
            POST_CREATE_URL: POST_CREATE_HTML,
            GROUP_URL: POST_GROUP_LIST_HTML,
            PROFILE_URL: POST_PROFILE_HTML,
            self.DETAIL_URL: POST_DETAIL_HTML,
            self.EDIT_URL: POST_EDIT_HTML,
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                self.assertTemplateUsed(
                    self.author.get(address), template
                )

    def test_assert_redirects(self):
        all_redirect_urls = [
            [self.EDIT_URL, self.another, self.DETAIL_URL],
            [self.EDIT_URL, self.guest, self.GUEST_EDIT_URL],
            [POST_CREATE_URL, self.guest, GUEST_CREATE_URL],
            [self.ADD_COMMENT, self.another, self.DETAIL_URL],
            [self.ADD_COMMENT, self.author, self.DETAIL_URL],
            [self.ADD_COMMENT, self.guest, self.GUEST_ADD_COMMENT]
        ]
        for address, client, redirect_address in all_redirect_urls:
            with self.subTest(
                url_address=address,
                user=client,
                redirect_url=redirect_address
            ):
                self.assertRedirects(client.get(address), redirect_address)
