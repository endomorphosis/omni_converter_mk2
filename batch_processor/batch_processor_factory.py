from logger import logger
from configs import configs
from core import make_processing_pipeline

from .batch_processor import BatchProcessor

# Type for progress callback function

def make_batch_processor() -> BatchProcessor:
    """
    Create a BatchProcessor instance.

    Args:
        configs: Configuration settings.
        resources: Dictionary of resources to be used by the BatchProcessor.

    Returns:
        An instance of BatchProcessor.
    """
    resources = resources or {
        'processing_pipeline': make_processing_pipeline(),
        'error_monitor': None,  # Placeholder for error monitor
        'resource_monitor': None,  # Placeholder for resource monitor
        'security_monitor': None,  # Placeholder for security monitor
        "logger": logger,
    }

    return BatchProcessor(configs=configs, resources=resources)