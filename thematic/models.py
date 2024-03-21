from django.db import models


class Theme(models.Model):

    # ------------------------------------------------------------------------------------------------------------------
    # Fields
    # ------------------------------------------------------------------------------------------------------------------

    id = models.AutoField(primary_key=True)

    name = models.CharField(
        verbose_name="Nom",
        max_length=100,
        unique=True,
        help_text="Nom de la thématique"
    )

    short_name = models.CharField(
        verbose_name="Nom court",
        max_length=20,
        unique=True,
        blank=True,
        null=True,
        help_text="Nom court de la thématique, utilisé dans les urls, tags, etc."
                  "Si laisser vide, le nom sera utilisé (tronqué à 20 caractères)."
    )

    short_desc = models.CharField(
        verbose_name="Description courte",
        max_length=200,
        blank=True,
        null=True,
        help_text="Description courte de la thématique, affichée dans la liste des thématiques."
    )

    long_desc = models.TextField(
        verbose_name="Description longue",
        blank=True,
        null=True,
        help_text="Description détaillée de la thématique, affichée sur la page de présentation de la thématique. "
                  "Si laissé vide, seul la description courte sera affichée."
    )

    splash_img = models.ImageField(
        verbose_name="Image de présentation",
        upload_to='images/thematic/splah',
        blank=True,
        null=True,
        help_text="Image de présentation de la thématique, affichée en haut de la page. "
                  "Si laissé vide, seul la couleur de fond sera affichée."
    )

    splash_color = models.CharField(
        verbose_name="Couleur de fond",
        max_length=7,
        default='#4BB166',
        blank=True,
        null=True,
        help_text="Couleur de fond de la page de présentation de la thématique, en format hexadécimal."
    )

    # ------------------------------------------------------------------------------------------------------------------
    # Meta
    # ------------------------------------------------------------------------------------------------------------------

    class Meta:
        verbose_name = "Thèmatique"
        verbose_name_plural = "Thèmatiques"

    # ------------------------------------------------------------------------------------------------------------------
    # Methods
    # ------------------------------------------------------------------------------------------------------------------

    def __str__(self):
        return self.name
