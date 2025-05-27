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
- Video Processor: Implementation for video thumbnail extraction and frame processing
"""

# Import processors for easy access
try:
    from format_handlers.processors.by_mime_type.pdf_processor import pdf_processor
except ImportError:
    pass

try:
    from format_handlers.processors.python_docx_processor import docx_processor
except ImportError:
    pass

try:
    from deprecated.processors.xlsx_processor import xlsx_processor
except ImportError:
    pass

try:
    from format_handlers.processors.by_ability.audio_processor import whisper_processor
except ImportError:
    pass

try:
    from format_handlers.processors.by_ability.ocr_processor import ocr_processor
except ImportError:
    pass
    
try:
    from format_handlers.processors.by_ability.video_processor import video_processor
except ImportError:
    pass