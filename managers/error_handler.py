"""
Error handler module for the Omni-Converter.

This module provides the ErrorHandler class for centralizing error handling and reporting.
"""

import traceback
from typing import Any, Dict, List, Optional, Set, Type, Union

from utils.logger import logger


class ErrorHandler:
    """
    Error handler for the Omni-Converter.
    
    This class centralizes error handling and reporting, providing consistent
    error management across the application.
    
    Attributes:
        logger: The logger to use for error logging.
        error_counters (Dict[str, int]): Counters for different error types.
        error_types (Set[str]): Set of known error types.
        suppress_errors (bool): Whether to suppress errors.
    """
    
    def __init__(self, custom_logger=None, suppress_errors: bool = False):
        """
        Initialize an error handler.
        
        Args:
            custom_logger: Custom logger to use. If None, the global logger will be used.
            suppress_errors: Whether to suppress errors.
        """
        self.logger = custom_logger or logger
        self.error_counters: Dict[str, int] = {}
        self.error_types: Set[str] = set()
        self.suppress_errors = suppress_errors
    
    def handle_error(self, error: Union[Exception, str], context: Optional[Dict[str, Any]] = None) -> None:
        """
        Handle an error.
        
        Args:
            error: The error to handle.
            context: Additional context for the error.
        
        Returns:
            None
        
        Raises:
            Exception: If suppress_errors is False and error is an exception.
        """
        # Get error type
        error_type = type(error).__name__ if isinstance(error, Exception) else "StringError"
        
        # Update counters
        self.error_types.add(error_type)
        self.error_counters[error_type] = self.error_counters.get(error_type, 0) + 1
        
        # Log the error
        self.log_error(error, context)
        
        # Raise the error if not suppressing
        if not self.suppress_errors and isinstance(error, Exception):
            raise error
    
    def log_error(self, error: Union[Exception, str], context: Optional[Dict[str, Any]] = None) -> None:
        """
        Log an error.
        
        Args:
            error: The error to log.
            context: Additional context for the error.
        """
        # Create error message
        if isinstance(error, Exception):
            error_message = f"{type(error).__name__}: {str(error)}"
            error_traceback = traceback.format_exc()
        else:
            error_message = str(error)
            error_traceback = ""
        
        # Add context
        context = context or {}
        context["error_type"] = type(error).__name__ if isinstance(error, Exception) else "StringError"
        
        if error_traceback:
            context["traceback"] = error_traceback
        
        # Log the error
        self.logger.error(error_message, context)
    
    def get_error_statistics(self) -> Dict[str, Any]:
        """
        Get error statistics.
        
        Returns:
            A dictionary of error statistics.
        """
        return {
            "total_errors": sum(self.error_counters.values()),
            "error_types": list(self.error_types),
            "error_counts": self.error_counters.copy()
        }
    
    def reset_error_counters(self) -> None:
        """Reset error counters."""
        self.error_counters = {}
    
    def set_error_suppression(self, suppress: bool) -> None:
        """
        Set error suppression.
        
        Args:
            suppress: Whether to suppress errors.
        """
        self.suppress_errors = suppress
    
    def get_most_common_errors(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get the most common errors.
        
        Args:
            limit: Maximum number of errors to return.
            
        Returns:
            A list of dictionaries with error type and count.
        """
        # Sort error types by count (descending)
        sorted_errors = sorted(
            self.error_counters.items(),
            key=lambda x: x[1],
            reverse=True
        )
        
        # Return the top N errors
        return [
            {"type": error_type, "count": count}
            for error_type, count in sorted_errors[:limit]
        ]
    
    def has_errors(self) -> bool:
        """
        Check if any errors have been handled.
        
        Returns:
            True if errors have been handled, False otherwise.
        """
        return sum(self.error_counters.values()) > 0
    
    def get_error_count(self, error_type: Optional[Union[str, Type[Exception]]] = None) -> int:
        """
        Get the count of a specific error type or total errors.
        
        Args:
            error_type: The error type to get the count for. If None, total errors are returned.
            
        Returns:
            The count of the specified error type or total errors.
        """
        if error_type is None:
            return sum(self.error_counters.values())
        
        if isinstance(error_type, type) and issubclass(error_type, Exception):
            error_type = error_type.__name__
            
        return self.error_counters.get(error_type, 0)


# Global error handler instance
error_handler = ErrorHandler()