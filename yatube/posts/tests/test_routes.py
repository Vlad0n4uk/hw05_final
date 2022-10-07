from django.test import TestCase
from django.urls import reverse
from posts.urls import app_name

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
    [f'/profile/{AUTHOR}/follow/', 'profile_follow', [AUTHOR]],
    [f'/profile/{AUTHOR}/unfollow/', 'profile_unfollow', [AUTHOR]],
]


class TestRoute(TestCase):
    def test_routes(self):
        for route, url, args in CASES:
            self.assertEqual(
                route,
                reverse(f'{app_name}:{url}', args=args)
            )
