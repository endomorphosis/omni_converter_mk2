"""
Base processor interfaces for format handlers.

This module provides the base interfaces for processors using the strategy pattern
to enable inversion of control in format handlers.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Tuple, Optional, BinaryIO

class BaseProcessor(ABC):
    """
    Base interface for all format processors.
    
    This abstract class defines the common interface that all format processors must implement.
    It follows the strategy pattern to enable inversion of control in format handlers.
    """
    
    @abstractmethod
    def can_process(self, format_name: str) -> bool:
        """
        Check if this processor can handle the given format.
        
        Args:
            format_name: The name of the format to check.
            
        Returns:
            True if this processor can handle the format, False otherwise.
        """
        pass
    
    @abstractmethod
    def supported_formats(self) -> List[str]:
        """
        Get the list of formats supported by this processor.
        
        Returns:
            A list of format names supported by this processor.
        """
        pass
    
    @abstractmethod
    def get_processor_info(self) -> Dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            A dictionary containing information about this processor, such as name, version,
            supported formats, and any other relevant metadata.
        """
        pass