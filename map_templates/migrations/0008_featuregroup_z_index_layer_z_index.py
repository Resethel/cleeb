# Generated by Django 5.0.2 on 2024-03-05 12:11

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_templates', '0007_maptemplate_center'),
    ]

    operations = [
        migrations.AddField(
            model_name='featuregroup',
            name='z_index',
            field=models.IntegerField(default=0, help_text="Index definissant l'ordre d'affichage des couches. Plus l'index est élevé, plus la couche est affichée en premier plan.", validators=[django.core.validators.MinValueValidator(0)], verbose_name='z-index'),
        ),
        migrations.AddField(
            model_name='layer',
            name='z_index',
            field=models.IntegerField(default=0, help_text="Index definissant l'ordre d'affichage des couches. Plus l'index est élevé, plus la couche est affichée en premier plan.", validators=[django.core.validators.MinValueValidator(0)], verbose_name='z-index'),
        ),
    ]
