"""
Interfaces package for the Omni-Converter.

This package contains the interfaces used by the Omni-Converter, including:
- Python API for programmatic access
- Configuration manager for handling settings
"""
from interfaces.interface_factory import interface_factory

from configs import configs as _configs
from .python_api import PythonAPI
from .cli import CLI



__all__ = [
    "python_api",
    "cli,"
    "PythonAPI", # For type hinting and documentation purposes
    "CLI", # For type hinting and documentation purposes
]
