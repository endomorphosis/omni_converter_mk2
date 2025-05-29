"""
Custom Types for the program.

Made because I there are too many types to keep track of in the main codebase,
and I want to keep the main codebase clean and readable.

"""
from typing import Any, Callable, Optional, TypeVar, Union
import logging





# from main directory
from configs import Configs as _Configs
from dependencies import Dependencies as _Dependencies
from external_programs import ExternalPrograms as _ExternalPrograms


Configs = TypeVar("Configs", bound=_Configs)
Logger = TypeVar("Logger", bound=logging.Logger)
Dependencies = TypeVar("Dependencies", bound=_Dependencies)
ExternalPrograms = TypeVar("ExternalPrograms", bound=_ExternalPrograms)


# from core/ directory
from core.processing_pipeline.pipeline_status import PipelineStatus as _PipelineStatus
from core.content_extractor.content import Content as _Content # TODO

from core.processing_pipeline.processing_result import ProcessingResult as _ProcessingResult

StatusListenerFunc = Callable[[str, dict[str, Any]], None]
PipelineStatus = TypeVar("PipelineStatus", bound=_PipelineStatus)
ProcessingResult = TypeVar("ProcessingResult", bound=_ProcessingResult)

Content = TypeVar("Content", bound=_Content)

# Text Normalizer
from core.text_normalizer._normalized_content import NormalizedContent as _NormalizedContent
NormalizedContent = TypeVar("NormalizedContent", bound=_NormalizedContent)
NormalizerFunc = Callable[[str], str]

# Batch Processing
ProgressCallback = Callable[[int, int, str], None]

# Security Monitor

SecurityResult = TypeVar("SecurityResult", bound=dict[str, Any])
SanitizedContent = TypeVar("SanitizedContent", bound=str)

# Batch Processing
BatchResult = TypeVar("BatchResult", bound=dict[str, Any])


# Type for formatter functions
FormatterFunc = Callable[[Content], str]
FormattedOutput = TypeVar("FormattedOutput", bound=Content)

# Interfaces
DataClass = TypeVar('DataClass')
PythonAPI = TypeVar('PythonAPI') # Avoid having an extra import just for type hinting
Cli = TypeVar('CLI') # Avoid having an extra import just for type hinting