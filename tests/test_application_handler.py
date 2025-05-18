"""
Test the application format handler.

This module tests the application format handler functionality.
"""

import os
import json
import logging
import unittest
import tempfile
import zipfile
from typing import Dict, Any
from io import BytesIO

from utils.filesystem import FileSystem
from utils.logger import test_logger
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
        
        # PDF test file (valid minimal PDF structure)
        pdf_path = os.path.join(self.test_dir, "test.pdf")
        with open(pdf_path, "wb") as f:
            # Create a minimal valid PDF file
            f.write(b'''\
%PDF-1.5
1 0 obj
<</Type /Catalog /Pages 2 0 R>>
endobj
2 0 obj
<</Type /Pages /Kids [3 0 R] /Count 1>>
endobj
3 0 obj
<</Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources <<>>>>
endobj
4 0 obj
<</Length 22>>
stream
BT
/F1 12 Tf
ET
endstream
endobj
xref
0 5
0000000000 65535 f
0000000009 00000 n
0000000057 00000 n
0000000112 00000 n
0000000204 00000 n
trailer
<</Size 5 /Root 1 0 R>>
startxref
273
%%EOF'''
            )
        files["pdf"] = pdf_path
        
        # DOCX test file (valid minimal docx structure)
        docx_path = os.path.join(self.test_dir, "test.docx")
        with zipfile.ZipFile(docx_path, 'w') as zipf:
            # Required file structure for a valid DOCX
            zipf.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
</Types>''')
            
            zipf.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>
</Relationships>''')
            
            zipf.writestr('word/document.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>
    <w:p>
      <w:r>
        <w:t>Test document content</w:t>
      </w:r>
    </w:p>
  </w:body>
</w:document>''')
            
            zipf.writestr('word/_rels/document.xml.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
</Relationships>''')
        
        files["docx"] = docx_path
        
        # XLSX test file (valid minimal xlsx structure)
        xlsx_path = os.path.join(self.test_dir, "test.xlsx")
        with zipfile.ZipFile(xlsx_path, 'w') as zipf:
            # Required file structure for a valid XLSX
            zipf.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
</Types>''')
            
            zipf.writestr('_rels/.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
</Relationships>''')
            
            zipf.writestr('xl/workbook.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheets>
    <sheet name="Sheet1" sheetId="1" r:id="rId1" xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships"/>
  </sheets>
</workbook>''')
            
            zipf.writestr('xl/_rels/workbook.xml.rels', '''<?xml version="1.0" encoding="UTF-8"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
  <Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet1.xml"/>
</Relationships>''')
            
            zipf.writestr('xl/worksheets/sheet1.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
  <sheetData>
    <row r="1">
      <c r="A1" t="s">
        <v>0</v>
      </c>
    </row>
  </sheetData>
</worksheet>''')
            
            # Add the shared strings file (required for text values)
            zipf.writestr('xl/sharedStrings.xml', '''<?xml version="1.0" encoding="UTF-8"?>
<sst xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main" count="1" uniqueCount="1">
  <si>
    <t>Test spreadsheet content</t>
  </si>
</sst>''')
            
            # Add the content type for shared strings
            zipf.writestr('[Content_Types].xml', '''<?xml version="1.0" encoding="UTF-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>
  <Override PartName="/xl/worksheets/sheet1.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>
  <Override PartName="/xl/sharedStrings.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sharedStrings+xml"/>
</Types>''')
            
        files["xlsx"] = xlsx_path
        
        return files
    
    def test_supported_formats(self):
        """Test that the handler supports the expected formats."""
        expected_formats = {"pdf", "json", "docx", "xlsx", "zip"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """Test that the handler reports its capabilities correctly."""
        capabilities = self.handler.capabilities
        self.assertEqual(capabilities["handler_name"], "ApplicationHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"pdf", "json", "docx", "xlsx", "zip"})
        self.assertEqual(capabilities["category"], "application")
    
    def test_can_handle(self):
        """Test that the handler correctly identifies supported files."""
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                test_logger.debug(f"Testing can_handle from '{type(self.handler)}' for '{file_path}'")
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
        
        # Check content
        self.assertIn("PDF", content.text)
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
    
    def test_extract_docx(self):
        """Test DOCX content extraction."""
        content = self.handler.extract_content(self.test_files["docx"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "docx")
        
        # Since we're using a minimal DOCX for testing,
        # we can only check for some basic content and structure
        
        # Check content
        self.assertIn("document", content.text.lower()) 
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
    
    def test_extract_xlsx(self):
        """Test XLSX content extraction."""
        content = self.handler.extract_content(self.test_files["xlsx"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "xlsx")
        
        # Since we're using a minimal XLSX for testing,
        # we can only check for some basic content and structure
        
        # Check content
        self.assertIn("spreadsheet", content.text.lower())
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
        
        # There should be at least one spreadsheet-related section
        self.assertTrue(any("sheet" in str(s.get("type", "")).lower() or 
                           "spreadsheet" in str(s.get("type", "")).lower() 
                           for s in content.sections))


if __name__ == "__main__":
    unittest.main()