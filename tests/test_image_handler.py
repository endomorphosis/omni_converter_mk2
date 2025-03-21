"""
Test the image format handler.

This module provides comprehensive tests for the ImageHandler class, which is responsible
for processing various image file formats (JPEG, PNG, GIF, WebP, SVG). The tests verify 
that the handler can correctly identify supported formats, extract image properties, 
parse metadata, and extract text content from vector formats like SVG.
"""

import os
import io
import unittest
import tempfile
from typing import Dict, Any
from PIL import Image

from utils.filesystem import FileSystem
from format_handlers.image_handler import ImageHandler


class TestImageHandler(unittest.TestCase):
    """
    Test suite for the ImageHandler class.
    
    This test class verifies that the ImageHandler correctly processes and extracts
    content from different image file formats, including JPEG, PNG, GIF, WebP, and SVG.
    Tests cover format detection, image property extraction, metadata parsing, and
    text content extraction capabilities for formats that support embedded text.
    """
    
    def setUp(self):
        """
        Set up the test environment before each test.
        
        Creates an ImageHandler instance and a temporary directory to store test files.
        The test files are generated with known properties for predictable test results.
        Different image formats (JPEG, PNG, GIF, WebP, SVG) are created with controlled
        dimensions and content.
        """
        self.handler = ImageHandler()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """
        Clean up after each test.
        
        Removes all test image files created during setup and the temporary directory
        to ensure a clean state for subsequent tests.
        """
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def _create_test_files(self) -> Dict[str, str]:
        """
        Create test files for different image formats with predetermined properties.
        
        Creates five different image files (JPEG, PNG, GIF, WebP, SVG) with known
        dimensions, color properties, and content to ensure consistent and predictable
        test results. Each file is created in the temporary test directory.
        
        Returns:
            Dict[str, str]: A dictionary mapping format names to absolute file paths.
        """
        files = {}
        
        # JPEG test file
        jpeg_path = os.path.join(self.test_dir, "test.jpg")
        img = Image.new('RGB', (100, 100), color='red')
        img.save(jpeg_path)
        files["jpeg"] = jpeg_path
        
        # PNG test file
        png_path = os.path.join(self.test_dir, "test.png")
        img = Image.new('RGBA', (100, 100), color=(0, 0, 255, 128))
        img.save(png_path)
        files["png"] = png_path
        
        # GIF test file
        gif_path = os.path.join(self.test_dir, "test.gif")
        img = Image.new('RGB', (100, 100), color='green')
        img.save(gif_path)
        files["gif"] = gif_path
        
        # WebP test file
        webp_path = os.path.join(self.test_dir, "test.webp")
        img = Image.new('RGB', (100, 100), color='blue')
        img.save(webp_path)
        files["webp"] = webp_path
        
        # SVG test file
        svg_content = """<?xml version="1.0" encoding="UTF-8"?>
<svg width="100px" height="100px" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
    <title>Test SVG Image</title>
    <desc>A test SVG image for the image handler</desc>
    <rect x="10" y="10" width="80" height="80" fill="yellow" />
    <text x="20" y="50">Hello SVG</text>
    <text x="20" y="70">This is text in SVG</text>
</svg>"""
        svg_path = os.path.join(self.test_dir, "test.svg")
        with open(svg_path, "w") as f:
            f.write(svg_content)
        files["svg"] = svg_path
        
        return files
    
    def test_supported_formats(self):
        """
        Test that the ImageHandler supports the expected image formats.
        
        Verifies that the ImageHandler correctly reports its supported formats,
        which should include JPEG, PNG, GIF, WebP, and SVG formats. This ensures
        the handler's format detection capabilities function properly.
        """
        expected_formats = {"jpeg", "png", "gif", "webp", "svg"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """
        Test that the ImageHandler reports its capabilities correctly.
        
        Verifies that the handler provides accurate information about its name,
        supported formats, and category through the get_capabilities() method.
        This ensures the handler properly identifies itself within the format registry system.
        """
        capabilities = self.handler.get_capabilities()
        self.assertEqual(capabilities["handler_name"], "ImageHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"jpeg", "png", "gif", "webp", "svg"})
        self.assertEqual(capabilities["category"], "image")
    
    def test_can_handle(self):
        """
        Test that the ImageHandler correctly identifies supported files.
        
        Verifies that the can_handle() method correctly identifies files of supported formats
        (JPEG, PNG, GIF, WebP, SVG) both with and without explicitly specifying the format.
        This ensures proper file format detection functionality.
        """
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                self.assertTrue(self.handler.can_handle(file_path))
                self.assertTrue(self.handler.can_handle(file_path, format_name))
    
    def test_extract_jpeg(self):
        """
        Test JPEG image content extraction functionality.
        
        Verifies that the ImageHandler can correctly extract content from a JPEG image file,
        including image dimensions, color mode, and other relevant properties. The test checks
        that the handler generates appropriate textual representation of the image and
        extracts accurate metadata about the image dimensions and format.
        """
        content = self.handler.extract_content(self.test_files["jpeg"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "jpeg")
        
        # Check that image info was extracted correctly
        self.assertIn("Dimensions: 100x100", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "jpeg")
        self.assertEqual(content.metadata.get("width"), 100)
        self.assertEqual(content.metadata.get("height"), 100)
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "image_info")
    
    def test_extract_png(self):
        """
        Test PNG image content extraction functionality.
        
        Verifies that the ImageHandler can correctly extract content from a PNG image file,
        including image dimensions, color mode (RGBA), transparency information, and other
        relevant properties. The test ensures that PNG-specific features like alpha channel
        transparency are correctly identified and included in the metadata.
        """
        content = self.handler.extract_content(self.test_files["png"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "png")
        
        # Check that image info was extracted correctly
        self.assertIn("Dimensions: 100x100", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "png")
        self.assertEqual(content.metadata.get("width"), 100)
        self.assertEqual(content.metadata.get("height"), 100)
        self.assertEqual(content.metadata.get("color_mode"), "RGBA")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "image_info")
    
    def test_extract_gif(self):
        """
        Test GIF image content extraction functionality.
        
        Verifies that the ImageHandler can correctly extract content from a GIF image file,
        including image dimensions, color information, and other relevant properties.
        The test ensures that the handler generates an appropriate textual representation
        of the GIF image and extracts accurate metadata about its features.
        """
        content = self.handler.extract_content(self.test_files["gif"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "gif")
        
        # Check that image info was extracted correctly
        self.assertIn("Dimensions: 100x100", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "gif")
        self.assertEqual(content.metadata.get("width"), 100)
        self.assertEqual(content.metadata.get("height"), 100)
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "image_info")
    
    def test_extract_webp(self):
        """
        Test WebP image content extraction functionality.
        
        Verifies that the ImageHandler can correctly extract content from a WebP image file,
        including image dimensions, color information, and other relevant properties.
        The test ensures that WebP-specific features are correctly identified and included
        in the metadata, and that the handler generates an appropriate textual
        representation of the image.
        """
        content = self.handler.extract_content(self.test_files["webp"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "webp")
        
        # Check that image info was extracted correctly
        self.assertIn("Dimensions: 100x100", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "webp")
        self.assertEqual(content.metadata.get("width"), 100)
        self.assertEqual(content.metadata.get("height"), 100)
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "image_info")
    
    def test_extract_svg(self):
        """
        Test SVG image content extraction functionality.
        
        Verifies that the ImageHandler can correctly extract content from an SVG vector image file,
        including image dimensions, embedded text content, and metadata like title and description.
        This test is particularly important as SVG is different from other image formats by
        containing parseable text content and XML-based structure. The test ensures that both
        the image information and the text content are properly extracted.
        """
        content = self.handler.extract_content(self.test_files["svg"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "svg")
        
        # Check that SVG was parsed correctly
        self.assertIn("Title: Test SVG Image", content.text)
        self.assertIn("Description: A test SVG image for the image handler", content.text)
        self.assertIn("Hello SVG", content.text)
        self.assertIn("This is text in SVG", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "svg")
        self.assertEqual(content.metadata.get("width"), "100px")
        self.assertEqual(content.metadata.get("height"), "100px")
        self.assertEqual(content.metadata.get("title"), "Test SVG Image")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 2)  # At least image_info and text_content
        self.assertEqual(content.sections[0]["type"], "image_info")
        
        # Find the text_content section
        text_sections = [s for s in content.sections if s["type"] == "text_content"]
        self.assertEqual(len(text_sections), 1)
        self.assertIn("Hello SVG", text_sections[0]["content"][0])


if __name__ == "__main__":
    unittest.main()