"""
Application format handlers for the Omni-Converter using IoC pattern.

This module provides handlers for application-based formats like PDF, JSON, DOCX, XLSX, and ZIP
using dependency injection for better modularity and testability, without inheritance.
"""

import json
import zipfile
from io import BytesIO
import re
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from utils.filesystem import FileSystem
from configs import Configs
from logger import logger
from format_handlers.unified_handler import BaseFormatHandler, Content, create_handler, map_extension_to_format
from format_handlers.constants import Constants
from core.format_detector import format_detector


def create_application_handler(resources: Dict[str, Any], configs: Optional[Configs] = None) -> BaseFormatHandler:
    """
    Create an application handler instance with injected dependencies.
    
    Args:
        resources: Resources dictionary with dependencies.
            Must contain:
            - pdf_processor: PDF processor for PDF files
            - docx_processor: DOCX processor for DOCX files  
            - xlsx_processor: XLSX processor for XLSX files
        configs: Configuration settings.
        
    Returns:
        BaseFormatHandler instance configured for application formats.
    """
    constants = resources["constants"]

    # Format-specific file extensions # TODO These should be in constants.
    format_extensions = {
        'pdf': ['.pdf'],
        'json': ['.json', '.jsonl'],
        'docx': ['.docx'],
        'xlsx': ['.xlsx'],
        'zip': ['.zip']
    }
    
    # Prepare parsers with the appropriate functions
    parsers = {
        "application": {
            "pdf": process_pdf,
            "json": process_json,
            "docx": process_docx,
            "xlsx": process_xlsx,
            "zip": process_zip
        }
    }
    
    # Additional resources specific to application handling
    application_resources = {
        "format_extensions": format_extensions
    }
    
    # Create and return the handler
    return create_handler(
        handler_name="ApplicationHandler",
        format_detector=format_detector,
        ext_to_format=map_extension_to_format,
        supported_formats=Constants.SUPPORTED_APPLICATION_FORMATS_SET,
        capabilities=Constants.APPLICATION_HANDLER_CAPABILITIES,
        parsers=parsers,
        resources_extra=application_resources,
        configs=configs
    )


def process_pdf(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a PDF file and extract content.
    
    Args:
        file_content: The file content to process (binary data).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the PDF file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use pdf_processor if available
    pdf_processor = options.get("pdf_processor")
    if pdf_processor and pdf_processor.can_process("pdf"):
        return pdf_processor.process_document(file_content.as_binary, options)
    
    # If no processor available, raise error since PDF is complex
    logger.warning("PDF processor not available, cannot process PDF files")
    raise ValueError("PDF processing is not available")


def process_json(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a JSON file and extract content.
    
    Args:
        file_content: The file content to process (binary data).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the JSON file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"] # TODO Unused variable.
    
    # Process JSON data directly since it doesn't require external dependencies
    try:
        # Decode JSON data
        json_text = file_content.as_binary.decode('utf-8')
        json_data: str = json.loads(json_text)
        
        # Extract metadata
        metadata = {
            'format': 'json',
            'content_type': 'application/json',
            'structure_type': 'object' if isinstance(json_data, dict) else 'array',
            'top_level_keys': list(json_data.keys()) if isinstance(json_data, dict) else [],
            'file_size_bytes': len(file_content.as_binary)
        }
        
        # Format JSON as plain text
        formatted_json = json.dumps(json_data, indent=2)
        
        # Create sections based on JSON structure
        sections = []
        match json_data:
            case dict():
                for key, value in json_data.items():
                    sections.append({
                        'type': 'json_field',
                        'field_name': key,
                        'content': str(value)
                    })
            case list():
                for i, item in enumerate(json_data):
                    sections.append({
                        'type': 'json_item',
                        'index': i,
                        'content': str(item)
                    })
            case _:
                raise TypeError(f"Unsupported JSON structure: {type(json_data).__name__}")

        return formatted_json, metadata, sections

    except (UnicodeDecodeError, json.JSONDecodeError) as e:
        logger.warning(f"JSON parsing failed: {e}")
        return f"[Invalid JSON: {e}]", {'format': 'json', 'is_valid': False}, []


def process_docx(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a DOCX file and extract content.
    
    Args:
        file_content: The file content to process (binary data).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the DOCX file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use docx_processor if available
    docx_processor = options.get("docx_processor")
    if docx_processor and docx_processor.can_process("docx"):
        return docx_processor.process_document(file_content.as_binary, options)
    
    # Fallback to basic ZIP-based extraction if python-docx is not available # TODO Fallback should be in a separate function.
    logger.warning("DOCX processor not available, using basic ZIP-based extraction")
    try:
        docx_file = BytesIO(file_content.as_binary)
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
                # Simplified XML content extraction
                doc_text = doc_content.decode('utf-8', errors='ignore')
                doc_text = doc_text.replace('<w:p>', '\n\n').replace('<w:t>', ' ').replace('</w:t>', '')
                # Remove all XML tags
                doc_text = re.sub(r'<[^>]+>', '', doc_text)
                # Normalize whitespace
                doc_text = re.sub(r'\s+', ' ', doc_text).strip()
        
        metadata = {
            'format': 'docx',
            'content_type': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'file_count': len(file_list),
            'xml_files': content_types,
            'file_size_bytes': len(file_content.as_binary)
        }
        
        # Create text content
        if doc_text:
            text = doc_text
        else:
            text = "[DOCX Content Extraction Placeholder]\n\n"
            text += f"This is a DOCX document with {len(file_list)} internal files.\n"
            text += "For better results, install python-docx.\n"
        
        # Create sections
        sections = [{
            'type': 'document_content',
            'content': text
        }]
        
        return text, metadata, sections
        
    except zipfile.BadZipFile:
        logger.warning("DOCX parsing failed: Not a valid DOCX file")
        return "[Invalid DOCX file]", {'format': 'docx', 'is_valid': False}, []


def process_xlsx(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process an XLSX file and extract content.
    
    Args:
        file_content: The file content to process (binary data).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the XLSX file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    # Use xlsx_processor if available
    xlsx_processor = options.get("xlsx_processor")
    if xlsx_processor and xlsx_processor.can_process("xlsx"):
        return xlsx_processor.process_document(file_content.as_binary, options)
    
    # Fallback to basic ZIP-based extraction if openpyxl is not available # TODO Fallback should be in a separate function.
    logger.warning("XLSX processor not available, using basic ZIP-based extraction")
    try:
        xlsx_file = BytesIO(file_content.as_binary)
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
            'sheets': sheets,
            'file_size_bytes': len(file_content.as_binary)
        }
        
        # Create placeholder text # TODO There needs to be SOME attempt at extracting content here.
        text = "[XLSX Content Extraction Placeholder]\n\n"
        text += f"This is an XLSX document with {len(sheets)} sheets.\n"
        text += "For better results, install openpyxl.\n"
        
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


def process_zip(file_content: Any, options: Dict[str, Any]) -> Tuple[str, Dict[str, Any], List[Dict[str, Any]]]:
    """
    Process a ZIP file and extract content.
    
    Args:
        file_content: The file content to process (binary data).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the ZIP file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        ValueError: If the file format is not supported.
        Exception: If an error occurs during processing.
    """
    # Extract key information from the options
    file_path = options["file_path"]
    
    try:
        zip_file = BytesIO(file_content.as_binary)
        with zipfile.ZipFile(zip_file) as zip_ref:
            file_list = zip_ref.namelist()
            
            # Get file sizes
            file_sizes = {name: zip_ref.getinfo(name).file_size for name in file_list}
            
            # Extract up to max_files text files for preview
            max_files = options.get('max_files', 5) # TODO This is a magic number, and should be in constants.
            max_size = options.get('max_size', 10240)  # 10 KB per file # TODO This is a magic number, and should be in constants.
            
            text_extensions = ['.txt', '.md', '.csv', '.json', '.xml', '.html'] # TODO These should be in constants.
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
            'total_size': sum(file_sizes.values()),
            'file_size_bytes': len(file_content.as_binary)
        }
        
        # Create human-readable text
        text = f"ZIP Archive with {len(file_list)} files\n\n"
        text += "File listing:\n"
        
        # List all files (or at least the first 50) # TODO '50' is a magic number, and should be in constants.
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