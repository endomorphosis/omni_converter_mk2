from typing import Any

def _fixture_dict() -> dict[str, Any]:
    """
    Create a fixture dictionary for testing.

    Returns:
        A dictionary containing various test fixtures.
    """
    from core import make_processing_pipeline
    from batch_processor.factory import make_batch_processor
    from monitors import make_resource_monitor, make_error_monitor, make_security_monitor
    from file_format_detector import make_file_format_detector
    from core.file_validator.factory import FileValidator, make_file_validator
    from core.content_extractor.factory import ContentExtractor
    from logger import logger
    from configs import configs
    from dependencies import dependencies
    from external_programs import ExternalPrograms

    return {
        "processing_pipeline": make_processing_pipeline,
        "batch_processor": make_batch_processor,
        "file_format_detector": make_file_format_detector,
        "resource_monitor": make_resource_monitor,
        "security_monitor": make_security_monitor,  # Placeholder for security monitor
        "logger": logger,  # Placeholder for logger
        "error_monitor": make_error_monitor,  # Placeholder for error monitor
        "configs": configs,  # Placeholder for configs
        "dependencies": dependencies,  # Placeholder for dependencies
        "external_programs": ExternalPrograms,  # Placeholder for external programs
        "file_validator": make_file_validator,
        "content_extractor_object": ContentExtractor,  # Placeholder for content extractor
    }

fixtures = _fixture_dict()
