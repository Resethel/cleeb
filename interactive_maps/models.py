from uuid import uuid4

from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from core.models import Organization
from map_thematics.models import Thematic

# ======================================================================================================================
# Rendered Map
# ======================================================================================================================

def map_render_embed_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"maps/{instance.slug}/embed.{extension}"
# End def map_render_embed_path

def map_render_full_path(instance, filename):
    # Get the extension of the file
    extension = filename.split('.')[-1]
    # Return the path
    return f"maps/{instance.slug}/full.{extension}"
# End def map_render_full_path

class MapRender(models.Model):
    """This class represents a map render."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----

    id = models.AutoField(
        primary_key=True,
        verbose_name="ID",
        help_text="L'ID de la carte.",
    )

    slug = models.SlugField(
        max_length=512,
        blank=True,
        null=True,
        default=None,
    )

    # ------ Description ------

    name = models.CharField(
        unique=True,
        max_length=255,
        verbose_name="Nom",
        help_text="Le nom du rendu."
    )

    # ----- Maps Render -----

    embed_html = models.FileField(
        name="embed_html",
        verbose_name="HTML intégrable",
        upload_to=map_render_embed_path,
        help_text="Le code HTML de la carte pouvant être intégré dans une page web.",
        null=True,
        default=None,
    )

    full_html = models.FileField(
        name="full_html",
        verbose_name="HTML complet",
        upload_to=map_render_full_path,
        help_text="Le code HTML d'une page web contenant la carte.",
        null=True,
        default=None,
    )

    # ----- Reference to MapTemplate (Optional) -----

    template = models.OneToOneField(
        to='map_templates.MapTemplate',
        related_name='render',
        on_delete=models.CASCADE,
        null=True,
        default=None,
        verbose_name='Modèle',
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Rendu de carte"
        verbose_name_plural = "Rendus de carte"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def clean(self, exclude=None):
        super().clean()
        self.slug = slugify(self.name)
    # End def clean_fields
# End class MapRender

# ======================================================================================================================
# Interactive Map
# ======================================================================================================================

class Map(models.Model):

    # ID of the thematic map
    id = models.AutoField(primary_key=True)

    # Title of the thematic map
    title = models.CharField(max_length=100)

    # Author of the thematic map
    authors = models.ManyToManyField(
        'core.Person',
        blank=True,
        help_text="Les auteur.ice.s de la carte interactive."
    )

    created_at = models.DateField(
        auto_now_add=True,
        help_text="La date de création de la carte interactive.",
        editable=False
    )

    last_modified = models.DateField(
        auto_now=True,
        help_text="La date de dernière modification de la carte interactive.",
        editable=False
    )

    # Themes of the thematic map
    thematics = models.ManyToManyField(
        'map_thematics.Thematic',
        blank=True,
        help_text="Les thématiques de la carte interactive."
    )

    map_render = models.ForeignKey(
        MapRender,
        verbose_name="Rendu de carte",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        help_text="Le rendu de carte généré par le serveur."
    )

    introduction = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="L'introduction de la carte interactive. Formaté en HTML."
                  "Seuls les balises de style (strong, em, etc.) seront conservées."
                  "Toutes balises de structure (section, article, h1, p, etc.) seront supprimées."
    )

    text = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Le texte de la carte interactive. Formaté en HTML."
    )

    slug = models.SlugField(
        max_length=100,
        blank=True,
        null=True,
        default=None,
        help_text="Le slug de la carte interactive. S'il n'est pas renseigné, il sera généré automatiquement."
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['id',]  # Order Thematic maps by 'title' field
# End class Map

@receiver(pre_save, sender=Map)
def generate_slug(sender, instance, **kwargs):
    if not instance.slug is None or instance.slug is None or instance.slug == "":
        instance.slug = slugify(instance.title)
