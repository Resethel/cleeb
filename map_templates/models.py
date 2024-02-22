# -*- coding: utf-8 -*-
from django.contrib import admin
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from xyzservices import TileProvider
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.core.exceptions import ValidationError
from colorfield.fields import ColorField

from map_templates import tasks
from map_templates.choices import GenerationStatus
from map_templates.objects.templates import MapTemplate as MapTemplateObject

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
        help_text="Indique si les bordures des formes doivent être dessinées."
    )

    # Color of the style
    color = ColorField(
        default='#3388ff',
        format="hex",
        help_text="La couleur des bordures des formes."
    )

    # Weight of the style
    weight = models.FloatField(
        default=3,
        validators=[
            MinValueValidator(0.0)
        ],
        help_text="L'épaisseur des bordures des formes."
    )

    # Opacity of the style
    opacity = models.FloatField(
        default=1.0,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        help_text="L'opacité des bordures des formes."
    )

    # Line cap of the style
    line_cap = models.CharField(
        max_length=6,
        choices=[
            ("butt"  , "Butt"),
            ("round" , "Round"),
            ("square", "Square")
        ],
        default="round",
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
        help_text="La jonction des bordures des formes."
    )

    # Dash array of the style
    dash_array = models.CharField(
        max_length=5,
        default=None,
        blank=True,
        null=True,
        help_text="Chaîne de charactères définissant le motif de la bordure des formes."
    )

    # Dash offset of the style
    dash_offset = models.CharField(
        max_length=5,
        default=None,
        blank=True,
        null=True,
        help_text="Chaîne définissant la distance entre les motifs de la bordure des formes."
    )

    # Fill of the style
    fill = models.BooleanField(
        default=False,
        blank=True,
        null=True,
        help_text="Indique si les formes doivent être remplies."
    )

    # Fill color of the style
    fill_color = ColorField(
        default=None,
        blank=True,
        null=True,
        help_text="La couleur de remplissage des formes. Si non défini, la couleur de bordure est utilisée."
    )

    # Fill opacity of the style
    fill_opacity = models.FloatField(
        default=0.2,
        validators=[
            MinValueValidator(0.0),
            MaxValueValidator(1.0)
        ],
        help_text="L'opacité de remplissage des formes."
    )

    # Fill rule of the style
    fill_rule = models.CharField(
        max_length=100,
        choices=[
            ("nonzero", "Nonzero"),
            ("evenodd", "Evenodd")
        ],
        default='evenodd',
        help_text="La règle de remplissage des formes."
    )

    # TODO: Add fill patterns

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        abstract = True
    # End class Meta
# End class BaseStyle

class Style(BaseStyle):

    id = models.AutoField(primary_key=True)

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
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"Style@{self.id}"
    # End def __str__
# End class LayerStyle

class PropertyStyle(BaseStyle):

    id = models.AutoField(primary_key=True)
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

    style = models.ForeignKey(
        'Style',
        related_name='property_styles',
        on_delete=models.CASCADE,
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"PropertyStyle[{self.key}={self.value}]@{self.id}"
    # End def __str__

    class Meta:
        verbose_name = "Style de propriété"
        verbose_name_plural = "Styles des propriétés"
# End class LayerPropertyStyle


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
# Layer
# ======================================================================================================================

class Layer(models.Model):
    """Represents a map layer.

    A map layer is a layer of data that can be shown or hidden on the map.
    The map layer to load is defined by its name in the database.
    """

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
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # Name of the layer
    name = models.CharField(
        max_length=100,
        help_text="Nom de la couche cartographique."
    )

    # Map layer to load
    map_layer = models.ForeignKey(
        'map_layers.MapLayer',
        on_delete=models.SET_NULL,
        default=None,
        blank=True,
        null=True
    )

    show = models.BooleanField(
        default=False,
        verbose_name="Afficher au démarrage",
        help_text="Si la couche doit être affichée au démarrage."
    )

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


# ======================================================================================================================
# Feature groups
# ======================================================================================================================

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

    task_id = models.CharField(
        verbose_name="ID de la tâche",
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="ID de la tâche asynchrone utilisée pour générer le rendu de la carte."
    )

    generation_status = models.CharField(
        verbose_name="Statut de la génération",
        max_length=10,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        help_text="Statut de la génération du rendu de la carte."
    )

    regenerate = models.BooleanField(
        verbose_name="Regénérer",
        default=False,
        help_text="Relance la génération du rendu de la carte."
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
    print(f"{instance}: {instance.generation_status}, {instance.task_id}")
    if instance.generation_status in [None, GenerationStatus.PENDING]:
        tasks.generate_map_render_from_map_template_task.delay(instance.id)

    # Edge case where something went wrong and a task was killed midway
    elif instance.generation_status == GenerationStatus.RUNNING:
        if instance.task_id is None:
            tasks.generate_map_render_from_map_template_task.delay(instance.id)

    # In the case where the status is either COMPLETED or FAILED,
    # only submit a task if the user has requested to regenerate the geometries
    elif instance.regenerate:
        tasks.generate_map_render_from_map_template_task.delay(instance.id)
        instance.regenerate = False
        instance.save()
# End def generate_map_layer_geometries