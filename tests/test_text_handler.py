"""
Test the text format handler.

This module provides comprehensive tests for the TextHandler class, which is responsible
for processing various text-based file formats (HTML, XML, plain text, calendar, CSV).
The tests verify that the handler can correctly identify supported formats, extract
text content, parse metadata, and organize content into appropriate sections based
on the source format structure.
"""

import os
import unittest
import tempfile
from typing import Any

from utils.filesystem import FileSystem
from core.content_extractor.text_handler import TextHandler


class TestTextHandler(unittest.TestCase):
    """
    Test suite for the TextHandler class.
    
    This test class verifies that the TextHandler correctly processes and extracts
    content from different text-based file formats, including HTML, XML, plain text,
    calendar (ICS), and CSV files. Tests cover format detection, content extraction,
    metadata parsing, and section organization capabilities.
    """
    
    def setUp(self):
        """
        Set up the test environment before each test.
        
        Creates a TextHandler instance and a temporary directory to store test files.
        The test files are generated with known content for predictable test results.
        """
        self.handler = TextHandler()
        self.test_dir = tempfile.mkdtemp()
        
        # Create test files
        self.test_files = self._create_test_files()
    
    def tearDown(self):
        """
        Clean up after each test.
        
        Removes all test files created during setup and the temporary directory
        to ensure a clean state for subsequent tests.
        """
        for file_path in self.test_files.values():
            if os.path.exists(file_path):
                os.remove(file_path)
        
        if os.path.exists(self.test_dir):
            os.rmdir(self.test_dir)
    
    def _create_test_files(self) -> dict[str, str]:
        """
        Create test files for different text formats with predetermined content.
        
        Creates five different text-based files (HTML, XML, plain text, ICS calendar,
        and CSV) with known content structure to ensure consistent and predictable
        test results. Each file is created in the temporary test directory.
        
        Returns:
            dict[str, str]: A dictionary mapping format names to absolute file paths.
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
        """
        Test that the TextHandler supports the expected text formats.
        
        Verifies that the TextHandler correctly reports its supported formats,
        which should include HTML, XML, plain text, calendar (ICS), and CSV formats.
        This ensures the handler's format detection capabilities function properly.
        """
        expected_formats = {"html", "xml", "plain", "calendar", "csv"}
        self.assertEqual(self.handler.supported_formats, expected_formats)
    
    def test_capabilities(self):
        """
        Test that the TextHandler reports its capabilities correctly.
        
        Verifies that the handler provides accurate information about its name,
        supported formats, and category through the capabilities method.
        This ensures the handler properly identifies itself within the format registry system.
        """
        capabilities = self.handler.capabilities
        self.assertEqual(capabilities["handler_name"], "TextHandler")
        self.assertEqual(set(capabilities["supported_formats"]), 
                         {"html", "xml", "plain", "calendar", "csv"})
        self.assertEqual(capabilities["category"], "text")
    
    def test_can_handle(self):
        """
        Test that the TextHandler correctly identifies supported files.
        
        Verifies that the can_handle() method correctly identifies files of supported formats
        (HTML, XML, plain text, calendar, CSV) both with and without explicitly specifying
        the format. This ensures proper file format detection functionality.
        """
        for format_name, file_path in self.test_files.items():
            with self.subTest(format=format_name):
                self.assertTrue(self.handler.can_handle(file_path))
                self.assertTrue(self.handler.can_handle(file_path, format_name))
    
    def test_extract_html(self):
        """
        Test HTML content extraction functionality.
        
        Verifies that the TextHandler can correctly extract content from an HTML file,
        including the main text content, metadata (like the title), and properly
        organized sections. The test checks that the content is properly stripped of
        HTML tags while preserving the text structure and that metadata is correctly
        identified from HTML elements like <title> and <meta> tags.
        """
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
        """
        Test XML content extraction functionality.
        
        Verifies that the TextHandler can correctly extract content from an XML file,
        including the text content, metadata (like root element information), and 
        properly organized sections. The test ensures that XML structure is properly 
        parsed and that text content is extracted in a meaningful way that preserves
        the hierarchical structure of the original XML document.
        """
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
        """
        Test plain text content extraction functionality.
        
        Verifies that the TextHandler can correctly extract content from a plain text file,
        preserving the line structure, paragraphs, and other textual elements. The test
        checks that the handler correctly identifies metadata (like line count) and
        organizes the content into appropriate sections while maintaining the original
        text formatting.
        """
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
        """
        Test calendar (ICS) content extraction functionality.
        
        Verifies that the TextHandler can correctly extract content from an ICS calendar file,
        including event details (summaries, descriptions, dates), metadata (like event count),
        and section organization. The test ensures that calendar events are properly parsed
        and formatted into human-readable text while preserving the essential structured
        information from the original calendar file.
        """
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
        """
        Test CSV content extraction functionality.
        
        Verifies that the TextHandler can correctly extract content from a CSV file,
        including the tabular data, metadata (like row and column counts), and proper
        sectioning of header and data rows. The test ensures that the CSV structure is
        preserved in a human-readable format with appropriate separators while maintaining
        the relationship between header fields and data values.
        """
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