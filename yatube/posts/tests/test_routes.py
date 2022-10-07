from django.test import TestCase
from django.urls import reverse
from posts.apps import PostsConfig

POST_ID = 1
AUTHOR = 'author'
SLUG = 'slugtest'
CASES = [
    ['/', 'index', []],
    ['/follow/', 'follow_index', []],
    ['/create/', 'post_create', []],
    [f'/group/{SLUG}/', 'group_list', [SLUG]],
    [f'/profile/{AUTHOR}/', 'profile', [AUTHOR]],
    [f'/posts/{POST_ID}/', 'post_detail', [POST_ID]],
    [f'/posts/{POST_ID}/edit/', 'post_edit', [POST_ID]],
]


class TestRoute(TestCase):
    def test_routes(self):
        for route, url, args in CASES:
            self.assertEqual(
                route,
                reverse(f'{PostsConfig.name}:{url}', args=args)
            )
