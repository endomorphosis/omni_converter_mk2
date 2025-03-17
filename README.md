# Omni-Converter

A Python-based application designed to convert various file types to plaintext for Large Language Model (LLM) training data preparation.

## Overview

Omni-Converter is a versatile file conversion utility that handles a wide range of document types, including:
- Text documents (HTML, XML, plain text, CSV, calendar)
- Image files (JPEG, PNG, GIF, WebP, SVG)
- Application files (PDF, JSON, DOCX, XLSX, ZIP)
- Audio files (coming soon)
- Video files (coming soon)

The primary purpose is to generate training data for Large Language Models (LLMs), providing high-quality plaintext extraction from various formats.

## Features

- **Multi-format Support:** Convert multiple file types within a single batch
- **Text Extraction:** Extract readable text from text-based documents
- **Centralized Format Registry:** Unified interface for format detection and handling
- **Batch Processing:** Process multiple files with appropriate error isolation
- **Error Handling:** Continue processing despite individual file failures
- **Resource Management:** Configurable limits for CPU and memory usage

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/omni_converter.git
cd omni_converter

# Install dependencies
./install.sh
```

## Usage

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

## Supported Formats

- **Text:** HTML, XML, Plain Text, CSV, Calendar (iCal)
- **Image:** JPEG, PNG, GIF, WebP, SVG
- **Application:** PDF, JSON, DOCX, XLSX, ZIP
- **Audio:** (Coming soon)
- **Video:** (Coming soon)

## Documentation

Detailed documentation is available in the `docs` directory:
- [Core Documentation](docs/index.md) - Main documentation index
- [System Architecture](SAD.md) - Architecture and implementation details
- [Product Requirements](PRD.md) - Product requirements specification
- [Phase 16 Implementation Plan](PHASE16_README.md) - Current implementation phase details
- [Implementation Status](IMPLEMENTATION_STATUS.md) - Detailed implementation status report

## Project Status

The project is currently in active development. Progress is tracked in the [PHASE16_README.md](PHASE16_README.md) file.

Current implementation status:
- ✅ Test Suite: All test components have been implemented
- ✅ Core Utilities: Configuration, logging, file system operations, format detection, and validation
- ✅ Format Handlers: Base handler interface with text, image, and application handlers implemented
- ✅ Format Registry: Centralized registry for format detection and handler management
- ✅ Core Processing Pipeline: Complete pipeline with extraction, normalization, and output formatting
- ❌ Managers: Not started
- 🔄 Interfaces: Basic CLI in main.py and ConfigManager implemented

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Python community for providing excellent libraries
- Open source projects that inspired this work