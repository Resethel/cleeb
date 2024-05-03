# Generated by Django 5.0.2 on 2024-04-25 14:19

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name='Name of the organization'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.CharField(help_text='Type of organization (e.g. NGO, Company, Political Party, etc.)', max_length=100, verbose_name='Type of organization'),
        ),
        migrations.AlterField(
            model_name='person',
            name='biography',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Biography'),
        ),
        migrations.AlterField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=254, null=True, verbose_name='Email'),
        ),
        migrations.AlterField(
            model_name='person',
            name='firstname',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='First name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='lastname',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Last name'),
        ),
        migrations.AlterField(
            model_name='person',
            name='picture',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=core.models.person_picture_path, verbose_name='Picture'),
        ),
        migrations.AlterField(
            model_name='person',
            name='pseudonym',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True, verbose_name='Pseudonym'),
        ),
        migrations.AlterField(
            model_name='person',
            name='website',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Website'),
        ),
    ]
