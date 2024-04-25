# -*- coding: utf-8 -*-
"""
Models for the core application.
"""
from pathlib import Path
from uuid import uuid4

from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _


# ======================================================================================================================
# Person (Author, Contributor, etc.)
# ======================================================================================================================

def person_picture_path(instance, filename):
    extension = Path(filename).suffix
    if not extension:
        return str(Path('images/authors/pictures') / instance.slug / f"picture_{uuid4()}")
    else:
        return str(Path('images/authors/pictures') / instance.slug / f"picture_{uuid4()}.{extension}")
# End def person_picture_path

class Person(models.Model):
    """Model that represents an author of a thematic map."""

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----
    id = models.AutoField(primary_key=True)
    slug = models.SlugField(
        max_length=300,
        unique=True,
        default=None,
        blank=True,
        null=True,
    )

    # ----- Description -----

    # Name of the author
    lastname = models.CharField(
        max_length=100,
        verbose_name=_("Last name"),
        blank=True,
        null=True,
        default=None
    )

    # First-name of the author
    firstname = models.CharField(
        max_length=100,
        verbose_name=_("First name"),
        blank=True,
        null=True,
        default=None
    )

    pseudonym = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Pseudonym"),
        blank=True,
        null=True,
        default=None
    )

    # Biography of the author
    biography = models.TextField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Biography")
    )

    # ----- Social Media -----

    email = models.EmailField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Email")
    )
    facebook = models.URLField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Facebook")
    )
    instagram = models.URLField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Instagram")
    )
    twitter_x = models.URLField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Twitter/X")
    )
    website = models.URLField(
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Website")
    )

    # ----- Picture -----

    # Picture of the author
    picture = models.ImageField(
        upload_to=person_picture_path,
        blank=True,
        null=True,
        default=None,
        verbose_name=_("Picture")
    )

    # ---- Organizations ----

    # Organization of the author
    organizations = models.ManyToManyField(
        'core.Organization',
        blank=True,
        default=None
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Properties
    # ------------------------------------------------------------------------------------------------------------------

    @property
    def full_name(self):
        if self.pseudonym and not self.lastname and not self.firstname:
            return self.pseudonym
        if self.lastname and self.firstname and not self.pseudonym:
            return f"{self.lastname} {self.firstname}"

        return f"{self.lastname} {self.firstname} (alias {self.pseudonym})"
    # End def full_name

    @property
    def display_name(self):
        if self.pseudonym:
            return self.pseudonym
        return f"{self.firstname} {self.lastname}"
    # End def display_name

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return f"{self.firstname} {self.lastname}"
    # End def __str__

    def clean(self):
        # The person must have a name and/or a pseudonym
        if not self.lastname and not self.firstname and not self.pseudonym:
            raise ValidationError(_("The person must have a first name and/or a last name, and/or a pseudonym."))

        # If the author as a first name or a last name, they must have the other as well
        if self.lastname and not self.firstname:
            raise ValidationError({"firstname": _("If the last name is filled in, the first name must be as well.")})
        if self.firstname and not self.lastname:
            raise ValidationError({"lastname": _("If the first name is filled in, the last name must be as well.")})
    # End def clean

    def clean_fields(self, exclude=None):
        # Capitalize the first letter of the first name and last name
        if self.lastname:
            self.lastname = self.lastname.strip().lower().capitalize()
        if self.firstname:
            self.firstname = self.firstname.strip().lower().capitalize()
    # End def clean_fields
    def get_absolute_url(self):
        return f"/person/{self.slug}"
    # End def get_absolute_url

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        ordering = ['lastname', 'firstname']
    # End class Meta
# End class Person

@receiver(pre_save, sender=Person)
def generate_person_slug(sender, instance, **kwargs):
    if instance.pseudonym:
        instance.slug = slugify(instance.pseudonym)
    else:
        instance.slug = slugify(f"{instance.firstname} {instance.lastname} {instance.id}")
# End def generate_person_slug



# ======================================================================================================================
# Organizations
# ======================================================================================================================

def organization_logo_path(instance, filename):
    extension = Path(filename).suffix
    if not extension:
        return str(Path('images/organizations') / instance.slug / f"logo_{uuid4()}")
    else:
        return str(Path('images/organizations') / instance.slug / f"logo_{uuid4()}.{extension}")
# End def organization_logo_path

class Organization(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    # ----- Identification -----

    id = models.AutoField(primary_key=True)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        default=None,
        blank=True,
        null=True,
    )

    # ----- Description -----

    name = models.CharField(
        unique=True,
        max_length=100,
        verbose_name=_("Name of the organization")
    )
    type = models.CharField(
        max_length=100,
        verbose_name=_("Type of organization"),
        help_text=_("Type of organization (e.g. NGO, Company, Political Party, etc.)"),
    )
    description = models.TextField(
        blank=True,
        null=True
    )
    logo = models.ImageField(
        upload_to=organization_logo_path,
        blank=True,
        null=True,
    )

    # ----- Social Media -----

    email = models.EmailField(max_length=100, blank=True, null=True)
    facebook = models.URLField(blank=True, null=True)
    instagram = models.URLField(blank=True, null=True)
    twitter_x = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
    # End def __str__

    def get_absolute_url(self):
        return f"/organization/{self.slug}"
    # End def get_absolute_url
# End class Organization

@receiver(pre_save, sender=Organization)
def generate_organization_slug(sender, instance, **kwargs):
    instance.slug = slugify(instance.name)