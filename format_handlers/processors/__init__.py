"""
Processor interfaces and implementations for format handlers.

This module provides the base interfaces and implementations for processors
that handle specific file formats using the strategy pattern for inversion of control.

Available processors:
- BaseProcessor: Base interface for all processors
- DocumentProcessor: Interface for document processors
- PDF Processor: Implementation using PyPDF2
- DOCX Processor: Implementation using python-docx
- XLSX Processor: Implementation using openpyxl
- Audio Processor: Implementation using Whisper for speech-to-text
- Image Processor: Interface for image processors
- OCR Processor: Implementation using PyTesseract for OCR
"""

# Import processors for easy access
try:
    from format_handlers.processors.pdf_processor import pdf_processor
except ImportError:
    pass

try:
    from format_handlers.processors.docx_processor import docx_processor
except ImportError:
    pass

try:
    from format_handlers.processors.xlsx_processor import xlsx_processor
except ImportError:
    pass

try:
    from format_handlers.processors.audio_processor import whisper_processor
except ImportError:
    pass

try:
    from format_handlers.processors.ocr_processor import ocr_processor
except ImportError:
    pass