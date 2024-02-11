# -*- coding: utf-8 -*-
"""
Utilities for the map_templates app
"""
from typing import Any


def camel_to_snake(text: str):
    """Convert a camel case string to snake case"""
    return text[0].lower() + ''.join(f'_{c.lower()}' if c.isupper() else c for c in text[1:])
# End def camel_to_snake

def snake_to_camel(text: str, capitalize_first: bool = True):
    """Convert a snake case string to camel case"""
    str_ = ''.join(c.capitalize() for c in text.split('_'))
    if not capitalize_first:
        str_ = str_[0].lower() + str_[1:]
    return str_
# End def snake_to_camel

def repr_str(obj : Any) -> str:
    """Return a string representation of an object"""
    return  "{class_}@{id:x}({attrs})".format(
            class_=obj.__class__.__name__,
            id=id(obj),
            attrs=", ".join("{}={!r}".format(k, v) for k, v in obj.__dict__.items()),
        )