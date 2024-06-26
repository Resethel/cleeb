# Generated by Django 5.0.2 on 2024-04-25 14:50

import datasets.models
import datasets.validators
import django.contrib.gis.db.models.fields
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0005_alter_datasetlayer_name_alter_datasetlayerfield_name'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='datasetcategory',
            options={'ordering': ['name'], 'verbose_name': 'Dataset Category', 'verbose_name_plural': 'Dataset Categories'},
        ),
        migrations.AlterModelOptions(
            name='datasetlayer',
            options={'verbose_name': 'Dataset Layer', 'verbose_name_plural': 'Dataset Layers'},
        ),
        migrations.AlterModelOptions(
            name='datasetlayerfield',
            options={'verbose_name': 'Dataset Layer Field', 'verbose_name_plural': 'Dataset Layer Fields'},
        ),
        migrations.AlterModelOptions(
            name='datasetversion',
            options={'ordering': ['-date'], 'verbose_name': 'Dataset Version', 'verbose_name_plural': 'Dataset Versions'},
        ),
        migrations.AlterModelOptions(
            name='feature',
            options={'verbose_name': 'Geographic Feature', 'verbose_name_plural': 'Geographic Features'},
        ),
        migrations.AlterField(
            model_name='dataset',
            name='categories',
            field=models.ManyToManyField(blank=True, help_text='Categories of the dataset.', to='datasets.datasetcategory', verbose_name='Categories'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='description',
            field=models.TextField(blank=True, default=None, help_text='Description of the dataset (optional).', null=True, verbose_name='Description'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='language',
            field=models.CharField(blank=True, default=None, help_text='Primary language of the dataset (optional).', max_length=30, null=True, verbose_name='Language'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='last_update',
            field=models.DateField(auto_now=True, help_text='Date of the last update of the dataset.', verbose_name='Last update'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='license',
            field=models.CharField(blank=True, default=None, help_text='License of the dataset (optional).', max_length=100, null=True, verbose_name='License'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='name',
            field=models.CharField(help_text='Name of the dataset.', max_length=100, unique=True, verbose_name='Dataset Name'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='public',
            field=models.BooleanField(default=True, help_text='Whether the dataset is public or not.', verbose_name='Public'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='short_desc',
            field=models.TextField(blank=True, default=None, help_text='Short description of the dataset, displayable as summary (max: 400 characters, optional).', max_length=400, null=True, verbose_name='Short description'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='source',
            field=models.CharField(blank=True, default=None, help_text='Source from which the dataset was obtained (optional).', max_length=100, null=True, verbose_name='Source'),
        ),
        migrations.AlterField(
            model_name='dataset',
            name='usage_restrictions',
            field=models.TextField(blank=True, default=None, help_text='Restrictions on the usage of the dataset (optional).', null=True, verbose_name='Usage restrictions'),
        ),
        migrations.AlterField(
            model_name='datasetcategory',
            name='icon',
            field=models.FileField(help_text='Icon of the dataset category. Must be a monochromatic SVG file (black, transparent background).', upload_to='datasets/category_icons', verbose_name='Icon'),
        ),
        migrations.AlterField(
            model_name='datasetcategory',
            name='name',
            field=models.CharField(help_text='Name of the category of the dataset.', max_length=100, unique=True, verbose_name='Category name'),
        ),
        migrations.AlterField(
            model_name='datasetlayer',
            name='bounding_box',
            field=django.contrib.gis.db.models.fields.PolygonField(blank=True, default=None, help_text='Bounding box of the layer of the dataset.', null=True, srid=4326, verbose_name='Bounding box'),
        ),
        migrations.AlterField(
            model_name='datasetlayer',
            name='feature_count',
            field=models.IntegerField(blank=True, default=None, help_text='Number of features in the layer.', null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Feature count'),
        ),
        migrations.AlterField(
            model_name='datasetlayer',
            name='geometry_type',
            field=models.CharField(blank=True, default=None, help_text='Type of the geometries in the layer.', max_length=50, null=True, verbose_name='Geometry type'),
        ),
        migrations.AlterField(
            model_name='datasetlayer',
            name='name',
            field=models.CharField(blank=True, default=None, help_text='Name of the layer of the dataset.', max_length=255, null=True, verbose_name='Layer name'),
        ),
        migrations.AlterField(
            model_name='datasetlayer',
            name='srid',
            field=models.IntegerField(blank=True, default=None, help_text='SRID (SRS) of the layer of the dataset.', null=True, verbose_name='SRID'),
        ),
        migrations.AlterField(
            model_name='datasetlayerfield',
            name='max_length',
            field=models.IntegerField(blank=True, default=None, help_text='Maximum length of the text field.', null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Max length'),
        ),
        migrations.AlterField(
            model_name='datasetlayerfield',
            name='precision',
            field=models.IntegerField(blank=True, default=None, help_text='Number of decimal places.', null=True, validators=[django.core.validators.MinValueValidator(0)], verbose_name='Precision'),
        ),
        migrations.AlterField(
            model_name='datasettechnicalinformation',
            name='dataset',
            field=models.ForeignKey(help_text='Dataset to which the technical information is related.', on_delete=django.db.models.deletion.CASCADE, related_name='technical_information', to='datasets.dataset', verbose_name='Dataset'),
        ),
        migrations.AlterField(
            model_name='datasettechnicalinformation',
            name='key',
            field=models.CharField(help_text='Sorting key of the technical information.', max_length=100, verbose_name='Key'),
        ),
        migrations.AlterField(
            model_name='datasettechnicalinformation',
            name='value',
            field=models.CharField(help_text="Valeur de l'information technique.", max_length=250, verbose_name='Value'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='date',
            field=models.DateTimeField(default=django.utils.timezone.now, help_text='Date of the version of the dataset.'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='encoding',
            field=models.CharField(choices=[('utf-8', 'UTF-8'), ('latin-1', 'Latin-1'), ('utf-16', 'UTF-16'), ('ascii', 'ASCII'), ('iso-8859-1', 'ISO-8859-1')], default='utf-8', help_text='Encoding of the dataset file.', max_length=10, verbose_name='Encoding'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='file',
            field=models.FileField(blank=True, default=None, help_text='File containing the dataset.', null=True, upload_to=datasets.models.dataset_version_filepath, validators=[datasets.validators.validate_dataset_version_file], verbose_name='File'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='regenerate',
            field=models.BooleanField(default=False, help_text='Regenerate the geographic features of the dataset.', verbose_name='Regenerate'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='task_id',
            field=models.UUIDField(blank=True, default=None, help_text='ID of the task that generates the geographic features.', null=True, verbose_name='Task ID'),
        ),
        migrations.AlterField(
            model_name='datasetversion',
            name='task_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure'), ('REVOKED', 'Revoked')], default=None, help_text='Status of the task that generates the geographic features.', max_length=25, null=True, verbose_name='Task status'),
        ),
    ]
