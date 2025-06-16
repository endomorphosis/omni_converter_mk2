"""
Centralized type-shed for the program.
Includes built-in types, custom types, and type aliases.

Made because there are too many types to keep track of in the main codebase,
and I want to keep it clean, readable, and un-import-error-able.
"""
from __future__ import annotations

import logging
from unittest.mock import MagicMock, Mock
from types import ModuleType
from typing import (
    Any, Callable, Optional,
    Protocol, TYPE_CHECKING,
    TypeAlias, TypedDict, 
    TypeVar, Union,
)
from protocols import Processor

try:
    from pydantic import BaseModel
except ImportError:
    raise ImportError("Critical dependency Pydantic is not installed.")

if TYPE_CHECKING:
    pass
    # #from configs import Configs
    # from core._pipeline_status import PipelineStatus
    # from core._processing_pipeline import ProcessingPipeline
    # # from core._processing_result import ProcessingResult
    # #from core.content_extractor.content import Content # TODO
    # #from core.text_normalizer._normalized_content import NormalizedContent
    # from dependencies import _Dependencies as Dependencies
    # from external_programs import ExternalPrograms
    # from file_format_detector._file_format_detector import FileFormatDetector
    # from monitors._resource_monitor import ResourceMonitor
    # from monitors.security_monitor._security_monitor import SecurityMonitor
    # #from monitors.security_monitor._security_result import SecurityResult
    # from supported_formats import SupportedFormats

# Convert imports to TypeVars
PipelineStatus = TypeVar('PipelineStatus')
ProcessingPipeline = TypeVar('ProcessingPipeline')
Dependencies = TypeVar('Dependencies')
ExternalPrograms = TypeVar('ExternalPrograms')
FileFormatDetector = TypeVar('FileFormatDetector')
ResourceMonitor = TypeVar('ResourceMonitor')
SecurityMonitor = TypeVar('SecurityMonitor')
SupportedFormats = TypeVar('SupportedFormats')
FormatRegistry = TypeVar('FormatRegistry')


Content = TypeVar('Content')
FormatterFunc: TypeAlias = Callable[[Content], str]
FormattedOutput: TypeAlias = Content
NormalizedContent = TypeVar('NormalizedContent', bound=str)
FileFormatDetector = TypeVar('FileFormatDetector', bound=ModuleType)
SupportedFormats = TypeVar('SupportedFormats', bound=dict[str, Any])

Logger: TypeAlias = logging.Logger
Dependency: TypeAlias = ModuleType
BuiltinModule: TypeAlias = ModuleType
Configs: TypeAlias = BaseModel


NormalizerFunc: TypeAlias = Callable[[str], str]
StatusListenerFunc: TypeAlias = Callable[[str], None]
ProgressCallback: TypeAlias = Callable[[int, int, str], None]
ProcessingResult: TypeAlias = Any # Dataclass
SecurityResult: TypeAlias = BaseModel
ProcessingPipeline: TypeAlias = Any # Dataclass
BatchResult = TypeVar("BatchResult", bound=dict[str, Any])
SanitizedContent = TypeVar("SanitizedContent", bound=str)
BatchProcessor = TypeVar("BatchProcessor")
ContentExtractor = TypeVar("ContentExtractor", bound=Callable[..., Any])

AbilityProcessor = TypeVar("AbilityProcessor", bound=Callable[..., Any])

# NOTE This is placeholder used to represent objects that are specific to a dependency
# Ex: DataFrames from Pandas, or Numpy arrays
# We do this because we don't know which dependencies will be used for any given processor.
DependencySpecificObject = TypeVar("DependencyObject", bound=Callable[..., Any])

# Interfaces
PythonAPI = TypeVar('PythonAPI')
Cli = TypeVar('CLI')
Gui = TypeVar('GUI')
Configs = TypeVar('Configs')
