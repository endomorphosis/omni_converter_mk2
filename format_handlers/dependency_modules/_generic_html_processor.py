"""
HTML processing with base python 3.12.

This module contains generic functions for processing HTML content.
It uses no external libraries and can be used when no third-party dependencies are available.
"""

import re
import html
from typing import Any, Dict, List, Optional, Tuple, Union

from logger import logger

def extract_html_metadata(
    html_content: str,
    options: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Extract metadata from HTML content.
    
    Args:
        html_content: The HTML content as text.
        options: Optional extraction options.
        
    Returns:
        Dictionary of metadata.
    """
    # Extract title
    title_match = re.search(r'<title[^>]*>(.*?)</title>', html_content, re.IGNORECASE | re.DOTALL)
    title = title_match.group(1) if title_match else ""
    
    # Extract metadata from meta tags
    metadata = {
        'title': title,
        'format': 'html'
    }
    
    # Extract description
    desc_match = re.search(r'<meta\s+name=["\']description["\']\s+content=["\'](.*?)["\']\s*/?>', 
                        html_content, re.IGNORECASE | re.DOTALL)
    if desc_match:
        metadata['description'] = desc_match.group(1)
    
    # Extract keywords
    keywords_match = re.search(r'<meta\s+name=["\']keywords["\']\s+content=["\'](.*?)["\']\s*/?>', 
                            html_content, re.IGNORECASE | re.DOTALL)
    if keywords_match:
        metadata['keywords'] = keywords_match.group(1)
    
    # Extract author
    author_match = re.search(r'<meta\s+name=["\']author["\']\s+content=["\'](.*?)["\']\s*/?>', 
                            html_content, re.IGNORECASE | re.DOTALL)
    if author_match:
        metadata['author'] = author_match.group(1)
    
    return metadata


def extract_html_content(
    html_content: str,
    options: Optional[Dict[str, Any]] = None
) -> str:
    """
    Extract plain text content from HTML.
    
    Args:
        html_content: The HTML content as text.
        options: Optional extraction options.
        
    Returns:
        Plain text extracted from HTML.
    """
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
    
    return text


def create_html_sections(
    html_content: str,
    metadata: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Create sections from HTML content.
    
    Args:
        html_content: The HTML content as text.
        metadata: Metadata extracted from the HTML.
        
    Returns:
        List of sections.
    """
    sections = []
    
    # Add title section if available
    title = metadata.get('title')
    if title:
        sections.append({
            'type': 'title',
            'content': title
        })
    
    # Extract headings
    heading_pattern = r'<h([1-6])[^>]*>(.*?)</h\1>'
    headings = re.findall(heading_pattern, html_content, re.IGNORECASE | re.DOTALL)
    
    for level, content in headings:
        # Clean up the heading content
        clean_content = re.sub(r'<[^>]*>', '', content)
        clean_content = html.unescape(clean_content).strip()
        
        if clean_content:
            sections.append({
                'type': f'heading{level}',
                'content': clean_content
            })
    
    # Add body section
    text = extract_html_content(html_content)
    sections.append({
        'type': 'body',
        'content': text
    })
    
    return sections


def process_html(
    file_content: Any,
    options: Dict[str, Any]
) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process HTML content.
    
    Args:
        file_content: The file content to process.
        options: Processing options.
        
    Returns:
        Tuple of (text content, metadata, sections).
    """
    # Get HTML content as text
    if hasattr(file_content, 'get_as_text'):
        html_content = file_content.get_as_text()
    else:
        html_content = file_content
    
    # Extract metadata
    metadata = extract_html_metadata(html_content, options)
    
    # Extract text content
    text = extract_html_content(html_content, options)
    
    # Create sections
    sections = create_html_sections(html_content, metadata)
    
    return text, metadata, sections