"""
Test the format registry.

This module tests the format registry functionality.
"""

import os
import unittest
from unittest.mock import patch, MagicMock

from format_registery.format_registry import FormatRegistry, format_registry
from core.content_extractor.base_handler import FormatHandler, Content
from file_format_detector.file_format_detector import file_format_detector


class MockHandler(FormatHandler):
    """Mock format handler for testing."""
    
    def __init__(self, name, formats, category):
        self.name = name
        self.formats = formats
        self.category = category
    
    def can_handle(self, file_path, format_name=None):
        """Check if this handler can process the given file."""
        if format_name:
            return format_name in self.formats
        return any(f in file_path for f in self.formats)

    def extract_content(self, file_path, options=None):
        """Extract content from a file."""
        return Content(
            text=f"Mock content from {file_path}", 
            metadata={"format": file_path.split(".")[-1]},
            sections=[],
            source_format=file_path.split(".")[-1],
            source_path=file_path
        )

    @property
    def capabilities(self):
        """Get the capabilities of this handler."""
        return {
            "handler_name": self.name,
            "supported_formats": self.formats,
            "category": self.category
        }


class TestRegistry(FormatRegistry):
    """Subclass for testing that doesn't register default handlers."""
    
    def __init__(self):
        """Initialize without registering default handlers."""
        self.handlers = {}
        self.format_to_handler_map = {}
        # Skip registering default handlers


class TestFormatRegistry(unittest.TestCase):
    """Test the format registry."""
    
    def setUp(self):
        """Set up the test environment."""
        # Create a test registry without default handlers
        self.registry = TestRegistry()
        
        # Create mock handlers
        self.text_handler = MockHandler("TextHandler", ["txt", "md", "rst"], "text")
        self.image_handler = MockHandler("ImageHandler", ["jpg", "png", "gif"], "image")
        self.app_handler = MockHandler("AppHandler", ["pdf", "docx"], "application")
    
    def test_register_handler(self):
        """Test registering a handler."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        
        # Check that handlers were registered
        self.assertEqual(len(self.registry.handlers), 2)
        self.assertIn("TextHandler", self.registry.handlers)
        self.assertIn("ImageHandler", self.registry.handlers)
        
        # Check that formats were registered
        for fmt in ["txt", "md", "rst"]:
            self.assertEqual(self.registry.format_to_handler_map.get(fmt), "TextHandler")
        
        for fmt in ["jpg", "png", "gif"]:
            self.assertEqual(self.registry.format_to_handler_map.get(fmt), "ImageHandler")
    
    def test_get_handler(self):
        """Test getting a handler for a format."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        
        # Check that we can get handlers by format
        self.assertEqual(self.registry.get_handler("txt"), self.text_handler)
        self.assertEqual(self.registry.get_handler("png"), self.image_handler)
        
        # Check that unknown formats return None
        self.assertIsNone(self.registry.get_handler("unknown"))
    
    @patch('format_handlers.format_registry.file_format_detector')
    def test_get_handler_for_file(self, mock_detector):
        """Test getting a handler for a file."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        
        # Mock format detector to return 'txt' for text files
        mock_detector.detect_format.return_value = ('txt', 'text')
        
        # Check that we can get handlers by file path
        self.assertEqual(self.registry.get_handler_for_file("document.txt"), self.text_handler)
        
        # Test fallback to extension when detector returns None
        mock_detector.detect_format.return_value = (None, None)
        self.assertEqual(self.registry.get_handler_for_file("image.png"), self.image_handler)
        
        # Test fallback to can_handle when extension is not in the map
        self.assertIsNone(self.registry.get_handler_for_file("unknown.xyz"))
    
    def test_extract_content(self):
        """Test extracting content using the registry."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        
        # Mock format detector to return 'txt' for text files
        with patch('format_handlers.format_registry.file_format_detector') as mock_detector:
            mock_detector.detect_format.return_value = ('txt', 'text')
            
            # Check that we can extract content
            content = self.registry.extract_content("document.txt")
            self.assertIsInstance(content, Content)
            self.assertEqual(content.source_format, "txt")
            
            # Test that an exception is raised for unknown formats
            mock_detector.detect_format.return_value = (None, None)
            with self.assertRaises(ValueError):
                self.registry.extract_content("unknown.xyz")
    
    def test_get_supported_formats(self):
        """Test getting supported formats."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        self.registry.register_handler(self.app_handler)
        
        # Check that we get all formats
        formats = self.registry.supported_formats
        self.assertEqual(len(formats), 8)  # 3 text + 3 image + 2 app
        
        for fmt in ["txt", "md", "rst", "jpg", "png", "gif", "pdf", "docx"]:
            self.assertIn(fmt, formats)
    
    def test_get_formats_by_category(self):
        """Test getting formats grouped by category."""
        # Register handlers
        self.registry.register_handler(self.text_handler)
        self.registry.register_handler(self.image_handler)
        self.registry.register_handler(self.app_handler)
        
        # Check that formats are grouped by category
        categories = self.registry.get_formats_by_category()
        self.assertEqual(len(categories), 3)
        
        self.assertIn("text", categories)
        self.assertEqual(set(categories["text"]), set(["txt", "md", "rst"]))
        
        self.assertIn("image", categories)
        self.assertEqual(set(categories["image"]), set(["jpg", "png", "gif"]))
        
        self.assertIn("application", categories)
        self.assertEqual(set(categories["application"]), set(["pdf", "docx"]))


class TestGlobalFormatRegistry(unittest.TestCase):
    """Test the global format registry instance."""
    
    def test_global_registry(self):
        """Test that the global registry works correctly."""
        # Check that the global registry has handlers registered
        self.assertGreater(len(format_registry.handlers), 0)
        self.assertGreater(len(format_registry.format_to_handler_map), 0)
        
        # Check that we can get formats by category
        categories = format_registry.get_formats_by_category()
        self.assertIn("text", categories)
        self.assertIn("image", categories)
        self.assertIn("application", categories)


if __name__ == '__main__':
    unittest.main()