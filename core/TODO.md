# Core Module TODO List

## Current Focus: IoC Architecture Implementation

The core module needs to be refactored to follow the Inversion of Control (IoC) pattern as specified in CLAUDE.md and implemented in format_handlers/factory.py.

### High Priority Tasks

- [x] **Implement core/factory.py with IoC pattern for all core components**
  - ✅ Created factory functions for all core components following the 5-step pattern
  - ✅ Implemented dependency injection with resources dictionary
  - ✅ Ensured fail-fast approach for missing dependencies
  - ✅ Followed the exact pattern from format_handlers/factory.py

- [x] **Refactor content_extractor.py to follow IoC pattern**
  - ✅ Added resources and configs parameters to constructor
  - ✅ Moved all dependencies to resources dictionary
  - ✅ Implemented fail-fast dependency checking
  - ✅ Removed direct instantiation of dependencies

- [x] **Refactor output_formatter.py to follow IoC pattern**
  - ✅ Added resources and configs parameters to constructor
  - ✅ Moved all dependencies to resources dictionary (including NormalizedContent)
  - ✅ Implemented fail-fast dependency checking
  - ✅ Removed direct instantiation of dependencies

- [x] **Refactor text_normalizer.py to follow IoC pattern**
  - ✅ Added resources and configs parameters to constructor
  - ✅ Moved all dependencies to resources dictionary
  - ✅ Implemented fail-fast dependency checking
  - ✅ Removed direct instantiation of dependencies

- [x] **Update core/__init__.py to only export processing_pipeline from factory**
  - ✅ Removed all direct imports and instantiations
  - ✅ Import only the factory-created processing_pipeline
  - ✅ Cleaned up __all__ exports to only include processing_pipeline
  - ✅ Removed broken global instance creation

- [ ] **Update processing_pipeline.py to use IoC dependencies**
  - ⚠️ DEFERRED - Left as-is per instruction
  - Note: Removed direct configs import but kept existing structure
  - May need future updates for full IoC compliance

### Additional Completed Tasks

- [x] **Complete validator.py IoC refactoring**
  - ✅ Removed direct format_detector import
  - ✅ Added format_detector as injected resource dependency
  - ✅ Updated all format detection calls to use injected dependency
  - ✅ Enhanced factory.py to create and inject format_detector dependency
  - ✅ Removed obsolete make_validator() function from validator.py

### Medium Priority Tasks

- [x] **Complete format_detector.py _init_format_extensions method**
  - ✅ Implemented the missing method body
  - ✅ Map file extensions to format names using FORMAT_EXTENSIONS
  - Note: Implementation may evolve as refactoring progresses

### Guidelines

- All components must follow the exact IoC pattern from CLAUDE.md
- Use the 5-step factory pattern: import, resources dict, configs, class instantiation, return
- Implement fail-fast approach with KeyError for missing dependencies
- Never use .get() method when accessing resources - direct dictionary access only
- All configuration must come through configs parameter
- Follow the "types determine processors" principle