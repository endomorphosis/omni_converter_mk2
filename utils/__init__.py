"""
Omni-Converter Utilities

This package provides core utility functions and classes that form the foundation of the
Omni-Converter application. These utilities handle configuration management, file system
operations, format detection, validation, and logging.

Modules:
    config: Configuration management with support for nested keys and default values.
        - Configs: Handles loading, saving, and validating configuration settings.
        
    filesystem: File system operations, metadata, and content extraction.
        - FileSystem: Utilities for file reading, writing, and information retrieval.
        - FileInfo: Information about files including size, type, and permissions.
        - FileContent: Container for file content with encoding support.
        
    format_detector: MIME type and extension-based format detection.
        - FormatDetector: Detects file formats based on content and extension.
        
    logger: Structured logging with multiple output targets.
        - Logger: Logging functionality with configurable levels and outputs.
        - LogRecord: Detailed log entries with context and metadata.
        
    validator: File validation with configurable rules.
        - BasicValidator: Validates files for processing with security checks.
        - ValidationResult: Contains validation status, errors, and metadata.

Implementation Status:
    These modules implement functionality described in the following class groups from the
    System Architecture Document:
    - Storage Class Group (FileSystem, Logger): 🔄 In Progress
    - Interface Class Group (Configs): 🔄 In Progress
    - Core Processing Class Group (FormatDetector, BasicValidator): 🔄 In Progress
    - Managers Class Group: ❌ Not Started
    - Format Handlers Class Group: ❌ Not Started
"""
