# Generated by Django 5.0.2 on 2024-03-19 17:48

import articles.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attachment',
            fields=[
                ('id', models.AutoField(help_text='Attachment ID', primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(help_text="Attachment's Name", max_length=100, verbose_name='Name')),
                ('type', models.CharField(choices=[('file', 'File'), ('pdf', 'PDF'), ('image', 'Image'), ('video', 'Video'), ('audio', 'Audio')], default=None, help_text="Attachment's Type", max_length=10, null=True, verbose_name='Type')),
                ('file', models.FileField(help_text="Attachment's File", max_length=500, upload_to=articles.models.get_attachment_upload_path, verbose_name='File')),
                ('article', models.ForeignKey(help_text='Article to which the attachment belongs to', on_delete=django.db.models.deletion.CASCADE, related_name='attachments', to='articles.article', verbose_name='Article')),
            ],
            options={
                'verbose_name': 'Attachment',
                'verbose_name_plural': 'Attachments',
                'unique_together': {('article', 'slug')},
            },
        ),
    ]
