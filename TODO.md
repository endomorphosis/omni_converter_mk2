# Omni Converter MK2 - TODO List

## Current Focus: Inversion of Control Implementation

The project is currently implementing Inversion of Control (IoC) and Dependency Injection patterns to improve the codebase structure, testability, and maintainability.

### High Priority Tasks

- [ ] Complete the IoC refactoring for all format handlers
  - [x] Audio handler refactoring complete
  - [x] Image handler refactoring complete
  - [x] Text handler refactoring complete
  - [ ] Video handler refactoring
  - [ ] Application handler refactoring

- [ ] Create isolated dependency modules for all third-party libraries
  - [x] Create utils/dependency_modules/ structure
  - [x] Image processing: PIL, SVG, OCR (pytesseract)
  - [x] Text processing: BeautifulSoup, lxml, iCalendar, CSV/pandas
  - [ ] Video processing: pymediainfo, OpenCV, ffmpeg
  - [ ] Application processing: PDF, DOCX, XLSX handlers

- [ ] Integrate IoC architecture with main application
  - [ ] Update main.py to use the new factory-based initialization
  - [ ] Ensure backward compatibility with existing interfaces
  - [ ] Validate all components work correctly together

### Medium Priority Tasks

- [ ] Improve test coverage for the refactored code
  - [ ] Create unit tests for all refactored handlers
  - [ ] Add integration tests for the complete pipeline
  - [ ] Verify backward compatibility with existing tests

- [ ] Enhance documentation
  - [ ] Update architecture diagrams to reflect IoC pattern
  - [ ] Create detailed documentation for the dependency injection approach
  - [ ] Add usage examples for the new factory-based initialization

### Low Priority Tasks

- [ ] Performance optimization
  - [ ] Benchmark handler performance before and after refactoring
  - [ ] Identify and fix performance bottlenecks
  - [ ] Optimize memory usage for large file processing

- [ ] Add new features leveraging the IoC architecture
  - [ ] Enable runtime swapping of dependencies
  - [ ] Add plugin system for format handlers
  - [ ] Implement advanced configuration options

## Guidelines

- All code must follow the project's style guide and documentation standards
- Backward compatibility must be maintained throughout the refactoring
- Follow the "Never remove features" policy - obsolete code should be moved to 'deprecated' folders
- All dependencies should be explicitly defined and passed via resources dictionary
- Use fail-fast approach for required resources