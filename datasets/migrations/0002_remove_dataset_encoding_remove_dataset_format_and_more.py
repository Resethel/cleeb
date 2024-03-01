# Generated by Django 5.0.2 on 2024-03-01 22:45

import datasets.models
import datasets.validators
import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='dataset',
            name='encoding',
        ),
        migrations.RemoveField(
            model_name='dataset',
            name='format',
        ),
        migrations.AddField(
            model_name='datasetversion',
            name='encoding',
            field=models.CharField(choices=[('utf-8', 'UTF-8'), ('latin-1', 'Latin-1'), ('utf-16', 'UTF-16'), ('ascii', 'ASCII'), ('iso-8859-1', 'ISO-8859-1')], default='utf-8', help_text='Encodage des propriétés du jeu de données.', max_length=10),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='file',
            field=models.FileField(blank=True, default=None, help_text='Fichier de la version du jeu de données.', null=True, upload_to=datasets.models.dataset_version_filepath, validators=[datasets.validators.validate_dataset_version_file], verbose_name='Fichier'),
        ),
        migrations.CreateModel(
            name='DatasetLayer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default=None, help_text='Nom de la couche de jeu de données.', max_length=50, null=True)),
                ('srid', models.IntegerField(blank=True, default=None, help_text='SRID de la couche de jeu de données.', null=True)),
                ('bounding_box', django.contrib.gis.db.models.fields.PolygonField(blank=True, default=None, help_text='Boîte englobante de la couche du jeu de données.', null=True, srid=4326)),
                ('feature_count', models.IntegerField(blank=True, default=None, help_text='Nombre de géométries dans la couche du jeu de données.', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('geometry_type', models.CharField(blank=True, default=None, help_text='Type de géométrie de la couche du jeu de données.', max_length=50, null=True)),
                ('dataset', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='layers', to='datasets.datasetversion')),
            ],
            options={
                'verbose_name': 'Couche de jeu de données',
                'verbose_name_plural': 'Couches de jeux de données',
                'unique_together': {('name', 'dataset')},
            },
        ),
        migrations.CreateModel(
            name='DatasetLayerField',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(blank=True, default=None, max_length=50, null=True)),
                ('type', models.CharField(blank=True, choices=[('OFTInteger', 'OFTInteger'), ('OFTIntegerList', 'OFTIntegerList'), ('OFTReal', 'OFTReal'), ('OFTRealList', 'OFTRealList'), ('OFTString', 'OFTString'), ('OFTStringList', 'OFTStringList'), ('OFTWideString', 'OFTWideString'), ('OFTWideStringList', 'OFTWideStringList'), ('OFTBinary', 'OFTBinary'), ('OFTDate', 'OFTDate'), ('OFTTime', 'OFTTime'), ('OFTDateTime', 'OFTDateTime')], default=None, max_length=50, null=True)),
                ('max_length', models.IntegerField(blank=True, default=None, help_text='Longueur maximale du champ de texte.', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('precision', models.IntegerField(blank=True, default=None, help_text='Précision du champ numérique.', null=True, validators=[django.core.validators.MinValueValidator(0)])),
                ('layer', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='fields', to='datasets.datasetlayer')),
            ],
            options={
                'verbose_name': 'Champ de couche de jeu de données',
                'verbose_name_plural': 'Champs de couche de jeu de données',
                'unique_together': {('name', 'layer')},
            },
        ),
    ]
