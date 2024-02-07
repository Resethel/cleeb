# -*- coding: utf-8 -*-
"""
Commands for the map_layers app.
"""
from django.core.management import BaseCommand

from datasets.models import Dataset
from map_layers.models import City, GenerationStatus

PREDEFINED_CITIES = [
    ("Amanvillers"             , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "AMANVILLERS"}),
    ("Ars-Laquenexy"           , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "ARS LAQUENEXY"}),
    ("Ars-sur-Moselle"         , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "ARS SUR MOSELLE"}),
    ("Augny"                   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "AUGNY"}),
    ("Le Ban-Saint-Martin"     , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LE BAN ST MARTIN"}),
    ("Châtel-Saint-Germain"    , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "CHATEL-SAINT-GERMAIN"}),
    ("Chesny"                  , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "CHESNY"}),
    ("Chieulles"               , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "CHIEULLES"}),
    ("Coin-lès-Cuvry"          , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "COIN-LES-CUVRY"}),
    ("Coin-sur-Seille"         , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "COIN-SUR-SEILLE"}),
    ("Cuvry"                   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "CUVRY"}),
    ("Féy"                     , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "FEY"}),
    ("Gravelotte"              , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "GRAVELOTTE"}),
    ("Jury"                    , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "JURY"}),
    ("Jussy"                   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "JUSSY"}),
    ("Laquenexy"               , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LAQUENEXY"}),
    ("Lessy"                   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LESSY"}),
    ("Longeville-lès-Metz"     , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LONGEVILLE-LES-METZ"}),
    ("Lorry-lès-Metz"          , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LORRY-LES-METZ"}),
    ("Lorry-Mardigny"          , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LORRY-MARDIGNY"}),
    ("Marieulles"              , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MARIEULLES"}),
    ("Marly"                   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MARLY"}),
    ("La Maxe"                 , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "LA MAXE"}),
    ("Mécleuves"               , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MECLEUVES"}),
    ("Metz"                    , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "METZ"}),
    ("Mey"                     , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MEY"}),
    ("Montigny-lès-Metz"       , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MONTIGNY LES METZ"}),
    ("Moulins-lès-Metz"        , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "MOULINS-LES-METZ"}),
    ("Noisseville"             , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "NOISSEVILLE"}),
    ("Nouilly"                 , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "NOUILLY"}),
    ("Peltre"                  , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "PELTRE"}),
    ("Plappeville"             , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "PLAPPEVILLE"}),
    ("Pouilly"                 , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "POUILLY"}),
    ("Pournoy-la-Chétive"      , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "POURNOY-LA-CHETIVE"}),
    ("Roncourt"                , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "RONCOURT"}),
    ("Rozérieulles"            , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "ROZERIEULLES"}),
    ("Saint-Julien-lès-Metz"   , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "SAINT-JULIEN-LES-METZ"}),
    ("Saint-Privat-la-Montagne", "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "SAINT-PRIVAT-LA-MONTAGNE"}),
    ("Sainte-Ruffine"          , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "SAINTE-RUFFINE"}),
    ("Saulny"                  , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "SAULNY"}),
    ("Scy-Chazelles"           , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "SCY-CHAZELLES"}),
    ("Vantoux"                 , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "VANTOUX"}),
    ("Vany"                    , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "VANY"}),
    ("Vaux"                    , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "VAUX"}),
    ("Vernéville"              , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "VERNEVILLE"}),
    ("Woippy"                  , "Communes de l'eurométropole de Metz", "Communes_emm.shp", {"nom": "WOIPPY"}),
]


class Command(BaseCommand):
    """A Django command to generate the map layers."""

    help = "Remplit les villes pré-définies."


    def handle(self, *args, **options):
        """Handle the command."""
        for city in PREDEFINED_CITIES:
            # Update the city if it exist, otherwise, create a new object
            if City.objects.filter(name=city[0]).exists():
                city_instance : City = City.objects.get(name=city[0])
                city_instance.limits_dataset = Dataset.objects.get(name=city[1])
                city_instance.limits_shapefile = city[2]
                city_instance.citydatasetkeyvalue_set.all().delete()
                for key, value in city[3].items():
                    city_instance.citydatasetkeyvalue_set.create(
                        key=key,
                        value=value
                    )
                city_instance.generation_status = GenerationStatus.PENDING
                city_instance.save()
                continue

            instance = City.objects.create(
                name=city[0],
                limits_dataset=Dataset.objects.get(name=city[1]),
                limits_shapefile=city[2],
                generation_status=GenerationStatus.PENDING
            )
            for key, value in city[3].items():
                instance.citydatasetkeyvalue_set.create(
                    key=key,
                    value=value
                )
            instance.save()
