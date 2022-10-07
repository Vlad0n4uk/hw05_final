from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class GenerationModel(models.Model):
    """Абстрактная модель. Добавляет дату создания, текст, автора."""
    text = models.TextField(
        verbose_name='Текст',
        help_text='Отредактируйте или введите новый текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='%(class)ss',
        verbose_name='Автор'
    )
    RETURN_STR = 'text={:.15}, pub_date={}'

    class Meta:
        # Это абстрактная модель:
        ordering = ('-pub_date',)
        abstract = True

    def __str__(self):
        return self.RETURN_STR.format(
            self.text, self.pub_date,
        )
