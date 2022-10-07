from core.models import GenerationModel
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    slug = models.SlugField(
        unique=True,
        verbose_name='Идентификатор'
    )
    description = models.TextField(
        verbose_name='Описание'
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title


class Post(GenerationModel):
    group = models.ForeignKey(
        Group,
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа'
    )
    image = models.ImageField(
        'Изображение',
        upload_to='posts/',
        blank=True
    )
    RETURN_STR = '{}, {}'

    class Meta(GenerationModel.Meta):
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.RETURN_STR.format(super().__str__(), self.group)


class Comment(GenerationModel):
    post = models.ForeignKey(
        Post,
        blank=True,
        null=True,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Пост',
    )

    class Meta(GenerationModel.Meta):
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="following",
        verbose_name='Автор'
    )
    RETURN_STR = 'user={} подписан на author={}'

    class Meta():
        verbose_name = "Подписка"
        verbose_name_plural = "Подписки"
        constraints = [
            models.UniqueConstraint(
                fields=("author", "user",),
                name="unique_follow"
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')),
                name="self follow is not accessed"
            )
        ]

    def __str__(self):
        return self.RETURN_STR.format(
            self.user.get_username(), self.author.get_username()
        )
