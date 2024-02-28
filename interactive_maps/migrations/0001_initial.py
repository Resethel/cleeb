# Generated by Django 5.0.2 on 2024-02-28 08:31

import django.db.models.deletion
import interactive_maps.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('core', '0001_initial'),
        ('map_templates', '0001_initial'),
        ('map_thematics', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MapRender',
            fields=[
                ('id', models.AutoField(help_text="L'ID de la carte.", primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(blank=True, default=None, max_length=512, null=True)),
                ('name', models.CharField(help_text='Le nom du rendu.', max_length=255, unique=True, verbose_name='Nom')),
                ('embed_html', models.FileField(default=None, help_text='Le code HTML de la carte pouvant être intégré dans une page web.', null=True, upload_to=interactive_maps.models.map_render_embed_path, verbose_name='HTML intégrable')),
                ('full_html', models.FileField(default=None, help_text="Le code HTML d'une page web contenant la carte.", null=True, upload_to=interactive_maps.models.map_render_full_path, verbose_name='HTML complet')),
                ('template', models.OneToOneField(default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='render', to='map_templates.maptemplate', verbose_name='Modèle')),
            ],
            options={
                'verbose_name': 'Rendu de carte',
                'verbose_name_plural': 'Rendus de carte',
            },
        ),
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=100)),
                ('created_at', models.DateField(auto_now_add=True, help_text='La date de création de la carte interactive.')),
                ('last_modified', models.DateField(auto_now=True, help_text='La date de dernière modification de la carte interactive.')),
                ('introduction', models.TextField(blank=True, default=None, help_text="L'introduction de la carte interactive. Formaté en HTML.Seuls les balises de style (strong, em, etc.) seront conservées.Toutes balises de structure (section, article, h1, p, etc.) seront supprimées.", null=True)),
                ('text', models.TextField(blank=True, default=None, help_text='Le texte de la carte interactive. Formaté en HTML.', null=True)),
                ('slug', models.SlugField(blank=True, default=None, help_text="Le slug de la carte interactive. S'il n'est pas renseigné, il sera généré automatiquement.", max_length=100, null=True)),
                ('authors', models.ManyToManyField(blank=True, help_text='Les auteur.ice.s de la carte interactive.', to='core.person')),
                ('thematics', models.ManyToManyField(blank=True, help_text='Les thématiques de la carte interactive.', to='map_thematics.thematic')),
                ('map_render', models.ForeignKey(blank=True, help_text='Le rendu de carte généré par le serveur.', null=True, on_delete=django.db.models.deletion.SET_NULL, to='interactive_maps.maprender', verbose_name='Rendu de carte')),
            ],
            options={
                'ordering': ['id'],
            },
        ),
    ]
