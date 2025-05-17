"""
Security manager module for the Omni-Converter.

This module provides the SecurityManager class for security validation and content sanitization.
"""

import os
import re
from typing import Any, Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

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
    
    def __init__(self):
        """Initialize a security manager."""
        # Default file size limits (in bytes)
        self.file_size_limits = {
            "default": 100 * 1024 * 1024,  # 100 MB general limit
            "text": 10 * 1024 * 1024,      # 10 MB for text files
            "image": 50 * 1024 * 1024,     # 50 MB for images
            "audio": 100 * 1024 * 1024,    # 100 MB for audio
            "video": 500 * 1024 * 1024,    # 500 MB for video
            "application": 100 * 1024 * 1024,  # 100 MB for applications
        }
        
        # All formats are allowed by default
        self.allowed_formats = []  # Empty means all formats are allowed
        
        # Security rules
        self.security_rules = {
            "reject_executable": True,
            "reject_encrypted": True,
            "reject_password_protected": True,
            "max_compression_ratio": 100,  # Reject files with compression ratio > 100:1
            "sanitize_content": True,
            "remove_scripts": True,
            "remove_active_content": True,
            "remove_personal_data": True,
            "remove_metadata": False,  # We generally want to keep metadata
        }
        
        # Patterns for dangerous content
        self._dangerous_patterns = [
            r"<script.*?>.*?</script>",
            r"javascript:",
            r"vbscript:",
            r"<iframe.*?>.*?</iframe>",
            r"eval\s*\(",
            r"document\.write\s*\(",
            r"<object.*?>.*?</object>",
            r"<embed.*?>.*?</embed>",
            r"<applet.*?>.*?</applet>",
            r"<form.*?>.*?</form>"
        ]
    
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
            file_size = os.path.getsize(file_path)
            metadata["file_size"] = file_size
            
            # Check file size limits
            category_limit = None
            if format_name:
                # Try to get category from format name
                category = None
                if format_name in ["html", "xml", "plain", "csv", "calendar"]:
                    category = "text"
                elif format_name in ["jpeg", "png", "gif", "webp", "svg"]:
                    category = "image"
                elif format_name in ["mp3", "wav", "ogg", "flac", "aac"]:
                    category = "audio"
                elif format_name in ["mp4", "webm", "avi", "mkv", "mov"]:
                    category = "video"
                elif format_name in ["pdf", "json", "docx", "xlsx", "zip"]:
                    category = "application"
                
                if category:
                    category_limit = self.file_size_limits.get(category)
            
            size_limit = category_limit or self.file_size_limits.get("default")
            
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
            if self.security_rules["reject_executable"] and self._is_executable(file_path):
                issues.append("File appears to be executable")
                is_safe = False
                risk_level = "high"
            
            # Additional checks for specific formats
            if format_name == "zip" and self.security_rules["reject_encrypted"]:
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
        if not self.security_rules["sanitize_content"]:
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
        if self.security_rules["remove_scripts"]:
            text, script_count = self._remove_scripts(text)
            if script_count > 0:
                applied_sanitizers.append("remove_scripts")
                removed_content["scripts"] = script_count
        
        if self.security_rules["remove_active_content"]:
            text, active_count = self._remove_active_content(text)
            if active_count > 0:
                applied_sanitizers.append("remove_active_content")
                removed_content["active_content"] = active_count
        
        if self.security_rules["remove_personal_data"]:
            text, pii_count = self._remove_personal_data(text)
            if pii_count > 0:
                applied_sanitizers.append("remove_personal_data")
                removed_content["personal_data"] = pii_count
        
        if self.security_rules["remove_metadata"]:
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
        """
        Set security rules.
        
        Args:
            rules: Dictionary of security rules.
        """
        for key, value in rules.items():
            if key in self.security_rules:
                self.security_rules[key] = value
            else:
                logger.warning(f"Unknown security rule: {key}")
        
        logger.info("Security rules updated", {"rules": self.security_rules})
    
    def set_allowed_formats(self, formats: List[str]) -> None:
        """
        Set allowed formats.
        
        Args:
            formats: List of allowed formats.
        """
        self.allowed_formats = formats
        logger.info("Allowed formats updated", {"formats": self.allowed_formats})
    
    def set_file_size_limits(self, limits: Dict[str, int]) -> None:
        """
        Set file size limits.
        
        Args:
            limits: Dictionary of file size limits by format (in bytes).
        """
        for key, value in limits.items():
            self.file_size_limits[key] = value
        
        logger.info("File size limits updated", {"limits": self.file_size_limits})
    
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
        ext = ext.lower()
        
        executable_extensions = [
            ".exe", ".com", ".bat", ".cmd", ".sh", ".ps1", ".vbs", ".js", ".jar", ".dll", ".so"
        ]
        
        if ext in executable_extensions:
            return True
        
        # Check if file has executable permissions (Unix only)
        try:
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
        count = 0
        # Remove script tags
        new_text, script_count = re.subn(r"<script.*?>.*?</script>", "", text, flags=re.IGNORECASE | re.DOTALL)
        count += script_count
        
        # Remove javascript: URLs
        new_text, js_count = re.subn(r"javascript:[^\s\"'<>]*", "", new_text, flags=re.IGNORECASE)
        count += js_count
        
        # Remove VBScript
        new_text, vbs_count = re.subn(r"vbscript:[^\s\"'<>]*", "", new_text, flags=re.IGNORECASE)
        count += vbs_count
        
        # Remove eval() and similar
        new_text, eval_count = re.subn(r"eval\s*\([^)]*\)", "", new_text, flags=re.IGNORECASE)
        count += eval_count
        
        return new_text, count
    
    def _remove_active_content(self, text: str) -> Tuple[str, int]:
        """
        Remove active content from text.
        
        Args:
            text: The text to sanitize.
            
        Returns:
            Tuple of (sanitized text, count of items removed).
        """
        count = 0
        new_text = text
        
        # Remove iframes
        new_text, iframe_count = re.subn(r"<iframe.*?>.*?</iframe>", "", new_text, flags=re.IGNORECASE | re.DOTALL)
        count += iframe_count
        
        # Remove objects and embeds
        new_text, obj_count = re.subn(r"<object.*?>.*?</object>", "", new_text, flags=re.IGNORECASE | re.DOTALL)
        count += obj_count
        
        new_text, embed_count = re.subn(r"<embed.*?>.*?</embed>", "", new_text, flags=re.IGNORECASE | re.DOTALL)
        count += embed_count
        
        # Remove applets
        new_text, applet_count = re.subn(r"<applet.*?>.*?</applet>", "", new_text, flags=re.IGNORECASE | re.DOTALL)
        count += applet_count
        
        # Remove forms
        new_text, form_count = re.subn(r"<form.*?>.*?</form>", "", new_text, flags=re.IGNORECASE | re.DOTALL)
        count += form_count
        
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
        
        # Very basic PII detection and removal (not comprehensive)
        patterns = [
            # Email addresses
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL REDACTED]'),
            
            # Phone numbers (various formats)
            (r'\b\d{3}[-.\s]?\d{3}[-.\s]?\d{4}\b', '[PHONE REDACTED]'),
            
            # Social Security Numbers
            (r'\b\d{3}[-.\s]?\d{2}[-.\s]?\d{4}\b', '[SSN REDACTED]'),
            
            # Credit card numbers (simplistic)
            (r'\b(?:\d{4}[-.\s]?){3}\d{4}\b', '[CREDIT CARD REDACTED]'),
            
            # Dates of birth (various formats)
            (r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', '[DATE REDACTED]'),
            
            # IP addresses
            (r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b', '[IP REDACTED]'),
            
            # URLs (simplified)
            (r'https?://[^\s<>"\']+', '[URL REDACTED]')
        ]
        
        for pattern, replacement in patterns:
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
        
        # Sensitive metadata keys to remove
        sensitive_keys = [
            "author", "creator", "producer", "owner", "company", "email", 
            "phone", "address", "gps", "location", "username", "user",
            "password", "key", "secret", "token", "api_key", "auth"
        ]
        
        removed_keys = []
        sanitized_metadata = {}
        
        for key, value in metadata.items():
            # Check if key contains sensitive information
            should_remove = False
            for sensitive in sensitive_keys:
                if sensitive.lower() in key.lower():
                    removed_keys.append(key)
                    should_remove = True
                    break
            
            if not should_remove:
                sanitized_metadata[key] = value
        
        return sanitized_metadata, removed_keys


# Global security manager instance
security_manager = SecurityManager()