# Generated by Django 5.0 on 2024-01-14 16:20

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_layers', '0005_maplayer_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='City',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Nom de la ville', max_length=100, unique=True, verbose_name='Nom')),
                ('generation_status', models.CharField(choices=[('PENDING', 'En attente de génération'), ('GENERATING', 'Génération en cours'), ('DONE', 'Génération terminée'), ('ERROR', 'Erreur lors de la génération')], default='PENDING', help_text='Statut de génération de la ville.', max_length=20, verbose_name='Statut de génération')),
                ('limits_shapefile', models.CharField(blank=True, default=None, help_text='Nom du fichier shapefile à utiliser.', max_length=500, null=True, verbose_name='Fichier shapefile')),
                ('limits_dataset', models.ForeignKey(help_text='Jeu de données utilisé pour les limites de la ville. Les limites de la ville seront générées à partir de ce jeu de données.Si le jeu de données est supprimé, les limites de la ville seront également supprimées.', on_delete=django.db.models.deletion.CASCADE, to='map_layers.dataset', verbose_name='Jeu de données des limites')),
            ],
            options={
                'verbose_name': 'Ville',
                'verbose_name_plural': 'Villes',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='CityDatasetKeyValue',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(help_text='Clé du jeu de données.', max_length=100, verbose_name='Clé')),
                ('value', models.CharField(help_text='Valeur du jeu de données.', max_length=100, verbose_name='Valeur')),
                ('city', models.ForeignKey(help_text='Ville à laquelle la clé/valeur est associée. Si la ville est supprimée, la clé/valeur sera également supprimée.', on_delete=django.db.models.deletion.CASCADE, to='map_layers.city')),
            ],
            options={
                'verbose_name': 'Clé/valeur du jeu de données',
                'verbose_name_plural': 'Clés/valeurs du jeu de données',
                'ordering': ['key'],
            },
        ),
    ]
