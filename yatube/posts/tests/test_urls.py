from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.settings import (ERROR_HTML, POST_CREATE_HTML, POST_DETAIL_HTML,
                            POST_EDIT_HTML, POST_GROUP_LIST_HTML,
                            POST_INDEX_HTML, POST_PROFILE_HTML,
                            FOLLOW_HTML)

USER = 'Vlad0n'
AUTHOR = 'author'
SLUG = 'slugtest'
OK = HTTPStatus.OK
REDIRECT = HTTPStatus.FOUND
ERROR = HTTPStatus.NOT_FOUND
LOGIN_URL = reverse('users:login')
INDEX_URL = reverse('posts:index')
FOLLOW_INDEX_URL = reverse('posts:follow_index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
POST_CREATE_URL = reverse('posts:post_create')
GROUP_URL = reverse('posts:group_list', args=[SLUG])
ERROR_URL = f'{INDEX_URL}unexisting_page'
GUEST_CREATE_URL = f'{LOGIN_URL}?next={POST_CREATE_URL}'
GUEST_FOLLOW_INDEX_URL = f'{LOGIN_URL}?next={FOLLOW_INDEX_URL}'
FOLLOW_URL = reverse('posts:profile_follow', args=[AUTHOR])
UNFOLLOW_URL = reverse('posts:profile_unfollow', args=[AUTHOR])
FOLLOW_URL_GUEST = f'{LOGIN_URL}?next={FOLLOW_URL}'


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
        cls.user_2 = User.objects.create_user(username=USER)
        cls.EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.GUEST_EDIT_URL = f'{LOGIN_URL}?next={cls.EDIT_URL}'
        cls.guest = Client()
        # Создаем второй клиент
        cls.author = Client()
        cls.another = Client()
        # Авторизуем пользователя
        cls.author.force_login(cls.user)
        cls.another.force_login(cls.user_2)
        cache.clear()

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
            [FOLLOW_INDEX_URL, self.author, OK],
            [FOLLOW_INDEX_URL, self.another, OK],
            [FOLLOW_INDEX_URL, self.guest, REDIRECT],
            [FOLLOW_URL, self.author, REDIRECT],
            [FOLLOW_URL, self.another, REDIRECT],
            [FOLLOW_URL, self.guest, REDIRECT],
            [UNFOLLOW_URL, self.author, ERROR],
            [UNFOLLOW_URL, self.another, REDIRECT],
            [UNFOLLOW_URL, self.guest, REDIRECT],
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
            FOLLOW_INDEX_URL: FOLLOW_HTML,
            ERROR_URL: ERROR_HTML,
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
            [FOLLOW_INDEX_URL, self.guest, GUEST_FOLLOW_INDEX_URL],
            [FOLLOW_URL, self.author, PROFILE_URL],
            [FOLLOW_URL, self.another, PROFILE_URL],
            [FOLLOW_URL, self.guest, FOLLOW_URL_GUEST],
            [UNFOLLOW_URL, self.another, PROFILE_URL],
        ]
        for address, client, redirect_address in all_redirect_urls:
            with self.subTest(
                url_address=address,
                user=client,
                redirect_url=redirect_address
            ):
                self.assertRedirects(client.get(address), redirect_address)
