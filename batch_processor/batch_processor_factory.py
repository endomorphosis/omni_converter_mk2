from logger import logger
from configs import configs
from core import make_processing_pipeline
from monitors import make_error_monitor, make_resource_monitor, make_security_monitor
from monitors._error_monitor import ErrorMonitor
from monitors._resource_monitor import ResourceMonitor
from monitors.security_monitor._security_monitor import SecurityMonitor
from core._processing_pipeline import ProcessingPipeline
from core._processing_result import ProcessingResult


from ._batch_processor import BatchProcessor
from ._batch_result import BatchResult


from types_ import Logger, TypedDict


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
        processing_pipeline: ProcessingPipeline
        error_monitor: ErrorMonitor
        resource_monitor: ResourceMonitor
        security_monitor: SecurityMonitor
        logger: Logger
        processing_result: ProcessingResult
        batch_result: BatchResult

    resources: _BatchProcessorResources = {
        'processing_pipeline': make_processing_pipeline(),
        'error_monitor': make_error_monitor(),
        'resource_monitor': make_resource_monitor(),
        'security_monitor': make_security_monitor(),
        "logger": logger,
        "processing_result": ProcessingResult,
        "batch_result": BatchResult,
    }
    return BatchProcessor(configs=configs, resources=resources)
