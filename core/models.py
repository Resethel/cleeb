from django.db import models
from django.dispatch import receiver
from django.template.defaultfilters import slugify


# ======================================================================================================================
# Modèle pour les Acteurs de la cartographie
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