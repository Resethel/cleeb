# Generated by Django 5.0.2 on 2024-02-13 16:14

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map_layers', '0008_remove_maplayer_encoding'),
    ]

    operations = [
        migrations.DeleteModel(
            name='City',
        ),
        migrations.DeleteModel(
            name='CityDatasetKeyValue',
        ),
        migrations.RemoveField(
            model_name='maplayer',
            name='status',
        ),
    ]
