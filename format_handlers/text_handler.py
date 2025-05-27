"""
Text format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for text-based formats like HTML, XML, plain text, etc.
using dependency injection for better modularity and testability, without inheritance.
"""

from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from configs import Configs
from logger import logger
from format_handlers.unified_handler import BaseFormatHandler, Content, create_handler, map_extension_to_format
from format_handlers.constants import Constants
from core.format_detector import format_detector


def create_text_handler(resources: Dict[str, Any], configs: Optional[Configs] = None) -> BaseFormatHandler:
    """
    Create a text handler instance with injected dependencies.
    
    Args:
        resources: Resources dictionary with dependencies.
            Must contain:
            - beautiful_soup_processor: HTML processor
            - lxml_processor: XML processor
            - icalendar_processor: Calendar file processor
            - csv_processor: CSV processor
        configs: Configuration settings.
        
    Returns:
        BaseFormatHandler instance configured for text formats.
    """
    # Format-specific file extensions # TODO These need to be moved to the constants file.
    format_extensions = {
        'html': ['.html', '.htm'],
        'xml': ['.xml'],
        'plain': ['.txt', '.text', '.md', '.rst', '.log'],
        'calendar': ['.ics'],
        'csv': ['.csv']
    }
    
    # Prepare parsers with the appropriate functions
    parsers = {
        "text": {
            "html": process_html,
            "xml": process_xml,
            "plain": process_plain_text,
            "calendar": process_calendar,
            "csv": process_csv
        }
    }
    
    # Additional resources specific to text handling
    text_resources = {
        "format_extensions": format_extensions
    }
    
    # Create and return the handler
    return create_handler(
        handler_name="TextHandler",
        format_detector=format_detector,
        ext_to_format=map_extension_to_format,
        supported_formats=Constants.SUPPORTED_TEXT_FORMATS_SET,
        capabilities=Constants.TEXT_HANDLER_CAPABILITIES,
        parsers=parsers,
        resources_extra=text_resources,
        configs=configs
    )


def process_html(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an HTML file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the HTML file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use beautiful_soup_processor if available
    bs_processor = options.get("beautiful_soup_processor")
    if bs_processor:
        return bs_processor.process_html(file_content, options)
    
    # Fallback to basic HTML processing
    logger.warning("BeautifulSoup processor not available, using basic HTML processing")
    
    # Get HTML content as text
    if hasattr(file_content, 'get_as_text'):
        html_content = file_content.get_as_text()
    else:
        html_content = file_content
    
    import re
    import html
    
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1) if title_match else ""
    
    # Extract metadata
    metadata = {
        'title': title,
        'format': 'html'
    }
    
    # Remove script and style tags
    text = re.sub(r'<script[^>]*>.*?</script>', '', html_content, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.IGNORECASE | re.DOTALL)
    
    # Replace common tags with newlines or spaces
    text = re.sub(r'<(br|p|div|h[1-6]|li)[^>]*>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'</(p|div|h[1-6]|li)>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<[^>]*>', ' ', text)
    
    # Decode HTML entities
    text = html.unescape(text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text).strip()
    
    # Create sections
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


def process_xml(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an XML file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the XML file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use lxml_processor if available
    lxml_processor = options.get("lxml_processor")
    if lxml_processor:
        return lxml_processor.process_xml(file_content, options)
    
    # Fallback to basic XML processing
    logger.warning("lxml processor not available, using basic XML processing")
    
    # Get XML content as text
    if hasattr(file_content, 'get_as_text'):
        xml_content = file_content.get_as_text()
    else:
        xml_content = file_content
    
    import re
    import xml.etree.ElementTree as ET
    
    try:
        root = ET.fromstring(xml_content)
        
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
        
    except ET.ParseError as e:
        # If XML parsing fails, fall back to plain text
        logger.warning(f"XML parsing failed, falling back to plain text: {e}")
        
        metadata = {
            'format': 'xml',
            'parse_error': str(e)
        }
        
        sections = [{
            'type': 'text',
            'content': xml_content
        }]
        
        return xml_content, metadata, sections


def process_plain_text(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a plain text file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the text file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Get text content
    if hasattr(file_content, 'get_as_text'):
        text = file_content.get_as_text()
    else:
        text = file_content
    
    # Plain text is already in the desired format
    metadata = {
        'format': 'plain',
        'line_count': text.count('\n') + 1,
        'character_count': len(text),
        'word_count': len(text.split())
    }
    
    # Create a single section
    sections = [{
        'type': 'text',
        'content': text
    }]
    
    return text, metadata, sections


def process_calendar(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a calendar file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the calendar file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use icalendar_processor if available
    ical_processor = options.get("icalendar_processor")
    if ical_processor:
        return ical_processor.process_calendar(file_content, options)
    
    # Fallback to basic calendar processing
    logger.warning("icalendar processor not available, using basic calendar processing")
    
    # Get calendar content as text
    if hasattr(file_content, 'get_as_text'):
        calendar_content = file_content.get_as_text()
    else:
        calendar_content = file_content
    
    # Basic iCal parsing
    metadata = {
        'format': 'calendar'
    }
    
    # Extract events
    events = []
    current_event = {}
    lines = [line.strip() for line in calendar_content.split('\n')]
    in_event = False
    
    for line in lines:
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


def process_csv(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a CSV file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the CSV file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use csv_processor if available
    csv_processor = options.get("csv_processor")
    if csv_processor:
        return csv_processor.process_csv(file_content, options)
    
    # Fallback to basic CSV processing
    logger.warning("csv processor not available, using basic CSV processing")
    
    # Get CSV content as text
    if hasattr(file_content, 'get_as_text'):
        csv_content = file_content.get_as_text()
    else:
        csv_content = file_content
    
    import csv
    from io import StringIO
    
    # Parse CSV using built-in CSV module
    csv_reader = csv.reader(StringIO(csv_content))
    rows = list(csv_reader)
    
    # Extract header if available
    header = []
    has_header = options.get('has_header', True)
    if rows and has_header:
        header = rows[0]
        rows = rows[1:]
    
    # Create metadata
    metadata = {
        'format': 'csv',
        'row_count': len(rows),
        'column_count': len(header) if header else (len(rows[0]) if rows else 0),
        'has_header': has_header
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