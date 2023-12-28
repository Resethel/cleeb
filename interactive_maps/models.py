from django.db import models

from core.models import Organization, Theme


class Text(models.Model):
    """Model that represents a thematic map's text."""

    # ID of the text
    id = models.AutoField(primary_key=True)

    # Title of the text
    title = models.CharField(max_length=100)

    # Map of the text
    map = models.OneToOneField(
        'Map',
        on_delete=models.DO_NOTHING,
        null=True,
    )

    def __str__(self):
        return f"Text: {self.title} (id: {self.id:05d})"
# End class Text


class Section(models.Model):
    """Model that represents a section of a thematic map's text."""

    # ID of the section
    id = models.AutoField(primary_key=True)

    # Title of the section
    title = models.CharField(max_length=100, null=True, default=None)

    # Content of the section
    content = models.TextField()

    # Order number of the section
    order = models.IntegerField()

    # Parent text of the section
    text = models.ForeignKey(Text, on_delete=models.CASCADE, null=True, default=None)

    def __str__(self):
        return f"Section: {self.title} (id: {self.id:05d})"
# End class Section


class Author(models.Model):
    """Model that represents an author of a thematic map."""
    # ID of the author
    id = models.AutoField(primary_key=True)

    # Name of the author
    name = models.CharField(max_length=100)

    # First-name of the author
    first_name = models.CharField(max_length=100)

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
        return f"{self.first_name} {self.name}"
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
    themes = models.ManyToManyField(
        'core.Theme',
        blank=True,
    )

    # TODO: The 'map' filed choices will be populated dynamically from the map backend
    map_choices = [
        *((f'test_{i}', f'Map Test {i}') for i in range(1, 4))
    ]
    map = models.CharField(
        max_length=100,
        choices=map_choices,
        default='town_limits'
    )

    def __str__(self):
        return f"{self.title}"

    class Meta:
        ordering = ['id',]  # Order Thematic maps by 'title' field
# End class Map
