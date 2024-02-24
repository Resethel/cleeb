# -*- coding: utf-8 -*-
"""
Validators for the `map_templates` application.
"""
from django.core.exceptions import ValidationError

def validate_dash_array(value):
    """
    Validator for the `dash_array` attribute of a `Style` object.
    """
    if value is not None and not isinstance(value, str):
        raise ValidationError(f"Expected 'dash_array' to be of type 'str', not '{type(value)}'")


    dashes = value.replace(",", " ").replace("%", "").split()
    for dash in dashes:
        try:
            float(dash)
        except ValueError:
            raise ValidationError(f"Expected 'dash_array' to be a list of comma and/or "
                                  f"white space separated <length>s and <percentage>s, not '{value}'") from None
# End def dash_array_validator