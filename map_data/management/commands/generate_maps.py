from __future__ import annotations

from typing import Callable

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import connection

from map_data.core.map.builder import MapBuilder
from map_data.core.map.template import FeatureGroup, Layer, MapTemplate, Style, Tile
from map_data.core.utils import snake_case
from map_data.models import MapRender

# ======================================================================================================================
# Helper functions
# ======================================================================================================================

def reset_auto_field(model):
    with connection.cursor() as cursor:
        cursor.execute(f"UPDATE sqlite_sequence SET seq = 0 WHERE name = '{model._meta.db_table}';")

# ======================================================================================================================
# Map templates functions
# ======================================================================================================================

# NOTE: This way of generating map templates is temporary for the prototype demonstration.
#       In the future, the map templates will be generated from the database in a separate application and in a more
#       dynamic way.
def impact_znieff_template() -> MapTemplate:
    template = MapTemplate()
    template.name = "Impacts du PLUi sur les ZNIEFF "

    template.zoom_start = 15
    template.enable_layer_control = True
    template.tile = Tile.CARTO_DB_POSITRON

    template.add_feature_group(
        FeatureGroup(
            name="ZNIEFF de type 1",
            show_on_startup=True,
            layers=[
                Layer(
                    name="ZNIEFF de type 1",
                    map_layer="znieff_type_1",
                    show_on_startup=True,
                    style=Style(
                        color="green",
                        fill_color="green",
                        fill_opacity=0.5,
                    ),
                    highlight=Style(
                        color="red",
                        fill_color="red",
                        fill_opacity=0.5,
                    )
                )
            ]
        )
    )

    return template
# End def impact_znieff_type_1_template




# ======================================================================================================================
# Command
# ======================================================================================================================

class Command(BaseCommand):
    help = "Regenerates the data linked to the map layers."

    TEMPLATES: list[Callable] = [
        impact_znieff_template,
    ]

    def handle(self, *args, **options):

        for template_generator in self.TEMPLATES:
            template = template_generator()
            map_render_name = template.name
            print(f"Generating map for {template.name}...")

            # 1. Generate the map
            map_ = MapBuilder(template_generator()).build()

            # 2. Check if the map already exists
            map_render : MapRender | None = MapRender.objects.filter(name=map_render_name).first()

            # 3. If the map does not exist, create it
            if map_render is None:
                print(f"Creating new map render '{template.name}'...")
                map_embed_html = ContentFile(name=f"{snake_case(template.name)}.html", content=map_._repr_html_())
                map_full_html = ContentFile(name=f"{snake_case(template.name)}_full.html",
                                            content=map_.get_root().render())
                MapRender.objects.create(
                    name=template.name,
                    embed_html=map_embed_html,
                    full_html=map_full_html,
                )

            # 4. If the map already exists, update it
            else:
                print(f"Updating map render '{template.name}'...")
                with map_render.embed_html.open("w") as f:
                    f.write(map_._repr_html_())
                with map_render.full_html.open("w") as f:
                    f.write(map_.get_root().render())
# End class Command


