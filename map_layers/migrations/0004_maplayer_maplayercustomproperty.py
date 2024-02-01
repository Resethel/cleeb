# Generated by Django 5.0 on 2024-01-07 01:19

import django.core.validators
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_layers', '0003_alter_dataset_file'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapLayer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Nom de la couche', max_length=100, unique=True, verbose_name='Nom')),
                ('short_desc', models.CharField(blank=True, default=None, help_text="Description courte de la couche. Optionnel. Utilisé pour générer l'aide contextuelle.", max_length=100, null=True, verbose_name='Description courte')),
                ('description', models.TextField(blank=True, default=None, help_text='Description de la couche. Optionnel.', null=True, verbose_name='Description')),
                ('shapefile', models.CharField(blank=True, default=None, help_text='Nom du fichier shapefile à utiliser.', max_length=500, null=True, verbose_name='Fichier shapefile')),
                ('encoding', models.CharField(choices=[('utf-8', 'UTF-8'), ('latin-1', 'Latin-1'), ('utf-16', 'UTF-16'), ('ascii', 'ASCII')], default='utf-8', help_text='Encodage du fichier shapefile.', max_length=50, verbose_name='Codage des caractères')),
                ('max_polygons_points', models.IntegerField(blank=True, default=None, help_text="Nombre maximum de points par polygone. Si un polygone contient plus de points, il sera ignoré.Si la valeur est nulle, il n'y a pas de limite.", null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Nombre maximum de points par polygone')),
                ('max_multipolygons_polygons', models.IntegerField(blank=True, default=None, help_text="Nombre maximum de polygones par multipolygone.\nSi un multipolygone contient plus de polygones, il sera ignoré.\nSi la valeur est nulle, il n'y a pas de limite.", null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Nombre maximum de polygones par multipolygone')),
                ('max_multiolygons_points', models.IntegerField(blank=True, default=None, help_text="Nombre maximum de points par multipolygone.\nSi un multipolygone contient plus de points, il sera ignoré.\nSi la valeur est nulle, il n'y a pas de limite.", null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Nombre maximum de points par multipolygone')),
                ('customize_properties', models.BooleanField(default=False, help_text="Personnalise les proppriétés de chaque feature du jeu de données selon les règles définies dans le champ 'Règles de conversion des propriétés'.Les anciennes propriétés seront supprimées.", verbose_name='Personnaliser les propriétés')),
                ('dataset', models.ForeignKey(help_text='Jeu de données utilisé pour la couche. La couche sera générée à partir de ce jeu de données.Si le jeu de données est supprimé, la couche sera également supprimée.', on_delete=django.db.models.deletion.CASCADE, to='map_layers.dataset', verbose_name='Jeu de données')),
            ],
            options={
                'verbose_name': 'Couche',
                'verbose_name_plural': 'Couches',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='MapLayerCustomProperty',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(help_text='Nom de la propriété personnalisée.', max_length=100, verbose_name='Nom')),
                ('value', models.CharField(help_text='Valeur de la propriété.Pour utiliser une propriété du jeu de données, utilisez la syntaxe suivante: ${nom_de_la_propriété}.Exemple: "${HECTARES} ha" convertira la valeur de la propriété "HECTARES" en chaîne de caractères et ajoutera " ha" à la fin.', max_length=100, verbose_name='Valeur')),
                ('map_layer', models.ForeignKey(help_text='Couche à laquelle la propriété est associée. Si la couche est supprimée, la propriété sera également supprimée.', on_delete=django.db.models.deletion.CASCADE, to='map_layers.maplayer')),
            ],
            options={
                'verbose_name': 'Propriété personnalisée',
                'verbose_name_plural': 'Propriétés personnalisées',
                'ordering': ['name'],
            },
        ),
    ]