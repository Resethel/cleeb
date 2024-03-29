# Generated by Django 5.0.2 on 2024-02-28 08:31

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Thematic',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(help_text='Nom de la thématique', max_length=100, unique=True, verbose_name='Nom')),
                ('short_name', models.CharField(blank=True, help_text='Nom court de la thématique, utilisé dans les urls, tags, etc.Si laisser vide, le nom sera utilisé (tronqué à 20 caractères).', max_length=20, null=True, unique=True, verbose_name='Nom court')),
                ('short_desc', models.CharField(blank=True, help_text='Description courte de la thématique, affichée dans la liste des thématiques.', max_length=200, null=True, verbose_name='Description courte')),
                ('long_desc', models.TextField(blank=True, help_text='Description détaillée de la thématique, affichée sur la page de présentation de la thématique. Si laissé vide, seul la description courte sera affichée.', null=True, verbose_name='Description longue')),
                ('splash_img', models.ImageField(blank=True, help_text='Image de présentation de la thématique, affichée en haut de la page. Si laissé vide, seul la couleur de fond sera affichée.', null=True, upload_to='images/thematic/splah', verbose_name='Image de présentation')),
                ('splash_color', models.CharField(blank=True, default='#4BB166', help_text='Couleur de fond de la page de présentation de la thématique, en format hexadécimal.', max_length=7, null=True, verbose_name='Couleur de fond')),
            ],
            options={
                'verbose_name': 'Thèmatique',
                'verbose_name_plural': 'Thèmatiques',
            },
        ),
    ]
