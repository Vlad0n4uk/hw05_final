from django.db import models


class CreatedModel(models.Model):
    """Абстрактная модель. Добавляет дату создания, текст."""
    text = models.TextField(
        max_length=200,
        verbose_name='Текст',
        help_text='Отредактируйте или введите новый текст'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        db_index=True
    )

    class Meta:
        # Это абстрактная модель:
        ordering = ('-pub_date',)
        abstract = True
