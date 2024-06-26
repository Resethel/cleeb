# Generated by Django 5.0.2 on 2024-03-29 15:17

import tinymce.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0005_article_themes'),
    ]

    operations = [
        migrations.AlterField(
            model_name='article',
            name='body',
            field=tinymce.models.HTMLField(help_text='The body of the article.', verbose_name='Article body'),
        ),
    ]
