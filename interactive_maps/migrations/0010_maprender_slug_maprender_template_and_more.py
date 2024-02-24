# Generated by Django 5.0.2 on 2024-02-23 06:48

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('interactive_maps', '0009_alter_maprender_embed_html_alter_maprender_full_html'),
        ('map_templates', '0003_maptemplate_generation_status_maptemplate_regenerate_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maprender',
            name='slug',
            field=models.SlugField(blank=True, default=None, max_length=512, null=True),
        ),
        migrations.AddField(
            model_name='maprender',
            name='template',
            field=models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='render', to='map_templates.maptemplate', verbose_name='Modèle'),
        ),
        migrations.AlterField(
            model_name='maprender',
            name='name',
            field=models.CharField(help_text='Le nom du rendu.', max_length=255, unique=True, verbose_name='Nom'),
        ),
    ]
