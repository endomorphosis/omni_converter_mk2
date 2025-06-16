from logger import logger
from configs import configs
from core import make_processing_pipeline
from monitors import make_error_monitor, make_resource_monitor, make_security_monitor

from ._batch_processor import BatchProcessor

from types_ import Any, Logger, TypedDict, ProcessingPipeline

from core._processing_result import ProcessingResult

def make_batch_processor() -> BatchProcessor:
    """Make a BatchProcessor instance.

    Returns:
        An instance of BatchProcessor.
    """

    class _BatchProcessorResources(TypedDict):
        """
        TypedDict for BatchProcessor resources.
        
        Attributes:
            processing_pipeline: Instance of ProcessingPipeline.
            error_monitor: Instance of ErrorMonitor.
            resource_monitor: Instance of ResourceMonitor.
            security_monitor: Instance of SecurityMonitor.
            logger: Logger instance.
        """
        # TODO typevar's won't cut it here, we need to import the actual classes.
        processing_pipeline: ProcessingPipeline
        error_monitor: Any  # Placeholder for actual type
        resource_monitor: Any  # Placeholder for actual type
        security_monitor: Any  # Placeholder for actual type
        logger: Logger
        processing_result: Any

    resources: _BatchProcessorResources = {
        'processing_pipeline': make_processing_pipeline(),
        'error_monitor': make_error_monitor(),  # Placeholder for error monitor
        'resource_monitor': make_resource_monitor(),  # Placeholder for resource monitor
        'security_monitor': make_security_monitor(),  # Placeholder for security monitor
        "logger": logger,
        "processing_result": ProcessingResult,
    }
    return BatchProcessor(configs=configs, resources=resources)
