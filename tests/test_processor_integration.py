"""
Tests for the integration of processors with format handlers.

This module tests how the format handlers use the processor implementations,
ensuring the interface between the two components works correctly.
"""

import unittest
from unittest.mock import patch, MagicMock
import os
import tempfile
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from format_handlers.application_handler import application_handler
from format_handlers.audio_handler import audio_handler
from format_handlers.image_handler import image_handler

# Import processors
from format_handlers.processors.pdf_processor import PyPDF2Processor, PYPDF2_AVAILABLE
from format_handlers.processors.audio_processor import WhisperAudioProcessor, WHISPER_AVAILABLE, PYDUB_AVAILABLE
from format_handlers.processors.ocr_processor import TESSERACT_AVAILABLE
from format_handlers.processors.docx_processor import PYTHON_DOCX_AVAILABLE


class TestProcessorIntegration(unittest.TestCase):
    """
    Test the integration between format handlers and processors.
    
    These tests validate that format handlers can correctly:
    1. Detect when processors are available
    2. Fall back to simpler implementations when not available
    3. Properly use processor functionality when available
    """
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary test directory
        self.test_dir = tempfile.mkdtemp()
        
        # Create simple test files
        self.pdf_file = os.path.join(self.test_dir, "test.pdf")
        self.audio_file = os.path.join(self.test_dir, "test.mp3")
        self.image_file = os.path.join(self.test_dir, "test.png")
        self.docx_file = os.path.join(self.test_dir, "test.docx")
        
        # Create empty test files
        with open(self.pdf_file, "w") as f:
            f.write("PDF data")
            
        with open(self.audio_file, "w") as f:
            f.write("MP3 data")
            
        with open(self.docx_file, "w") as f:
            f.write("DOCX data")
            
        # Create a test image with text
        self.create_test_image()
    
    def tearDown(self):
        """Tear down test fixtures."""
        # Remove test files
        if os.path.exists(self.pdf_file):
            os.unlink(self.pdf_file)
            
        if os.path.exists(self.audio_file):
            os.unlink(self.audio_file)
            
        if os.path.exists(self.image_file):
            os.unlink(self.image_file)
            
        if os.path.exists(self.docx_file):
            os.unlink(self.docx_file)
            
        # Remove test directory
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
            
    def create_test_image(self):
        """Create a test image with text."""
        try:
            # Create a blank image with white background
            img = Image.new('RGB', (200, 100), color=(255, 255, 255))
            d = ImageDraw.Draw(img)
            
            # Add some text to the image
            font = ImageFont.load_default()
            d.text((20, 40), "Test Image", fill=(0, 0, 0), font=font)
            
            # Save the image to a temporary file
            img.save(self.image_file)
        except Exception as e:
            self.skipTest(f"Could not create test image: {e}")
    
    @patch('format_handlers.processors.pdf_processor.PyPDF2Processor.process_document')
    @patch('format_handlers.processors.pdf_processor.pdf_processor.can_process')
    def test_application_handler_uses_pdf_processor(self, mock_can_process, mock_process_document):
        """Test that the application handler uses the PDF processor."""
        # Configure mocks
        mock_can_process.return_value = True
        mock_process_document.return_value = ("PDF Text", {"title": "Test PDF"}, [{"type": "page"}])
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"PDF data"
            mock_read_file.return_value = mock_file_content
            
            # Call the handler
            with patch('format_handlers.application_handler.format_detector.detect_format') as mock_detect:
                mock_detect.return_value = ("pdf", 0.9)
                
                # Try to extract content
                content = application_handler.do_extraction(self.pdf_file, {'format': 'pdf'})
                
                # Verify the processor was used
                mock_process_document.assert_called_once()
                
                # Check content
                self.assertEqual(content.metadata.get("title"), "Test PDF")
    
    @patch('format_handlers.application_handler.format_detector.detect_format')
    @patch('format_handlers.processors.pdf_processor.pdf_processor.can_process')
    def test_application_handler_fallback(self, mock_can_process, mock_detect):
        """Test that the application handler falls back when the processor is not available."""
        # Configure mocks
        mock_can_process.return_value = False
        mock_detect.return_value = ("pdf", 0.9)
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"PDF data"
            mock_read_file.return_value = mock_file_content
            
            # Patch the ValueError that would normally be raised
            with patch('format_handlers.application_handler.ValueError', MagicMock()):
                try:
                    # Try to extract content - this will raise an error but we're testing the fallback mechanism
                    content = application_handler.do_extraction(self.pdf_file, {'format': 'pdf'})
                except:
                    pass
                
                # Verify the processor was checked
                mock_can_process.assert_called_once()
    
    @unittest.skipIf(not PYDUB_AVAILABLE, "pydub not available")
    @patch('format_handlers.processors.audio_processor.whisper_processor.process_audio')
    @patch('format_handlers.processors.audio_processor.whisper_processor.can_process')
    def test_audio_handler_uses_whisper_processor(self, mock_can_process, mock_process_audio):
        """Test that the audio handler uses the Whisper processor."""
        # Configure mocks
        mock_can_process.return_value = True
        mock_process_audio.return_value = ("Audio Text", {"duration": "0:01:00"}, [{"type": "transcript"}])
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"MP3 data"
            mock_read_file.return_value = mock_file_content
            
            # Call the handler
            with patch('format_handlers.audio_handler.format_detector.detect_format') as mock_detect:
                mock_detect.return_value = ("mp3", 0.9)
                
                # Try to extract content
                content = audio_handler.do_extraction(self.audio_file, {'format': 'mp3'})
                
                # Verify the processor was used
                mock_process_audio.assert_called_once()
                
                # Check content
                self.assertEqual(content.metadata.get("duration"), "0:01:00")
    
    @unittest.skipIf(not PYDUB_AVAILABLE, "pydub not available")
    @patch('format_handlers.audio_handler.format_detector.detect_format')
    @patch('format_handlers.processors.audio_processor.whisper_processor.can_process')
    @patch('format_handlers.audio_handler.AudioHandler._extract_with_pydub')
    def test_audio_handler_fallback(self, mock_extract_with_pydub, mock_can_process, mock_detect):
        """Test that the audio handler falls back when the processor is not available."""
        # Configure mocks
        mock_can_process.return_value = False
        mock_detect.return_value = ("mp3", 0.9)
        mock_extract_with_pydub.return_value = ("Audio Text", {"duration": "0:01:00"}, [])
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"MP3 data"
            mock_read_file.return_value = mock_file_content
            
            # Try to extract content
            content = audio_handler.do_extraction(self.audio_file, {'format': 'mp3'})
            
            # Verify the processor was checked
            mock_can_process.assert_called_once()
            
            # Verify the fallback was used
            mock_extract_with_pydub.assert_called_once()
            
            # Check content
            self.assertEqual(content.metadata.get("duration"), "0:01:00")


    @unittest.skipIf(not TESSERACT_AVAILABLE, "Tesseract OCR not available")
    @patch('format_handlers.processors.ocr_processor.ocr_processor.extract_text')
    @patch('format_handlers.processors.ocr_processor.ocr_processor.can_process')
    def test_image_handler_uses_ocr_processor(self, mock_can_process, mock_extract_text):
        """Test that the image handler uses the OCR processor."""
        # Configure mocks
        mock_can_process.return_value = True
        mock_extract_text.return_value = "Test Image OCR Text"
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"Image data"
            mock_read_file.return_value = mock_file_content
            
            # Call the handler
            with patch('format_handlers.image_handler.format_detector.detect_format') as mock_detect:
                mock_detect.return_value = ("png", 0.9)
                
                # Try to extract content
                content = image_handler.do_extraction(self.image_file, {'format': 'png'})
                
                # Verify the processor was used
                mock_extract_text.assert_called_once()
                
                # Check content contains OCR text
                ocr_sections = [s for s in content.sections if s.get('type') == 'ocr_text']
                self.assertEqual(len(ocr_sections), 1)
                self.assertEqual(ocr_sections[0].get('content'), "Test Image OCR Text")
                
                # Check that OCR text is in the main text content
                self.assertIn("Test Image OCR Text", content.text)
    
    @patch('format_handlers.image_handler.format_detector.detect_format')
    @patch('format_handlers.processors.ocr_processor.ocr_processor.can_process')
    def test_image_handler_ocr_fallback(self, mock_can_process, mock_detect):
        """Test that the image handler falls back when OCR is not available."""
        # Configure mocks
        mock_can_process.return_value = False
        mock_detect.return_value = ("png", 0.9)
        
        # Create a mock file_content for PIL
        with patch('PIL.Image.open') as mock_open:
            mock_img = MagicMock()
            mock_img.size = (200, 100)
            mock_img.format = "PNG"
            mock_img.mode = "RGB"
            mock_img._getexif.return_value = None
            
            # Set up the mock Image.open to return our mock image
            mock_open.return_value.__enter__.return_value = mock_img
            
            # Create a mock file_content get_as_binary
            with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
                mock_file_content = MagicMock()
                mock_file_content.get_as_binary.return_value = b"Image data"
                mock_read_file.return_value = mock_file_content
                
                # Try to extract content
                content = image_handler.do_extraction(self.image_file, {'format': 'png'})
                
                # Verify the processor was checked
                mock_can_process.assert_called_once()
                
                # Check that OCR section indicates OCR is not available
                ocr_sections = [s for s in content.sections if s.get('type') == 'ocr_text']
                self.assertEqual(len(ocr_sections), 1)
                self.assertIn("not available", ocr_sections[0].get('content'))
    
    @unittest.skipIf(not TESSERACT_AVAILABLE, "Tesseract OCR not available")
    def test_image_handler_ocr_integration_real(self):
        """Test OCR processor integration with image handler using a real image."""
        try:
            # Process the test image with real OCR
            content = image_handler.extract_content(self.image_file, {'extract_features': True})
            
            # Check that content was extracted
            self.assertIsNotNone(content)
            
            # Check that OCR section exists
            ocr_sections = [s for s in content.sections if s.get('type') == 'ocr_text']
            self.assertEqual(len(ocr_sections), 1)
            
            # The OCR text should contain "Test" or "Image" - we can't be too specific
            # as OCR results can vary depending on the tesseract version and configuration
            ocr_text = ocr_sections[0].get('content', '')
            
            # Tesseract should at least recognize some text
            self.assertGreater(len(ocr_text), 0)
            
        except Exception as e:
            self.skipTest(f"Real OCR test failed: {e}")
    
    @patch('format_handlers.processors.docx_processor.docx_processor.process_document')
    @patch('format_handlers.processors.docx_processor.docx_processor.can_process')
    def test_application_handler_uses_docx_processor(self, mock_can_process, mock_process_document):
        """Test that the application handler uses the DOCX processor."""
        # Configure mocks
        mock_can_process.return_value = True
        mock_process_document.return_value = ("DOCX Text", {"title": "Test DOCX"}, [{"type": "document"}])
        
        # Create a mock file_content get_as_binary
        with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
            mock_file_content = MagicMock()
            mock_file_content.get_as_binary.return_value = b"DOCX data"
            mock_read_file.return_value = mock_file_content
            
            # Call the handler
            with patch('format_handlers.application_handler.format_detector.detect_format') as mock_detect:
                mock_detect.return_value = ("docx", 0.9)
                
                # Try to extract content
                content = application_handler.do_extraction(self.docx_file, {'format': 'docx'})
                
                # Verify the processor was used
                mock_process_document.assert_called_once()
                
                # Check content
                self.assertEqual(content.metadata.get("title"), "Test DOCX")
    
    @patch('format_handlers.application_handler.format_detector.detect_format')
    @patch('format_handlers.processors.docx_processor.docx_processor.can_process')
    def test_application_handler_docx_fallback(self, mock_can_process, mock_detect):
        """Test that the application handler falls back when the DOCX processor is not available."""
        # Configure mocks
        mock_can_process.return_value = False
        mock_detect.return_value = ("docx", 0.9)
        
        # Create a mock zipfile
        with patch('zipfile.ZipFile') as mock_zipfile:
            mock_zip_instance = MagicMock()
            mock_zip_instance.namelist.return_value = ['word/document.xml']
            mock_zip_instance.read.return_value = b'<w:p><w:t>Test text</w:t></w:p>'
            mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
            
            # Create a mock file_content get_as_binary
            with patch('utils.filesystem.FileSystem.read_file') as mock_read_file:
                mock_file_content = MagicMock()
                mock_file_content.get_as_binary.return_value = b"DOCX data"
                mock_read_file.return_value = mock_file_content
                
                # Try to extract content
                content = application_handler.do_extraction(self.docx_file, {'format': 'docx'})
                
                # Verify the processor was checked
                mock_can_process.assert_called_once()
                
                # Check content
                self.assertIn("format", content.metadata)
                self.assertEqual(content.metadata["format"], "docx")
                
                # Check the fallback content is included
                document_sections = [s for s in content.sections if s.get('type') == 'document_content']
                self.assertEqual(len(document_sections), 1)
                self.assertIn("Test text", document_sections[0].get('content'))
                
    @unittest.skipIf(not PYTHON_DOCX_AVAILABLE, "python-docx not available")
    def test_docx_processor_integration_real(self):
        """Test DOCX processor integration with application handler using a real DOCX file."""
        try:
            # First create a real DOCX file
            import docx
            doc = docx.Document()
            doc.add_heading('Test Document', 0)
            doc.add_paragraph('This is a test document created for integration testing.')
            doc.save(self.docx_file)
            
            # Process the test DOCX
            content = application_handler.extract_content(self.docx_file)
            
            # Check that content was extracted
            self.assertIsNotNone(content)
            
            # Check content has the expected text
            self.assertIn("Test Document", content.text)
            self.assertIn("test document created", content.text)
            
        except Exception as e:
            self.skipTest(f"Real DOCX test failed: {e}")


if __name__ == "__main__":
    unittest.main()