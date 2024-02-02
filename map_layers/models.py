from __future__ import annotations

import uuid
import zipfile

import geojson
from celery import current_app
from django.contrib.contenttypes.fields import GenericRelation
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator
from django.db import models, transaction
from django.db.models.signals import pre_save
from django.dispatch import receiver

# ======================================================================================================================
# Choices
# ======================================================================================================================

# Dataset formats
SHAPEFILE = 'shapefile'
GEOJSON = 'geojson'
DATASET_FORMAT_CHOICES = {
    SHAPEFILE: 'Shapefile',
    GEOJSON: 'GeoJSON'
}

# Encodings
UTF8 = 'utf-8'
UTF16 = 'utf-16'
LATIN1 = 'latin-1'
ASCII = 'ascii'
ENCODING_CHOICES = {
    UTF8: 'UTF-8',
    LATIN1: 'Latin-1',
    UTF16: 'UTF-16',
    ASCII: 'ASCII'
}

# ======================================================================================================================
# Enums
# ======================================================================================================================

class GenerationStatus(models.TextChoices):
    """Status of a map layer."""
    PENDING = 'PENDING', 'En attente de génération'
    GENERATING = 'GENERATING', 'Génération en cours'
    DONE = 'DONE', 'Génération terminée'
    ERROR = 'ERROR', 'Erreur lors de la génération'
# End class GenerationStatus


# ======================================================================================================================
# Dataset Model
# ======================================================================================================================

def validate_dataset_file(instance : Dataset):
    if instance.format == SHAPEFILE:
        if not zipfile.is_zipfile(instance.file):
            raise ValidationError('Le fichier doit être un fichier ZIP.')
        else:
            try:
                zip_file : zipfile.ZipFile
                with zipfile.ZipFile(instance.file) as zip_file:
                    if not zip_file.testzip() is None:
                        raise ValidationError('Le fichier ZIP est corrompu.')
                    else:
                        # Check that the zip file contains at least one file with a .shp extension
                        shapefile_found = False
                        for file_name in zip_file.namelist():
                            if file_name.endswith('.shp'):
                                shapefile_found = True
                                break
                        if not shapefile_found:
                            raise ValidationError('Le fichier ZIP doit contenir au moins un fichier avec une extension .shp.')
            except zipfile.BadZipFile:
                raise ValidationError('Le fichier ZIP est corrompu.')

    elif instance.format == GEOJSON:
        try:
            obj : geojson.GeoJSON = geojson.loads(instance.file.read())
            if not obj.is_valid:
                raise ValidationError('Le fichier doit être un fichier GeoJSON valide. (erreur: {})'.format(obj.errors()))
        except ValueError:
            raise ValidationError('Le fichier doit être un fichier GeoJSON.')

        finally:
            # Reset the file pointer to the beginning of the file
            instance.file.seek(0)

    else:
        raise ValidationError('Le format du jeu de données est invalide.')
# End def validate_dataset_file

class Dataset(models.Model):
    """A dataset is a file containing geographic data.

    It can be either a ZIP file containing a shapefile, or a GeoJSON.
    """

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Nom du jeu de données"
    )

    category = models.CharField(
        max_length=100,
        blank=True,
        help_text="Catégorie du jeu de données. Optionnel."
    )

    short_desc = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Description courte du jeu de données. Optionnel. Utilisé pour générer l'aide contextuelle."
    )

    description = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Description du jeu de données. Optionnel."
    )

    format = models.CharField(
        max_length=10,
        choices=DATASET_FORMAT_CHOICES,
        help_text="Format du jeu de données. Soit un fichier ZIP contenant un fichier shapefile, soit un fichier GeoJSON."
    )

    def get_file_path(self, _):
        return f'datasets/{uuid.uuid4()}'
    # End def get_file_path

    file = models.FileField(
        upload_to=get_file_path,
        help_text="Fichier du jeu de données. Le fichier doit correspondre au format choisi.",
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self):
        validate_dataset_file(self)
    # End def clean

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Jeu de données"
        verbose_name_plural = "Jeux de données"
        ordering = ['name']
    # End class Meta
# End class Dataset

@receiver(pre_save, sender=Dataset)
def dataset_pre_save(sender, instance, **kwargs):
    """Validate the dataset file format and complete the description field if it is empty."""

    # 1. Nullify empty descriptions
    if instance.short_desc is not None and instance.short_desc.strip() == '':
        instance.short_desc = None
    if instance.description is not None and instance.description.strip() == '':
        instance.description = None

    # 2. Complete the category field if it is empty
    if instance.category is None or instance.category.strip() == '':
        instance.category = 'Non classé'
    instance.category = instance.category.strip()
# End def dataset_pre_save


# ======================================================================================================================
# MapLayer Model
# ======================================================================================================================


class MapLayerCustomProperty(models.Model):
    """A custom property for a map layer."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    map_layer = models.ForeignKey(
        'MapLayer',
        on_delete=models.CASCADE,
        help_text="Couche à laquelle la propriété est associée. Si la couche est supprimée, la propriété sera également supprimée."
    )

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        help_text="Nom de la propriété personnalisée."
    )

    value = models.CharField(
        verbose_name="Valeur",
        max_length=100,
        help_text="Valeur de la propriété."
        "Pour utiliser une propriété du jeu de données, utilisez la syntaxe suivante: ${nom_de_la_propriété}."
        "Exemple: \"${HECTARES} ha\" convertira la valeur de la propriété \"HECTARES\" en chaîne de caractères et ajoutera \" ha\" à la fin."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"\"{self.name}\": \"{self.value}\""

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Propriété personnalisée"
        verbose_name_plural = "Propriétés personnalisées"
        ordering = ['name']
    # End class Meta
# End class MapLayerCustomProperty

class MapLayer(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        unique=True,
        help_text="Nom de la couche"
    )

    short_desc = models.CharField(
        verbose_name="Description courte",
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Description courte de la couche. Optionnel. Utilisé pour générer l'aide contextuelle."
    )

    description = models.TextField(
        verbose_name="Description",
        blank=True,
        null=True,
        default=None,
        help_text="Description de la couche. Optionnel."
    )

    dataset = models.ForeignKey(
        'Dataset',
        verbose_name="Jeu de données",
        on_delete=models.CASCADE,
        help_text=
            "Jeu de données utilisé pour la couche. La couche sera générée à partir de ce jeu de données."
            "Si le jeu de données est supprimé, la couche sera également supprimée."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Shapefile specific fields
    # ------------------------------------------------------------------------------------------------------------------

    shapefile = models.CharField(
        verbose_name="Fichier shapefile",
        max_length=500,
        blank=True,
        null=True,
        default=None,
        help_text="Nom du fichier shapefile à utiliser."
    )

    encoding = models.CharField(
        verbose_name="Codage des caractères",
        max_length=50,
        choices=ENCODING_CHOICES,
        default=UTF8,
        help_text="Encodage du fichier shapefile."
    )

    max_polygons_points = models.IntegerField(
        verbose_name="Nombre maximum de points par polygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de points par polygone. Si un polygone contient plus de points, il sera ignoré."
        "Si la valeur est nulle, il n'y a pas de limite."
    )

    max_multipolygons_polygons = models.IntegerField(
        verbose_name="Nombre maximum de polygones par multipolygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de polygones par multipolygone.\n"
                  "Si un multipolygone contient plus de polygones, il sera ignoré.\n"
                  "Si la valeur est nulle, il n'y a pas de limite."
    )

    max_multiolygons_points = models.IntegerField(
        verbose_name="Nombre maximum de points par multipolygone",
        blank=True,
        null=True,
        default=None,
        validators=[MinValueValidator(0)],
        help_text="Nombre maximum de points par multipolygone.\n"
                  "Si un multipolygone contient plus de points, il sera ignoré.\n"
                  "Si la valeur est nulle, il n'y a pas de limite."
    )

    customize_properties = models.BooleanField(
        verbose_name="Personnaliser les propriétés",
        default=False,
        help_text="Personnalise les proppriétés de chaque feature du jeu de données selon les règles définies dans le champ 'Règles de conversion des propriétés'."
        "Les anciennes propriétés seront supprimées."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Shapes
    # ------------------------------------------------------------------------------------------------------------------

    status = models.CharField(
        verbose_name="Statut",
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        help_text="Statut de la couche."
    )

    shapes = GenericRelation('shapes.Shape')

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def get_config_dict(self):
        """Return a dictionary containing the map layer's data.
        Used when generating the geojson file of the map layers.
        """
        # Create the config dictionary
        config_dict = {
            'name': self.name,
            'dataset': self.dataset.name,
            'dataset_format': self.dataset.format
        }

        if self.dataset.format == SHAPEFILE:
            config_dict.extend({
                'shapefile': self.shapefile,
                'encoding': self.encoding,
                'max_polygons_points': self.max_polygons_points,
                'max_multipolygons_polygons': self.max_multipolygons_polygons,
                'max_multiolygons_points': self.max_multiolygons_points
            })

        config_dict['customize_properties'] = True
        if self.customize_properties is True:
            config_dict['custom_properties'] = {key: value for key, value in self.custom_properties.values_list('name', 'value')}

        return config_dict
    # End def get_config_dict

    def save(self, *args, **kwargs):
        """Save the map layer and generate its shapes if it is ready."""
        super().save(*args, **kwargs)

        if self.status == GenerationStatus.PENDING:
            transaction.on_commit(
                lambda: current_app.send_task('generate_map_layers_shapes', args=[self.id])
            )
    # End def save


    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Couche"
        verbose_name_plural = "Couches"
        ordering = ['name']
    # End class Meta
# End class MapLayer

# ======================================================================================================================
# City Model
# ======================================================================================================================


class CityDatasetKeyValue(models.Model):
    """A key/value pair for a city dataset."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    city = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        help_text="Ville à laquelle la clé/valeur est associée. Si la ville est supprimée, la clé/valeur sera également supprimée."
    )
    key = models.CharField(
        verbose_name="Clé",
        max_length=100,
        help_text="Clé du jeu de données."
    )

    value = models.CharField(
        verbose_name="Valeur",
        max_length=100,
        help_text="Valeur du jeu de données."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.city.name} - \"{self.key}\": \"{self.value}\""

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Clé/valeur du jeu de données"
        verbose_name_plural = "Clés/valeurs du jeu de données"
        ordering = ['key']
    # End class Meta


# End class CityDatasetKeyValue

class City(models.Model):
    """A city."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        unique=True,
        help_text="Nom de la ville"
    )

    generation_status = models.CharField(
        verbose_name="Statut de génération",
        max_length=20,
        choices=GenerationStatus.choices,
        default=GenerationStatus.PENDING,
        help_text="Statut de génération de la ville."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Shapes
    # ------------------------------------------------------------------------------------------------------------------

    limits_dataset = models.ForeignKey(
        'Dataset',
        verbose_name="Jeu de données des limites",
        on_delete=models.CASCADE,
        help_text=
            "Jeu de données utilisé pour les limites de la ville. Les limites de la ville seront générées à partir de ce jeu de données."
            "Si le jeu de données est supprimé, les limites de la ville seront également supprimées."
    )

    limits_shapefile = models.CharField(
        verbose_name="Fichier shapefile",
        max_length=500,
        blank=True,
        null=True,
        default=None,
        help_text="Nom du fichier shapefile à utiliser."
    )

    limits = GenericRelation('shapes.Shape')

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """Save the city and generate its shapes if it is ready."""
        super().save(*args, **kwargs)

        if self.generation_status == GenerationStatus.PENDING:
            transaction.on_commit(
                lambda: current_app.send_task('generate_city_shape', args=[self.id])
            )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Ville"
        verbose_name_plural = "Villes"
        ordering = ['name']
    # End class Meta
# End class City