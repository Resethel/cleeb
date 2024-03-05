# -*- coding: utf-8 -*-
"""
Models for the `map_templates` application.
"""
from colorfield.fields import ColorField
from django.contrib import admin
from django.contrib.gis.db import models as gis_models
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from xyzservices import TileProvider

from common.utils.tasks import TaskStatus
from map_templates import tasks
from map_templates.services.templates import MapTemplate as MapTemplateObject
from map_templates.validators import validate_dash_array

# ======================================================================================================================
# Constants
# ======================================================================================================================

MIN_ZOOM = 5
MAX_ZOOM = 18

# ======================================================================================================================
# Tile
# ======================================================================================================================

class TileLayer(models.Model):
    """Represents a Leaflet/Folium tile layer."""

    # ID of the tile
    id = models.AutoField(primary_key=True)

    # Name of the tile
    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name="Nom",
        help_text="Nom de la tuile de carte."
    )

    verbose_name = models.CharField(
        unique=True,
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name="Nom d'affichage",
        help_text="Le nom d'affichage de la tuile de carte. Laisser vide pour utiliser le nom par défaut."
    )

    transparent = models.BooleanField(
        default=False,
        verbose_name="Transparence",
        help_text="Si les tuiles de carte doivent être transparentes."
    )

    overlay = models.BooleanField(
        default=True,
        verbose_name="Superposition",
        help_text="Si les tuiles de carte sont des superpositions."
    )

    control = models.BooleanField(
        default=True,
        verbose_name="Contrôle",
        help_text="Si les tuiles de carte peuvent être sélectionner."
    )

    type = models.CharField(
        max_length=7,
        choices=[
            ('builtin', 'Intégrée'),
            ('xyz', 'XYZ')
        ],
        default='folium',
        verbose_name="Type",
        help_text="Le type de tuile de carte.Si 'folium', la tuile est gérée par Folium et les autres champs sont ignorés."
    )

    # URL of the tile
    url = models.URLField(
        max_length=500,
        default=None,
        blank=True,
        null=True,
        verbose_name="URL",
        help_text="L'URL 'XYZ' de la tuile de carte."
    )


    # Attribution of the tile
    attribution = models.CharField(
        max_length=200,
        default=None,
        blank=True,
        null=True,
        verbose_name="Attribution",
        help_text="L'attribution de la tuile de carte."
    )

    # Access token of the tile (if any)
    access_token = models.CharField(
        max_length=100,
        default=None,
        blank=True,
        null=True,
        verbose_name="Jeton d'accès",
        help_text="Le jeton d'accès de la tuile de carte."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def clean(self):

        # First, call the parent clean method
        super().clean()

        # For built-in tiles, the URL and the attribution should be empty
        if self.type == "builtin":
            self.url = None
            self.attribution = None
            self.access_token = None
            return

        if self.url is None or self.url == "":
            raise ValidationError("L'URL est requise pour les tuiles XYZ.")
        if self.attribution is None or self.attribution == "":
            raise ValidationError("L'attribution est requise pour les tuiles XYZ.")

        # Check if the access token is required
        temp_provider : TileProvider = TileProvider(
            name=self.name,
            url=self.url,
            attribution=self.attribution
        )

        # Check if the access token is required
        requires_token = temp_provider.requires_token()
        if not requires_token:
            # If the access token is not required, it should be empty to avoid confusion
            self.access_token = None
        # If it is required, check if it is provided
        elif self.access_token is None or self.access_token == "":
            raise ValidationError(f"Un jeton d'accès est requis pour la tuile '{self.name}@{self.url}'.")
        # If it is provided, check if it is valid
        else:
            temp_provider["accessToken"] = self.access_token
            if temp_provider.requires_token(): # requires_token() should return False if the token is valid
                raise ValidationError(f"Le jeton d'accès fourni est invalide pour la tuile '{self.name}@{self.url}'.")

        # The url can be quite long, so it is splittable in multiple lines in the admin
        # So we must make sure that no line break is present in the URL
        if self.url is not None:
            self.url = self.url.replace("\n", "")
            self.url = self.url.replace("\r", "")
            self.url = self.url.replace("\t", "")
            self.url = self.url.strip()
            self.url = self.url.replace(" ", "")
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Tuile de carte"
        verbose_name_plural = "Tuiles de carte"
    # End class Meta
# End class TileLayer

@receiver(pre_save, sender=TileLayer)
def fill_missing_verbose_name(sender, instance, **kwargs):
    """If the verbose name is not set, fill it with the name."""
    if instance.verbose_name is None or instance.verbose_name == "":
        instance.verbose_name = instance.name.title()
# End def fill_missing_verbose_name

# ======================================================================================================================
# FillPatterns
# ======================================================================================================================

class FillPattern(models.Model):
    """Represent a Leaflet pattern."""

    # ------------------------------------------------------------------------------------------------------------------
    # Identification fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    color = ColorField(
        default="#000000FF",
        format="hexa",
        verbose_name="Couleur des Bandes",
        help_text="La couleur des bandes."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description="Opacité")
    def opacity(self) -> float:
        return int(self.color[7:9], 16) / 255
    # End def opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        abstract = True
    # End class Meta
# End class FillPattern

class StripePattern(FillPattern):
    """ Represents a Leaflet stripe pattern. """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    space_color = ColorField(
        default="#FFFFFFFF",
        format="hexa",
        verbose_name="Couleur des Espaces",
        help_text="La couleur de l'espace entre les bandes."
    )

    # Stripe width
    weight = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Largeur",
        help_text="La largeur des bandes (en pixels)."
    )

    space_weight = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Largeur des espaces",
        help_text="La largeur de l'espace entre les bandes (en pixels)."
    )

    angle = models.FloatField(
        default=0.5,
        validators=[
            MinValueValidator(-360.0),
            MaxValueValidator(360.0)
        ],
        verbose_name="Angle",
        help_text="L'angle des bandes (en degrés)."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description="Opacité des espaces")
    def space_opacity(self) -> float:
        return int(self.space_color[7:9], 16) / 255
    # End def space_opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"StripePattern@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------
    class Meta:
        verbose_name = "Motif à rayures"
        verbose_name_plural = "Motifs à rayures"
    # End class Meta
# End class StripePattern

class CirclePattern(FillPattern):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    width = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Distance horizontale",
        help_text="Distance (horizontale) entre les cercles"
    )

    height = models.IntegerField(
        default=4,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Distance verticale",
        help_text="Distance (verticale) entre les cercles"
    )

    radius = models.IntegerField(
        default=12,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Rayon",
        help_text="Le rayon des cercles (en pixels)."
    )

    fill_color = ColorField(
        default="#3388FF33",
        format="hexa",
        verbose_name="Couleur de remplissage",
        help_text="La couleur de remplissage des cercles."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description="Opacité de remplissage")
    def fill_opacity(self) -> float:
        return int(self.fill_color[7:9], 16) / 255
    # End def fill_opacity

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"CirclePattern@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Motif en cercle"
        verbose_name_plural = "Motifs en cercle"
    # End class Meta
# End class CirclePattern

# ======================================================================================================================
# Styles
# ======================================================================================================================

class BaseStyle(models.Model):
    """Represents a Leaflet style."""

    # ID of the style
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    stroke = models.BooleanField(
        default=True,
        verbose_name="Bordures",
        help_text="Indique si les bordures des formes doivent être dessinées."
    )

    # Color of the style
    color = ColorField(
        default='#3388ffff',
        format="hexa",
        verbose_name="Couleur",
        help_text="La couleur des bordures des formes."
    )

    # Weight of the style
    weight = models.FloatField(
        default=3,
        validators=[
            MinValueValidator(0.0)
        ],
        verbose_name="Épaisseur",
        help_text="L'épaisseur des bordures des formes (en pixels)."
    )

    # Line cap of the style
    line_cap = models.CharField(
        max_length=6,
        choices=[
            ("butt"  , "Plate"),
            ("round" , "Ronde"),
            ("square", "Carrée")
        ],
        default="round",
        verbose_name="Terminaison",
        help_text="La terminaison des bordures des formes."
    )

    # Line join of the style
    line_join = models.CharField(
        max_length=10,
        choices=[
            ("arcs"      , "Arcs"),
            ("bevel"     , "Bevel"),
            ("miter"     , "Miter"),
            ("miter-clip", "Miter-clip"),
            ("round"     , "Round")
        ],
        default="round",
        verbose_name="Jonction",
        help_text="La jonction des bordures des formes."
    )

    # Dash array of the style
    dash_array = models.CharField(
        max_length=50,
        default=None,
        blank=True,
        null=True,
        validators=[validate_dash_array],
        verbose_name="Pointillés",
        help_text="Motif des Pointillés.",
    )

    # Dash offset of the style
    dash_offset = models.CharField(
        max_length=5,
        default=None,
        blank=True,
        null=True,
        verbose_name="Espacement des pointillés",
        help_text="Espacements des Pointillés."
    )

    # Fill of the style
    fill = models.BooleanField(
        default=True,
        verbose_name="Remplissage",
        help_text="Indique si les formes doivent être remplies."
    )

    # Fill color of the style
    fill_color = ColorField(
        default='#3388ff33',
        format="hexa",
        blank=True,
        null=True,
        verbose_name="Couleur de remplissage",
        help_text="La couleur de remplissage des formes. Si non défini, la couleur de bordure est utilisée."
    )

    # Fill rule of the style
    fill_rule = models.CharField(
        max_length=100,
        choices=[
            ("nonzero", "Nonzero"),
            ("evenodd", "Evenodd")
        ],
        default='evenodd',
        verbose_name="Règle de remplissage",
        help_text="La règle de remplissage des formes."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Pattern fields
    # ------------------------------------------------------------------------------------------------------------------

    circle_pattern = models.OneToOneField(
        'CirclePattern',
        related_name='%(class)s',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    stripe_pattern = models.OneToOneField(
        'StripePattern',
        related_name='%(class)s',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Non-persistent fields
    # ------------------------------------------------------------------------------------------------------------------

    @property
    @admin.display(description="Opacité")
    def opacity(self) -> float:
        return int(self.color[7:9], 16) / 255
    # End def opacity

    @property
    @admin.display(description="Opacité de remplissage")
    def fill_opacity(self) -> float:
        return int(self.fill_color[7:9], 16) / 255
    # End def fill_opacity

    @property
    @admin.display(description="Motif de remplissage")
    def fill_pattern(self):
        if self.circle_pattern is not None:
            return self.circle_pattern
        if self.stripe_pattern is not None:
            return self.stripe_pattern
        return None
    # End def fill_pattern

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"
    # End def __str__

    def clean(self):
        super().clean()
        if self.stroke is False and self.fill is False:
            raise ValidationError("Le style ne peut pas être vide.")

        if self.circle_pattern is not None and self.stripe_pattern is not None:
            raise ValidationError(
                "Le style ne peut être remplit à la fois par un motif en cercle et par un motif à rayures.",
                params={
                    "circle_pattern": self.circle_pattern,
                    "stripe_pattern": self.stripe_pattern
                }
            )
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        abstract = True
    # End class Meta
# End class BaseStyle

class Style(BaseStyle):

    # ------------------------------------------------------------------------------------------------------------------
    # Admin display
    # ------------------------------------------------------------------------------------------------------------------

    @admin.display(description="Type")
    def style_type(self):
        if hasattr(self, "style_of") and self.style_of is not None:
            return "Style"
        if hasattr(self, "highlight_of") and self.highlight_of is not None:
            return "Surbrillance"
        return "Non défini"
    # End def style_type

    @admin.display(description="Couche")
    def owning_layer(self):
        if hasattr(self, "style_of") and isinstance(self.style_of, Layer):
            return str(self.style_of)
        if hasattr(self, "highlight_of") and isinstance(self.highlight_of, Layer):
            return str(self.highlight_of)
        return "Non défini"


    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Style"
        verbose_name_plural = "Styles"
# End class LayerStyle

class PropertyStyle(BaseStyle):

    # ------------------------------------------------------------------------------------------------------------------
    # Parent fields
    # ------------------------------------------------------------------------------------------------------------------

    style = models.ForeignKey(
        'Style',
        related_name='property_styles',
        on_delete=models.CASCADE,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Filter fields
    # ------------------------------------------------------------------------------------------------------------------

    key = models.CharField(max_length=100)
    value = models.CharField(max_length=100)
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", "String"),
            ("number", "Number"),
            ("boolean", "Boolean")
        ],
        default="string"
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"PropertyStyle[{self.key}={self.value}]@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Style de propriété"
        verbose_name_plural = "Styles des propriétés"
# End class PropertyStyle


# ======================================================================================================================
# Filter
# ======================================================================================================================

class Filter(models.Model):

    # ID of the filter
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Ownership fields
    # ------------------------------------------------------------------------------------------------------------------

    layer = models.ForeignKey(
        'Layer',
        related_name='filters',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    key = models.CharField(max_length=100)

    # Operator of the filter
    operator = models.CharField(
        max_length=100,
        choices=[
            ("==", "=="),
            ("!=", "!="),
            (">", ">"),
            (">=", ">="),
            ("<", "<"),
            ("<=", "<=")
        ]
    )

    # Value of the filter
    value = models.CharField(max_length=100)
    value_type = models.CharField(
        max_length=10,
        choices=[
            ("string", "String"),
            ("number", "Number"),
            ("boolean", "Boolean")
        ],
        default="string"
    )


    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Filter[{self.key}{self.operator}{self.value}]@{self.id}"
    # End def __str__

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Filtre"
        verbose_name_plural = "Filtres"
        unique_together = ('layer', 'key', 'operator', 'value')
    # End class Meta
# End class Filter

# ======================================================================================================================
# MapFeatures
# ======================================================================================================================

# TODO: Add an abstract class for the map features

class Layer(models.Model):
    """Represents a map layer.

    A map layer is a layer of data that can be shown or hidden on the map.
    The map layer to load is defined by its name in the database.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Identification fields
    # ------------------------------------------------------------------------------------------------------------------

    # ID of the layer
    id = models.AutoField(primary_key=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Ownership fields
    # ------------------------------------------------------------------------------------------------------------------

    owner_feature_group = models.ForeignKey(
        'FeatureGroup',
        related_name='layers',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    owner_map_template = models.ForeignKey(
        'MapTemplate',
        related_name='layers',
        on_delete=models.CASCADE,
        default=None,
        blank=True,
        null=True
    )

    @property
    def owner(self):
        if self.owner_feature_group is not None:
            return self.owner_feature_group
        elif self.owner_map_template is not None:
            return self.owner_map_template
        else:
            return None
    # End def owner

    # ------------------------------------------------------------------------------------------------------------------
    # Metadata Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Name of the layer
    name = models.CharField(
        max_length=100,
        help_text="Nom de la couche cartographique."
    )

    show = models.BooleanField(
        default=False,
        verbose_name="Afficher au démarrage",
        help_text="Si la couche doit être affichée au démarrage."
    )

    z_index = models.IntegerField(
        default=0,
        verbose_name="z-index",
        help_text="Index definissant l'ordre d'affichage des couches. "
                  "Plus l'index est élevé, plus la couche est affichée en premier plan.",
        validators=[
            MinValueValidator(0)
        ]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Dataset relations Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Dataset Layer to load
    dataset_layer = models.ForeignKey(
        'datasets.DatasetLayer',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True,
        verbose_name="Couche de jeu de données",
    )

    # Boundaries of the layer
    boundaries = gis_models.MultiPolygonField(
        blank=True,
        null=True,
        default=None,
        verbose_name="Délimitations",
        help_text="La délimitations de la couche cartographique. Tout ce qui est en dehors de cette zone ne sera pas utilisé."
    )

    boundary_type = models.CharField(
        max_length=15,
        choices=[
            ("intersect", "Intersection"),
            ("strict", "Stricte"),
            ("crop", "Recadrement"),
        ],
        default="intersect",
        verbose_name="Type de délimitation",
        help_text="Le type de délimitation de la couche cartographique."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Style Fields
    # ------------------------------------------------------------------------------------------------------------------

    style = models.OneToOneField(
        'Style',
        related_name='style_of',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    highlight = models.OneToOneField(
        'Style',
        related_name='highlight_of',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
       return f"Layer[{self.name}]@{self.id}"
    # End def __str__

    def clean(self):
        if self.owner_feature_group is None and self.owner_map_template is None:
            raise ValidationError("La couche doit appartenir à un groupe de fonctionnalités ou à un modèle de carte.")
        if self.owner_feature_group is not None and self.owner_map_template is not None:
            raise ValidationError("La couche ne peut appartenir à la fois à un groupe de fonctionnalités et à un modèle de carte.")
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche"
        verbose_name_plural = "Couches"
# End class Layer

class FeatureGroup(models.Model):
    """Represents a group of features on the map.

    A feature group is a group of features that can be shown or hidden on the map.
    The feature group to load is defined by its name in the database.
    """

    # ID of the feature group
    id = models.AutoField(primary_key=True)

    # Name of the feature group
    name = models.CharField(
        max_length=100,
        help_text="Nom du groupe de fonctionnalités."
    )

    # Related map template
    map_template = models.ForeignKey(
        'MapTemplate',
        related_name='feature_groups',
        on_delete=models.CASCADE,
        verbose_name="Modèle de carte",
        help_text="Le modèle de carte auquel appartient le groupe de fonctionnalités."
    )

    overlay = models.BooleanField(
        default=True,
        verbose_name="Superposable",
        help_text="Si le groupe de fonctionnalités est superposable (cochée avec une case à cocher) ou non (cochée avec un bouton radio)."
    )

    control = models.BooleanField(
        default=True,
        verbose_name="Contrôlable",
        help_text="Si le groupe de fonctionnalités est inclue dans le contrôle des couches."
    )

    show_on_startup = models.BooleanField(
        default=False,
        help_text="Si le groupe de fonctionnalités doit être affiché au démarrage."
    )

    z_index = models.IntegerField(
        default=0,
        verbose_name="z-index",
        help_text="Index definissant l'ordre d'affichage des couches. "
                   "Plus l'index est élevé, plus la couche est affichée en premier plan.",
        validators=[
            MinValueValidator(0)
        ]
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"FeatureGroup[{self.name}]@{self.id}"

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Groupe de fonctionnalités"
        verbose_name_plural = "Groupes de fonctionnalités"
    # End class Meta
# End class FeatureGroup

# ======================================================================================================================
# Map template
# ======================================================================================================================

class MapTemplate(models.Model):
    """Represents a map template.

    Used by the map creator to render a Leaflet map with the desired layers and features.
    Once defined, the map template is validated and saved in the database.
    A routine then generates the corresponding HTML file to be used in the web application.
    """

    # ID of the map template
    id = models.AutoField(primary_key=True)

    # Name of the map template
    name = models.CharField(
        unique=True,
        max_length=100,
        help_text="Nom du modèle de carte.",
        verbose_name="Nom du modèle"
    )

    # Zoom start of the map template
    zoom_start = models.SmallIntegerField(
        default=int(MIN_ZOOM + 2/3 * (MAX_ZOOM - MIN_ZOOM)),
        validators=[
            MinValueValidator(MIN_ZOOM),
            MaxValueValidator(MAX_ZOOM)
        ],
        help_text="Le niveau de zoom initial de la carte.",
        verbose_name="Niveau de zoom initial"
    )

    # Center of the map template
    # Defaults to Metz, France: lat=49.119308, lon=6.175715 (because why not?)
    center = gis_models.PointField(
        default=Point(6.175715, 49.119308, srid=4326),
        srid=4326, # Keep the SRID to 4326 for compatibility with Leaflet
        verbose_name="Centre",
        help_text="Le centre de la carte."
    )

    # Enable layer control of the map template
    layer_control = models.BooleanField(
        default=True,
        help_text="Activer le contrôle des couches de la carte.",
        verbose_name="Activer le contrôle des couches"
    )

    # Enable zoom control of the map template
    zoom_control = models.BooleanField(
        default=True,
        help_text="Activer le contrôle du zoom de la carte.",
        verbose_name="Activer le contrôle du zoom"
    )

    # Tiles to load on the map
    tiles = models.ManyToManyField(
        'TileLayer',
        verbose_name="Tuiles de carte",
        help_text="Les tuiles de carte à charger sur la carte."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Task specific fields
    # ------------------------------------------------------------------------------------------------------------------

    task_id = models.UUIDField(
        blank=True,
        null=True,
        default=None,
        verbose_name="ID de la tâche",
        help_text="ID de la tâche de génération des entités géographiques."
    )

    task_status = models.CharField(
        max_length=25,
        blank=True,
        null=True,
        default=None,
        choices=TaskStatus,
        help_text="Statut de la tâche de génération des entités géographiques."
    )

    regenerate = models.BooleanField(
        default=False,
        help_text="Indique si les entités géographiques doivent être régénérées."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def as_template_object(self) -> MapTemplateObject:
        """Returns the map template object."""
        return MapTemplateObject.from_model(self)
    # End def as_template_object

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Modèle de carte"
        verbose_name_plural = "Modèles de carte"
    # End class Meta
# End class MapTemplate


@receiver(post_save, sender=MapTemplate)
def generate_map_render(sender, instance, created, **kwargs):
    """Generate the render of the map template."""
    if created:
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
    elif instance.regenerate:
        # Revoke the previous task to avoid multiple renders
        if instance.task_id is not None:
            tasks.generate_maprender_from_maptemplate_task.AsyncResult(str(instance.task_id)).revoke()
        tasks.generate_maprender_from_maptemplate_task.delay(instance.id)
# End def generate_map_render