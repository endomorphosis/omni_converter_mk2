"""
Text normalizer module for the Omni-Converter.

This module provides the TextNormalizer class for normalizing text content.
"""
import re
from types_ import Any, Callable, Configs, Content, Logger, NormalizedContent, NormalizerFunc, Optional


class TextNormalizer:
    """
    Text normalizer for the Omni-Converter.
    
    This class normalizes text content by applying various normalization functions.
    
    Attributes:
        normalizers (dict[str, NormalizerFunc]): Dictionary of normalizer functions.
    """

    def __init__(self, 
                 resources: dict[str, Any] = None, 
                 configs: 'Configs' = None
                 ):
        """
        Initialize a text normalizer.
        
        Args:
            resources: A dictionary of callable objects and dependencies.
            configs: A pydantic model containing configuration settings.
        """
        self.resources = resources
        self.configs = configs

        self._normalized_content: NormalizedContent = self.resources["normalized_content"]

        self._logger: Logger = self.resources["logger"]
        self.normalizers: dict[str, NormalizerFunc] = {}
        
        # Register default normalizers
        self._register_default_normalizers()
    
    def _register_default_normalizers(self) -> None:
        """Register the default text normalizers."""
        self.register_normalizer("whitespace", self._normalize_whitespace)
        self.register_normalizer("line_endings", self._normalize_line_endings)
        self.register_normalizer("empty_lines", self._normalize_empty_lines)
        self.register_normalizer("unicode", self._normalize_unicode)
    
    @staticmethod
    def _normalize_whitespace(text: str) -> str:
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
        return re.sub(r" {2,}", " ", text)
    
    @staticmethod
    def _normalize_line_endings(text: str) -> str:
        """
        Normalize line endings in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace all types of line endings with Unix-style line endings
        return text.replace("\r\n", "\n").replace("\r", "\n")
    
    @staticmethod
    def _normalize_empty_lines(text: str) -> str:
        """
        Normalize empty lines in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace three or more consecutive newlines with two newlines
        return re.sub(r"\n{3,}", "\n\n", text)
    
    @staticmethod
    def _normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters in text.
        
        Args:
            text: The text to normalize.
            
        Returns:
            The normalized text.
        """
        # Replace non-breaking spaces with regular spaces
        text = text.replace("\u00A0", " ")

        # Normalize various Unicode characters to their ASCII equivalents
        unicode_replacements = [
            # Dash characters
            (r"[\u2010-\u2015]", "-"),     # Hyphen, non-breaking hyphen, figure dash, en dash, em dash, horizontal bar
            (r"[\u2212]", "-"),            # Minus sign
            # Quote characters
            (r"[\u2018\u2019]", "'"),      # Left and right single quotation marks
            (r"[\u201A\u201B]", "'"),      # Single low-9 quotation mark, single high-reversed-9 quotation mark
            (r"[\u201C\u201D]", '"'),      # Left and right double quotation marks
            (r"[\u201E\u201F]", '"'),      # Double low-9 quotation mark, double high-reversed-9 quotation mark
            (r"[\u2039\u203A]", "'"),      # Single left and right-pointing angle quotation marks
            (r"[\u00AB\u00BB]", '"'),      # Left and right-pointing double angle quotation marks
            # Apostrophe variants
            (r"[\u02BC\u2032]", "'"),      # Modifier letter apostrophe, prime
            # Space characters
            (r"[\u2000-\u200A]", " "),     # Various space characters (en quad, em quad, thin space, etc.)
            (r"[\u202F\u205F]", " "),      # Narrow no-break space, medium mathematical space
            # Ellipsis
            (r"\u2026", "..."),            # Horizontal ellipsis
            # Bullet points
            (r"[\u2022\u2023\u2043]", "*"), # Bullet, triangular bullet, hyphen bullet
            # Mathematical symbols
            (r"\u00D7", "x"),              # Multiplication sign
            (r"\u00F7", "/"),              # Division sign
            # Currency symbols (convert to text representations)
            (r"\u00A3", "GBP "),           # Pound sign
            (r"\u00A5", "JPY "),           # Yen sign
            (r"\u20AC", "EUR "),           # Euro sign
        ]
        
        for pattern, repl in unicode_replacements:
            text = re.sub(pattern, repl, text)
        return text
    
    def normalize_text(self, content: 'Content', normalizers: Optional[list[str]] = None) -> 'NormalizedContent':
        """
        Normalize text content.
        
        Args:
            content: The content to normalize.
            normalizers: list of normalizer names to apply. If None, all normalizers are applied.
            
        Returns:
            The normalized content.
            
        Raises:
            ValueError: If an unknown normalizer is specified.
        """
        self._logger.debug(f"Normalizing text from {content.source_path}", {'format': content.source_format})
        
        # If no normalizers are specified, use all of them
        if normalizers is None:
            normalizers = list(self.normalizers.keys())
        
        # Check for unknown normalizers
        unknown_normalizers = [n for n in normalizers if n not in self.normalizers]
        if unknown_normalizers:
            raise ValueError(f"Unknown normalizers: {', '.join(unknown_normalizers)}")
        
        # Apply each normalizer in sequence
        text = content.text
        normalized_text = None
        applied_normalizers = []
        
        for name in normalizers:
            normalizer = self.normalizers.get(name)
            if normalizer:
                normalized_text = normalizer(text)
                applied_normalizers.append(name)
                self._logger.debug(f"Applied normalizer: {name}")

        content.text = normalized_text if normalized_text is not None else text
        
        # Create normalized content
        return self._normalized_content(
            content=content,
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
        self._logger.debug(f"Registered normalizer: {name}")

    @property
    def applied_normalizers(self) -> list[str]:
        """
        Get the names of all registered normalizers.
        
        Returns:
            list of normalizer names.
        """
        return list(self.normalizers.keys())
