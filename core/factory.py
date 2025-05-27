"""
Factory module for creating core processing components.

This module provides factory functions for creating core components and assembling
them into a processing pipeline. It centralizes the creation of these components
and manages their dependencies following the IoC pattern.
"""

from typing import Any, Dict, Optional

from configs import Configs
from logger import logger


def create_format_detector(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create a FormatDetector instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of FormatDetector.
    """
    # Import here to avoid circular imports
    from core.format_detector import FormatDetector
    from utils.constants import FORMAT_SIGNATURES, FORMAT_EXTENSIONS
    
    # Create resources dictionary
    detector_resources = {
        "format_signatures": FORMAT_SIGNATURES,
        "format_extensions": FORMAT_EXTENSIONS,
    }
    
    # Add any additional resources
    if resources:
        detector_resources.update(resources)
    
    # Use provided configs or default
    detector_configs = configs or globals()['configs']
    
    return FormatDetector(resources=detector_resources, configs=detector_configs)


def create_validator(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create a BasicValidator instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of BasicValidator.
    """
    # Import here to avoid circular imports
    from core.validator import BasicValidator
    from core.validation_result import ValidationResult
    from utils.filesystem import FileSystem
    
    # Create format detector dependency
    format_detector = create_format_detector(resources, configs)
    
    # Create resources dictionary
    validator_resources = {
        "file_exists": FileSystem.file_exists,
        "get_file_info": FileSystem.get_file_info,
        "validation_result": ValidationResult,
        "format_detector": format_detector,
    }
    
    # Add any additional resources
    if resources:
        validator_resources.update(resources)
    
    # Use provided configs or default
    validator_configs = configs or globals()['configs']
    
    return BasicValidator(resources=validator_resources, configs=validator_configs)


def create_content_extractor(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create a ContentExtractor instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of ContentExtractor.
    """
    # Import here to avoid circular imports
    from core.content_extractor import ContentExtractor
    from format_handlers.format_registry import create_format_registry
    
    # Create resources dictionary
    extractor_resources = {
        "registry": create_format_registry(),
    }
    
    # Add any additional resources
    if resources:
        extractor_resources.update(resources)
    
    # Use provided configs or default
    extractor_configs = configs or globals()['configs']
    
    return ContentExtractor(resources=extractor_resources, configs=extractor_configs)


def create_text_normalizer(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create a TextNormalizer instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of TextNormalizer.
    """
    # Import here to avoid circular imports
    from core.text_normalizer import TextNormalizer
    
    # Create resources dictionary
    normalizer_resources = {}
    
    # Add any additional resources
    if resources:
        normalizer_resources.update(resources)
    
    # Use provided configs or default
    normalizer_configs = configs or globals()['configs']
    
    return TextNormalizer(resources=normalizer_resources, configs=normalizer_configs)


def create_output_formatter(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create an OutputFormatter instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of OutputFormatter.
    """
    # Import here to avoid circular imports
    from core.output_formatter import OutputFormatter
    from core.text_normalizer import NormalizedContent
    
    # Create resources dictionary
    formatter_resources = {
        "normalized_content": NormalizedContent,
    }
    
    # Add any additional resources
    if resources:
        formatter_resources.update(resources)
    
    # Use provided configs or default
    formatter_configs = configs or globals()['configs']
    
    return OutputFormatter(resources=formatter_resources, configs=formatter_configs)


def create_processing_result():
    """
    Factory function to create a ProcessingResult class reference.
    
    Returns:
        The ProcessingResult class for instantiation.
    """
    # Import here to avoid circular imports
    from core.processing_result import ProcessingResult
    
    return ProcessingResult

def create_pipeline_status():
    """
    Factory function to create a PipelineStatus class reference.
    
    Returns:
        The PipelineStatus instance.
    """
    # Import here to avoid circular imports
    from core.pipeline_status import PipelineStatus
    
    return PipelineStatus()

def create_processing_pipeline(resources: Optional[Dict[str, Any]] = None, configs: Optional[Configs] = None):
    """
    Factory function to create a ProcessingPipeline instance.
    
    Args:
        resources: Additional resources to provide.
        configs: Configuration settings.
        
    Returns:
        An instance of ProcessingPipeline.
    """
    # Import here to avoid circular imports
    from core.processing_pipeline import ProcessingPipeline
    from core.pipeline_status import PipelineStatus
    
    # Create core components
    detector = create_format_detector(resources, configs)
    validator = create_validator(resources, configs)
    extractor = create_content_extractor(resources, configs)
    normalizer = create_text_normalizer(resources, configs)
    formatter = create_output_formatter(resources, configs)
    processing_result = create_processing_result()
    pipeline_status = create_pipeline_status()

    # Create resources dictionary
    pipeline_resources = {
        "detector": detector,
        "validator": validator,
        "extractor": extractor,
        "normalizer": normalizer,
        "formatter": formatter,
        "processing_result": processing_result,
        "pipeline_status": pipeline_status,
    }
    
    # Add any additional resources
    if resources:
        pipeline_resources.update(resources)
    
    # Use provided configs or default
    pipeline_configs = configs or globals()['configs']
    
    return ProcessingPipeline(resources=pipeline_resources, configs=pipeline_configs)


# Global processing pipeline instance
processing_pipeline = create_processing_pipeline()