from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
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

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        str_post = self.post.RETURN_STR.format(
            self.post.text, self.post.pub_date, self.post.group
        )
        self.assertEqual(str_post, str(self.post))
        self.assertEqual(self.group.title, str(self.group))
