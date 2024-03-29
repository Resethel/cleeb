# Generated by Django 5.0.2 on 2024-03-18 14:38

import articles.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Article',
            fields=[
                ('id', models.AutoField(help_text="L'ID de l'article.", primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, default=None, max_length=512, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True, help_text='The date of creation of the article.', verbose_name='Created at')),
                ('last_modified_at', models.DateTimeField(auto_now=True, help_text='The date of the last modification of the article.', verbose_name='Last modified at')),
                ('title', models.CharField(help_text='The title of the article.', max_length=512, verbose_name='Title')),
                ('cover_image', models.ImageField(blank=True, help_text='The splash image of the article.', null=True, upload_to=articles.models.get_cover_image_upload_path, verbose_name='Splash image')),
                ('body', models.TextField(help_text='The body of the article.', verbose_name='Article body')),
                ('authors', models.ManyToManyField(blank=True, help_text='Authors of the article.', to='core.person', verbose_name='Authors')),
            ],
            options={
                'verbose_name': 'Article',
                'verbose_name_plural': 'Articles',
            },
        ),
    ]
