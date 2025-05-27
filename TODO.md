# Omni Converter MK2 - TODO List

## Current Focus: IoC Architecture Testing & Integration

The project has implemented a complete Inversion of Control (IoC) architecture with dependency injection across **both format handlers AND core modules**. **CRITICAL**: This implementation requires comprehensive testing before integration.

### High Priority Tasks

- [ ] **CRITICAL: Test core module IoC architecture implementation**
  - [ ] Create unit tests for core/factory.py component creation
  - [ ] Test processing pipeline factory function with dependencies
  - [ ] Verify all core components follow IoC pattern correctly
  - [ ] Test fail-fast behavior for missing core dependencies
  - [ ] Validate ProcessingPipeline works with factory-created components
  - [ ] Test BasicValidator with injected format_detector dependency

- [ ] **CRITICAL: Test format handlers IoC architecture implementation** 
  - [ ] Create unit tests for format_handlers/factory.py processor creation
  - [ ] Test make_processor function with various dependency scenarios
  - [ ] Verify multi-dependency fallback system works correctly
  - [ ] Test automatic mocking when dependencies unavailable
  - [ ] Validate all processor types follow standardized pattern

- [ ] **Test processor hierarchy and delegation**
  - [ ] Test ability processors (image, text, video, ocr)
  - [ ] Test MIME-type specific processors (xlsx, pdf, html, etc.)
  - [ ] Verify delegation chain: specific → ability → dependency modules
  - [ ] Test cross-processor communication (e.g., XLSX with images)

- [ ] **Integration testing with main application**
  - [ ] Update main.py to use new factory-based initialization for core
  - [ ] Test backward compatibility with existing interfaces
  - [ ] Validate end-to-end processing pipeline works
  - [ ] Ensure no regression in functionality

### Medium Priority Tasks

- [ ] Improve test coverage for the refactored code
  - [ ] Create unit tests for all refactored core components
  - [ ] Create unit tests for all refactored format handlers
  - [ ] Add integration tests for the complete pipeline
  - [ ] Verify backward compatibility with existing tests

- [ ] Enhance documentation
  - [ ] Update architecture diagrams to reflect IoC pattern in both core and format handlers
  - [ ] Create detailed documentation for the dependency injection approach
  - [ ] Add usage examples for the new factory-based initialization
  - [ ] Document the core module refactoring completion

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