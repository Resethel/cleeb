# -*- coding: utf-8 -*-
"""
Utility module for file related operations.
"""
from io import IOBase
from pathlib import Path

import magic
from PIL import Image
from pypdf import PdfReader


# ======================================================================================================================
# PDF related functions
# ======================================================================================================================

def is_pdf(file: str | Path | IOBase) -> bool:
    try:
        type_ = __get_file_mime_type(file)
    except Exception:
        return False
    return True if type_.split('/')[1] == 'pdf' else False
# End def is_pdf

def is_valid_pdf(file):
    """Reads a file and returns True if its a valid PDF file."""
    try:
       PdfReader(file)
    except Exception as e:
        print(e)
        return False
    return True
# End def is_valid_pdf

# ======================================================================================================================
# Image related functions
# ======================================================================================================================

def is_image(file: str | Path | IOBase) -> bool:
    try:
        type_ = __get_file_mime_type(file)
    except Exception:
        return False
    return True if type_.split('/')[0] == 'image' else False
# End def is_image

def is_valid_image(file_path : str | Path | IOBase) -> bool:
    """Returns `True` if the file is a valid image, `False` otherwise."""
    try:
        with Image.open(file_path) as img:
            img.verify()
    except Exception:
        return False

    return True
# End def is_valid_image

# ======================================================================================================================
# Video related functions
# ======================================================================================================================

def is_video(file: str | Path | IOBase) -> bool:
    try:
        type_ = __get_file_mime_type(file)
    except Exception:
        return False
    return True if type_.split('/')[0] == 'video' else False
# End def is_video

# ======================================================================================================================
# Audio related functions
# ======================================================================================================================

def is_audio(file: str | Path | IOBase) -> bool:
    try:
        type_ = __get_file_mime_type(file)
    except Exception:
        return False
    return True if type_.split('/')[0] == 'audio' else False
# End def is_audio

# ======================================================================================================================
# Helper functions
# ======================================================================================================================

def __get_file_mime_type(file: str | Path | IOBase) -> str:
    if isinstance(file, str | Path):
        type_ = magic.from_file(file, mime=True)
    else:
        cursor_pos = file.tell()
        try:
            file.seek(0)
            type_ = magic.from_buffer(file.read(), mime=True)
        finally:
            file.seek(cursor_pos)
    return type_
# End def __get_file_mime_type
