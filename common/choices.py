# -*- coding: utf-8 -*-
"""
Common choices for the models of the website.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _

# ======================================================================================================================
# Constants
# ======================================================================================================================

LICENSES_URLS = {
    "cc-by-4.0"           : "https://creativecommons.org/licenses/by/4.0/",
    "cc-by-3.0"           : "https://creativecommons.org/licenses/by/3.0/",
    "cc-by-2.5"           : "https://creativecommons.org/licenses/by/2.5/",
    "cc-by-2.0"           : "https://creativecommons.org/licenses/by/2.0/",
    "cc-by-1.0"           : "https://creativecommons.org/licenses/by/1.0/",
    "cc-by-sa-4.0"        : "https://creativecommons.org/licenses/by-sa/4.0/",
    "cc-by-sa-3.0"        : "https://creativecommons.org/licenses/by-sa/3.0/",
    "cc-by-sa-2.5"        : "https://creativecommons.org/licenses/by-sa/2.5/",
    "cc-by-sa-2.0"        : "https://creativecommons.org/licenses/by-sa/2.0/",
    "cc-by-sa-1.0"        : "https://creativecommons.org/licenses/by-sa/1.0/",
    "cc-by-nc-4.0"        : "https://creativecommons.org/licenses/by-nc/4.0/",
    "cc-by-nc-3.0"        : "https://creativecommons.org/licenses/by-nc/3.0/",
    "cc-by-nc-2.5"        : "https://creativecommons.org/licenses/by-nc/2.5/",
    "cc-by-nc-2.0"        : "https://creativecommons.org/licenses/by-nc/2.0/",
    "cc-by-nc-1.0"        : "https://creativecommons.org/licenses/by-nc/1.0/",
    "cc-by-nc-sa-4.0"     : "https://creativecommons.org/licenses/by-nc-sa/4.0/",
    "cc-by-nc-sa-3.0"     : "https://creativecommons.org/licenses/by-nc-sa/3.0/",
    "cc-by-nc-sa-2.5"     : "https://creativecommons.org/licenses/by-nc-sa/2.5/",
    "cc-by-nc-sa-2.0"     : "https://creativecommons.org/licenses/by-nc-sa/2.0/",
    "cc-by-nc-sa-1.0"     : "https://creativecommons.org/licenses/by-nc-sa/1.0/",
    "cc-by-nd-4.0"        : "https://creativecommons.org/licenses/by-nd/4.0/",
    "cc-by-nd-3.0"        : "https://creativecommons.org/licenses/by-nd/3.0/",
    "cc-by-nd-2.5"        : "https://creativecommons.org/licenses/by-nd/2.5/",
    "cc-by-nd-2.0"        : "https://creativecommons.org/licenses/by-nd/2.0/",
    "cc-by-nd-1.0"        : "https://creativecommons.org/licenses/by-nd/1.0/",
    "cc-by-nc-nd-4.0"     : "https://creativecommons.org/licenses/by-nc-nd/4.0/",
    "cc-by-nc-nd-3.0"     : "https://creativecommons.org/licenses/by-nc-nd/3.0/",
    "cc-by-nc-nd-2.5"     : "https://creativecommons.org/licenses/by-nc-nd/2.5/",
    "cc-by-nc-nd-2.0"     : "https://creativecommons.org/licenses/by-nc-nd/2.0/",
    "cc-by-nc-nd-1.0"     : "https://creativecommons.org/licenses/by-nc-nd/1.0/",
}

# ======================================================================================================================
# Choices
# ======================================================================================================================

class PublicationStatus(models.TextChoices):
    """Choices for the `Article` model."""
    DRAFT = "draft", _("Draft")
    PUBLISHED = "published", _("Published")
# End class PublicationStatus

class License(models.TextChoices):
    """Choices for the `File` model."""
    CC_BY_40            = "cc-by-4.0"           , "CC BY 4.0"
    CC_BY_30            = "cc-by-3.0"           , "CC BY 3.0"
    CC_BY_25            = "cc-by-2.5"           , "CC BY 2.5"
    CC_BY_20            = "cc-by-2.0"           , "CC BY 2.0"
    CC_BY_10            = "cc-by-1.0"           , "CC BY 1.0"
    CC_BY_SA_40         = "cc-by-sa-4.0"        , "CC BY-SA 4.0"
    CC_BY_SA_30         = "cc-by-sa-3.0"        , "CC BY-SA 3.0"
    CC_BY_SA_25         = "cc-by-sa-2.5"        , "CC BY-SA 2.5"
    CC_BY_SA_20         = "cc-by-sa-2.0"        , "CC BY-SA 2.0"
    CC_BY_SA_10         = "cc-by-sa-1.0"        , "CC BY-SA 1.0"
    CC_BY_NC_40         = "cc-by-nc-4.0"        , "CC BY-NC 4.0"
    CC_BY_NC_30         = "cc-by-nc-3.0"        , "CC BY-NC 3.0"
    CC_BY_NC_25         = "cc-by-nc-2.5"        , "CC BY-NC 2.5"
    CC_BY_NC_20         = "cc-by-nc-2.0"        , "CC BY-NC 2.0"
    CC_BY_NC_10         = "cc-by-nc-1.0"        , "CC BY-NC 1.0"
    CC_BY_NC_SA_40      = "cc-by-nc-sa-4.0"     , "CC BY-NC-SA 4.0"
    CC_BY_NC_SA_30      = "cc-by-nc-sa-3.0"     , "CC BY-NC-SA 3.0"
    CC_BY_NC_SA_25      = "cc-by-nc-sa-2.5"     , "CC BY-NC-SA 2.5"
    CC_BY_NC_SA_20      = "cc-by-nc-sa-2.0"     , "CC BY-NC-SA 2.0"
    CC_BY_NC_SA_10      = "cc-by-nc-sa-1.0"     , "CC BY-NC-SA 1.0"
    CC_BY_ND_40         = "cc-by-nd-4.0"        , "CC BY-ND 4.0"
    CC_BY_ND_30         = "cc-by-nd-3.0"        , "CC BY-ND 3.0"
    CC_BY_ND_25         = "cc-by-nd-2.5"        , "CC BY-ND 2.5"
    CC_BY_ND_20         = "cc-by-nd-2.0"        , "CC BY-ND 2.0"
    CC_BY_ND_10         = "cc-by-nd-1.0"        , "CC BY-ND 1.0"
    CC_BY_NC_ND_40      = "cc-by-nc-nd-4.0"     , "CC BY-NC-ND 4.0"
    CC_BY_NC_ND_30      = "cc-by-nc-nd-3.0"     , "CC BY-NC-ND 3.0"
    CC_BY_NC_ND_25      = "cc-by-nc-nd-2.5"     , "CC BY-NC-ND 2.5"
    CC_BY_NC_ND_20      = "cc-by-nc-nd-2.0"     , "CC BY-NC-ND 2.0"
    CC_BY_NC_ND_10      = "cc-by-nc-nd-1.0"     , "CC BY-NC-ND 1.0"
    ALL_RIGHTS_RESERVED = "all-rights-reserved" , _("All rights reserved")
    PUBLIC_DOMAIN       = "public-domain"       , _("Public domain")
    UNKNOWN             = "unknown"             , _("Unknown")
    NO_COPYRIGHT        = "no-copyright"        , _("No copyright")
# End class License

def get_license_url(license_: str) -> str | None:
    """Return the URL of the license.

    Returns:
        str | None: The URL of the license if it exists, None otherwise.
    """
    return LICENSES_URLS.get(license_, None)
