# Manually created on 2024-01-10 18:02
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shapes', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL("""
            INSERT INTO shapes_shape (
                id,
                feature_type,
                geometry_type,
                geometry_coordinates,
                properties,
                content_type_id,
                object_id
            )
            SELECT
                id,
                feature_type,
                geometry_type,
                geometry_coordinates,
                properties,
                content_type_id,
                object_id
            FROM map_data_shape
        """, reverse_sql="""
            INSERT INTO map_data_shape (
                id,
                feature_type,
                geometry_type,
                geometry_coordinates,
                properties,
                content_type_id,
                object_id
            )
            SELECT
                id,
                feature_type,
                geometry_type,
                geometry_coordinates,
                properties,
                content_type_id,
                object_id
            FROM shapes_shapes
        """)
    ]
