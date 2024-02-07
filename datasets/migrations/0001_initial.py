# Generated by Django 5.0 on 2024-02-03 20:47

import datasets.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            state_operations=[
                migrations.CreateModel(
                    name='Dataset',
                    fields=[
                        ('id', models.AutoField(primary_key=True, serialize=False)),
                        ('name', models.CharField(help_text='Nom du jeu de données', max_length=100, unique=True)),
                        ('category', models.CharField(blank=True, help_text='Catégorie du jeu de données. Optionnel.', max_length=100)),
                        ('short_desc', models.CharField(blank=True, default=None, help_text="Description courte du jeu de données. Optionnel. Utilisé pour générer l'aide contextuelle.", max_length=100, null=True)),
                        ('description', models.TextField(blank=True, default=None, help_text='Description du jeu de données. Optionnel.', null=True)),
                        ('format', models.CharField(choices=[('shapefile', 'Shapefile'), ('geojson', 'GeoJSON')], help_text='Format du jeu de données. Soit un fichier ZIP contenant un fichier shapefile, soit un fichier GeoJSON.', max_length=10)),
                        ('file', models.FileField(help_text='Fichier du jeu de données. Le fichier doit correspondre au format choisi.', upload_to='datasets.models.Dataset.get_file_path')),
                    ],
                    options={
                        'verbose_name': 'Jeu de données',
                        'verbose_name_plural': 'Jeux de données',
                        'ordering': ['name'],
                    },
                ),
            ],
            # Table already exists. See map_layers/migrations/0007_[...].py
            database_operations = [],
        )
    ]
