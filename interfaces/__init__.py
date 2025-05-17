"""
Interfaces package for the Omni-Converter.

This package contains the interfaces used by the Omni-Converter, including:
- Python API for programmatic access
- Configuration manager for handling settings
"""
from interfaces import (
    python_api,
    interface_factory
)

from .python_api import PythonAPI
from .interface_factory import Configs

__all__ = [
    "python_api",
    "interface_factory",
    "PythonAPI",
    "Configs"
]
