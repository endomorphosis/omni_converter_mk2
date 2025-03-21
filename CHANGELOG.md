# Changelog

All notable changes to the Omni-Converter project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.4.0] - 2025-03-21

### Added
- DOCX processor implementation using python-docx
  - Added DocxProcessor with full DOCX parsing capabilities
  - Added text extraction from paragraphs and tables
  - Added metadata extraction including title, author, and document properties
  - Added structure extraction for headings, sections, and tables
- Enhanced application handler to use DOCX processor
  - Integrated DOCX processor into the application handler pipeline
  - Added graceful fallback when python-docx is not available
  - Preserved backward compatibility with existing code
- Comprehensive test coverage for DOCX functionality
  - Unit tests for DocxProcessor component
  - Integration tests with ApplicationHandler
  - Tests for fallback behavior when python-docx is unavailable
- Added documentation for DOCX processor architecture

### Changed
- Refactored ApplicationHandler to use the processor architecture for DOCX files
- Updated implementation status in project documentation
- Enhanced error handling for DOCX processing

### Technical Details
- Extended dependency checking for python-docx library
- Added content extraction from tables and formatted text
- Implemented proper document structure analysis
- Enhanced fallback ZIP-based extraction when library is not available

## [1.3.0] - 2025-03-21

### Added
- OCR capability for image processing using PyTesseract
  - Added ImageProcessor interface for image processing
  - Implemented PyTesseractProcessor with OCR capabilities
  - Added text extraction from images with multiple language support
  - Added metadata extraction including dimensions, format, and EXIF data
  - Added visual feature extraction including text regions and bounding boxes
- Enhanced image handler to use OCR processor
  - Integrated OCR into the image processing pipeline
  - Added graceful fallback when Tesseract is not available
  - Preserved backward compatibility with existing code
- Comprehensive test coverage for OCR functionality
  - Unit tests for PyTesseractProcessor component
  - Integration tests with ImageHandler
  - Tests for fallback behavior when OCR is unavailable
- Expanded processor architecture documentation
  - Updated format handlers documentation with processor details
  - Added dedicated README for the processors module
  - Extended main documentation with recent updates

### Changed
- Refactored ImageHandler to use the processor architecture
- Updated documentation to reflect new OCR capabilities
- Updated implementation status in project documentation
- Enhanced error handling for OCR processing

### Technical Details
- Extended Strategy pattern across all processors for consistency
- Implemented proper dependency checking for Tesseract
- Added support for multiple OCR languages and configurations
- Implemented feature extraction capabilities beyond basic OCR

## [1.2.0] - 2025-03-18

### Added
- Enhanced format handlers with processor architecture using Strategy pattern
  - Created processor interfaces with dependency inversion
  - Implemented PDF processing with PyPDF2
  - Implemented speech-to-text with Whisper
  - Added support for text extraction from all PDF pages
  - Added support for PDF metadata extraction
  - Added support for audio transcription with timestamps
  - Added waveform data extraction for audio files
- Added comprehensive unit tests for manager components
  - Complete test coverage for BatchProcessor component
  - Complete test coverage for ResourceMonitor component
  - Complete test coverage for SecurityManager component
  - Integration tests for all manager components

### Changed
- Refactored PDF parsing to use PyPDF2 processor
- Refactored audio handler to use Whisper processor
- Updated documentation to reflect new architecture
- Added required dependencies to requirements.txt
- Improved error handling with graceful fallbacks

### Technical Details
- Implemented BaseProcessor and specialized processor interfaces
- Created modular processor implementations with dependency checks
- Added support for multiple Whisper models (tiny to large)
- Enhanced PDF processing with structure extraction
- Implemented robust test fixtures with mocking of external dependencies
- Added tests for edge cases in batch processing, resource monitoring, and security validation

## [1.1.0] - 2025-03-17

### Added
- Programmatic access with new PythonAPI and InterfaceFactory
  - PythonAPI implementation for programmatic file conversion
  - InterfaceFactory for creating different interface instances
  - Single file and batch conversion methods
  - Configuration management methods
  - Comprehensive test coverage for all API methods
  - Example scripts demonstrating API usage
  - Detailed documentation for programmatic usage
  - Integration with existing components (processing pipeline, batch processor, format registry)

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