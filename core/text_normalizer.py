"""
Text normalizer module for the Omni-Converter.

This module provides the TextNormalizer class for normalizing text content.
"""

import re
from typing import Any, Callable, Dict, List, Optional, Union

from format_handlers.base_handler import Content
from utils.logger import logger


class NormalizedContent(Content):
    """
    Normalized content from a file.
    
    This class extends the base Content class with normalization metadata.
    
    Attributes:
        normalized_by (List[str]): List of normalizers applied to the content.
    """
    
    def __init__(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        sections: Optional[List[Dict[str, Any]]] = None,
        source_format: Optional[str] = None,
        source_path: Optional[str] = None,
        normalized_by: Optional[List[str]] = None
    ):
        """
        Initialize normalized content.
        
        Args:
            text: The normalized text content.
            metadata: Metadata about the content.
            sections: Sections of the content (if applicable).
            source_format: The format of the source file.
            source_path: The path to the source file.
            normalized_by: List of normalizers applied to the content.
        """
        super().__init__(text, metadata, sections, source_format, source_path)
        self.normalized_by = normalized_by or []
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the normalized content.
        """
        result = super().to_dict()
        result['normalized_by'] = self.normalized_by
        return result


# Type for normalizer functions
NormalizerFunc = Callable[[str], str]


class TextNormalizer:
    """
    Text normalizer for the Omni-Converter.
    
    This class normalizes text content by applying various normalization functions.
    
    Attributes:
        normalizers (Dict[str, NormalizerFunc]): Dictionary of normalizer functions.
    """
    
    def __init__(self):
        """Initialize a text normalizer."""
        self.normalizers: Dict[str, NormalizerFunc] = {}
        
        # Register default normalizers
        self._register_default_normalizers()
    
    def _register_default_normalizers(self) -> None:
        """Register the default text normalizers."""
        self.register_normalizer("whitespace", self._normalize_whitespace)
        self.register_normalizer("line_endings", self._normalize_line_endings)
        self.register_normalizer("empty_lines", self._normalize_empty_lines)
        self.register_normalizer("unicode", self._normalize_unicode)
    
    def _normalize_whitespace(self, text: str) -> str:
        """
        Normalize whitespace in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace tabs with spaces
        text = text.replace("\t", "    ")
        
        # Replace multiple spaces with a single space
        text = re.sub(r" {2,}", " ", text)
        
        return text
    
    def _normalize_line_endings(self, text: str) -> str:
        """
        Normalize line endings in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace all types of line endings with Unix-style line endings
        text = text.replace("\r\n", "\n")
        text = text.replace("\r", "\n")
        
        return text
    
    def _normalize_empty_lines(self, text: str) -> str:
        """
        Normalize empty lines in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace three or more consecutive newlines with two newlines
        text = re.sub(r"\n{3,}", "\n\n", text)
        
        return text
    
    def _normalize_unicode(self, text: str) -> str:
        """
        Normalize Unicode characters in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace non-breaking spaces with regular spaces
        text = text.replace("\u00A0", " ")
        
        # Replace various dash characters with a standard dash
        text = re.sub(r"[\u2012-\u2015]", "-", text)
        
        # Replace various quote characters with standard quotes
        text = re.sub(r"[\u2018\u2019]", "'", text)
        text = re.sub(r"[\u201C\u201D]", '"', text)
        
        return text
    
    def normalize_text(self, content: Content, normalizers: Optional[List[str]] = None) -> NormalizedContent:
        """
        Normalize text content.
        
        Args:
            content: The content to normalize.
            normalizers: List of normalizer names to apply. If None, all normalizers are applied.
            
        Returns:
            The normalized content.
            
        Raises:
            ValueError: If an unknown normalizer is specified.
        """
        logger.debug(f"Normalizing text from {content.source_path}", {'format': content.source_format})
        
        # If no normalizers are specified, use all of them
        if normalizers is None:
            normalizers = list(self.normalizers.keys())
        
        # Check for unknown normalizers
        unknown_normalizers = [n for n in normalizers if n not in self.normalizers]
        if unknown_normalizers:
            raise ValueError(f"Unknown normalizers: {', '.join(unknown_normalizers)}")
        
        # Apply each normalizer in sequence
        text = content.text
        applied_normalizers = []
        
        for name in normalizers:
            normalizer = self.normalizers.get(name)
            if normalizer:
                text = normalizer(text)
                applied_normalizers.append(name)
                logger.debug(f"Applied normalizer: {name}")
        
        # Create normalized content
        return NormalizedContent(
            text=text,
            metadata=content.metadata,
            sections=content.sections,
            source_format=content.source_format,
            source_path=content.source_path,
            normalized_by=applied_normalizers
        )
    
    def register_normalizer(self, name: str, normalizer: NormalizerFunc) -> None:
        """
        Register a normalizer.
        
        Args:
            name: The name of the normalizer.
            normalizer: The normalizer function.
            
        Raises:
            ValueError: If a normalizer with the same name already exists.
        """
        if name in self.normalizers:
            raise ValueError(f"A normalizer with the name '{name}' already exists")
        
        self.normalizers[name] = normalizer
        logger.debug(f"Registered normalizer: {name}")
    
    def get_applied_normalizers(self) -> List[str]:
        """
        Get the names of all registered normalizers.
        
        Returns:
            List of normalizer names.
        """
        return list(self.normalizers.keys())