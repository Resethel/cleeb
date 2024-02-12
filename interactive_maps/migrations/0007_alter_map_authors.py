# Generated by Django 5.0.2 on 2024-02-12 10:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_rename_author_person'),
        ('interactive_maps', '0006_move_author_to_core_app'),
    ]

    operations = [
        migrations.AlterField(
            model_name='map',
            name='authors',
            field=models.ManyToManyField(blank=True, help_text='Les auteur.ice.s de la carte interactive.', to='core.person'),
        ),
    ]
