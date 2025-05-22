"""
Security manager module for the Omni-Converter.

This module provides the SecurityManager class for security validation and content sanitization.
"""

import os
import re
from typing import Any, Callable, Dict, List, Optional, Tuple, Union


from pydantic import BaseModel, Field


from utils.configs import configs, Configs
from utils.logger import logger
from format_handlers.base_handler import Content
from core.validation_result import ValidationResult


class SecurityResult(BaseModel):
    """
    Result of security validation.
    
    This class represents the result of security validation for a file.
    
    Attributes:
        is_safe (bool): Whether the file is considered safe.
        issues (List[str]): List of security issues found.
        risk_level (str): Risk level assessment ('low', 'medium', 'high').
        metadata (Dict[str, Any]): Additional metadata about the security check.
    """
    is_safe: bool
    issues: List[str] = Field(default_factory=list)
    risk_level: str = "low"
    metadata: Dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.

        Returns:
            A dictionary representation of the security result.
        """
        return self.model_dump()


class SanitizedContent(Content):
    """
    Sanitized content from a file.
    
    This class extends the base Content class with sanitization information.
    
    Attributes:
        sanitization_applied (List[str]): List of sanitization techniques applied.
        removed_content (Dict[str, Any]): Information about content that was removed.
    """
    sanitization_applied: List[str] = Field(default_factory=list)
    removed_content: Dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the sanitized content.
        """
        result = super().to_dict()
        result["sanitization_applied"] = self.sanitization_applied
        result["removed_content"] = self.removed_content
        return result


class SecurityManager:
    """
    Security manager for the Omni-Converter.
    
    This class handles security validation and content sanitization.
    
    Attributes:
        file_size_limits (Dict[str, int]): Maximum file size limits by format (in bytes).
        allowed_formats (List[str]): List of allowed formats.
        security_rules (Dict[str, Any]): Security rules for validation and sanitization.
    """
    
    def __init__(self, 
                resources: Dict[str, Callable] = None, 
                configs: Configs = None
                ) -> None:
        """Initialize a security manager."""
        self.configs = configs
        self.resources = resources

        self._dangerous_patterns:          list[re.Pattern] = self.resources['dangerous_patterns']
        self._executable_extensions:       list[str] = self.resources['executable_extensions']
        self._file_size_limits:            dict[str, int] = self.resources['file_size_limits_in_bytes']
        self._format_names:                dict[str, list[str]] = self.resources['format_names']
        self._pii_detection:               list[tuple[re.Pattern, str]] = self.resources['pii_detection_regex']
        self._remove_active_content_regex: list[re.Pattern] = self.resources['remove_active_content_regex']
        self._remove_scripts_regex:        list[re.Pattern] = self.resources['remove_scripts_regex']
        self._security_rules:              dict[str, Any] = self.resources['security_rules']
        self._sensitive_keys:              list[str] = self.resources['sensitive_keys']

        # All formats are allowed by default
        self.allowed_formats = []  # Empty means all formats are allowed

    def validate_security(self, file_path: str, format_name: Optional[str] = None) -> SecurityResult:
        """
        Validate the security of a file.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            A SecurityResult object with the validation results.
        """
        issues = []
        is_safe = True
        risk_level = "low"
        metadata = {"file_path": file_path, "format": format_name}

        try:
            # Check if file exists
            if not os.path.exists(file_path):
                issues.append("File does not exist")
                return SecurityResult(is_safe=False, issues=issues, risk_level="high", metadata=metadata)
            
            # Get file size
            metadata["file_size"] = file_size = os.path.getsize(file_path)
            
            # Check file size limits
            category_limit = None
            if format_name:
                # Try to get category from format name
                category = None
                if format_name in self._format_names["text"]:
                    category = "text"
                elif format_name in self._format_names["image"]:
                    category = "image"
                elif format_name in self._format_names["audio"]:
                    category = "audio"
                elif format_name in self._format_names["video"]:
                    category = "video"
                elif format_name in self._format_names["application"]:
                    category = "application"
                
                if category:
                    category_limit = self._file_size_limits[category]
            
            size_limit = category_limit or self._file_size_limits["default"]
            
            if file_size > size_limit:
                issues.append(f"File size {file_size} bytes exceeds limit of {size_limit} bytes")
                is_safe = False
                risk_level = "medium"
            
            # Check if format is allowed
            if self.allowed_formats and format_name and format_name not in self.allowed_formats:
                issues.append(f"Format {format_name} is not allowed")
                is_safe = False
                risk_level = "medium"
            
            # Check for executable files
            if self._security_rules["reject_executable"] and self._is_executable(file_path):
                issues.append("File appears to be executable")
                is_safe = False
                risk_level = "high"
            
            # Additional checks for specific formats
            # We want to check for storage formats like zip, tar, etc.
            # This is because they may contain other files that might be malicious.
            if format_name == "zip" and self._security_rules["reject_encrypted"]:
                # Basic check for encrypted ZIP (this is not comprehensive)
                with open(file_path, 'rb') as f:
                    header = f.read(1024)
                    if b"password" in header.lower() or b"encrypt" in header.lower():
                        issues.append("ZIP file may be encrypted or password protected")
                        is_safe = False
                        risk_level = "high"
            
            # Assess overall risk level
            if len(issues) > 2:
                risk_level = "high"
            elif len(issues) > 0:
                risk_level = "medium"
            
            return SecurityResult(is_safe=is_safe, issues=issues, risk_level=risk_level, metadata=metadata)
            
        except Exception as e:
            issues.append(f"Error during security validation: {e}")
            logger.error(f"Security validation error for {file_path}: {e}")
            return SecurityResult(is_safe=False, issues=issues, risk_level="high", metadata=metadata)
    
    def is_file_safe(self, file_path: str, format_name: Optional[str] = None) -> bool:
        """
        Check if a file is safe.
        
        Args:
            file_path: The path to the file.
            format_name: The format of the file, if known.
            
        Returns:
            True if the file is safe, False otherwise.
        """
        result = self.validate_security(file_path, format_name)
        return result.is_safe
    
    def sanitize_content(self, content: Content) -> SanitizedContent:
        """
        Sanitize content for security.
        
        Args:
            content: The content to sanitize.
            
        Returns:
            Sanitized content.
        """
        if not self._security_rules["sanitize_content"]:
            # Return content as-is if sanitization is disabled
            return SanitizedContent(
                text=content.text,
                metadata=content.metadata,
                sections=content.sections,
                source_format=content.source_format,
                source_path=content.source_path,
                sanitization_applied=["none"],
                removed_content={}
            )
        
        text = content.text
        metadata = content.metadata.copy() if content.metadata else {}
        sections = content.sections.copy() if content.sections else []
        applied_sanitizers = []
        removed_content = {}
        
        # Apply sanitization rules
        if self._security_rules["remove_scripts"]:
            text, script_count = self._remove_scripts(text)
            if script_count > 0:
                applied_sanitizers.append("remove_scripts")
                removed_content["scripts"] = script_count
        
        if self._security_rules["remove_active_content"]:
            text, active_count = self._remove_active_content(text)
            if active_count > 0:
                applied_sanitizers.append("remove_active_content")
                removed_content["active_content"] = active_count
        
        if self._security_rules["remove_personal_data"]:
            text, pii_count = self._remove_personal_data(text)
            if pii_count > 0:
                applied_sanitizers.append("remove_personal_data")
                removed_content["personal_data"] = pii_count
        
        if self._security_rules["remove_metadata"]:
            metadata, removed_keys = self._sanitize_metadata(metadata)
            if removed_keys:
                applied_sanitizers.append("remove_metadata")
                removed_content["metadata_keys"] = removed_keys
        
        # Create sanitized content
        return SanitizedContent(
            text=text,
            metadata=metadata,
            sections=sections,
            source_format=content.source_format,
            source_path=content.source_path,
            sanitization_applied=applied_sanitizers,
            removed_content=removed_content
        )

    def set_security_rules(self, rules: Dict[str, Any]) -> None:
        """Set the dictionary of security rules."""
        for key, value in rules.items():
            if key in self._security_rules:
                self._security_rules[key] = value
            else:
                logger.warning(f"Unknown security rule: {key}")
        
        logger.info("Security rules updated", {"rules": self._security_rules})
    
    def set_allowed_formats(self, formats: List[str]) -> None:
        """Set the list of allowed formats."""
        self.allowed_formats = formats
        logger.info(f"Allowed formats updated '{self.allowed_formats}'")
    
    def set_file_size_limits(self, limits: Dict[str, int]) -> None:
        """
        Set file size limits.
        
        Args:
            limits: Dictionary of file size limits by format (in bytes).
        """
        for key, value in limits.items(): # TODO Add pydantic validation here.
            self._file_size_limits[key] = value
        
        logger.info(f"File size limits updated to '{self._file_size_limits}'")
    
    def _is_executable(self, file_path: str) -> bool:
        """
        Check if a file is executable.
        
        Args:
            file_path: The path to the file.
            
        Returns:
            True if the file is executable, False otherwise.
        """
        # Check file extension
        _, ext = os.path.splitext(file_path)

        if ext.lower() in self._executable_extensions:
            return True
        
        # Check if file has executable permissions (Unix only)
        try:
            if os.name == "nt":
                return False  # Windows does not support this check. # TODO Find a way to inform the user about this.
            return os.access(file_path, os.X_OK)
        except Exception:
            return False
    
    def _remove_scripts(self, text: str) -> Tuple[str, int]:
        """
        Remove script content from text.
        
        Args:
            text: The text to sanitize.
            
        Returns:
            Tuple of (sanitized text, count of items removed).
        """
        # Remove the following: script tags, javascript: URLs, VBScript, eval() and similar
        count = 0
        new_text = text
        for regex in self._remove_scripts_regex:
            flags = re.IGNORECASE | re.DOTALL
            new_text, removal_count = re.subn(regex, "", new_text, flags=flags)
            count += removal_count
        return new_text, count
    
    def _remove_active_content(self, text: str) -> Tuple[str, int]:
        """
        Remove active content from text.
        
        Args:
            text: The text to sanitize.
            
        Returns:
            Tuple of (sanitized text, count of items removed).
        """
        # Remove active content like iframes, objects, embeds, applets, forms
        count = 0
        new_text = text
        for regex in self._remove_active_content_regex:
            flags = re.IGNORECASE | re.DOTALL
            new_text, removal_count = re.subn(regex, "", new_text, flags=flags)
            count += removal_count

        return new_text, count
    
    def _remove_personal_data(self, text: str) -> Tuple[str, int]:
        """
        Remove personal data from text.
        
        Args:
            text: The text to sanitize.
            
        Returns:
            Tuple of (sanitized text, count of items removed).
        """
        count = 0
        new_text = text
        # Very basic PII detection and removal (not comprehensive) TODO see constants.py
        for pattern, replacement in self._pii_detection:
            new_text, replacements = re.subn(pattern, replacement, new_text)
            count += replacements
        
        return new_text, count
    
    def _sanitize_metadata(self, metadata: Dict[str, Any]) -> Tuple[Dict[str, Any], List[str]]:
        """
        Sanitize metadata.
        
        Args:
            metadata: The metadata to sanitize.
            
        Returns:
            Tuple of (sanitized metadata, list of removed keys).
        """
        if not metadata:
            return metadata, []

        removed_keys = []
        sanitized_metadata = {}
        
        for key, value in metadata.items():
            # Check if key contains sensitive information
            should_remove = False
            for sensitive in self._sensitive_keys:
                if sensitive.lower() in key.lower():
                    removed_keys.append(key)
                    should_remove = True
                    break
            
            if not should_remove:
                sanitized_metadata[key] = value
        
        return sanitized_metadata, removed_keys

from .constants import Constants
resources = {
    "dangerous_patterns": Constants.SecurityManager.DANGEROUS_PATTERNS_REGEX,
    "executable_extensions": Constants.SecurityManager.EXECUTABLE_EXTENSIONS,
    "file_size_limits_in_bytes": Constants.SecurityManager.FILE_SIZE_LIMITS_IN_BYTES,
    "format_names": Constants.SecurityManager.FORMAT_NAMES,
    "pii_detection_regex": Constants.SecurityManager.PII_DETECTION_REGEX,
    "remove_active_content_regex": Constants.SecurityManager.REMOVE_ACTIVE_CONTENT_REGEX,
    "remove_scripts_regex": Constants.SecurityManager.REMOVE_SCRIPTS_REGEX,
    "security_rules": Constants.SecurityManager.SECURITY_RULES,
    "sensitive_keys": Constants.SecurityManager.SENSITIVE_KEYS
}

# Global security manager instance
security_manager = SecurityManager(resources=resources, configs=configs)
