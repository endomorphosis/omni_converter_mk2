"""
XML processing utilities using lxml.

This module contains functions for processing XML content using lxml
for robust XML parsing with fallback to ElementTree if the library
is not available.
"""

import re
from typing import Any, Dict, List, Optional, Tuple, Union

from utils.logger import logger

# Check if lxml is available
try:
    from lxml import etree
    LXML_AVAILABLE = True
except ImportError:
    LXML_AVAILABLE = False
    logger.warning("lxml not available, XML processing will use ElementTree instead")
    import xml.etree.ElementTree as etree


def extract_xml_metadata(
    xml_content: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract metadata from XML content using lxml.
    
    Args:
        xml_content: The XML content as text.
        options: Optional extraction options.
        
    Returns:
        Dictionary of metadata.
    """
    try:
        # Parse XML
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        # Basic metadata
        metadata = {
            'root_element': root.tag,
            'format': 'xml'
        }
        
        # Count child elements
        metadata['child_count'] = len(root)
        
        # Get namespace info
        nsmap = {}
        if hasattr(root, 'nsmap'):
            # lxml specific
            nsmap = root.nsmap
        else:
            # ElementTree fallback
            for match in re.finditer(r'xmlns:(\w+)=["\'](.*?)["\']', xml_content):
                prefix, uri = match.groups()
                nsmap[prefix] = uri
        
        if nsmap:
            metadata['namespaces'] = nsmap
        
        # Document statistics
        element_count = 0
        attr_count = 0
        max_depth = 0
        
        def count_elements(element, depth=0):
            nonlocal element_count, attr_count, max_depth
            element_count += 1
            attr_count += len(element.attrib)
            max_depth = max(max_depth, depth)
            
            for child in element:
                count_elements(child, depth + 1)
        
        count_elements(root)
        
        metadata.update({
            'element_count': element_count,
            'attribute_count': attr_count,
            'max_depth': max_depth
        })
        
        return metadata
    
    except Exception as e:
        logger.warning(f"XML parsing failed: {e}")
        return {
            'format': 'xml',
            'parse_error': str(e)
        }


def extract_xml_text(element) -> str:
    """
    Extract text from XML element and its children.
    
    Args:
        element: The XML element to process.
        
    Returns:
        Extracted text.
    """
    text = element.text or ""
    for child in element:
        text += f" {extract_xml_text(child)}"
    if element.tail:
        text += f" {element.tail}"
    return text


def create_xml_sections(
    xml_content: str,
    options: Optional[Dict[str, Any]] = None
) -> List[Dict[str, Any]]:
    """
    Create sections from XML content.
    
    Args:
        xml_content: The XML content as text.
        options: Optional extraction options.
        
    Returns:
        List of sections.
    """
    try:
        # Parse XML
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        sections = []
        
        # Create a section for each top-level element
        for child in root:
            child_text = extract_xml_text(child)
            
            # Get attributes as a dictionary
            attrs = dict(child.attrib) if hasattr(child, 'attrib') else {}
            
            section = {
                'type': child.tag,
                'content': child_text.strip()
            }
            
            if attrs:
                section['attributes'] = attrs
            
            sections.append(section)
        
        return sections
    
    except Exception as e:
        logger.warning(f"XML section creation failed: {e}")
        return [{
            'type': 'error',
            'content': f"XML parsing error: {e}"
        }]


def process_xml(
    file_content: Any,
    options: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process XML content using lxml.
    
    Args:
        file_content: The file content to process.
        options: Processing options.
        
    Returns:
        Tuple of (text content, metadata, sections).
    """
    # Get XML content as text
    if hasattr(file_content, 'get_as_text'):
        xml_content = file_content.get_as_text()
    else:
        xml_content = file_content
    
    try:
        # Parse XML with error recovery
        parser = etree.XMLParser(recover=True)
        root = etree.fromstring(xml_content.encode('utf-8'), parser)
        
        # Extract metadata
        metadata = extract_xml_metadata(xml_content, options)
        
        # Extract text
        text = extract_xml_text(root)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Create sections
        sections = create_xml_sections(xml_content, options)
        
        return text, metadata, sections
    
    except Exception as e:
        logger.warning(f"XML processing failed, falling back to plain text: {e}")
        
        # Fallback to plain text
        metadata = {
            'format': 'xml',
            'parse_error': str(e)
        }
        
        sections = [{
            'type': 'text',
            'content': xml_content
        }]
        
        return xml_content, metadata, sections