import shutil
import tempfile

from django import forms
from django.contrib.auth import get_user_model
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Comment, Group, Post, User

AUTHOR = 'author'
POST_CREATE_URL = reverse('posts:post_create')
PROFILE_URL = reverse('posts:profile', args=[AUTHOR])
LOGIN_URL = reverse('users:login')
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)
NEW_NAME_GIF = 'new_small.gif'
NAME_GIF = 'small.gif'
User = get_user_model()
small_gif = (
    b'\x47\x49\x46\x38\x39\x61\x02\x00'
    b'\x01\x00\x80\x00\x00\x00\x00\x00'
    b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
    b'\x00\x00\x00\x2C\x00\x00\x00\x00'
    b'\x02\x00\x01\x00\x00\x02\x02\x0C'
    b'\x0A\x00\x3B'
)


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
        cls.group_2 = Group.objects.create(
            title='Тестовая группа_2',
            slug='slugtest2',
            description='Тестовое описание_2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.POST_DETAIL_URL = reverse('posts:post_detail', args=[cls.post.pk])
        cls.POST_EDIT_URL = reverse('posts:post_edit', args=[cls.post.pk])
        cls.ADD_COMMENT = reverse('posts:add_comment', args=[cls.post.pk])
        cls.ADD_COMMENT_GUEST = f'{LOGIN_URL}?next={cls.ADD_COMMENT}'
        cls.POST_EDIT_URL_REDIRECT = f'{LOGIN_URL}?next={cls.POST_EDIT_URL}'
        cls.author = Client()
        cls.another = Client()
        cls.author.force_login(cls.user)
        cls.another.force_login(cls.user_2)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.image = SimpleUploadedFile(
            name=NAME_GIF,
            content=small_gif,
            content_type='image/gif'
        )
        self.new_image = SimpleUploadedFile(
            name=NEW_NAME_GIF,
            content=small_gif,
            content_type='image/gif'
        )

    def test_post_create(self):
        old_posts_id = set(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Новый текст',
            'author': self.user,
            'group': self.group.id,
            'image': self.image
        }
        response = self.author.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        objects_exclude = Post.objects.exclude(id__in=old_posts_id)
        self.assertEqual(len(objects_exclude), 1)
        get_posts = objects_exclude.get()
        self.assertEqual(get_posts.text, form_data['text'])
        self.assertEqual(get_posts.group.id, form_data['group'])
        self.assertEqual(get_posts.author, self.post.author)
        self.assertEqual(get_posts.image, f"posts/{form_data['image']}")
        self.assertRedirects(response, PROFILE_URL)

    def test_anonim_create_post(self):
        old_posts_id = set(Post.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Новый текст',
            'author': self.user,
            'group': self.group.id,
            'image': self.image
        }
        self.client.post(
            POST_CREATE_URL,
            data=form_data,
            follow=True
        )
        objects_exclude = Post.objects.exclude(id__in=old_posts_id)
        self.assertEqual(len(objects_exclude), 0)

    def test_post_edit(self):
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_2.id,
            'image': self.new_image
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
        self.assertEqual(post.image.name, f"posts/{form_data['image']}")
        self.assertEqual(post.author, self.post.author)
        self.assertRedirects(response, self.POST_DETAIL_URL)

    def test_post_edit_anonim(self):
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_2.id,
            'image': self.new_image
        }
        response = self.client.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.POST_EDIT_URL_REDIRECT)

    def test_post_edit_another(self):
        form_data = {
            'text': 'Измененный текст',
            'group': self.group_2.id,
            'image': self.new_image
        }
        response = self.another.post(
            self.POST_EDIT_URL,
            data=form_data,
            follow=True
        )
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
        old_comments = set(Comment.objects.all().values_list('id', flat=True))
        form_data = {
            'text': 'Новый комментарий',
            'author': self.user_2,
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
        self.assertEqual(objects_exclude.get().author, form_data['author'])
        self.assertEqual(objects_exclude.get().post, self.post)

    def test_anonim_create_comment(self):
        form_data = {
            'text': 'Новый комментарий',
            'author': self.user_2,
        }
        response = self.client.post(
            self.ADD_COMMENT,
            data=form_data,
            follow=True
        )
        self.assertRedirects(response, self.ADD_COMMENT_GUEST)
