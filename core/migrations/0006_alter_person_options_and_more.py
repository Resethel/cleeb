# Generated by Django 5.0.2 on 2024-02-12 13:22

import core.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_author_person'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='person',
            options={'ordering': ['lastname', 'firstname']},
        ),
        migrations.RenameField(
            model_name='organization',
            old_name='twitter',
            new_name='twitter_x',
        ),
        migrations.RenameField(
            model_name='person',
            old_name='organization',
            new_name='organizations',
        ),
        migrations.RemoveField(
            model_name='organization',
            name='contact',
        ),
        migrations.AddField(
            model_name='organization',
            name='email',
            field=models.EmailField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='email',
            field=models.EmailField(blank=True, default=None, max_length=254, null=True, verbose_name='Courriel'),
        ),
        migrations.AddField(
            model_name='person',
            name='facebook',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Facebook'),
        ),
        migrations.AddField(
            model_name='person',
            name='instagram',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Instagram'),
        ),
        migrations.AddField(
            model_name='person',
            name='pseudonym',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, unique=True, verbose_name='Pseudonyme'),
        ),
        migrations.AddField(
            model_name='person',
            name='slug',
            field=models.SlugField(blank=True, default=None, max_length=300, null=True, unique=True),
        ),
        migrations.AddField(
            model_name='person',
            name='twitter_x',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Twitter/X'),
        ),
        migrations.AddField(
            model_name='person',
            name='website',
            field=models.URLField(blank=True, default=None, null=True, verbose_name='Site web'),
        ),
        migrations.AlterField(
            model_name='organization',
            name='logo',
            field=models.ImageField(blank=True, null=True, upload_to=core.models.organization_logo_path),
        ),
        migrations.AlterField(
            model_name='organization',
            name='name',
            field=models.CharField(max_length=100, unique=True, verbose_name="Nom de l'organisation"),
        ),
        migrations.AlterField(
            model_name='organization',
            name='slug',
            field=models.SlugField(blank=True, default=None, max_length=200, null=True, unique=True),
        ),
        migrations.AlterField(
            model_name='organization',
            name='type',
            field=models.CharField(max_length=100, verbose_name="Type d'organisation"),
        ),
        migrations.AlterField(
            model_name='person',
            name='biography',
            field=models.TextField(blank=True, default=None, null=True, verbose_name='Biographie'),
        ),
        migrations.AlterField(
            model_name='person',
            name='firstname',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Prénom'),
        ),
        migrations.AlterField(
            model_name='person',
            name='lastname',
            field=models.CharField(blank=True, default=None, max_length=100, null=True, verbose_name='Nom de famille'),
        ),
        migrations.AlterField(
            model_name='person',
            name='picture',
            field=models.ImageField(blank=True, default=None, null=True, upload_to=core.models.person_picture_path, verbose_name='Photo'),
        ),
    ]