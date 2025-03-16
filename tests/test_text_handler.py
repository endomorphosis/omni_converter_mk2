"""
Test the text format handler.

This module tests the text format handler functionality.
"""

import os
import unittest
import tempfile
from typing import Dict, Any

from utils.filesystem import FileSystem
from format_handlers.text_handler import TextHandler


class TestTextHandler(unittest.TestCase):
    """Test the text format handler."""
    
    def setUp(self):
        """Set up the test environment."""
        self.handler = TextHandler()
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
        Create test files for different text formats.
        
        Returns:
            A dictionary mapping format names to file paths.
        """
        files = {}
        
        # HTML test file
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Test HTML Document</title>
            <meta name="description" content="A test HTML document">
        </head>
        <body>
            <h1>Hello, World!</h1>
            <p>This is a <em>test</em> HTML document.</p>
            <div>
                <p>It contains multiple paragraphs.</p>
                <p>And <strong>formatted</strong> text.</p>
            </div>
        </body>
        </html>
        """
        html_path = os.path.join(self.test_dir, "test.html")
        with open(html_path, "w") as f:
            f.write(html_content)
        files["html"] = html_path
        
        # XML test file
        xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<root>
    <header>
        <title>Test XML Document</title>
        <date>2025-03-16</date>
    </header>
    <body>
        <section>
            <heading>Introduction</heading>
            <paragraph>This is a test XML document.</paragraph>
        </section>
        <section>
            <heading>Conclusion</heading>
            <paragraph>XML is a versatile format.</paragraph>
        </section>
    </body>
</root>"""
        xml_path = os.path.join(self.test_dir, "test.xml")
        with open(xml_path, "w") as f:
            f.write(xml_content)
        files["xml"] = xml_path
        
        # Plain text test file
        plain_content = """
        This is a plain text file.
        It contains multiple lines.
        And paragraphs.
        
        Like this one.
        """
        plain_path = os.path.join(self.test_dir, "test.txt")
        with open(plain_path, "w") as f:
            f.write(plain_content)
        files["plain"] = plain_path
        
        # Calendar test file
        calendar_content = """
        BEGIN:VCALENDAR
        VERSION:2.0
        PRODID:-//hacksw/handcal//NONSGML v1.0//EN
        BEGIN:VEVENT
        UID:uid1@example.com
        DTSTAMP:20250316T120000Z
        DTSTART:20250317T100000Z
        DTEND:20250317T110000Z
        SUMMARY:Meeting with Team
        LOCATION:Conference Room A
        DESCRIPTION:Weekly team meeting to discuss project progress.
        END:VEVENT
        BEGIN:VEVENT
        UID:uid2@example.com
        DTSTAMP:20250316T120000Z
        DTSTART:20250318T140000Z
        DTEND:20250318T150000Z
        SUMMARY:Client Call
        LOCATION:Phone
        DESCRIPTION:Call with client to review requirements.
        END:VEVENT
        END:VCALENDAR
        """
        calendar_path = os.path.join(self.test_dir, "test.ics")
        with open(calendar_path, "w") as f:
            f.write(calendar_content)
        files["calendar"] = calendar_path
        
        # CSV test file
        csv_content = """
        Name,Age,Country
        John Doe,30,USA
        Jane Smith,25,Canada
        Bob Johnson,45,UK
        Alice Williams,35,Australia
        """
        csv_path = os.path.join(self.test_dir, "test.csv")
        with open(csv_path, "w") as f:
            f.write(csv_content.strip())
        files["csv"] = csv_path
        
        return files
    
    def test_supported_formats(self):
        """Test that the handler supports the expected formats."""
        expected_formats = {"html", "xml", "plain", "calendar", "csv"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """Test that the handler reports its capabilities correctly."""
        capabilities = self.handler.get_capabilities()
        self.assertEqual(capabilities["handler_name"], "TextHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"html", "xml", "plain", "calendar", "csv"})
        self.assertEqual(capabilities["category"], "text")
    
    def test_can_handle(self):
        """Test that the handler correctly identifies supported files."""
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                self.assertTrue(self.handler.can_handle(file_path))
                self.assertTrue(self.handler.can_handle(file_path, format_name))
    
    def test_extract_html(self):
        """Test HTML content extraction."""
        content = self.handler.extract_content(self.test_files["html"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "html")
        
        # Check that HTML was parsed correctly
        self.assertIn("Hello, World!", content.text)
        self.assertIn("test HTML document", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("title"), "Test HTML Document")
        self.assertEqual(content.metadata.get("format"), "html")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
    
    def test_extract_xml(self):
        """Test XML content extraction."""
        content = self.handler.extract_content(self.test_files["xml"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "xml")
        
        # Check that XML was parsed correctly
        self.assertIn("Test XML Document", content.text)
        self.assertIn("Introduction", content.text)
        self.assertIn("XML is a versatile format", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("root_element"), "root")
        self.assertEqual(content.metadata.get("format"), "xml")
        
        # Check sections
        self.assertGreaterEqual(len(content.sections), 1)
    
    def test_extract_plain_text(self):
        """Test plain text content extraction."""
        content = self.handler.extract_content(self.test_files["plain"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "plain")
        
        # Check that plain text was parsed correctly
        self.assertIn("This is a plain text file", content.text)
        self.assertIn("It contains multiple lines", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "plain")
        self.assertGreaterEqual(content.metadata.get("line_count", 0), 5)
        
        # Check sections
        self.assertEqual(len(content.sections), 1)
        self.assertEqual(content.sections[0]["type"], "text")
    
    def test_extract_calendar(self):
        """Test calendar content extraction."""
        content = self.handler.extract_content(self.test_files["calendar"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "calendar")
        
        # Check that calendar was parsed correctly
        self.assertIn("Meeting with Team", content.text)
        self.assertIn("Client Call", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "calendar")
        self.assertEqual(content.metadata.get("event_count"), 2)
        
        # Check sections
        self.assertEqual(len(content.sections), 2)
        self.assertEqual(content.sections[0]["type"], "event")
        self.assertEqual(content.sections[1]["type"], "event")
    
    def test_extract_csv(self):
        """Test CSV content extraction."""
        content = self.handler.extract_content(self.test_files["csv"])
        
        # Check basic content properties
        self.assertIsNotNone(content.text)
        self.assertGreater(len(content.text), 0)
        self.assertEqual(content.source_format, "csv")
        
        # Check that CSV was parsed correctly
        self.assertIn("Name | Age | Country", content.text)
        self.assertIn("John Doe | 30 | USA", content.text)
        
        # Check metadata
        self.assertEqual(content.metadata.get("format"), "csv")
        self.assertEqual(content.metadata.get("row_count"), 4)
        self.assertEqual(content.metadata.get("column_count"), 3)
        
        # Check sections
        self.assertEqual(len(content.sections), 2)
        self.assertEqual(content.sections[0]["type"], "header")
        self.assertEqual(content.sections[1]["type"], "data")


if __name__ == "__main__":
    unittest.main()