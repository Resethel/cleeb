# Generated by Django 5.0 on 2024-01-01 22:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_thematics', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='thematic',
            name='text',
        ),
        migrations.AddField(
            model_name='thematic',
            name='long_desc',
            field=models.TextField(blank=True, help_text='Description détaillée de la thématique, affichée sur la page de présentation de la thématique. Si laissé vide, seul la description courte sera affichée.', null=True, verbose_name='Description longue'),
        ),
        migrations.AddField(
            model_name='thematic',
            name='short_desc',
            field=models.CharField(blank=True, help_text='Description courte de la thématique, affichée dans la liste des thématiques.', max_length=200, null=True, verbose_name='Description courte'),
        ),
    ]
