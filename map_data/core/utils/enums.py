# -*- coding: utf-8 -*-
"""
Enumerations
"""
from enum import Enum


class EPSGProjection(Enum):
    """Enumeration of the different EPSG projections."""
    EPSG_2154 = 2154 # Lambert 93
    EPSG_4326 = 4326 # WGS 84


class Encoding(Enum):
    """Enumeration of the different encoding types."""
    UTF_8 = 'utf-8'
    ISO_8859_1 = 'iso-8859-1'
    LATIN_1 = 'latin-1'
    UTF_16 = 'utf-16'
    ASCII = 'ascii'