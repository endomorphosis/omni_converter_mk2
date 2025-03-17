# Changelog

All notable changes to the Omni-Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-03-17

### Added
- Video format support with new VideoHandler class
  - MP4 format support
  - WebM format support
  - AVI format support
  - MKV format support
  - MOV format support
  - Comprehensive metadata extraction with pymediainfo
  - Support for video, audio, and subtitle track information
  - Fallback mode for environments without pymediainfo
  - Unit tests for VideoHandler
  - Integration with FormatRegistry
  - Increased format coverage from 80% to 100%
- Complete test coverage for all Manager components
  - Unit tests for BatchProcessor implementation
  - Unit tests for ResourceMonitor implementation
  - Unit tests for SecurityManager implementation
  - Integration tests for all Manager components
- Milestone: Achieved 100% format coverage across all MIME-type categories
  - Complete implementation of all planned format handlers
  - Full test coverage for all handlers
  - Comprehensive metadata extraction for all supported formats
  - Graceful fallbacks for all formats when specialized libraries are unavailable

## [0.6.0] - 2025-03-17

### Added
- Audio format support with new AudioHandler class
  - MP3 format support
  - WAV format support
  - OGG format support
  - FLAC format support
  - AAC format support
  - Comprehensive metadata extraction with pydub
  - Fallback mode for environments without pydub
  - Unit tests for AudioHandler
  - Integration with FormatRegistry
  - Increased format coverage from 60% to 80%

## [0.5.2] - 2025-03-17

### Added
- Enhanced documentation generator with path ignoring capabilities
  - Added ability to ignore specific paths when generating documentation
  - Support for a `.docignore` file to store paths to ignore
  - Command-line options to specify paths to ignore
  - Automatic saving of ignore paths for future use
  - Unit tests for the new ignore functionality
  - Updated TOOLS.md with documentation for the new features

## [0.5.1] - 2025-03-17

### Added
- Enhanced Command-Line Interface with batch processing
  - Directory processing support with BatchProcessor integration
  - Parallel processing with configurable thread count
  - Progress bar visualization using tqdm
  - Resource utilization reporting
  - Support for glob patterns and wildcards
  - Batch processing summary statistics

### Changed
- Updated main.py to use BatchProcessor for directory processing
- Enhanced command-line options with parallel processing and resource limits
- Updated IMPLEMENTATION_STATUS.md to mark CommandLineInterface as complete
- Updated PHASE16_README.md to reflect CLI implementation

## [0.5.0] - 2025-03-17

### Added
- Complete Manager Components
  - BatchProcessor: Orchestrates batch processing with parallel and sequential processing modes
  - ResourceMonitor: Monitors system resource usage with configurable CPU and memory limits
  - ErrorHandler: Centralizes error handling with detailed error tracking and reporting
  - SecurityManager: Validates file security and sanitizes content with configurable rules
  - BatchResult: Tracks batch processing results with detailed statistics
- Test coverage for Manager components
  - Unit tests for BatchResult implementation
  - Unit tests for ErrorHandler implementation
  - Unit tests for ResourceMonitor implementation
  - Unit tests for SecurityManager implementation
  - Unit tests for BatchProcessor implementation

### Changed
- Updated IMPLEMENTATION_STATUS.md to reflect completed Manager components
- Updated PHASE16_README.md to show Manager components are fully implemented
- Improved project stability with error tracking and resource monitoring

## [0.4.0] - 2025-03-16

### Added
- Complete Core Processing Pipeline
  - ProcessingPipeline: Orchestrates the entire conversion process
  - ContentExtractor: Extracts content using format handlers
  - TextNormalizer: Normalizes text with whitespace, line ending, and Unicode normalization
  - OutputFormatter: Formats text in txt, json, and markdown formats
  - ProcessingResult: Tracks and reports detailed processing results
- Enhanced CLI capabilities with format and normalizer options
- Support for different output formats (txt, json, markdown)
- Text normalization with configurable normalizers

### Changed
- Updated main.py to use full ProcessingPipeline for conversion
- Enhanced command-line interface with new options for normalization
- Updated IMPLEMENTATION_STATUS.md to reflect completed Core Processing components
- Updated PHASE16_README.md with complete Core Processing Class Group
- Reorganized next steps in documentation to focus on Manager components

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