"""
Tests for the OCR processor implementation.

This module contains tests for the PyTesseractProcessor class, covering text extraction, 
metadata extraction, feature extraction, and error handling.
"""

import os
import unittest
from unittest.mock import MagicMock, patch
import tempfile
from io import BytesIO

# Import the processor to test
from core.content_extractor.processors.by_ability.ocr_processor import PyTesseractProcessor, TESSERACT_AVAILABLE

# Create a sample image for testing
SAMPLE_IMAGE_DATA = None  # This will be populated in setUpModule

def setUpModule():
    """Set up the module level fixtures."""
    global SAMPLE_IMAGE_DATA
    
    # Skip creating test data if PIL is not available
    if not TESSERACT_AVAILABLE:
        return
    
    # Create a simple test image with text
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # Create a blank image with white background
        img = Image.new('RGB', (400, 200), color=(255, 255, 255))
        d = ImageDraw.Draw(img)
        
        # Try to load a font or use default
        try:
            font = ImageFont.truetype("arial.ttf", 24)
        except IOError:
            font = ImageFont.load_default()
        
        # Add some text to the image
        d.text((50, 50), "Hello, OCR Test!", fill=(0, 0, 0), font=font)
        d.text((50, 100), "This is a test image.", fill=(0, 0, 0), font=font)
        
        # Save the image to a buffer
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        
        # Get the image data
        SAMPLE_IMAGE_DATA = buffer.getvalue()
    
    except ImportError:
        # If PIL is not available, we can't create a test image
        SAMPLE_IMAGE_DATA = None


@unittest.skipIf(not TESSERACT_AVAILABLE, "Tesseract OCR not available")
class TestPyTesseractProcessor(unittest.TestCase):
    """Test the PyTesseractProcessor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.processor = PyTesseractProcessor()
        
        # Check if we have test data
        if SAMPLE_IMAGE_DATA is None:
            self.skipTest("Could not create test image data")
        
        # Create a temporary test file if needed for specific tests
        self.test_file = None
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove temporary file if it was created
        if self.test_file and os.path.exists(self.test_file):
            try:
                os.unlink(self.test_file)
            except:
                pass
    
    def test_initialization(self):
        """Test that the processor is initialized correctly."""
        self.assertIn("png", self.processor.supported_formats)
        self.assertIn("jpg", self.processor.supported_formats)
        self.assertIsInstance(self.processor, PyTesseractProcessor)
    
    def test_can_process(self):
        """Test the can_process method."""
        self.assertTrue(self.processor.can_process("png"))
        self.assertTrue(self.processor.can_process("JPG"))
        self.assertFalse(self.processor.can_process("pdf"))
        self.assertFalse(self.processor.can_process(""))
    
    def test_get_supported_formats(self):
        """Test the supported_formats method."""
        formats = self.processor.supported_formats
        self.assertIn("png", formats)
        self.assertIn("jpg", formats)
        self.assertIn("jpeg", formats)
    
    def test_get_processor_info(self):
        """Test the get_processor_info method."""
        info = self.processor.get_processor_info()
        self.assertEqual(info["name"], "PyTesseractProcessor")
        self.assertTrue(info["available"])
        self.assertIn("version", info)
        self.assertIn("png", info["supported_formats"])
    
    @patch('pytesseract.image_to_string')
    def test_extract_text(self, mock_image_to_string):
        """Test extracting text from an image."""
        # Mock the tesseract response
        mock_image_to_string.return_value = "Hello, OCR Test!\nThis is a test image."
        
        # Test with the sample image data
        text = self.processor.extract_text(SAMPLE_IMAGE_DATA, {})
        
        # Check that the text contains expected content
        self.assertIn("Hello", text)
        self.assertIn("OCR Test", text)
        self.assertIn("test image", text)
        
        # Check that pytesseract was called correctly
        mock_image_to_string.assert_called_once()
        
        # Test with different language
        self.processor.extract_text(SAMPLE_IMAGE_DATA, {"language": "deu"})
        mock_image_to_string.assert_called_with(unittest.mock.ANY, lang="deu", config="")
    
    def test_extract_metadata(self):
        """Test extracting metadata from an image."""
        # Test with the sample image data
        metadata = self.processor.extract_metadata(SAMPLE_IMAGE_DATA, {})
        
        # Check that the metadata contains expected fields
        self.assertIn("format", metadata)
        self.assertEqual(metadata["format"], "png")
        self.assertIn("width", metadata)
        self.assertEqual(metadata["width"], 400)
        self.assertIn("height", metadata)
        self.assertEqual(metadata["height"], 200)
        self.assertIn("mode", metadata)
        self.assertIn("size", metadata)
        self.assertIn("aspect_ratio", metadata)
        self.assertIn("extraction_time", metadata)
    
    @patch('pytesseract.image_to_data')
    def test_extract_features(self, mock_image_to_data):
        """Test extracting features from an image."""
        # Mock the tesseract response
        mock_image_to_data.return_value = {
            'text': ['Hello,', 'OCR', 'Test!', 'This', 'is', 'a', 'test', 'image.'],
            'conf': [90, 90, 90, 90, 90, 90, 90, 90],
            'left': [50, 100, 150, 50, 100, 120, 150, 180],
            'top': [50, 50, 50, 100, 100, 100, 100, 100],
            'width': [50, 30, 30, 30, 20, 10, 30, 40],
            'height': [20, 20, 20, 20, 20, 20, 20, 20]
        }
        
        # Test with the sample image data
        features = self.processor.extract_features(SAMPLE_IMAGE_DATA, {'include_boxes': True})
        
        # Check that we have feature entries
        self.assertGreater(len(features), 0)
        
        # Check that we have the expected feature types
        feature_types = [f["type"] for f in features]
        self.assertIn("dimensions", feature_types)
        
        # If include_boxes was processed, we should have text regions
        if mock_image_to_data.called:
            self.assertIn("text_regions", feature_types)
        
        # Check dimensions feature
        dimensions = next(f for f in features if f["type"] == "dimensions")
        self.assertEqual(dimensions["content"]["width"], 400)
        self.assertEqual(dimensions["content"]["height"], 200)
    
    @patch('pytesseract.image_to_string')
    def test_process_image(self, mock_image_to_string):
        """Test processing a complete image."""
        # Mock the tesseract response
        mock_image_to_string.return_value = "Hello, OCR Test!\nThis is a test image."
        
        # Test with the sample image data
        text, metadata, sections = self.processor.process_image(SAMPLE_IMAGE_DATA, {})
        
        # Check the results
        self.assertIsInstance(text, str)
        self.assertIsInstance(metadata, dict)
        self.assertIsInstance(sections, list)
        
        # Check that the text includes metadata and content
        self.assertIn("Image: 400x200", text)
        self.assertIn("PNG", text)
        self.assertIn("Extracted Text", text)
        self.assertIn("Hello", text)
        
        # Check that sections has both image info and OCR text
        section_types = [s.get("type") for s in sections]
        self.assertIn("image_info", section_types)
        self.assertIn("ocr_text", section_types)
        
        # Check OCR text section
        ocr_section = next(s for s in sections if s["type"] == "ocr_text")
        self.assertIn("Hello", ocr_section["content"])
    
    def test_invalid_image(self):
        """Test handling of invalid image data."""
        # Create some invalid image data
        invalid_data = b"This is not an image file"
        
        # Test all methods with invalid data and verify they raise ValueError
        with self.assertRaises(ValueError):
            self.processor.extract_text(invalid_data, {})
        
        with self.assertRaises(ValueError):
            self.processor.extract_metadata(invalid_data, {})
        
        with self.assertRaises(ValueError):
            self.processor.extract_features(invalid_data, {})
        
        with self.assertRaises(ValueError):
            self.processor.process_image(invalid_data, {})
    
    @patch('format_handlers.processors.ocr_processor.TESSERACT_AVAILABLE', False)
    def test_unavailable(self):
        """Test behavior when Tesseract is not available."""
        # Create a processor with TESSERACT_AVAILABLE patched to False
        processor = PyTesseractProcessor()
        
        # Check that it correctly reports no supported formats
        self.assertEqual(processor.supported_formats, [])
        self.assertFalse(processor.can_process("png"))
        
        # Check that all methods raise ValueError
        with self.assertRaises(ValueError):
            processor.extract_text(SAMPLE_IMAGE_DATA, {})
        
        with self.assertRaises(ValueError):
            processor.extract_metadata(SAMPLE_IMAGE_DATA, {})
        
        with self.assertRaises(ValueError):
            processor.extract_features(SAMPLE_IMAGE_DATA, {})
        
        with self.assertRaises(ValueError):
            processor.process_image(SAMPLE_IMAGE_DATA, {})


if __name__ == "__main__":
    unittest.main()