# TODO: Format Handlers Refactoring

This document tracks the tasks and issues related to implementing Inversion of Control (IoC) via Dependency Injection for format handlers.

## IMPORTANT: File Preservation Policy

**NEVER DELETE ANY FILES** during this refactoring. According to project guidelines, once a feature has been implemented, it must never be removed, even if it causes test failures. Instead:

- Move obsolete or unessential files to a 'deprecated' folder
- Maintain backward compatibility with existing code
- Adapt tests to match new functionality rather than removing features

## Completed Tasks

- [x] Create 'deprecated' folder for storing obsolete files
- [x] Finalize `unified_handler.py` implementation
  - [x] Fix indentation issues
  - [x] Complete the `map_extension_to_format` function to handle all supported extensions
  - [x] Remove inheritance in favor of composition
  - [x] Centralize resource extraction in constructor
  - [x] Implement proper error handling
- [x] Refactor audio handler to use the new pattern
  - [x] Create `refactored_audio_handler.py` using composition
  - [x] Convert class methods to standalone functions
  - [x] Add factory function for dependency injection
- [x] Create a refactored format registry implementation
  - [x] Implement with resource injection
  - [x] Add factory functions for handler creation
- [x] Add a factory module for centralized component creation
  - [x] Implement handler factory functions
  - [x] Add initialization function for format registry
- [x] Create utils/dependency_modules/ directory for isolated third-party dependencies
  - [x] Create pil_processor.py for PIL-based image processing
  - [x] Create svg_processor.py for SVG file handling
  - [x] Create pytesseract_processor.py for OCR functionality
  - [x] Create skeleton_vllm_processor.py as placeholder for advanced ML-based processing
  - [x] Create beautiful_soup_processor.py for HTML processing
  - [x] Create lxml_processor.py for XML processing
  - [x] Create icalendar_processor.py for calendar file handling
  - [x] Create csv_processor.py for CSV handling
- [x] Refactor image handler to use the new IoC pattern
  - [x] Create `refactored_image_handler.py` using composition
  - [x] Extract PIL, SVG, and OCR dependencies to dedicated modules
  - [x] Implement fail-fast approach for required resources
- [x] Refactor text handler to use the new IoC pattern
  - [x] Create `refactored_text_handler.py` using composition
  - [x] Extract HTML, XML, calendar, and CSV dependencies to dedicated modules
  - [x] Ensure all text-based formats are properly handled
- [x] Update factory.py to include new handlers
  - [x] Add image handler to factory
  - [x] Add text handler to factory
  - [x] Add initialization for all processors

## Remaining Tasks

- [ ] Update remaining format handlers to use the new IoC pattern
  - [ ] Refactor `video_handler.py` to use the new pattern
  - [ ] Refactor `application_handler.py` to use the new pattern

- [ ] Create additional processor modules for remaining dependencies
  - [ ] Create pymediainfo_processor.py for video metadata extraction
  - [ ] Create cv2_processor.py for video frame extraction
  - [ ] Create ffmpeg_processor.py for video processing
  - [ ] Create pdf_processor.py for PDF handling
  - [ ] Create docx_processor.py for DOCX handling
  - [ ] Create xlsx_processor.py for XLSX handling

- [ ] Update main.py and other modules to use the new registry
  - [ ] Replace global format_registry with factory-created instance
  - [ ] Update imports to use new modules

- [ ] Create comprehensive tests for the refactored code
  - [ ] Test the unified handler implementation
  - [ ] Test all handlers with the new pattern
  - [ ] Test the registry with dependency-injected handlers
  - [ ] Test integration with the processing pipeline

- [ ] Update documentation to reflect the new architecture
  - [ ] Document the IoC pattern and dependency injection approach
  - [ ] Update handler documentation to reflect the new pattern
  - [ ] Create diagrams illustrating the new architecture
  - [ ] Document the preservation strategy for obsolete files

## Implementation Notes

1. All handlers should follow the pattern established in `refactored_audio_handler.py`:
   - No inheritance (use composition)
   - Class methods converted to standalone functions
   - Factory function for creation with dependencies
   - Resources passed explicitly, not imported

2. The BaseFormatHandler class in unified_handler.py now:
   - Takes only resources and configs parameters
   - Extracts specific resources in the constructor (fail-fast)
   - Passes file_path and format to processors via options dictionary

3. New code organization:
   - Main handler logic in unified_handler.py
   - Format-specific processors in separate modules
   - Factory functions in factory.py
   - Constants in constants.py

4. Technical requirements:
   - Python 3.10+ for match/case syntax
   - Pydantic for data models
   - Consistent type hints throughout