# Changelog

All notable changes to the Omni-Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2025-03-16

### Added
- FormatRegistry component for centralized format handling
  - Centralized handler registration and management
  - Unified interface for format detection and content extraction
  - Format categorization by MIME type
  - Comprehensive test suite for the registry
- Updated main.py to use FormatRegistry for content extraction
- Revised format listing to use categorized formats from registry

### Changed
- Simplified process_file function in main.py using FormatRegistry
- Updated IMPLEMENTATION_STATUS.md with completed FormatRegistry
- Updated PHASE16_README.md to include FormatRegistry in Format Handlers group
- Reorganized next steps in IMPLEMENTATION_STATUS.md

## [0.2.0] - 2025-03-16

### Added
- Application format support with new ApplicationHandler class
  - PDF format support
  - JSON format support
  - DOCX format support
  - XLSX format support
  - ZIP format support
- New test file for ApplicationHandler
- Comprehensive documentation for the ApplicationHandler
- Added a test JSON file for manual testing

### Changed
- Updated main.py to handle application formats
- Updated format_handlers/__init__.py with application handler info
- Increased format coverage from 40% to 60%
- Improved IMPLEMENTATION_STATUS.md with updated next steps
- Updated PHASE16_README.md to reflect current status
- Updated README.md with application format support information

### Fixed
- Fixed missing format support in --list-formats output

## [0.1.0] - 2025-03-15

### Added
- Initial implementation of the Omni-Converter
- Core utility modules:
  - Configuration management
  - File system operations
  - Format detection
  - Logging
  - Validation
- Format handlers:
  - Base handler interface
  - Text handler (HTML, XML, plain text, CSV, calendar)
  - Image handler (JPEG, PNG, GIF, WebP, SVG)
- Command-line interface in main.py
- Comprehensive test suite:
  - Format support coverage tests
  - Processing success rate tests
  - Resource utilization tests
  - Processing speed tests
  - Error handling tests
  - Security effectiveness tests
  - Text quality tests
- Documentation:
  - README.md
  - SAD.md (System Architecture Document)
  - PRD.md (Product Requirements Document)
  - PHASE16_README.md
  - IMPLEMENTATION_STATUS.md