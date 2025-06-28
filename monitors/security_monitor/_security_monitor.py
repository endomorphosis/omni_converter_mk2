"""
Security manager module for the Omni-Converter.

This module provides the SecurityMonitor class for security validation and content sanitization.
"""
from __future__ import annotations
from contextlib import closing
import os
import re
import zipfile
import tarfile
import tempfile


from types_ import Any, Callable, Optional, Configs, Logger, SecurityResult
from supported_formats import SupportedFormats


class SecurityMonitor:
    """
    Security manager for the Omni-Converter.
    
    This class handles security validation.
    
    Attributes:
        file_size_limits (dict[str, int]): Maximum file size limits by format (in bytes).
        allowed_formats (list[str]): list of allowed formats.
        security_rules (dict[str, Any]): Security rules for validation and sanitization.
    """
    
    def __init__(self, 
                resources: dict[str, Callable] = None, 
                configs: Configs = None
                ) -> None:
        """Initialize a security manager."""
        self.configs = configs
        self.resources = resources

        self._dangerous_patterns:    list[re.Pattern] = self.resources['dangerous_patterns']
        self._executable_extensions: list[str] = self.resources['executable_extensions']
        self._file_size_limits:      dict[str, int] = self.resources['file_size_limits_in_bytes']

        self._security_rules:           dict[str, Any]   = self.resources['security_rules']
        self._supported_formats_object: SupportedFormats = SupportedFormats # TODO Move this into the constructor after testing.
        self._security_result:          SecurityResult   = self.resources['security_result']
        self._logger:                   Logger           = self.resources['logger']

        # All formats are allowed by default
        self.allowed_formats: list[str] = [] # Empty means all formats are allowed

    def validate_security(self, file_path: str, format_name: Optional[str] = None) -> 'SecurityResult':
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
                return self._security_result(is_safe=False, issues=issues, risk_level="high", metadata=metadata)

            # Get file size
            metadata["file_size"] = file_size = os.path.getsize(file_path)

            # Check file size limits
            category_limit = None
            if format_name:
                # Try to get category from format name
                category = None
                if format_name in self._supported_formats_object.SUPPORTED_TEXT_FORMATS:
                    category = "text"
                elif format_name in self._supported_formats_object.SUPPORTED_IMAGE_FORMATS:
                    category = "image"
                elif format_name in self._supported_formats_object.SUPPORTED_AUDIO_FORMATS:
                    category = "audio"
                elif format_name in self._supported_formats_object.SUPPORTED_VIDEO_FORMATS:
                    category = "video"
                elif format_name in self._supported_formats_object.SUPPORTED_APPLICATION_FORMATS:
                    category = "application"
                else:
                    # If format is not recognized, 
                    issues.append(f"Unrecognized format name '{format_name}'")
                    return self._security_result(is_safe=False, issues=issues, risk_level="high", metadata=metadata)

                if category:
                    category_limit = self._file_size_limits[category]

            size_limit = category_limit or self._file_size_limits["default"]

            if file_size > size_limit:
                self._logger.warning(f"File size {file_size} bytes exceeds limit of {size_limit} bytes for format '{format_name}'")
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

            # Check for archive/container formats that may contain malicious content
            if format_name in ["zip", "tar", "rar", "7z", "gz", "bz2", "xz"]:
                archive_issues = self._check_archive_security(file_path, format_name)
                if archive_issues:
                    issues.extend(archive_issues)
                    is_safe = False
                    risk_level = "high"

            # Check for document formats that may contain macros or embedded content
            elif format_name in ["docx", "xlsx", "pptx", "doc", "xls", "ppt", "pdf", "odt", "ods", "odp"]:
                doc_issues = self._check_document_security(file_path, format_name)
                if doc_issues:
                    issues.extend(doc_issues)
                    is_safe = False
                    risk_level = "medium"

            # Check for image formats that may contain embedded payloads
            elif format_name in ["svg", "eps", "ps"]:
                img_issues = self._check_image_security(file_path, format_name)
                if img_issues:
                    issues.extend(img_issues)
                    is_safe = False
                    risk_level = "medium"

            # Additional checks for specific formats
                # We want to check for storage formats like zip, tar, etc.
                # As they may contain other files that might be malicious.
                # Or be malicious themselves (e.g. zip bombs).

            # Assess overall risk level
            if len(issues) > 2:
                risk_level = "high"
            elif len(issues) > 0:
                risk_level = "medium"

            return self._security_result(
                is_safe=is_safe, 
                issues=issues, 
                risk_level=risk_level, 
                metadata=metadata
            )

        except Exception as e:
            issues.append(f"Error during security validation: {e}")
            self._logger.error(f"Security validation error for {file_path}: {e}")
            return self._security_result(
                is_safe=False, 
                issues=issues, 
                risk_level="high", 
                metadata=metadata
            )

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
    
    @staticmethod
    def _get_compression_ratio(file_path: str, format_name: str) -> float:
        """Calculate the compression ratio of an archive file.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            Compression ratio (uncompressed_size / compressed_size).
            Returns 1.0 if unable to determine ratio.
        """
        try:
            compressed_size = os.path.getsize(file_path)
            if compressed_size == 0:
                return 1.0

            uncompressed_size = 0

            if format_name == "zip": # TODO Find a way to un-hardcode this.
                with closing(zipfile.ZipFile(file_path, 'r')) as archive:
                    for info in archive.infolist():
                        uncompressed_size += info.file_size
            elif format_name in ["tar", "gz", "bz2", "xz"]:
                with closing(tarfile.open(file_path, 'r')) as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            uncompressed_size += member.size
            else:
                # For other formats, return 1.0 (no compression detected)
                return 1.0

            return uncompressed_size / compressed_size if compressed_size > 0 else 1.0

        except Exception:
            # If we can't determine the ratio, assume no compression # TODO Why assume no compression? This needs to be clarified.
            return 1.0
    
    @staticmethod
    def _is_archive_encrypted(file_path: str, format_name: str) -> bool:
        """Check if an archive is encrypted or password protected.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            True if the archive is encrypted, False otherwise.
        """
        try:
            if format_name == "zip":
                with closing(zipfile.ZipFile(file_path, 'r')) as archive:
                    for info in archive.infolist():
                        if info.flag_bits & 0x1:  # Check encryption flag
                            return True
                    # Additional check: try to read first file
                    if archive.infolist():
                        try:
                            archive.read(archive.infolist()[0].filename)
                        except RuntimeError as e:
                            if "password" in str(e).lower() or "encrypted" in str(e).lower():
                                return True
            elif format_name in ["tar", "gz", "bz2", "xz"]:
                # TAR files don't have built-in encryption, but check for GPG/PGP signatures
                with open(file_path, 'rb') as f:
                    header = f.read(512)
                    # Check for GPG/PGP magic bytes
                    if header.startswith(b'\x85\x01') or header.startswith(b'\x95\x01'):
                        return True
                    # Check for password-protected compressed files
                    if b'ENCRYPTED' in header or b'PASSWORD' in header:
                        return True
                        
                # Try to open and read archive structure
                try:
                    with closing(tarfile.open(file_path, 'r')) as tar_file:
                        tar_file.getnames()  # This will fail if encrypted
                except tarfile.ReadError as e:
                    if "password" in str(e).lower() or "encrypted" in str(e).lower():
                        return True
            return False
        except Exception:
            # If we can't analyze the archive, assume it might be encrypted
            return True
        
    @staticmethod
    def _count_nested_archives(file_path: str, format_name: str) -> int:
        """Count the number of nested archive levels in an archive file.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            Number of nested archive levels found.
        """
        def _is_archive_file(filename: str) -> bool:
            """Check if a filename appears to be an archive."""
            archive_extensions = {'.zip', '.tar', '.gz', '.bz2', '.xz', '.rar', '.7z'}
            _, ext = os.path.splitext(filename.lower())
            return ext in archive_extensions
        
        def _count_nested_in_zip(zip_path: str, current_depth: int = 0, max_depth: int = 10) -> int:
            """Recursively count nested archives in a ZIP file."""
            if current_depth >= max_depth:
                return current_depth
            
            max_nested = current_depth
            try:
                with closing(zipfile.ZipFile(zip_path, 'r')) as archive:
                    for info in archive.infolist():
                        if not info.is_dir() and _is_archive_file(info.filename):
                            # Found a nested archive - extract and analyze it
                            nested_depth = current_depth + 1
                            max_nested = max(max_nested, nested_depth)
                            
                            # Extract nested archive to temp location for deeper analysis
                            with tempfile.TemporaryDirectory() as temp_dir:
                                temp_path = os.path.join(temp_dir, info.filename)
                                with open(temp_path, 'wb') as temp_file:
                                    temp_file.write(archive.read(info.filename))
                                
                                # Recursively analyze the nested archive
                                deeper_nested = _count_nested_in_zip(temp_path, nested_depth, max_depth)
                                max_nested = max(max_nested, deeper_nested)
                            
            except Exception:
                pass  # Ignore errors and return what we found so far
            
            return max_nested
        
        def _count_nested_in_tar(tar_path: str, current_depth: int = 0, max_depth: int = 10) -> int:
            """Recursively count nested archives in a TAR file."""
            if current_depth >= max_depth:
                return current_depth
            
            max_nested = current_depth
            try:
                with closing(tarfile.open(tar_path, 'r')) as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile() and _is_archive_file(member.name):
                            # Found a nested archive
                            nested_depth = current_depth + 1
                            max_nested = max(max_nested, nested_depth)
                            
                            # For deeper analysis, we'd need to extract and analyze
                            # but for security reasons, we'll just count this level
                            
            except Exception:
                pass  # Ignore errors and return what we found so far
            
            return max_nested
        
        try:
            if format_name == "zip":
                return _count_nested_in_zip(file_path)
            elif format_name in ["tar", "gz", "bz2", "xz"]:
                return _count_nested_in_tar(file_path)
            else:
                return 0  # Unknown format, assume no nesting
                
        except Exception:
            return 0  # If we can't analyze, assume no nesting

    @staticmethod
    def _check_archive_paths(file_path: str, format_name: str) -> list[str]:
        """Check for suspicious file paths in an archive.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            List of suspicious file paths found in the archive.
        """
        suspicious_paths = []
        
        try:
            if format_name == "zip":
                with closing(zipfile.ZipFile(file_path, 'r')) as archive:
                    for info in archive.infolist():
                        path = info.filename
                        if SecurityMonitor._is_suspicious_path(path):
                            suspicious_paths.append(path)
                            
            elif format_name in ["tar", "gz", "bz2", "xz"]:
                with closing(tarfile.open(file_path, 'r')) as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            path = member.name
                            if SecurityMonitor._is_suspicious_path(path):
                                suspicious_paths.append(path)
                                
        except Exception:
            # If we can't read the archive, return empty list
            pass
            
        return suspicious_paths
    
    @staticmethod
    def _is_suspicious_path(path: str) -> bool:
        """Check if a file path is suspicious.
        
        Args:
            path: The file path to check.
            
        Returns:
            True if the path is suspicious, False otherwise.
        """
        # Check for directory traversal attempts
        if ".." in path or path.startswith("/") or path.startswith("\\"):
            return True
            
        # Check for Windows drive letters or UNC paths
        if len(path) > 1 and path[1] == ":" or path.startswith("\\\\"):
            return True
            
        # Check for hidden files (starting with .)
        filename = os.path.basename(path)
        if filename.startswith(".") and filename not in [".gitignore", ".gitkeep"]:
            return True
            
        # Check for system directories
        system_dirs = ["system32", "windows", "program files", "etc", "bin", "sbin", "usr"]
        path_lower = path.lower()
        for sys_dir in system_dirs:
            if sys_dir in path_lower:
                return True

        # Check for very long paths (potential buffer overflow)
        if len(path) > 255:
            return True

        return False

    @staticmethod
    def _check_archive_executables(file_path: str, format_name: str) -> list[str]:
        """Check for executable files in an archive.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            List of executable file paths found in the archive.
        """
        executable_files = []
        # TODO Move executable_extensions to the resources. This way it can be fine-tuned.
        executable_extensions = {'.exe', '.bat', '.cmd', '.com', '.scr', '.pif', '.app', '.deb', '.rpm', '.dmg', '.pkg', '.msi', '.sh', '.bash', '.zsh', '.fish', '.csh', '.tcsh', '.pl', '.py', '.rb', '.php', '.jar', '.class', '.vbs', '.js', '.ps1', '.psm1', '.psd1'}

        try:
            if format_name == "zip":
                with closing(zipfile.ZipFile(file_path, 'r')) as archive:
                    for info in archive.infolist():
                        if not info.is_dir():
                            filename = info.filename
                            _, ext = os.path.splitext(filename.lower())
                            
                            # Check file extension
                            if ext in executable_extensions:
                                executable_files.append(filename)
                            # Check for files without extension that might be executable (Unix)
                            elif not ext and not filename.endswith('/'):
                                executable_files.append(filename)
                            # Check for shebang in first few bytes
                            elif filename.lower().endswith(('.sh', '.py', '.pl', '.rb', '.php')):
                                try:
                                    file_content = archive.read(info.filename)
                                    if file_content.startswith(b'#!'):
                                        executable_files.append(filename)
                                except Exception:
                                    pass  # If we can't read the file, skip shebang check

            elif format_name in ["tar", "gz", "bz2", "xz"]:
                with closing(tarfile.open(file_path, 'r')) as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            filename = member.name
                            _, ext = os.path.splitext(filename.lower())
                            
                            # Check file extension
                            if ext in executable_extensions:
                                executable_files.append(filename)
                            # Check file permissions (Unix executable bit)
                            elif member.mode & 0o111:  # Check if any execute bit is set
                                executable_files.append(filename)
                            # Check for files without extension that might be executable
                            elif not ext and not filename.endswith('/'):
                                executable_files.append(filename)
                                
        except Exception:
            # If we can't read the archive, return empty list
            pass
            
        return executable_files

    @staticmethod
    def _count_archive_files(file_path: str, format_name: str) -> int:
        """Count the total number of files in an archive.
        
        Args:
            file_path: Path to the archive file.
            format_name: Format of the archive (zip, tar, etc.).
            
        Returns:
            Total number of files in the archive (excluding directories).
        """
        file_count = 0

        try:
            if format_name == "zip":
                with closing(zipfile.ZipFile(file_path, 'r')) as archive:
                    for info in archive.infolist():
                        if not info.is_dir():
                            file_count += 1
                            
            elif format_name in ["tar", "gz", "bz2", "xz"]:
                with closing(tarfile.open(file_path, 'r')) as tar_file:
                    for member in tar_file.getmembers():
                        if member.isfile():
                            file_count += 1
            else:
                # For unknown formats, return 0
                return 0

        except Exception:
            # If we can't read the archive, return 0
            return 0

        return file_count

    def _check_archive_security(self, file_path: str, format_name: str, issues: list[str]) -> tuple[bool, str, list[str]]:
        # Comprehensive security checks for archive formats
        is_safe = True
        risk_level = "low"

        try:
            file_size = os.path.getsize(file_path)

            # Check for zip bombs (suspiciously large uncompressed size)
            if format_name in ["zip", "tar", "gz", "bz2", "xz"]:
                compressed_ratio = self._get_compression_ratio(file_path, format_name)
                if compressed_ratio > 100:  # Uncompressed is 100x larger than compressed # TODO compressed_ratio is Magic number, should be configurable.
                    issues.append(f"Suspicious compression ratio: {compressed_ratio}:1 (possible zip bomb)")

            # Check for encrypted archives
            if self._security_rules["reject_encrypted"]:
                if self._is_archive_encrypted(file_path, format_name):
                    issues.append("Archive is encrypted or password protected")

            # Check for nested archives (archives within archives)
            if self._security_rules.get("reject_nested_archives", True):
                nested_count = self._count_nested_archives(file_path, format_name)
                if nested_count > 3:  # More than 3 levels of nesting # TODO nested_count is a magic number, should be configurable.
                    issues.append(f"Excessive archive nesting detected: {nested_count} levels")

            # Check for suspicious file paths in archive
            suspicious_paths = self._check_archive_paths(file_path, format_name)
            if suspicious_paths:
                issues.extend([f"Suspicious file path in archive: {path}" for path in suspicious_paths])

            # Check for executable files in archive
            if self._security_rules["reject_executable"]:
                executable_files = self._check_archive_executables(file_path, format_name)
                if executable_files:
                    issues.extend([f"Executable file in archive: {exe}" for exe in executable_files])

            # Check total number of files in archive
            file_count = self._count_archive_files(file_path, format_name)
            max_files = self._security_rules.get("max_archive_files", 10000) # TODO max_files is a magic number, should be configurable.
            if file_count > max_files:
                issues.append(f"Archive contains too many files: {file_count} (max: {max_files})")

        except Exception as e:
            issues.append(f"Error analyzing archive: {e}")

        if issues:
            is_safe, risk_level = False, "high" if len(issues) > 2 else "medium"

        return is_safe, risk_level, issues

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

    def set_security_rules(self, rules: dict[str, Any]) -> None:
        """Set the dictionary of security rules."""
        for key, value in rules.items():
            if key in self._security_rules:
                self._security_rules[key] = value
            else:
                self._logger.warning(f"Unknown security rule: {key}")
        
        self._logger.info("Security rules updated", {"rules": self._security_rules})

    def set_allowed_formats(self, formats: list[str]) -> None:
        """Set the list of allowed formats."""
        self.allowed_formats = formats
        self._logger.info(f"Allowed formats updated '{self.allowed_formats}'")
    
    def set_file_size_limits(self, limits: dict[str, int]) -> None:
        """Set file size limits.
        
        Args:
            limits: Dictionary of file size limits by format (in bytes).
        """
        for key, value in limits.items(): # TODO Add pydantic validation here.
            self._file_size_limits[key] = value
        
        self._logger.info(f"File size limits updated to '{self._file_size_limits}'")
    

