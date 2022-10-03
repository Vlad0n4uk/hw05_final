from django.test import TestCase
from django.urls import reverse

from ..models import Group, Post, User
from posts.settings import COUNT_POST_ON_PAGE

SLUG = 'slugtest'
AUTHOR = 'author'
COUNT_LAST_PAGE_POSTS = 3
INDEX_URL = reverse('posts:index')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
GROUP_URL = reverse('posts:group_list', args=[SLUG])
GROUP_URL_LAST_PAGE = GROUP_URL + '?page=2'
PROFILE_URL_LAST_PAGE = PROFILE_URL + '?page=2'
INDEX_URL_LAST_PAGE = INDEX_URL + '?page=2'


class PaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug=SLUG,
            description='Тестовое описание',
        )
        Post.objects.bulk_create(Post(
            author=cls.user,
            text=f'Тестовый пост {post_number}',
            group=cls.group
        ) for post_number in range(
            COUNT_POST_ON_PAGE + COUNT_LAST_PAGE_POSTS)
        )

    def test_count_posts_on_page(self):
        url_and_count_list = [
            [INDEX_URL, COUNT_POST_ON_PAGE],
            [GROUP_URL, COUNT_POST_ON_PAGE],
            [PROFILE_URL, COUNT_POST_ON_PAGE],
            [INDEX_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS],
            [GROUP_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS],
            [PROFILE_URL_LAST_PAGE, COUNT_LAST_PAGE_POSTS],
        ]
        for url, count in url_and_count_list:
            with self.subTest(address=url, count_posts=count):
                self.assertEqual(
                    len(self.client.get(url).context['page_obj']),
                    count
                )
