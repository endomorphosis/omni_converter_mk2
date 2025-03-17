"""
Application format handlers for the Omni-Converter.

This module provides handlers for application-based formats like PDF, JSON, DOCX, XLSX, and ZIP.
"""

import os
import json
import zipfile
from io import BytesIO, StringIO
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from utils.logger import logger
from utils.format_detector import format_detector
from format_handlers.base_handler import BaseFormatHandler, Content


class ApplicationHandler(BaseFormatHandler):
    """
    Handler for application-based formats.
    
    Handles common application formats like PDF, JSON, DOCX, XLSX, and ZIP.
    """
    
    def __init__(self):
        """Initialize the application handler."""
        super().__init__(
            handler_name="ApplicationHandler",
            supported_formats={"pdf", "json", "docx", "xlsx", "zip"},
            capabilities={
                'category': 'application',
                'preserves_structure': True,
                'extracts_metadata': True,
                'supports_nested_files': True
            }
        )
        
        # Format-specific parsers
        self.format_parsers = {
            'pdf': self._parse_pdf,
            'json': self._parse_json,
            'docx': self._parse_docx,
            'xlsx': self._parse_xlsx,
            'zip': self._parse_zip
        }
    
    def do_extraction(self, file_path: str, options: Dict[str, Any]) -> Content:
        """
        Extract content from an application file.
        
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
            if ext == 'json':
                format_name = 'json'
            elif ext == 'docx':
                format_name = 'docx'
            elif ext == 'xlsx':
                format_name = 'xlsx'
            elif ext == 'zip':
                format_name = 'zip'
        
        if not format_name or format_name not in self.supported_formats:
            raise ValueError(f"Unsupported format: {format_name}")
        
        # Get file content
        file_content = FileSystem.read_file(file_path, 'rb')
        
        # Parse content based on format
        parser = self.format_parsers.get(format_name)
        if not parser:
            raise ValueError(f"No parser available for format: {format_name}")
        
        logger.debug(f"Extracting content from {format_name} file: {file_path}")
        
        try:
            text, metadata, sections = parser(file_content.get_as_binary(), options)
            
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
    
    def _parse_pdf(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse PDF content.
        
        Args:
            data: The PDF binary data.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Note: In a real implementation, use a proper PDF parsing library like PyPDF2 or pdfminer
        # This is a placeholder implementation
        
        # For this placeholder, we'll just return some basic info
        metadata = {
            'format': 'pdf',
            'file_size': len(data),
            'content_type': 'application/pdf'
        }
        
        # Create placeholder text
        text = "[PDF Content Extraction Placeholder]\n\n"
        text += f"This is a PDF document with {len(data)} bytes of data.\n"
        text += "In a full implementation, text would be extracted using a PDF parsing library.\n"
        
        # Create basic sections
        sections = [{
            'type': 'document_info',
            'content': 'PDF Document'
        }]
        
        return text, metadata, sections
    
    def _parse_json(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse JSON content.
        
        Args:
            data: The JSON binary data.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Decode JSON data
        try:
            json_text = data.decode('utf-8')
            json_data = json.loads(json_text)
            
            # Extract metadata
            metadata = {
                'format': 'json',
                'content_type': 'application/json',
                'structure_type': 'object' if isinstance(json_data, dict) else 'array',
                'top_level_keys': list(json_data.keys()) if isinstance(json_data, dict) else []
            }
            
            # Format JSON as plain text
            formatted_json = json.dumps(json_data, indent=2)
            
            # Create sections based on JSON structure
            sections = []
            
            if isinstance(json_data, dict):
                for key, value in json_data.items():
                    sections.append({
                        'type': 'json_field',
                        'field_name': key,
                        'content': str(value)
                    })
            elif isinstance(json_data, list):
                for i, item in enumerate(json_data):
                    sections.append({
                        'type': 'json_item',
                        'index': i,
                        'content': str(item)
                    })
            
            return formatted_json, metadata, sections
            
        except (UnicodeDecodeError, json.JSONDecodeError) as e:
            logger.warning(f"JSON parsing failed: {str(e)}")
            return f"[Invalid JSON: {str(e)}]", {'format': 'json', 'is_valid': False}, []
    
    def _parse_docx(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse DOCX content.
        
        Args:
            data: The DOCX binary data.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Note: In a real implementation, use a proper DOCX parsing library like python-docx
        # This is a placeholder implementation
        
        # We can extract some basic info from the DOCX (which is a ZIP file)
        try:
            docx_file = BytesIO(data)
            with zipfile.ZipFile(docx_file) as zip_ref:
                file_list = zip_ref.namelist()
                
                # Extract content types
                content_types = []
                for filename in file_list:
                    if filename.endswith('.xml'):
                        content_types.append(filename)
                
                # Attempt to extract document.xml if it exists
                doc_text = ""
                if 'word/document.xml' in file_list:
                    doc_content = zip_ref.read('word/document.xml')
                    # In a real implementation, parse this XML properly
                    doc_text = doc_content.decode('utf-8', errors='ignore')
                    # Simplified XML content extraction
                    doc_text = doc_text.replace('<w:p>', '\n\n').replace('<w:t>', ' ').replace('</w:t>', '')
                    # Remove all XML tags
                    import re
                    doc_text = re.sub(r'<[^>]+>', '', doc_text)
                    # Normalize whitespace
                    doc_text = re.sub(r'\s+', ' ', doc_text).strip()
            
            metadata = {
                'format': 'docx',
                'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
                'file_count': len(file_list),
                'xml_files': content_types
            }
            
            # Create text content
            if doc_text:
                text = doc_text
            else:
                text = "[DOCX Content Extraction Placeholder]\n\n"
                text += f"This is a DOCX document with {len(file_list)} internal files.\n"
                text += "In a full implementation, text would be extracted using a DOCX parsing library.\n"
            
            # Create sections
            sections = [{
                'type': 'document_content',
                'content': text
            }]
            
            return text, metadata, sections
            
        except zipfile.BadZipFile:
            logger.warning("DOCX parsing failed: Not a valid DOCX file")
            return "[Invalid DOCX file]", {'format': 'docx', 'is_valid': False}, []
    
    def _parse_xlsx(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse XLSX content.
        
        Args:
            data: The XLSX binary data.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        # Note: In a real implementation, use a proper XLSX parsing library like openpyxl
        # This is a placeholder implementation
        
        # We can extract some basic info from the XLSX (which is a ZIP file)
        try:
            xlsx_file = BytesIO(data)
            with zipfile.ZipFile(xlsx_file) as zip_ref:
                file_list = zip_ref.namelist()
                
                # Extract sheet names if possible
                sheets = []
                for filename in file_list:
                    if filename.startswith('xl/worksheets/sheet') and filename.endswith('.xml'):
                        sheet_name = filename.split('/')[-1].replace('.xml', '')
                        sheets.append(sheet_name)
            
            metadata = {
                'format': 'xlsx',
                'content_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                'file_count': len(file_list),
                'sheets': sheets
            }
            
            # Create placeholder text
            text = "[XLSX Content Extraction Placeholder]\n\n"
            text += f"This is an XLSX document with {len(sheets)} sheets.\n"
            text += "In a full implementation, text would be extracted using an XLSX parsing library.\n"
            
            # Create sections
            sections = []
            for sheet in sheets:
                sections.append({
                    'type': 'spreadsheet',
                    'sheet_name': sheet,
                    'content': f"Content from sheet {sheet}"
                })
            
            return text, metadata, sections
            
        except zipfile.BadZipFile:
            logger.warning("XLSX parsing failed: Not a valid XLSX file")
            return "[Invalid XLSX file]", {'format': 'xlsx', 'is_valid': False}, []
    
    def _parse_zip(self, data: bytes, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
        """
        Parse ZIP content.
        
        Args:
            data: The ZIP binary data.
            options: Parsing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
        """
        try:
            zip_file = BytesIO(data)
            with zipfile.ZipFile(zip_file) as zip_ref:
                file_list = zip_ref.namelist()
                
                # Get file sizes
                file_sizes = {name: zip_ref.getinfo(name).file_size for name in file_list}
                
                # Extract up to max_files text files for preview
                max_files = options.get('max_files', 5)
                max_size = options.get('max_size', 10240)  # 10 KB per file
                
                text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html']
                text_files = [name for name in file_list 
                             if any(name.lower().endswith(ext) for ext in text_extensions)
                             and file_sizes[name] <= max_size]
                
                # Sample a few files for preview
                sample_files = text_files[:max_files]
                
                # Extract sample content
                sample_contents = {}
                for name in sample_files:
                    content = zip_ref.read(name)
                    try:
                        # Try to decode as UTF-8, fallback to latin1
                        sample_contents[name] = content.decode('utf-8', errors='replace')
                    except UnicodeDecodeError:
                        sample_contents[name] = "[Binary content]"
            
            # Create metadata
            metadata = {
                'format': 'zip',
                'content_type': 'application/zip',
                'file_count': len(file_list),
                'directory_count': sum(1 for name in file_list if name.endswith('/')),
                'total_size': sum(file_sizes.values())
            }
            
            # Create human-readable text
            text = f"ZIP Archive with {len(file_list)} files\n\n"
            text += "File listing:\n"
            
            # List all files (or at least the first 50)
            for i, name in enumerate(sorted(file_list)[:50]):
                text += f"- {name} ({file_sizes[name]} bytes)\n"
            
            if len(file_list) > 50:
                text += f"... and {len(file_list) - 50} more files\n"
            
            text += "\nSample content:\n"
            for name, content in sample_contents.items():
                text += f"\n--- {name} ---\n"
                # Show first 1000 chars of each file
                text += content[:1000]
                if len(content) > 1000:
                    text += "...[truncated]..."
            
            # Create sections
            sections = [{
                'type': 'file_list',
                'content': file_list
            }]
            
            for name, content in sample_contents.items():
                sections.append({
                    'type': 'file_content',
                    'filename': name,
                    'content': content[:1000]
                })
            
            return text, metadata, sections
            
        except zipfile.BadZipFile:
            logger.warning("ZIP parsing failed: Not a valid ZIP file")
            return "[Invalid ZIP file]", {'format': 'zip', 'is_valid': False}, []


# Global application handler instance
application_handler = ApplicationHandler()