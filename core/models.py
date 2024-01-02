from django.db import models

# ======================================================================================================================
# Modèle pour les Acteurs de la cartographie
# ======================================================================================================================

class Organization(models.Model):

    name = models.CharField(max_length=100)
    type = models.CharField(max_length=100)
    description = models.TextField()
    logo = models.ImageField(upload_to='images/orga/')
    contact = models.CharField(max_length=100)

    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.name
