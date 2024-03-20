# -*- coding: utf-8 -*-
"""
Tests for the `common/utils/files.py` file.
"""
import pypdf
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest import TestCase

import requests
from PIL import Image

from common.utils import files

# ======================================================================================================================
# Module Setup and TearDown
# ======================================================================================================================

test_dir : TemporaryDirectory | None = None

# ======================================================================================================================
# Module Setup and TearDown
# ======================================================================================================================

def setUpModule():
    global test_dir
    test_dir = TemporaryDirectory()
# End def setUpModule

def tearDownModule():
    global test_dir
    if test_dir is not None:
        test_dir.cleanup()
# End def tearDownModule

# ======================================================================================================================
# Tests
# ======================================================================================================================
class TestIsPdf(TestCase):

    def test_shouldReturnTrue_ifFileIsAPdfFile(self):
        file_path = Path(test_dir.name) / 'valid_pdf.pdf'
        with pypdf.PdfWriter() as pdf_writer:
            pdf_writer.add_blank_page(width=8.27 * 72, height=11.7 * 72)
            pdf_writer.write(file_path)
        self.assertTrue(files.is_pdf(file_path))
    # End def test_shouldReturnTrue_ifFileIsAPdfFile

    def test_shouldReturnFalse_ifFileIsNotAPdfFile(self):
        file_path = Path(test_dir.name) / 'invalid_pdf.pdf'
        with file_path.open('wb') as f:
            f.write(b'fake data')
        self.assertFalse(files.is_pdf(file_path))
    # End def test_shouldReturnFalse_ifFileIsNotAPdfFile
# End class TestIsPdf

class TestIsValidPdf(TestCase):

    def test_shouldReturnTrue_ifFileIsAValidPdfFile(self):
        file_path = Path(test_dir.name) / 'valid_pdf.pdf'
        with pypdf.PdfWriter() as pdf_writer:
            pdf_writer.add_blank_page(width=8.27 * 72, height=11.7 * 72)
            pdf_writer.write(file_path)
        self.assertTrue(files.is_valid_pdf(file_path))
    # End def test_shouldReturnTrue_ifFileIsAPdfFile

    def test_shouldReturnFalse_ifFileIsNotAPdfFile(self):
        file_path = Path(test_dir.name) / 'invalid_pdf.pdf'
        with pypdf.PdfWriter() as pdf_writer:
            pdf_writer.add_blank_page(width=8.27 * 72, height=11.7 * 72)
            pdf_writer.write(file_path)
        # Re-write the file to make it invalid
        with file_path.open('wb') as f:
            f.write(b'fake data')
        self.assertFalse(files.is_valid_pdf(file_path))
    # End def test_shouldReturnFalse_ifFileIsNotAPdfFile
# End class TestIsValidPdf

class TestIsImage(TestCase):

    def test_shouldReturnTrue_ifFileIsAnImage(self):
        paths = {
            "png"  : Path(test_dir.name) / 'image.png',
            "jpeg" : Path(test_dir.name) / 'image.jpg',
            "webp" : Path(test_dir.name) / 'image.webp',
            "tiff" : Path(test_dir.name) / 'image.tiff',
         }
        img = Image.new(mode="RGB", size=(200, 200))
        for path in paths.values():
            img.save(path)
            self.assertTrue(files.is_image(path))
    # End def test_shouldReturnTrue_ifFileIsAnImage

    def test_shouldReturnFalse_ifFileIsNotAnImage(self):
        file_path = Path(test_dir.name) / 'invalid_image.png'
        with file_path.open('wb') as f:
            f.write(b'fake data')
        self.assertFalse(files.is_image(file_path))
    # End def test_shouldReturnFalse_ifFileIsNotAnImage
# End class TestIsImage

class TestIsVideo(TestCase):

    valid_video_path = None

    # ------------------------------------------------------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------------------------------------------------------

    @classmethod
    def setUpClass(cls):
        # Download a test video
        cls.valid_video_path = Path(test_dir.name) / "valid_video.mp4"
        cls.valid_video_path.parent.mkdir(parents=True, exist_ok=True)
        try:
            response = requests.get("https://storage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4")
            response.raise_for_status()
            with cls.valid_video_path.open("wb") as f:
                f.write(response.content)
        except Exception as e:
            cls.skipTest(cls, reason=f"Could not download the test video: {e}")
    # End def setUpClass


    # ------------------------------------------------------------------------------------------------------------------
    # Tests
    # ------------------------------------------------------------------------------------------------------------------

    def test_shouldReturnTrue_ifFileIsAVideo(self):
        # Download a test video
        self.assertTrue(files.is_video(self.valid_video_path))
    # End def test_shouldReturnTrue_ifFileIsAVideo

    def test_shouldReturnFalse_ifFileIsNotAVideo(self):
        file_path = Path(test_dir.name) / 'invalid_video.mp4'
        with file_path.open('wb') as f:
            f.write(b'fake data')
        self.assertFalse(files.is_video(file_path))
    # End def test_shouldReturnTrue_ifFileIsNotAVideo
# End class TestIsVideo

class TestIsAudio(TestCase):

    bytes_ = (b"RIFF$\x00\x00\x00WAVE"
              b"fmt \x10\x00\x00\x00\x01\x00\x01\x00\x00\x04\x00\x00\x00\x04\x00\x00\x01\x00\x08\x00"
              b"data\x00\x00\x00\x00")

    def test_shouldReturnTrue_ifFileIsAnAudio(self):
        file_path = Path(test_dir.name) / 'valid_audio.wav'
        with file_path.open('wb') as f:
            f.write(self.bytes_)
        self.assertTrue(files.is_audio(file_path))
    # End def test_shouldReturnTrue_ifFileIsAnAudio

    def test_shouldReturnFalse_ifFileIsNotAnAudio(self):
        file_path = Path(test_dir.name) / 'invalid_audio.mp3'
        with file_path.open('wb') as f:
            f.write(b'fake data')
        self.assertFalse(files.is_audio(file_path))
    # End def test_shouldReturnFalse_ifFileIsNotAnAudio
# End class TestIsAudio
