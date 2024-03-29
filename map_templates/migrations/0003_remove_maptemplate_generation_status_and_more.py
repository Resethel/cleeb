# Generated by Django 5.0.2 on 2024-03-03 17:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('map_templates', '0002_remove_layer_map_layer_layer_dataset_layer_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='maptemplate',
            name='generation_status',
        ),
        migrations.AddField(
            model_name='maptemplate',
            name='task_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure'), ('REVOKED', 'Revoked')], default=None, help_text='Statut de la tâche de génération des entités géographiques.', max_length=25, null=True),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='regenerate',
            field=models.BooleanField(default=False, help_text='Indique si les entités géographiques doivent être régénérées.'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='task_id',
            field=models.UUIDField(blank=True, default=None, help_text='ID de la tâche de génération des entités géographiques.', null=True, verbose_name='ID de la tâche'),
        ),
    ]
