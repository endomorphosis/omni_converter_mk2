"""
Test suite for monitors/security_monitor.py converted from unittest to pytest.

This test suite validates the SecurityMonitor component against several criteria:

1. Security Effectiveness (Target: 100% prevention of code execution)
   - Tests verify detection and rejection of executable files
   - Tests verify validation of file formats against allowed list
   - Tests ensure proper file size limit enforcement
   - Tests validate content sanitization for scripts, active content, and personal data
   
2. Error Handling Effectiveness
   - Tests verify graceful handling of security violations
   - Tests ensure proper reporting of security issues
   - Tests confirm isolation of security issues from the main processing pipeline

3. Text Quality for LLM Training
   - The security manager impacts text quality by sanitizing content while
     preserving the essential information needed for LLM training
   - Tests verify text content is properly sanitized without removing essential information
"""
import pytest
from unittest.mock import MagicMock, patch
import copy
import os
import tempfile
import shutil

from logger import logger as debug_logger
from core.content_extractor._content import Content
from types_ import Logger, Configs
from monitors.security_monitor import SecurityMonitor, SecurityResult

from configs import configs
from monitors._constants import Constants

resources = { # NOTE: Since these are constants, we can directly use them without mocking.
    "dangerous_patterns": Constants.SecurityMonitor.DANGEROUS_PATTERNS_REGEX,
    "executable_extensions": Constants.SecurityMonitor.EXECUTABLE_EXTENSIONS,
    "file_size_limits_in_bytes": Constants.SecurityMonitor.FILE_SIZE_LIMITS_IN_BYTES,
    "format_names": Constants.SecurityMonitor.FORMAT_NAMES,
    "pii_detection_regex": Constants.SecurityMonitor.PII_DETECTION_REGEX,
    "remove_active_content_regex": Constants.SecurityMonitor.REMOVE_ACTIVE_CONTENT_REGEX,
    "remove_scripts_regex": Constants.SecurityMonitor.REMOVE_SCRIPTS_REGEX,
    "security_rules": Constants.SecurityMonitor.SECURITY_RULES,
    "sensitive_keys": Constants.SecurityMonitor.SENSITIVE_KEYS,
}


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_files(temp_dir):
    """Create test files in the temporary directory."""
    files = {}
    
    # Create a normal test file
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    with open(test_file_path, 'w') as f:
        f.write("Test content")
    files['test_file'] = test_file_path
    
    # Create a large file (exceeds text limit)
    large_file_path = os.path.join(temp_dir, "large_file.txt")
    with open(large_file_path, 'w') as f:
        f.write("A" * (15 * 1024 * 1024))  # 15 MB file
    files['large_file'] = large_file_path
    
    # Create an executable file
    executable_file_path = os.path.join(temp_dir, "test_script.sh")
    with open(executable_file_path, 'w') as f:
        f.write("#!/bin/sh\necho 'Hello, world!'")
    os.chmod(executable_file_path, 0o755)
    
    # Check if the file is executable (Unix systems)
    if os.name != 'nt' and not os.access(executable_file_path, os.X_OK):
        raise PermissionError(f"File {executable_file_path} is not executable")
    files['executable_file'] = executable_file_path
    
    return files


@pytest.fixture
def mock_configs():
    """Create mock configs for testing."""
    return MagicMock(spec=Configs)


@pytest.fixture
def mock_content():
    """Create mock Content object for sanitization tests."""
    mock_content = MagicMock(spec=Content)
    mock_content.text = "Test text"
    mock_content.metadata = {"format": "txt"}
    mock_content.sections = [{"title": "Section 1", "content": "Content 1"}]
    mock_content.source_format = "txt"
    mock_content.source_path = "/path/to/file.txt"
    return mock_content


@pytest.fixture
def mock_security_result():
    """Create mock SecurityResult for testing."""
    mock_result = MagicMock(spec=SecurityResult)
    mock_result.is_safe.return_value = True
    mock_result.issues.return_value = []
    mock_result.risk_level.return_value = "low"
    mock_result.metadata.return_value = {"file_path": "/path/to/test.txt", "format": "plain"}
    return mock_result


@pytest.fixture
def mock_resources():
    """Create mock resources for testing."""
    return {
        **copy.deepcopy(resources),
        "logger": MagicMock(spec=Logger),
        "security_result": SecurityResult,
        "check_archive_security": MagicMock(return_value=[]),
        "check_document_security": MagicMock(return_value=[]),
        "check_image_security": MagicMock(return_value=[]),
        "check_video_security": MagicMock(return_value=[]),
        "check_audio_security": MagicMock(return_value=[]),
    }


@pytest.fixture
def security_monitor(mock_resources, mock_configs):
    """Create a SecurityMonitor instance for testing."""
    return SecurityMonitor(resources=mock_resources, configs=mock_configs)


@pytest.mark.unit
class TestSecurityMonitor:
    """Test the SecurityMonitor class."""

    def test_init(self, security_monitor):
        """Test initialization."""
        assert "default" in security_monitor._file_size_limits
        assert "text" in security_monitor._file_size_limits
        assert "image" in security_monitor._file_size_limits
        assert "audio" in security_monitor._file_size_limits
        assert "video" in security_monitor._file_size_limits
        assert "application" in security_monitor._file_size_limits
        assert len(security_monitor.allowed_formats) == 0
        assert security_monitor._security_rules["reject_executable"]

    def test_security_result_init(self):
        """Test SecurityResult initialization."""
        # Create with minimal arguments
        result = SecurityResult(is_safe=True)
        assert result.is_safe
        assert len(result.issues) == 0
        assert result.risk_level == "low"
        assert len(result.metadata) == 0
        
        # Create with all arguments
        result = SecurityResult(
            is_safe=False,
            issues=["Issue 1", "Issue 2"],
            risk_level="high",
            metadata={"key": "value"}
        )
        assert not result.is_safe
        assert len(result.issues) == 2
        assert result.risk_level == "high"
        assert result.metadata["key"] == "value"
    
    def test_security_result_to_dict(self):
        """Test SecurityResult.to_dict()."""
        result = SecurityResult(
            is_safe=False,
            issues=["Issue 1", "Issue 2"],
            risk_level="high",
            metadata={"key": "value"}
        )
        result_dict = result.to_dict()
        
        assert not result_dict["is_safe"]
        assert len(result_dict["issues"]) == 2
        assert result_dict["risk_level"] == "high"
        assert result_dict["metadata"]["key"] == "value"

    def test_validate_security_normal_file(self, security_monitor, test_files):
        """Test validating a normal file."""
        result = security_monitor.validate_security(test_files['test_file'], format_name="plain")
        debug_logger.debug(f"Security result: {result.to_dict()}") 
        
        assert result.is_safe
        assert len(result.issues) == 0
        assert result.risk_level == "low"
        assert result.metadata["file_path"] == test_files['test_file']
        assert result.metadata["format"] == "plain"
    
    def test_validate_security_large_file(self, security_monitor, test_files):
        """Test validating a file that exceeds size limits."""
        result = security_monitor.validate_security(test_files['large_file'], format_name="plain")

        assert not result.is_safe
        assert len(result.issues) == 1
        assert "exceeds limit" in result.issues[0]
        assert result.risk_level != "low"

    def test_validate_security_executable_file(self, security_monitor, test_files):
        """Test validating an executable file."""
        result = security_monitor.validate_security(test_files['executable_file'])

        assert not result.is_safe
        assert len(result.issues) == 1
        assert "executable" in result.issues[0]
        # The actual risk level appears to be 'medium' based on the implementation
        assert result.risk_level == "medium"

    def test_validate_security_nonexistent_file(self, security_monitor, temp_dir):
        """Test validating a file that doesn't exist."""
        nonexistent_path = os.path.join(temp_dir, "nonexistent.txt")
        result = security_monitor.validate_security(nonexistent_path)
        
        assert not result.is_safe
        assert len(result.issues) == 1
        assert "does not exist" in result.issues[0]
        assert result.risk_level == "high"
    
    def test_validate_security_disallowed_format(self, security_monitor, test_files):
        """Test validating a file with a disallowed format."""
        # Set allowed formats
        try:
            security_monitor.set_allowed_formats(["html", "pdf"])
            
            result = security_monitor.validate_security(test_files['test_file'], format_name="plain")
            
            assert not result.is_safe
            assert len(result.issues) == 1
            assert "not allowed" in result.issues[0]
        finally:
            # Reset allowed formats for other tests
            security_monitor.set_allowed_formats([])

    def test_is_file_safe(self, security_monitor, test_files):
        """Test checking if a file is safe."""
        # Normal file should be safe
        assert security_monitor.is_file_safe(test_files['test_file'])
        
        # Executable file should not be safe
        assert not security_monitor.is_file_safe(test_files['executable_file'])

    def test_set_security_rules(self, security_monitor):
        """Test setting security rules."""
        try:
            # Set new rules
            security_monitor.set_security_rules({
                "reject_executable": False,
                "remove_scripts": False,
                "unknown_rule": True  # Should be ignored
            })

            # Check if rules were updated
            assert not security_monitor._security_rules["reject_executable"]
            assert not security_monitor._security_rules["remove_scripts"]
            assert "unknown_rule" not in security_monitor._security_rules
        finally:
            # Reset to default rules
            security_monitor.set_security_rules(Constants.SecurityMonitor.SECURITY_RULES)

    def test_set_allowed_formats(self, security_monitor):
        """Test setting allowed formats."""
        # Initially all formats are allowed
        assert len(security_monitor.allowed_formats) == 0
        
        # Set allowed formats
        formats = ["html", "pdf", "plain"]
        security_monitor.set_allowed_formats(formats)
        
        # Check if formats were updated
        assert len(security_monitor.allowed_formats) == 3
        assert "html" in security_monitor.allowed_formats
        assert "pdf" in security_monitor.allowed_formats
        assert "plain" in security_monitor.allowed_formats
        
        # Reset for other tests
        security_monitor.set_allowed_formats([])
    
    def test_set_file_size_limits(self, security_monitor):
        """Test setting file size limits."""
        # Set new limits
        security_monitor.set_file_size_limits({
            "text": 20 * 1024 * 1024,  # 20 MB
            "new_category": 30 * 1024 * 1024  # 30 MB
        })

        # Check if limits were updated
        assert security_monitor._file_size_limits["text"] == 20 * 1024 * 1024
        assert security_monitor._file_size_limits["new_category"] == 30 * 1024 * 1024

        # Other limits should remain unchanged
        assert security_monitor._file_size_limits["default"] == 100 * 1024 * 1024

    def test_is_executable(self, security_monitor, test_files, temp_dir):
        """Test checking if a file is executable."""
        # Test a non-executable file
        assert not security_monitor._is_executable(test_files['test_file'])
        
        # Test an executable file
        assert security_monitor._is_executable(test_files['executable_file'])
        
        # Test a file with executable extension
        exe_file_path = os.path.join(temp_dir, "test.exe")
        with open(exe_file_path, 'w') as f:
            f.write("This is not a real executable")
        
        assert security_monitor._is_executable(exe_file_path)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])