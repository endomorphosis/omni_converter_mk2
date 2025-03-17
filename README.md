# Omni-Converter v1.0.0

A Python-based application designed to convert various file types to plaintext for Large Language Model (LLM) training data preparation.

## Overview

Omni-Converter is a versatile file conversion utility that handles a wide range of document types, including:
- Text documents (HTML, XML, plain text, CSV, calendar)
- Image files (JPEG, PNG, GIF, WebP, SVG)
- Application files (PDF, JSON, DOCX, XLSX, ZIP)
- Audio files (MP3, WAV, OGG, FLAC, AAC)
- Video files (MP4, WebM, AVI, MKV, MOV)

The primary purpose is to generate training data for Large Language Models (LLMs), providing high-quality plaintext extraction from various formats and comprehensive metadata for all supported file types.

## Features

- **Multi-format Support:** Convert multiple file types within a single batch
- **Text Extraction:** Extract readable text from text-based documents
- **Metadata Extraction:** Comprehensive metadata extraction for all supported formats
- **Centralized Format Registry:** Unified interface for format detection and handling
- **Batch Processing:** Process multiple files with appropriate error isolation
- **Parallel Execution:** Configurable parallel processing of files
- **Error Handling:** Continue processing despite individual file failures
- **Resource Management:** Configurable limits for CPU and memory usage
- **Security Validation:** Robust security checks for all processed files
- **100% Format Coverage:** Complete support for all 25 targeted formats across 5 categories

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/omni_converter.git
cd omni_converter

# Install dependencies
./install.sh
```

## Usage

### Command Line Interface

```bash
# Run the converter on a single file
./start.sh my_file.html

# Run with specific output file
./start.sh my_file.html -o output.txt

# List supported formats
./start.sh --list-formats

# Show version information
./start.sh --version

# Enable verbose output
./start.sh -v my_file.html
```

### Python API

```python
# Import the API
from interfaces.python_api import api

# Convert a single file
result = api.convert_file('my_file.html')
print(f"Extracted text: {result.content}")

# Process a directory of files
batch_result = api.convert_batch('/path/to/directory', output_dir='/path/to/output')
print(f"Processed {batch_result.total_files} files with {batch_result.successful_files} successful")

# Get supported formats
formats = api.get_supported_formats()
print(formats)

# Configure the converter
api.set_config({
    'output.format': 'json',
    'processing.normalize_text': True
})
```

For more examples, see the [examples directory](examples/).

## Supported Formats

| Category | Formats |
|----------|---------|
| **Text** | HTML, XML, Plain Text, CSV, Calendar (iCal) |
| **Image** | JPEG, PNG, GIF, WebP, SVG |
| **Audio** | MP3, WAV, OGG, FLAC, AAC |
| **Video** | MP4, WebM, AVI, MKV, MOV |
| **Application** | PDF, JSON, DOCX, XLSX, ZIP |

## Documentation

Detailed documentation is available in the `docs` directory:
- [Core Documentation](docs/index.md) - Main documentation index
- [System Architecture](SAD.md) - Architecture and implementation details
- [Product Requirements](PRD.md) - Product requirements specification
- [Phase 16 Implementation Plan](PHASE16_README.md) - Current implementation phase details
- [Implementation Status](IMPLEMENTATION_STATUS.md) - Detailed implementation status report

## Project Status

The project has reached version 1.1.0, with all core features implemented. Progress details are available in the [PHASE16_README.md](PHASE16_README.md) file.

Current implementation status:
- ✅ Test Suite: All test components have been implemented and passed
- ✅ Core Utilities: Configuration, logging, file system operations, format detection, and validation
- ✅ Format Handlers: Complete implementation of all handlers (Text, Image, Audio, Video, Application)
- ✅ Format Registry: Centralized registry for format detection and handler management
- ✅ Core Processing Pipeline: Complete pipeline with extraction, normalization, and output formatting
- ✅ Managers: Batch processing, resource monitoring, error handling, and security validation implemented
- ✅ Interfaces: Complete implementation of CLI, PythonAPI, ConfigManager, and InterfaceFactory

### Format Coverage

The project has achieved 100% format coverage across all targeted MIME-type categories:

| MIME-type Category | Coverage | Formats Implemented |
|-------------------|----------|---------------------|
| Text | 100% | 5/5 formats |
| Image | 100% | 5/5 formats |
| Audio | 100% | 5/5 formats |
| Video | 100% | 5/5 formats |
| Application | 100% | 5/5 formats |
| **Overall** | **100%** | **25/25 formats** |

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Python community for providing excellent libraries
- Open source projects that inspired this work