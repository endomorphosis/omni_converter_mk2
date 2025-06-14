"""
Centralized type-shed for the program.
Includes built-in types, custom types, and type aliases.

Made because there are too many types to keep track of in the main codebase,
and I want to keep it clean, readable, and un-import-error-able.
"""
from __future__ import annotations

import logging
from types import ModuleType
from typing import (
    Any, Callable, Optional,
    Protocol, TYPE_CHECKING,
    TypeAlias, TypedDict, 
    TypeVar, Union
)

try:
    from pydantic import BaseModel
except ImportError:
    raise ImportError("Critical dependency Pydantic is not installed.")

if TYPE_CHECKING:
    from batch_processor._batch_processor import BatchProcessor
    #from configs import Configs
    from core._pipeline_status import PipelineStatus
    from core._processing_pipeline import ProcessingPipeline
    from core._processing_result import ProcessingResult
    #from core.content_extractor.content import Content # TODO
    #from core.text_normalizer._normalized_content import NormalizedContent
    from dependencies import _Dependencies as Dependencies
    from external_programs import ExternalPrograms
    from file_format_detector._file_format_detector import FileFormatDetector
    from monitors._resource_monitor import ResourceMonitor
    from monitors.security_monitor._security_monitor import SecurityMonitor
    #from monitors.security_monitor._security_result import SecurityResult


Content = TypeVar('Content')
FormatterFunc: TypeAlias = Callable[[Content], str]
FormattedOutput: TypeAlias = Content
NormalizedContent = TypeVar('NormalizedContent', bound=str)
FileFormatDetector = TypeVar('FileFormatDetector', bound=ModuleType)

Logger: TypeAlias = logging.Logger
Dependency: TypeAlias = ModuleType
BuiltinModule: TypeAlias = ModuleType
NormalizerFunc: TypeAlias = Callable[[str], str]
StatusListenerFunc: TypeAlias = Callable[[str], None]
ProgressCallback: TypeAlias = Callable[[int, int, str], None]

SecurityResult: TypeAlias = BaseModel
BatchResult = TypeVar("BatchResult", bound=dict[str, Any])
SanitizedContent = TypeVar("SanitizedContent", bound=str)

# Interfaces
PythonAPI = TypeVar('PythonAPI')
Cli = TypeVar('CLI')
Gui = TypeVar('GUI')
Configs = TypeVar('Configs')
