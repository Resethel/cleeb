from django.db import models

from core.models import Organization
from map_thematics.models import Thematic


class Author(models.Model):
    """Model that represents an author of a thematic map."""
    # ID of the author
    id = models.AutoField(primary_key=True)

    # Name of the author
    lastname = models.CharField(max_length=100)

    # First-name of the author
    firstname = models.CharField(max_length=100)

    # Biography of the author
    biography = models.TextField(
        blank=True
    )

    # Picture of the author
    picture = models.ImageField(
        upload_to='interactive_maps/authors/pictures',
        blank=True,
        null=True,
        default=None
    )

    # Organization of the author
    organization = models.ManyToManyField(
        'core.Organization',
        blank=True,
        default=None
    )

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
# End class Author


class Map(models.Model):

    # ID of the thematic map
    id = models.AutoField(primary_key=True)

    # Title of the thematic map
    title = models.CharField(max_length=100)

    # Author of the thematic map
    authors = models.ManyToManyField(
        'Author',
        blank=True,
    )

    # Themes of the thematic map
    thematics = models.ManyToManyField(
        'map_thematics.Thematic',
        blank=True,
    )

    map_render = models.ForeignKey(
        'map_data.MapRender',
        verbose_name="Rendu de carte",
        help_text="Le rendu de carte généré par le serveur.",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )

    text = models.TextField(
        blank=True,
        null=True,
        default=None,
        help_text="Le texte de la carte interactive. Formaté en HTML."
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['id',]  # Order Thematic maps by 'title' field
# End class Map
