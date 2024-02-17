from __future__ import annotations

from typing import Callable

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import connection
from django.utils.text import slugify
from folium.plugins import CirclePattern, StripePattern

from map_data.core.map.builder import MapBuilder
from map_data.core.map.template import FeatureGroup, Filter, Layer, MapTemplate, Style, Tile
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
                    map_layer="ZNIEFF de type 1",
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

    template.add_feature_group(
        FeatureGroup(
            name="Zones à urbaniser",
            show_on_startup=True,
            layers=[
                Layer(
                    name="Zones à urbaniser",
                    map_layer="PLUi - Zonage Géneral",
                    filters=[
                        Filter("Type de Zone", '==', 'AU')
                    ],
                    show_on_startup=True,
                    style=Style(
                        color="red",
                        fill_color="red",
                        fill_opacity=1.0,
                    ),
                    highlight=None
                )
            ],
        )
    )

    return template
# End def impact_znieff_type_1_template

def impact_zones_humides_template() -> MapTemplate:
    template = MapTemplate()
    template.name = "Impacts du zonage du PLUi sur les Zones Humides, Cours d'eau, Marres et Étangs."

    template.zoom_start = 15
    template.enable_layer_control = True
    template.tile = Tile.CARTO_DB_POSITRON

    template.add_feature_group(
        FeatureGroup(
            name="Zones Humides probables (seuillées)",
            show_on_startup=True,
            layers=[
                Layer(
                    name="Zones Humides probables seuillées",
                    map_layer="Zones humides probables (seuillées)",
                    show_on_startup=True,
                    style=Style(
                        color="orange",
                        weight=2,
                        fill_color="orange",
                        fill_opacity=0.2,
                        fill_pattern=StripePattern(
                            angle=-45,
                            weight=2,
                            color="orange",
                            space_opacity=0
                        ),
                    ),
                    highlight=None,
                )
            ]
        )
    )

    template.add_feature_group(
        FeatureGroup(
            name="Cours d'eau, Marres, Étangs et Zones Humides répertoriés dans le PLUi",
            show_on_startup=True,
            layers=[
                Layer(
                    name="Cours d'eau, Marres et Étangs répertoriés dans le PLUi",
                    map_layer="PLUi - Préscriptions surfaciques",
                    show_on_startup=True,
                    style=Style(
                        color="#EE82EE",
                        weight=1,
                        fill_color="#EE82EE",
                        fill_opacity=0.2,
                        fill_pattern=CirclePattern(radius=5, color="#0000FF")
                    ),
                    filters=[
                        Filter("Type", '==', "Eléments de paysage, sites et secteurs à préserver pour des motifs d’ordre écologique – Mares, étangs, cours d’eau"),
                    ],
                    highlight=None,
                ),
                Layer(
                    name="Zones Humides répertoriées dans le PLUi",
                    map_layer="PLUi - Préscriptions surfaciques",
                    show_on_startup=True,
                    style=Style(
                        color="darkblue",
                        weight=1,
                        fill_color="darkblue",
                        fill_opacity=0.2,
                        fill_pattern=StripePattern(
                            weight=2,
                            angle=45,
                            color="darkblue",
                            space_opacity=0
                        )
                    ),
                    filters=[
                        Filter("Type", '==',
                               "Eléments de paysage, sites et secteurs à préserver pour des motifs d’ordre écologique – Zones humides"),
                    ],
                    highlight=None,
                )
            ]
        )
    )



    template.add_feature_group(
        FeatureGroup(
            name="Zones à urbaniser",
            show_on_startup=True,
            layers=[
                Layer(
                    name="Zones à urbaniser",
                    map_layer="PLUi - Zonage Géneral",
                    show_on_startup=True,
                    filters=[
                        Filter("Type de Zone", '==', 'AU')
                    ],
                    style=Style(
                        color="red",
                        fill_color="red",
                        fill_opacity=1,
                    ),
                    highlight=Style(
                        color="red",
                        fill_color="red",
                        fill_opacity=1,
                    )
                )
            ]
        )
    )

    template.add_feature_group(
        FeatureGroup(
            name="OAPs répertoriées dans le PLUi",
            show_on_startup=True,
            layers=[
                Layer(
                    name="OAPs",
                    map_layer="PLUi - OAPs",
                    show_on_startup=True,
                    style=Style(
                        color="#8B0000", # Dark red
                        fill_color="#8B0000",
                        fill_opacity=1.0,
                        weight=5,
                    ),
                    highlight=Style(
                        color="#4B0000", # Darker red
                        fill_color="#4B0000",
                        fill_opacity=1,
                        weight=7,
                    )
                )
            ],
        )
    )

    return template
# End def impact_zones_humides_template



# ======================================================================================================================
# Command
# ======================================================================================================================

class Command(BaseCommand):
    help = "Regenerates the data linked to the map layers."

    TEMPLATES: list[Callable] = [
        impact_znieff_template,
        impact_zones_humides_template
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
                map_embed_html = ContentFile(name=f"{slugify(template.name)}.html", content=map_._repr_html_())
                map_full_html = ContentFile(name=f"{slugify(template.name)}_full.html",
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


