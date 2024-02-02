# Generated by Django 5.0 on 2024-01-06 22:52

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Dataset',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Nom du jeu de données', max_length=100, unique=True)),
                ('short_desc', models.CharField(blank=True, default=None, help_text="Description courte du jeu de données. Optionnel. Utilisé pour générer l'aide contextuelle.", max_length=100, null=True)),
                ('description', models.TextField(blank=True, default=None, help_text='Description du jeu de données. Optionnel.', null=True)),
                ('format', models.CharField(choices=[('shapefile', 'Shapefile'), ('geojson', 'GeoJSON')], help_text='Format du jeu de données. Soit un fichier ZIP contenant un fichier shapefile, soit un fichier GeoJSON.', max_length=10)),
                ('file', models.FileField(help_text='Fichier du jeu de données. Le fichier doit correspondre au format choisi.', upload_to='datasets')),
            ],
            options={
                'verbose_name': 'Jeu de données',
                'verbose_name_plural': 'Jeux de données',
                'ordering': ['name'],
            },
        ),
    ]
