"""
Core processing system for the Omni-Converter.

This package provides components for the core processing pipeline, including:
- Processing pipeline orchestration
- Format detection
- Content validation
- Content extraction
- Text normalization
- Output formatting

The core processing system is the heart of the Omni-Converter, handling the
conversion of input files to plaintext output.

Implementation Status:
    - ProcessingPipeline: ✅ Complete (IoC Pattern)
    - FormatDetector: ✅ Complete (IoC Pattern)
    - BasicValidator: ✅ Complete (IoC Pattern)
    - ContentExtractor: ✅ Complete (IoC Pattern)
    - TextNormalizer: ✅ Complete (IoC Pattern)
    - OutputFormatter: ✅ Complete (IoC Pattern)
"""

# Import only the processing pipeline from factory
from .factory import processing_pipeline

__all__ = [
    'processing_pipeline',
]
