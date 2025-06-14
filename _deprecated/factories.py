# """
# Factory module for creating core processing components.

# This module provides factory functions for creating core components and assembling
# them into a processing pipeline. It centralizes the creation of these components
# and manages their dependencies following the IoC pattern.
# """

# from typing import Any, Optional

# from configs import Configs
# from logger import logger


# from core.file_format_detector import make_file_format_detector

# # Import here to avoid circular imports
# from core.content_extractor.format_registry import make_format_registry
# from core.file_validator import make_file_validator


# # Individual module factories are now in their respective modules
# # Import them here for convenience


# def make_processing_pipeline():
#     """
#     Factory function to create a ProcessingPipeline instance.
    
#     Returns:
#         An instance of ProcessingPipeline.
#     """
#     # Import here to avoid circular imports
#     from core.processing_pipeline import make_processing_pipeline
    
#     return make_processing_pipeline()
