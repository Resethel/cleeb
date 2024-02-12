from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify

# ======================================================================================================================
# Person (Author, Contributor, etc.)
# ======================================================================================================================

class Person(models.Model):
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




# ======================================================================================================================
# Organizations
# ======================================================================================================================

class Organization(models.Model):

    id = models.AutoField(primary_key=True)

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    logo = models.ImageField(upload_to='images/orga/')
    contact = models.CharField(max_length=100)

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    slug = models.SlugField(
        max_length=100,
        unique=True,
        default=None,
        blank=True,
        null=True,
        help_text="Laissez vide pour générer automatiquement."
    )

    def __str__(self):
        return self.name
# End class Organization

@receiver(models.signals.pre_save, sender=Organization)
def auto_slugify(sender, instance, **kwargs):
    if not instance.slug or instance.slug is None or instance.slug == '':
        instance.slug = slugify(instance.name)