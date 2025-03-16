"""
Tests package for the Omni-Converter.

This package contains test modules for each aspect of the converter:
- Format support coverage tests
- Processing success rate tests
- Resource utilization tests
- Processing speed tests
- Error handling effectiveness tests
- Security effectiveness tests
- Text quality tests
"""

# Import test modules for easier access
from .test_format_support_coverage import FormatSupportCoverageTest
from .test_processing_success_rate import ProcessingSuccessRateTest
from .test_resource_utilization import ResourceUtilizationTest
from .test_processing_speed import ProcessingSpeedTest
from .test_error_handling import ErrorHandlingTest
from .test_security_effectiveness import SecurityEffectivenessTest
from .test_text_quality import TextQualityTest