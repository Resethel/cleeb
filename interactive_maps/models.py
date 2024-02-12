from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify

from core.models import Organization
from map_data.models import MapRender
from map_thematics.models import Thematic

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
        'core.Author',
        blank=True,
        help_text="Les auteurs de la carte interactive."
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
        'map_data.MapRender',
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
