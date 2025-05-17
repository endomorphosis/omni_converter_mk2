"""
Text format handlers for the Omni-Converter.

This module provides handlers for text-based formats like HTML, XML, plain text, etc.
"""

import os
import re
import csv
import html
import xml.etree.ElementTree as ET
from datetime import datetime
from io import StringIO
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from utils.logger import logger
from utils.format_detector import format_detector
from format_handlers.base_handler import BaseFormatHandler, Content


class TextHandler(BaseFormatHandler):
    """
    Handler for text-based formats.
    
    Handles common text formats like HTML, XML, plain text, calendar, and CSV.
    """
    
    def __init__(self):
        """Initialize the text handler."""
        super().__init__(
            handler_name="TextHandler",
            supported_formats={"html", "xml", "plain", "calendar", "csv"},
            capabilities={
                'category': 'text',
                'preserves_structure': True,
                'extracts_metadata': True,
                'supports_encoding_detection': True
            }
        )
        
        # Format-specific parsers
        self.format_parsers = {
            'html': self._parse_html,
            'xml': self._parse_xml,
            'plain': self._parse_plain_text,
            'calendar': self._parse_calendar,
            'csv': self._parse_csv
        }
    
    def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
        """
        Extract content from a text file.
        
        Args:
            file_path: The path to the file.
            options: Extraction options.
            
        Returns:
            The extracted content.
            
        Raises:
            ValueError: If the file format is not supported.
            Exception: If an error occurs during extraction.
        """
        # Detect format if not provided in options
        format_name = options.get('format')
        if not format_name:
            format_name, _ = format_detector.detect_format(file_path)
            
            # Override format detection based on file extension if needed
            _, ext = os.path.splitext(file_path)
            ext = ext.lower().lstrip('.')
            
            # Handle special cases
            if ext == 'xml':
                format_name = 'xml'
            elif ext == 'ics':
                format_name = 'calendar'
            elif ext == 'csv':
                format_name = 'csv'
        
        if not format_name or format_name not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")
        
        # Get file content
        file_content = FileSystem.read_file(file_path, 'r')
        
        # Parse content based on format
        parser = self.format_parsers.get(format_name)
        if not parser:
            raise ValueError(f"No parser available for format: {format_name}")
        
        logger.debug(f"Extracting content from {format_name} file: {file_path}")
        
        try:
            text, metadata, sections = parser(file_content.get_as_text(), options)
            
            # Create content object
            content = Content(
                text=text,
                metadata=metadata,
                sections=sections,
                source_format=format_name,
                source_path=file_path
            )
            
            return content
            
        except Exception as e:
            logger.error(f"Error extracting content from {format_name} file: {file_path}", 
                        {'error': str(e)})
            raise
    
    def _parse_html(self, text: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse HTML content.
        
        Args:
            text: The HTML text.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections). 
        """
        # TODO: Implement a more robust HTML parser with BeautifulSoup.
        # Basic HTML parsing - in a real implementation, use a proper HTML parser like BeautifulSoup #TODO
        # This is a simplified version for demonstration purposes
        
        # Extract title
        title_match = re.search(r'<title[^>]*>(.*?)</title>', text, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1) if title_match else ""
        
        # Extract metadata from meta tags
        metadata = {
            'title': title,
            'format': 'html'
        }
        
        # Remove script and style tags
        text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
        
        # Replace common tags with newlines or spaces
        text = re.sub(r'<(br|p|div|h[1-6]|li)[^>]*>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'</(p|div|h[1-6]|li)>', '\n', text, flags=re.IGNORECASE)
        text = re.sub(r'<[^>]*>', ' ', text)
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # TODO - Extract more metadata (like author, date, etc.) if available
        # Split into sections (just a simple example - real implementation would be more sophisticated) # TODO
        sections = []
        if title:
            sections.append({
                'type': 'title',
                'content': title
            })
        
        sections.append({
            'type': 'body',
            'content': text
        })
        
        return text, metadata, sections
    
    def _parse_xml(self, text: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse XML content.
        
        Args:
            text: The XML text.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # TODO - Implement a more robust XML parser with lxml or similar library.
        # Basic XML parsing
        try:
            root = ET.fromstring(text)
            
            # Extract metadata
            metadata = {
                'root_element': root.tag,
                'format': 'xml'
            }
            
            # Function to extract text from element and children
            def extract_text(element):
                text = element.text or ""
                for child in element:
                    text += f" {extract_text(child)}"
                if element.tail:
                    text += f" {element.tail}"
                return text
            
            # Extract text from the XML
            extracted_text = extract_text(root)
            
            # Normalize whitespace
            extracted_text = re.sub(r'\s+', ' ', extracted_text).strip()
            
            # Create sections
            sections = []
            for child in root:
                child_text = extract_text(child)
                sections.append({
                    'type': child.tag,
                    'content': child_text
                })
            
            return extracted_text, metadata, sections
            
        except ET.ParseError:
            # If XML parsing fails, fall back to plain text
            logger.warning("XML parsing failed, falling back to plain text")
            return self._parse_plain_text(text, options)
    
    def _parse_plain_text(self, text: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse plain text content.
        
        Args:
            text: The plain text.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Plain text is already in the desired format
        metadata = {
            'format': 'plain',
            'line_count': text.count('\n') + 1
        }
        
        # Create a single section
        sections = [{
            'type': 'text',
            'content': text
        }]
        
        return text, metadata, sections
    
    def _parse_calendar(self, text: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse calendar content (iCal format).
        
        Args:
            text: The calendar text.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # TODO - Implement a more robust iCal parser with icalendar or similar library.
        # Basic iCal parsing
        metadata = {
            'format': 'calendar'
        }
        
        # Extract events
        events = []
        current_event = {}
        lines = [line.strip() for line in text.split('\n')]
        in_event = False

        for line in lines:
            match line:
                case 'BEGIN:VEVENT':
                    in_event = True
                    current_event = {}
                case 'END:VEVENT':
                    in_event = False
                    if current_event:
                        events.append(current_event)
                case _ if in_event and ':' in line:
                    key, value = line.split(':', 1)
                    current_event[key] = value
                case _:
                    # Ignore other lines
                    pass

            if line == 'BEGIN:VEVENT':
                in_event = True
                current_event = {}
            elif line == 'END:VEVENT':
                in_event = False
                if current_event:
                    events.append(current_event)
            elif in_event and ':' in line:
                key, value = line.split(':', 1)
                current_event[key] = value
        
        # Create human-readable text
        output_text = ""
        
        for event in events:
            if 'SUMMARY' in event:
                output_text += f"Event: {event['SUMMARY']}\n"
            if 'DTSTART' in event:
                output_text += f"Start: {event['DTSTART']}\n"
            if 'DTEND' in event:
                output_text += f"End: {event['DTEND']}\n"
            if 'LOCATION' in event:
                output_text += f"Location: {event['LOCATION']}\n"
            if 'DESCRIPTION' in event:
                output_text += f"Description: {event['DESCRIPTION']}\n"
            output_text += "\n"
        
        # Create sections
        sections = []
        for event in events:
            if 'SUMMARY' in event:
                sections.append({
                    'type': 'event',
                    'content': event.get('DESCRIPTION', ''),
                    'title': event.get('SUMMARY', ''),
                    'start': event.get('DTSTART', ''),
                    'end': event.get('DTEND', '')
                })
        
        metadata['event_count'] = len(events)
        
        return output_text, metadata, sections
    
    def _parse_csv(self, text: str, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse CSV content.
        
        Args:
            text: The CSV text.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Parse CSV using built-in CSV module
        csv_reader = csv.reader(StringIO(text))
        rows = list(csv_reader)
        
        # Extract header if available
        header = []
        if rows and options.get('has_header', True):
            header = rows[0]
            rows = rows[1:]
        
        # Create metadata
        metadata = {
            'format': 'csv',
            'row_count': len(rows),
            'column_count': len(header) if header else (len(rows[0]) if rows else 0)
        }
        
        # Create human-readable text
        output_text = ""
        
        # Add header
        if header:
            output_text += " | ".join(header) + "\n"
            output_text += "-" * (sum(len(h) for h in header) + 3 * (len(header) - 1)) + "\n"
        
        # Add rows
        for row in rows:
            output_text += " | ".join(row) + "\n"
        
        # Create sections
        sections = []
        
        if header:
            sections.append({
                'type': 'header',
                'content': header
            })
        
        sections.append({
            'type': 'data',
            'content': rows
        })
        
        return output_text, metadata, sections


# Global text handler instance
text_handler = TextHandler()
