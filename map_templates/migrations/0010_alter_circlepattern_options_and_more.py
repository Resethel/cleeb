# Generated by Django 5.0.2 on 2024-04-26 09:36

import colorfield.fields
import django.contrib.gis.db.models.fields
import django.contrib.gis.geos.point
import django.core.validators
import django.db.models.deletion
import map_templates.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datasets', '0006_alter_datasetcategory_options_and_more'),
        ('map_templates', '0009_tooltip_tooltipfield'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='circlepattern',
            options={'verbose_name': 'Circle Pattern', 'verbose_name_plural': 'Circle Patterns'},
        ),
        migrations.AlterModelOptions(
            name='featuregroup',
            options={'verbose_name': 'Feature Group', 'verbose_name_plural': 'Feature Groups'},
        ),
        migrations.AlterModelOptions(
            name='filter',
            options={'verbose_name': 'Filter', 'verbose_name_plural': 'Filters'},
        ),
        migrations.AlterModelOptions(
            name='layer',
            options={'verbose_name': 'Layer', 'verbose_name_plural': 'Layers'},
        ),
        migrations.AlterModelOptions(
            name='maptemplate',
            options={'verbose_name': 'Map Template', 'verbose_name_plural': 'Map Templates'},
        ),
        migrations.AlterModelOptions(
            name='propertystyle',
            options={'verbose_name': "Property's Style", 'verbose_name_plural': "Properties' Styles"},
        ),
        migrations.AlterModelOptions(
            name='stripepattern',
            options={'verbose_name': 'Stripe Pattern', 'verbose_name_plural': 'Stripe Patterns'},
        ),
        migrations.AlterModelOptions(
            name='tilelayer',
            options={'verbose_name': 'Tile Layer', 'verbose_name_plural': 'Tile Layers'},
        ),
        migrations.AlterModelOptions(
            name='tooltip',
            options={'verbose_name': 'Tooltip', 'verbose_name_plural': 'Tooltips'},
        ),
        migrations.AlterModelOptions(
            name='tooltipfield',
            options={'verbose_name': 'Tooltip Field', 'verbose_name_plural': 'Tooltip Fields'},
        ),
        migrations.AlterField(
            model_name='circlepattern',
            name='color',
            field=colorfield.fields.ColorField(default='#000000FF', help_text='The color of the fill pattern.', image_field=None, max_length=25, samples=None, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='circlepattern',
            name='fill_color',
            field=colorfield.fields.ColorField(default='#3388FF33', help_text='The fill color of the circles.', image_field=None, max_length=25, samples=None, verbose_name='Fill Color'),
        ),
        migrations.AlterField(
            model_name='circlepattern',
            name='height',
            field=models.IntegerField(default=4, help_text='The vertical distance between the circles (in pixels).', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Vertical Space'),
        ),
        migrations.AlterField(
            model_name='circlepattern',
            name='radius',
            field=models.IntegerField(default=12, help_text='The radius of the circles (in pixels).', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Radius'),
        ),
        migrations.AlterField(
            model_name='circlepattern',
            name='width',
            field=models.IntegerField(default=4, help_text='The horizontal distance between the circles (in pixels).', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Horizontal Space'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='control',
            field=models.BooleanField(default=True, help_text='Whether the feature group should be shown in the layer control.', verbose_name='Show in Layer Control'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='map_template',
            field=models.ForeignKey(help_text='The map template to which the feature group belongs.', on_delete=django.db.models.deletion.CASCADE, related_name='feature_groups', to='map_templates.maptemplate', verbose_name='Parent Map Template'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='name',
            field=models.CharField(help_text='The name of the feature group.', max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='overlay',
            field=models.BooleanField(default=True, help_text='Whether the feature group is an overlay, i.e., can be superimposed on other layers.', verbose_name='Is an Overlay'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='show_on_startup',
            field=models.BooleanField(default=False, help_text='Whether the display of the feature group should be enabled at startup.', verbose_name='Show on Startup'),
        ),
        migrations.AlterField(
            model_name='featuregroup',
            name='z_index',
            field=models.IntegerField(default=0, help_text='The index defining the display order of the feature groups. The higher the index, the more the feature group is displayed in the foreground.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Z-index'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='boundaries',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(blank=True, default=None, help_text='The boundaries of the layer. Any feature outside these boundaries will not be processed.', null=True, srid=4326, verbose_name='Boundaries'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='boundary_type',
            field=models.CharField(choices=[('intersect', 'Intersect'), ('strict', 'Strict'), ('crop', 'Crop')], default='intersect', help_text='Defines how the boundaries should be used. Intersect: any features intersecting or within the boundaries are kept in their entirety; Strict: only features completely within the boundaries are kept; Crop: any features intersecting the boundaries are cropped to fit within the boundaries, features outside are removed.', max_length=15, verbose_name='Boundary Type'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='dataset_layer',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='datasets.datasetlayer', verbose_name='Dataset Layer'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='name',
            field=models.CharField(help_text='The name of the layer.', max_length=100, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='show',
            field=models.BooleanField(default=True, help_text='Whether the display of the layer should be enabled at startup.', verbose_name='Show on Startup'),
        ),
        migrations.AlterField(
            model_name='layer',
            name='z_index',
            field=models.IntegerField(default=0, help_text='The index defining the display order of the layers. The higher the index, the more the layer is displayed in the foreground.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Z-index'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='center',
            field=django.contrib.gis.db.models.fields.PointField(default=django.contrib.gis.geos.point.Point(6.175715, 49.119308, srid=4326), help_text='The center of the map at startup.', srid=4326, verbose_name='Center'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='layer_control',
            field=models.BooleanField(default=True, help_text='Whether the layer control should be enabled.', verbose_name='Enable Layer Control'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='name',
            field=models.CharField(help_text='The name of the map template.', max_length=100, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='regenerate',
            field=models.BooleanField(default=False, help_text='Whether the map render should be regenerated.', verbose_name='Regenerate'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='task_id',
            field=models.UUIDField(blank=True, default=None, help_text='ID of the task generating the map render.', null=True, verbose_name='Task ID'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='task_status',
            field=models.CharField(blank=True, choices=[('PENDING', 'Pending'), ('STARTED', 'Started'), ('SUCCESS', 'Success'), ('FAILURE', 'Failure'), ('REVOKED', 'Revoked')], default=None, help_text='Status of the task generating the map render.', max_length=25, null=True, verbose_name='Task Status'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='tiles',
            field=models.ManyToManyField(help_text='The tiles to load on the map.', to='map_templates.tilelayer', verbose_name='Tiles'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='zoom_control',
            field=models.BooleanField(default=True, help_text='Whether the zoom control should be enabled.', verbose_name='Enable Zoom Control'),
        ),
        migrations.AlterField(
            model_name='maptemplate',
            name='zoom_start',
            field=models.SmallIntegerField(default=13, help_text='The zoom level of the map at startup.', validators=[django.core.validators.MinValueValidator(5), django.core.validators.MaxValueValidator(18)], verbose_name='Zoom Level at startup'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='color',
            field=colorfield.fields.ColorField(default='#3388ffff', help_text='The color of the shape.', image_field=None, max_length=25, samples=None, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='dash_array',
            field=models.CharField(blank=True, default=None, help_text="The dash pattern of the shape's border. A list of space-separated values that specify distances to alternately draw a line and a gap. ", max_length=50, null=True, validators=[map_templates.validators.validate_dash_array], verbose_name='Border dashes'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='dash_offset',
            field=models.CharField(blank=True, default=None, help_text="The offset between the dashes of the shape's border.", max_length=5, null=True, verbose_name="Border dashes' offset"),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='fill',
            field=models.BooleanField(default=True, help_text='Whether the shape should be filled.', verbose_name="Enable shape's fill"),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='fill_color',
            field=colorfield.fields.ColorField(blank=True, default='#3388ff33', help_text="The color of the shape's fill. If not set, the shape will use the color of the border.", image_field=None, max_length=25, null=True, samples=None, verbose_name='Fill Color'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='fill_rule',
            field=models.CharField(choices=[('nonzero', 'Nonzero'), ('evenodd', 'Even-Odd')], default='evenodd', help_text='The fill rule of the shape. Nonzero: the shape is filled if the winding number is not zero; Even-Odd: the shape is filled if the winding number is odd.', max_length=100, verbose_name='Fill Rule'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='line_cap',
            field=models.CharField(choices=[('butt', 'Butt'), ('round', 'Round'), ('square', 'Square')], default='round', help_text="The cap of the shape's border. Butt: flat ends (i.e., no cap); Round: rounded ends; Square: square ends.", max_length=6, verbose_name='Line Cap'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='line_join',
            field=models.CharField(choices=[('arcs', 'Arcs'), ('bevel', 'Bevel'), ('miter', 'Miter'), ('miter-clip', 'Miter-Clip'), ('round', 'Round')], default='round', help_text="The join of the shape's border. Arcs: arcs between the lines; Bevel: beveled corners; Miter: mitered corners; Miter-Clip: mitered corners with clipping; Round: rounded corners.", max_length=10, verbose_name='Line Join'),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='stroke',
            field=models.BooleanField(default=True, help_text='Whether the shapes border should be drawn.', verbose_name="Enable shape's borders"),
        ),
        migrations.AlterField(
            model_name='propertystyle',
            name='weight',
            field=models.FloatField(default=3, help_text="The width of the shape's border (in pixels).", validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Border Width'),
        ),
        migrations.AlterField(
            model_name='stripepattern',
            name='angle',
            field=models.FloatField(default=0.5, help_text='The angle of the stripes, in degrees, from an horizontal eastward line).', validators=[django.core.validators.MinValueValidator(-360.0), django.core.validators.MaxValueValidator(360.0)], verbose_name='Angle'),
        ),
        migrations.AlterField(
            model_name='stripepattern',
            name='color',
            field=colorfield.fields.ColorField(default='#000000FF', help_text='The color of the fill pattern.', image_field=None, max_length=25, samples=None, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='stripepattern',
            name='space_color',
            field=colorfield.fields.ColorField(default='#FFFFFFFF', help_text='The color of the spaces between the stripes.', image_field=None, max_length=25, samples=None, verbose_name='Space Color'),
        ),
        migrations.AlterField(
            model_name='stripepattern',
            name='space_weight',
            field=models.IntegerField(default=4, help_text='The width of the spaces between the stripes (in pixels).', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Space Width'),
        ),
        migrations.AlterField(
            model_name='stripepattern',
            name='weight',
            field=models.IntegerField(default=4, help_text='The width of the stripes (in pixels).', validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Stripe Width'),
        ),
        migrations.AlterField(
            model_name='style',
            name='color',
            field=colorfield.fields.ColorField(default='#3388ffff', help_text='The color of the shape.', image_field=None, max_length=25, samples=None, verbose_name='Color'),
        ),
        migrations.AlterField(
            model_name='style',
            name='dash_array',
            field=models.CharField(blank=True, default=None, help_text="The dash pattern of the shape's border. A list of space-separated values that specify distances to alternately draw a line and a gap. ", max_length=50, null=True, validators=[map_templates.validators.validate_dash_array], verbose_name='Border dashes'),
        ),
        migrations.AlterField(
            model_name='style',
            name='dash_offset',
            field=models.CharField(blank=True, default=None, help_text="The offset between the dashes of the shape's border.", max_length=5, null=True, verbose_name="Border dashes' offset"),
        ),
        migrations.AlterField(
            model_name='style',
            name='fill',
            field=models.BooleanField(default=True, help_text='Whether the shape should be filled.', verbose_name="Enable shape's fill"),
        ),
        migrations.AlterField(
            model_name='style',
            name='fill_color',
            field=colorfield.fields.ColorField(blank=True, default='#3388ff33', help_text="The color of the shape's fill. If not set, the shape will use the color of the border.", image_field=None, max_length=25, null=True, samples=None, verbose_name='Fill Color'),
        ),
        migrations.AlterField(
            model_name='style',
            name='fill_rule',
            field=models.CharField(choices=[('nonzero', 'Nonzero'), ('evenodd', 'Even-Odd')], default='evenodd', help_text='The fill rule of the shape. Nonzero: the shape is filled if the winding number is not zero; Even-Odd: the shape is filled if the winding number is odd.', max_length=100, verbose_name='Fill Rule'),
        ),
        migrations.AlterField(
            model_name='style',
            name='line_cap',
            field=models.CharField(choices=[('butt', 'Butt'), ('round', 'Round'), ('square', 'Square')], default='round', help_text="The cap of the shape's border. Butt: flat ends (i.e., no cap); Round: rounded ends; Square: square ends.", max_length=6, verbose_name='Line Cap'),
        ),
        migrations.AlterField(
            model_name='style',
            name='line_join',
            field=models.CharField(choices=[('arcs', 'Arcs'), ('bevel', 'Bevel'), ('miter', 'Miter'), ('miter-clip', 'Miter-Clip'), ('round', 'Round')], default='round', help_text="The join of the shape's border. Arcs: arcs between the lines; Bevel: beveled corners; Miter: mitered corners; Miter-Clip: mitered corners with clipping; Round: rounded corners.", max_length=10, verbose_name='Line Join'),
        ),
        migrations.AlterField(
            model_name='style',
            name='stroke',
            field=models.BooleanField(default=True, help_text='Whether the shapes border should be drawn.', verbose_name="Enable shape's borders"),
        ),
        migrations.AlterField(
            model_name='style',
            name='weight',
            field=models.FloatField(default=3, help_text="The width of the shape's border (in pixels).", validators=[django.core.validators.MinValueValidator(0.0)], verbose_name='Border Width'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='access_token',
            field=models.CharField(blank=True, default=None, help_text='Some tile providers require an access token to access their tiles. This field should be empty if no access token is required.', max_length=100, null=True, verbose_name='Access Token'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='attribution',
            field=models.CharField(blank=True, default=None, help_text='The attribution (credits) of the tile layer.', max_length=200, null=True, verbose_name='Attribution'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='control',
            field=models.BooleanField(default=True, help_text='Whether the tile layer should be shown in the layer control.', verbose_name='Show in Layer Control'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='name',
            field=models.CharField(help_text='The name of the tile layer.', max_length=100, unique=True, verbose_name='Name'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='overlay',
            field=models.BooleanField(default=True, help_text='Whether the tile layer is an overlay, i.e., can be superimposed on other layers.', verbose_name='Overlay'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='transparent',
            field=models.BooleanField(default=False, help_text='Whether the tile layer is transparent, i.e., has an alpha channel.', verbose_name='Transparent'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='type',
            field=models.CharField(choices=[('builtin', 'Built-in'), ('xyz', 'XYZ')], default='folium', help_text="The type of the tile layer. If 'folium', the tile is managed by Folium and the other fields are ignored.", max_length=7, verbose_name='Type'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='url',
            field=models.URLField(blank=True, default=None, help_text='The XYZ URL of the tile layer.', max_length=500, null=True, verbose_name='URL'),
        ),
        migrations.AlterField(
            model_name='tilelayer',
            name='verbose_name',
            field=models.CharField(blank=True, default=None, help_text='The verbose name of the tile layer.', max_length=100, null=True, unique=True, verbose_name='Verbose Name'),
        ),
        migrations.AlterField(
            model_name='tooltip',
            name='sticky',
            field=models.BooleanField(default=True, help_text='Whether the tooltip should stick to the mouse cursor.', verbose_name='Sticky'),
        ),
        migrations.AlterField(
            model_name='tooltip',
            name='style',
            field=models.TextField(blank=True, default=None, help_text='The CSS style of the tooltip.', null=True, verbose_name='Style'),
        ),
        migrations.AlterField(
            model_name='tooltipfield',
            name='alias',
            field=models.CharField(help_text='The alias of the field in the tooltip.', max_length=255, verbose_name='Alias'),
        ),
        migrations.AlterField(
            model_name='tooltipfield',
            name='index',
            field=models.IntegerField(default=0, help_text='The index of the field in the tooltip.', validators=[django.core.validators.MinValueValidator(0)], verbose_name='Index'),
        ),
    ]
