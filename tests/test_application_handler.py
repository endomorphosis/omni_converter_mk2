"""
Test the application format handler.

This module tests the application format handler functionality.
"""

import os
import json
import unittest
import tempfile
import zipfile
from typing import Dict, Any
from io import BytesIO

from utils.filesystem import FileSystem
from format_handlers.application_handler import ApplicationHandler


class TestApplicationHandler(unittest.TestCase):
    """Test the application format handler."""
    
    def setUp(self):
        """Set up the test environment."""
        self.handler = ApplicationHandler()
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
        Create test files for different application formats.
        
        Returns:
            A dictionary mapping format names to file paths.
        """
        files = {}
        
        # JSON test file
        json_content = {
            "name": "Test Document",
            "version": "1.0",
            "data": [
                {"id": 1, "value": "First item"},
                {"id": 2, "value": "Second item"},
                {"id": 3, "value": "Third item"}
            ],
            "metadata": {
                "author": "Test Author",
                "created": "2025-03-16T12:00:00Z"
            }
        }
        json_path = os.path.join(self.test_dir, "test.json")
        with open(json_path, "w") as f:
            json.dump(json_content, f, indent=2)
        files["json"] = json_path
        
        # ZIP test file
        zip_path = os.path.join(self.test_dir, "test.zip")
        with zipfile.ZipFile(zip_path, 'w') as zipf:
            # Add some text files to the zip
            zipf.writestr("file1.txt", "This is the first file in the ZIP archive.")
            zipf.writestr("file2.txt", "This is the second file in the ZIP archive.")
            zipf.writestr("data/file3.txt", "This is a file in a subdirectory.")
            
            # Add a small JSON file
            zipf.writestr("data.json", json.dumps({"key": "value"}))
        files["zip"] = zip_path
        
        # Create placeholder files for formats we don't parse yet
        # These will still be detected by extension
        
        # PDF test file (just a placeholder)
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.5\nPlaceholder PDF content")
        files["pdf"] = pdf_path
        
        # DOCX test file (minimal valid docx structure)
        docx_path = os.path.join(self.test_dir, "test.docx")
        with zipfile.ZipFile(docx_path, 'w') as zipf:
            zipf.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
            zipf.writestr('word/document.xml', '<?xml version="1.0" encoding="UTF-8"?><w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:t>Test document content</w:t></w:p></w:body></w:document>')
        files["docx"] = docx_path
        
        # XLSX test file (minimal valid xlsx structure)
        xlsx_path = os.path.join(self.test_dir, "test.xlsx")
        with zipfile.ZipFile(xlsx_path, 'w') as zipf:
            zipf.writestr('[Content_Types].xml', '<?xml version="1.0" encoding="UTF-8"?><Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types"></Types>')
            zipf.writestr('xl/worksheets/sheet1.xml', '<?xml version="1.0" encoding="UTF-8"?><worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main"><sheetData><row><c><v>Test spreadsheet content</v></c></row></sheetData></worksheet>')
        files["xlsx"] = xlsx_path
        
        return files
    
    def test_supported_formats(self):
        """Test that the handler supports the expected formats."""
        expected_formats = {"pdf", "json", "docx", "xlsx", "zip"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """Test that the handler reports its capabilities correctly."""
        capabilities = self.handler.get_capabilities()
        self.assertEqual(capabilities["handler_name"], "ApplicationHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"pdf", "json", "docx", "xlsx", "zip"})
        self.assertEqual(capabilities["category"], "application")
    
    def test_can_handle(self):
        """Test that the handler correctly identifies supported files."""
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                self.assertTrue(self.handler.can_handle(file_path))
                self.assertTrue(self.handler.can_handle(file_path, format_name))
    
    def test_extract_json(self):
        """Test JSON content extraction."""
        content = self.handler.extract_content(self.test_files["json"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "json")
        
        # Check that JSON was parsed correctly
        self.assertIn("Test Document", content.text)
        self.assertIn("First item", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "json")
        self.assertEqual(content.metadata.get("structure_type"), "object")
        self.assertIn("name", content.metadata.get("top_level_keys", []))
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        
        # Find fields in sections
        field_sections = [s for s in content.sections if s["type"] == "json_field"]
        self.assertGreaterEqual(len(field_sections), 1)
    
    def test_extract_zip(self):
        """Test ZIP content extraction."""
        content = self.handler.extract_content(self.test_files["zip"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "zip")
        
        # Check that ZIP was parsed correctly
        self.assertIn("ZIP Archive with", content.text)
        self.assertIn("file1.txt", content.text)
        self.assertIn("This is the first file", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "zip")
        self.assertGreaterEqual(content.metadata.get("file_count", 0), 4)
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        
        # Find file_list section
        file_list_sections = [s for s in content.sections if s["type"] == "file_list"]
        self.assertEqual(len(file_list_sections), 1)
        
        # Check file contents
        file_content_sections = [s for s in content.sections if s["type"] == "file_content"]
        self.assertGreaterEqual(len(file_content_sections), 1)
    
    def test_extract_pdf(self):
        """Test PDF content extraction."""
        content = self.handler.extract_content(self.test_files["pdf"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "pdf")
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "pdf")
        self.assertEqual(content.metadata.get("content_type"), "application/pdf")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "document_info")
    
    def test_extract_docx(self):
        """Test DOCX content extraction."""
        content = self.handler.extract_content(self.test_files["docx"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "docx")
        
        # Since we're not actually parsing DOCX content in our placeholder,
        # we can only check for the metadata and structure
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "docx")
        self.assertEqual(content.metadata.get("content_type"), 
                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "document_content")
    
    def test_extract_xlsx(self):
        """Test XLSX content extraction."""
        content = self.handler.extract_content(self.test_files["xlsx"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "xlsx")
        
        # Since we're not actually parsing XLSX content in our placeholder,
        # we can only check for the metadata and structure
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "xlsx")
        self.assertEqual(content.metadata.get("content_type"), 
                        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        
        # There should be at least one spreadsheet section
        sheet_sections = [s for s in content.sections if s["type"] == "spreadsheet"]
        self.assertGreaterEqual(len(sheet_sections), 1)


if __name__ == "__main__":
    unittest.main()