"""
Managers for the Omni-Converter.

This package provides manager classes for orchestrating and monitoring the conversion process,
including batch processing, resource monitoring, error handling, and security validation.

Modules:
    batch_processor: Orchestrates batch processing of multiple files.
    resource_monitor: Monitors and manages system resources during conversion.
    error_handler: Centralizes error handling and reporting.
    security_manager: Validates file security and implements content sanitization.
    batch_result: Tracks and reports results of batch processing operations.

Implementation Status:
    - BatchProcessor: ✅ Complete
    - ResourceMonitor: ✅ Complete
    - ErrorHandler: ✅ Complete
    - SecurityManager: ✅ Complete
    - BatchResult: ✅ Complete
"""

from managers import (
    batch_processor,
    resource_monitor,
    error_handler,
    security_manager,
    batch_result
)

from .batch_processor import BatchProcessor
from .resource_monitor import ResourceMonitor
from .error_handler import ErrorHandler
from .security_manager import SecurityManager
from .batch_result import BatchResult

__all__ = [
    "batch_processor",
    "resource_monitor",
    "error_handler",
    "security_manager",
    "batch_result",
    "BatchProcessor",
    "ResourceMonitor",
    "ErrorHandler",
    "SecurityManager",
    "BatchResult"
]