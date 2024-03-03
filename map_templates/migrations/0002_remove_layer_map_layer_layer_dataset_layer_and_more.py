# Generated by Django 5.0.2 on 2024-03-03 16:57

import django.contrib.gis.db.models.fields
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0004_datasetversion_regenerate_datasetversion_task_id_and_more'),
        ('map_templates', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='layer',
            name='map_layer',
        ),
        migrations.AddField(
            model_name='layer',
            name='dataset_layer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.datasetlayer', verbose_name='Couche de jeu de données'),
        ),
        migrations.AddField(
            model_name='layer',
            name='boundaries',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, default=None, help_text='La délimitations de la couche cartographique. Tout ce qui est en dehors de cette zone ne sera pas utilisé.', null=True, srid=4326, verbose_name='Délimitations'),
        ),
    ]
