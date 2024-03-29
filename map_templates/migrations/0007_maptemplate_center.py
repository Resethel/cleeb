# Generated by Django 5.0.2 on 2024-03-05 11:13

import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('map_templates', '0006_circlepattern_stripepattern_alter_style_options_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='maptemplate',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(6.175715, 49.119308, srid=4326), help_text='Le centre de la carte.', srid=4326, verbose_name='Centre'),
        ),
    ]
