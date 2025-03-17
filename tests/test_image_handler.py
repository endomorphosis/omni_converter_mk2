"""
Test the image format handler.

This module tests the image format handler functionality.
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
    """Test the image format handler."""
    
    def setUp(self):
        """Set up the test environment."""
        self.handler = ImageHandler()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """Clean up after the test."""
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def _create_test_files(self) -> Dict[str, str]:
        """
        Create test files for different image formats.
        
        Returns:
            A dictionary mapping format names to file paths.
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
        """Test that the handler supports the expected formats."""
        expected_formats = {"jpeg", "png", "gif", "webp", "svg"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """Test that the handler reports its capabilities correctly."""
        capabilities = self.handler.get_capabilities()
        self.assertEqual(capabilities["handler_name"], "ImageHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"jpeg", "png", "gif", "webp", "svg"})
        self.assertEqual(capabilities["category"], "image")
    
    def test_can_handle(self):
        """Test that the handler correctly identifies supported files."""
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                self.assertTrue(self.handler.can_handle(file_path))
                self.assertTrue(self.handler.can_handle(file_path, format_name))
    
    def test_extract_jpeg(self):
        """Test JPEG content extraction."""
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
        """Test PNG content extraction."""
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
        """Test GIF content extraction."""
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
        """Test WebP content extraction."""
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
        """Test SVG content extraction."""
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