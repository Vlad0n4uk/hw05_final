# Generated by Django 2.2.6 on 2022-05-10 13:49

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('posts', '0008_auto_20220506_1826'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='group',
            options={'verbose_name': 'Группа', 'verbose_name_plural': 'Группы'},
        ),
        migrations.AlterModelOptions(
            name='post',
            options={'ordering': ('-pub_date',), 'verbose_name': 'Пост', 'verbose_name_plural': 'Посты'},
        ),
    ]
