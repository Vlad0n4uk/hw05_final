import shutil
import tempfile

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

AUTHOR = 'author'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NAME_GIF = 'posts/small.gif'


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username=AUTHOR)
        cls.user_2 = User.objects.create_user(username='Неавтор')
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
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='slugtest2',
            description='Тестовое описание_2',
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.ADD_COMMENT = reverse('posts:add_comment', args=[cls.post.pk])

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author = Client()
        self.another = Client()
        self.author.force_login(self.user)
        self.another.force_login(self.user_2)
        self.image = SimpleUploadedFile(
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

    def test_post_create(self):
        old_posts_id = list(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Новый текст',
            'group': self.group.id,
            'image': self.image
        }
        response = self.author.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        objects_exclude = Post.objects.exclude(id__in=old_posts_id)
        get_posts = objects_exclude.get()
        self.assertEqual(len(objects_exclude), 1)
        self.assertEqual(get_posts.text, form_data['text'])
        self.assertEqual(get_posts.group.id, form_data['group'])
        self.assertEqual(get_posts.author, self.user)
        self.assertEqual(get_posts.image.name, NAME_GIF)
        self.assertRedirects(response, PROFILE_URL)

    def test_post_edit(self):
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_2.id,
        }
        response = self.author.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        post = response.context['post']
        self.assertEqual(self.post.id, post.id)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(post.image.name, self.post.image.name)
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_post_create_and_edit_show_correct_context(self):
        urls = [
            POST_CREATE_URL,
            self.POST_EDIT_URL,
        ]
        form_fields = [
            ['text', forms.fields.CharField],
            ['group', forms.fields.ChoiceField],
            ['image', forms.fields.ImageField],
        ]
        for url in urls:
            context = self.author.get(url).context
            for form, expected in form_fields:
                with self.subTest(form=form):
                    form_field_create = context.get('form').fields.get(form)
                    self.assertIsInstance(form_field_create, expected)

    def test_create_comment(self):
        old_comments = list(Comment.objects.all().values_list('id', flat=True))
        form_data = {
            'post': self.post,
            'text': 'Новый комментарий'
        }
        response = self.another.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_DETAIL_URL)
        objects_exclude = Comment.objects.exclude(id__in=old_comments)
        self.assertEqual(len(objects_exclude), 1)
        self.assertEqual(objects_exclude.get().text, form_data['text'])
