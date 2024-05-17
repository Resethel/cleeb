# Generated by Django 5.0.6 on 2024-05-17 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('articles', '0008_delete_attachment'),
        ('files', '0003_alter_file_unique_together_alter_file_slug_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='article',
            name='attachments',
            field=models.ManyToManyField(blank=True, help_text='Files attached to the article.', related_name='articles', to='files.file', verbose_name='Attached files'),
        ),
    ]
