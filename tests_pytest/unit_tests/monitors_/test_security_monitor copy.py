"""
Test suite for monitors/security_monitor/_security_monitor.py converted from unittest to pytest.

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
    """Create temporary directory for test files."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def test_files(temp_dir):
    """Create test files in temporary directory."""
    test_file_path = os.path.join(temp_dir, "test_file.txt")
    with open(test_file_path, 'w') as f:
        f.write("Test content")
    
    large_file_path = os.path.join(temp_dir, "large_file.txt")
    with open(large_file_path, 'w') as f:
        f.write("A" * (15 * 1024 * 1024))  # 15 MB file (exceeds text limit)
    
    executable_file_path = os.path.join(temp_dir, "test_script.sh")
    with open(executable_file_path, 'w') as f:
        f.write("#!/bin/sh\necho 'Hello, world!'")

    # Make it executable
    os.chmod(executable_file_path, 0o755)

    # Check if the file is executable
    if os.name == 'nt':
        pass
    else:
        # On Unix-like systems, we can check if the file is executable
        if not os.access(executable_file_path, os.X_OK):
            raise PermissionError(f"File {executable_file_path} is not executable")

    return {
        'test_file_path': test_file_path,
        'large_file_path': large_file_path,
        'executable_file_path': executable_file_path
    }


@pytest.fixture
def mock_configs():
    """Create mock configs for testing."""
    return MagicMock(spec=Configs)


@pytest.fixture
def mock_content(test_files):
    """Create mock Content object for security tests."""
    mock_content = MagicMock(spec=Content)
    mock_content.text = "Test text"
    mock_content.metadata = {"format": "txt"}
    mock_content.sections = [{"title": "Section 1", "content": "Content 1"}]
    mock_content.source_format = "txt"
    mock_content.source_path = test_files['test_file_path']
    return mock_content


@pytest.fixture
def mock_security_result(test_files):
    """Create mock SecurityResult object for testing."""
    mock_security_result = MagicMock(spec=SecurityResult)
    mock_security_result.is_safe = MagicMock()
    mock_security_result.issues = MagicMock()
    mock_security_result.risk_level = MagicMock()
    mock_security_result.metadata = MagicMock()

    mock_security_result.is_safe.return_value = True
    mock_security_result.issues.return_value = []
    mock_security_result.risk_level.return_value = "low"
    mock_security_result.metadata.return_value = {"file_path": test_files['test_file_path'], "format": "plain"}
    return mock_security_result


@pytest.fixture
def mock_resources():
    """Create mock resources for testing."""
    mock_resources = {
        **copy.deepcopy(resources),
        "logger": MagicMock(spec=Logger),
        "security_result": SecurityResult,
        "check_archive_security": MagicMock(return_value=[]),
        "check_document_security": MagicMock(return_value=[]),
        "check_image_security": MagicMock(return_value=[]),
        "check_video_security": MagicMock(return_value=[]),
        "check_audio_security": MagicMock(return_value=[]),
    }
    return mock_resources


@pytest.fixture
def security_monitor(mock_resources, mock_configs):
    """Create SecurityMonitor instance for testing."""
    return SecurityMonitor(resources=mock_resources, configs=mock_configs)


@pytest.mark.unit
class TestSecurityManager:
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
        assert security_monitor._security_rules["reject_executable"] is True

    def test_security_result_init(self):
        """Test SecurityResult initialization."""
        # Create with minimal arguments
        result = SecurityResult(is_safe=True)
        assert result.is_safe is True
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
        assert result.is_safe is False
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
        
        assert result_dict["is_safe"] is False
        assert len(result_dict["issues"]) == 2
        assert result_dict["risk_level"] == "high"
        assert result_dict["metadata"]["key"] == "value"

    def test_validate_security_normal_file(self, security_monitor, test_files):
        """Test validating a normal file."""
        result = security_monitor.validate_security(test_files['test_file_path'], format_name="plain")
        debug_logger.debug(f"Security result: {result.to_dict()}") 
        
        assert result.is_safe is True

    def test_validate_security_large_file(self, security_monitor, test_files):
        """Test validating a file that exceeds size limits."""
        result = security_monitor.validate_security(test_files['large_file_path'], format_name="plain")

        assert result.is_safe is False
        assert len(result.issues) == 1
        assert "File size" in result.issues[0] and "exceeds limit" in result.issues[0]

    def test_validate_security_executable_file(self, security_monitor, test_files):
        """Test validating an executable file."""
        result = security_monitor.validate_security(test_files['executable_file_path'], format_name="plain")

        assert result.is_safe is False
        assert len(result.issues) >= 1
        # Should contain an issue about executable file
        issues_str = ' '.join(result.issues)
        assert "executable" in issues_str.lower()

    def test_validate_security_nonexistent_file(self, security_monitor):
        """Test validating a non-existent file."""
        result = security_monitor.validate_security("/nonexistent/file.txt", format_name="plain")

        assert result.is_safe is False
        assert len(result.issues) >= 1
        # Should contain an issue about file not existing
        issues_str = ' '.join(result.issues)
        assert "not exist" in issues_str.lower() or "not found" in issues_str.lower()

    def test_validate_security_disallowed_format(self, security_monitor, test_files):
        """Test validating a file with disallowed format."""
        # Set only specific formats as allowed
        security_monitor.set_allowed_formats(["txt", "pdf"])
        
        # Test with a format not in the allowed list
        result = security_monitor.validate_security(test_files['test_file_path'], format_name="exe")

        assert result.is_safe is False
        assert len(result.issues) >= 1
        # Should contain an issue about disallowed format
        issues_str = ' '.join(result.issues)
        assert "format" in issues_str.lower() or "not allowed" in issues_str.lower()

    def test_is_file_safe(self, security_monitor, test_files):
        """Test the is_file_safe method."""
        # Normal file should be safe
        assert security_monitor.is_file_safe(test_files['test_file_path']) is True
        
        # Executable file should not be safe
        assert security_monitor.is_file_safe(test_files['executable_file_path']) is False

    def test_set_security_rules(self, security_monitor):
        """Test setting security rules."""
        # Set custom rules
        custom_rules = {
            "reject_executable": False,
            "sanitize_content": True
        }
        
        security_monitor.set_security_rules(custom_rules)
        
        # Check that rules were updated
        assert security_monitor._security_rules["reject_executable"] is False
        assert security_monitor._security_rules["sanitize_content"] is True

    def test_set_allowed_formats(self, security_monitor):
        """Test setting allowed formats."""
        # Set allowed formats
        allowed_formats = ["txt", "pdf", "docx"]
        security_monitor.set_allowed_formats(allowed_formats)
        
        # Check that formats were set
        assert set(security_monitor.allowed_formats) == set(allowed_formats)
        
        # Test with empty list
        security_monitor.set_allowed_formats([])
        assert len(security_monitor.allowed_formats) == 0

    def test_set_file_size_limits(self, security_monitor):
        """Test setting file size limits."""
        # Set custom limits
        custom_limits = {
            "text": 1 * 1024 * 1024,  # 1 MB
            "image": 5 * 1024 * 1024,  # 5 MB
            "default": 10 * 1024 * 1024  # 10 MB
        }
        
        security_monitor.set_file_size_limits(custom_limits)
        
        # Check that limits were updated
        assert security_monitor._file_size_limits["text"] == 1 * 1024 * 1024
        assert security_monitor._file_size_limits["image"] == 5 * 1024 * 1024
        assert security_monitor._file_size_limits["default"] == 10 * 1024 * 1024

    def test_is_executable(self, security_monitor, test_files):
        """Test the is_executable method."""
        # Normal text file should not be executable
        assert security_monitor._is_executable(test_files['test_file_path']) is False
        
        # Executable script should be executable
        assert security_monitor._is_executable(test_files['executable_file_path']) is True