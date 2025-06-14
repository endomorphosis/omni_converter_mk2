"""
Factory module for creating ProcessingPipeline instances.

This module provides the factory function for creating ProcessingPipeline instances
following the IoC pattern.
"""
from configs import configs
from logger import logger
from file_format_detector import make_file_format_detector

from types_ import Callable, Logger, TypedDict

from ._processing_pipeline import ProcessingPipeline
from ._pipeline_status import PipelineStatus
from ._processing_result import ProcessingResult
from .file_validator import make_file_validator
from .text_normalizer import make_text_normalizer
from .output_formatter import make_output_formatter
from .content_extractor import make_content_extractor


def make_processing_pipeline() -> ProcessingPipeline:
    """
    Factory function to create a ProcessingPipeline instance.
    
    Returns:
        An instance of ProcessingPipeline configured with proper dependencies.
    """
    class _ProcessingPipelineResources(TypedDict):
        file_format_detector: Callable
        file_validator: Callable
        content_extractor: Callable
        text_normalizer: Callable
        output_formatter: Callable
        processing_result: ProcessingResult
        pipeline_status: PipelineStatus
        logger: Logger

    resources: _ProcessingPipelineResources = {
        "file_format_detector": make_file_format_detector(),
        "file_validator": make_file_validator(),
        "content_extractor": make_content_extractor(),  # TODO: Add when content_extractor factory is available
        "text_normalizer": make_text_normalizer(),
        "output_formatter": make_output_formatter(),
        "processing_result": ProcessingResult,
        "pipeline_status": PipelineStatus(),
        "logger": logger,
    }
    return ProcessingPipeline(resources=resources, configs=configs)
