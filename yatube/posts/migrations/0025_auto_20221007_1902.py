# Generated by Django 2.2.16 on 2022-10-07 16:02

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0024_auto_20221006_2215'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='follow',
            options={'verbose_name': 'Подписка', 'verbose_name_plural': 'Подписки'},
        ),
        migrations.RemoveField(
            model_name='follow',
            name='pub_date',
        ),
        migrations.RemoveField(
            model_name='follow',
            name='text',
        ),
    ]
