# Refactoring Opportunities: Dataclasses and Pydantic Models

This document identifies classes that could be refactored into either Python dataclasses or Pydantic models in the `core` and `format_handlers` directories.

## Dataclass Candidates

Classes that primarily store data with minimal behavior and would benefit from dataclass simplification:

### 1. `ProcessingResult` - `/home/kylerose1946/omni_converter_mk2/core/processing_result.py`

**Current Implementation:**
- Attributes: `success`, `file_path`, `output_path`, `format`, `errors`, `metadata`, `content_hash`, `timestamp`
- Methods: `add_error()`, `add_metadata()`, `to_dict()`, `get_error_string()`, `__str__()`

**Refactored as Dataclass:**
```python
@dataclass
class ProcessingResult:
    success: bool
    file_path: str
    output_path: str = ""
    format: str = ""
    errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    content_hash: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.success = False
    
    def add_metadata(self, key: str, value: Any) -> None:
        self.metadata[key] = value
    
    def get_error_string(self) -> str:
        if not self.errors:
            return "No errors"
        return "\n".join(f"- {error}" for error in self.errors)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'success': self.success,
            'file_path': self.file_path,
            'output_path': self.output_path,
            'format': self.format,
            'errors': self.errors,
            'metadata': self.metadata,
            'content_hash': self.content_hash,
            'timestamp': self.timestamp.isoformat()
        }
```

**Rationale:**
- Primarily stores data with simple initialization
- Clear attribute fields with defaults
- Minimal behavior beyond data storage/retrieval
- Benefits from simplified initialization and equality operations

### 2. `BatchResult` - `/home/kylerose1946/omni_converter_mk2/managers/batch_result.py`

**Current Implementation:**
- Attributes: `total_files`, `successful_files`, `failed_files`, `results`, `statistics`, `start_time`, `end_time`
- Methods: `add_result()`, `complete()`, `get_summary()`, `get_failed_files()`, `get_successful_files()`, `to_dict()`, `__str__()`

**Refactored as Dataclass:**
```python
@dataclass
class BatchResult:
    results: List[ProcessingResult] = field(default_factory=list)
    statistics: Dict[str, Any] = field(default_factory=dict)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    total_files: int = field(init=False)
    successful_files: int = field(init=False)
    failed_files: int = field(init=False)
    
    def __post_init__(self):
        # Calculate counts
        self.total_files = len(self.results)
        self.successful_files = sum(1 for r in self.results if r.success)
        self.failed_files = sum(1 for r in self.results if not r.success)
    
    def add_result(self, result: ProcessingResult) -> None:
        self.results.append(result)
        self.total_files += 1
        if result.success:
            self.successful_files += 1
        else:
            self.failed_files += 1
    
    def complete(self) -> None:
        self.end_time = datetime.now()
        self.statistics['duration_seconds'] = (self.end_time - self.start_time).total_seconds()
        self.statistics['success_rate'] = (
            (self.successful_files / self.total_files) * 100 if self.total_files > 0 else 0
        )
    
    # Other methods remain similar
```

**Rationale:**
- Primarily stores and tracks processing results
- Derived fields can be calculated in post_init
- Clear attribute fields with defaults
- Benefits from reduced initialization boilerplate

### 3. `FormattedOutput` - `/home/kylerose1946/omni_converter_mk2/core/output_formatter.py`

**Current Implementation:**
- Attributes: `content`, `format`, `metadata`, `output_path`
- Methods: `to_dict()`, `write_to_file()`

**Refactored as Dataclass:**
```python
@dataclass
class FormattedOutput:
    content: str
    format: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    output_path: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'content': self.content,
            'format': self.format,
            'metadata': self.metadata,
            'output_path': self.output_path
        }
    
    def write_to_file(self, output_path: Optional[str] = None) -> str:
        # Method implementation remains the same
```

**Rationale:**
- Simple data container with minimal behavior
- Primarily stores formatted output with basic operations
- Straightforward serialization to dictionary
- Benefits from simplified initialization and repr

## Pydantic Model Candidates

Classes that would benefit from Pydantic's validation capabilities, serialization features, and inheritance model:

### 1. `Content` - `/home/kylerose1946/omni_converter_mk2/format_handlers/base_handler.py`

**Current Implementation:**
- Attributes: `text`, `metadata`, `sections`, `source_format`, `source_path`, `extraction_time`
- Methods: `to_dict()`

**Refactored as Pydantic Model:**
```python
class Content(BaseModel):
    text: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    sections: List[Dict[str, Any]] = Field(default_factory=list)
    source_format: str = ""
    source_path: str = ""
    extraction_time: datetime = Field(default_factory=datetime.now)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
```

**Rationale:**
- Data container that benefits from validation
- Has a clear structure that spans multiple derived classes
- Used across the system as data transfer object
- Serialization/deserialization is important for this class
- Pydantic's JSON handling simplifies working with timestamps

### 2. `NormalizedContent` - `/home/kylerose1946/omni_converter_mk2/core/text_normalizer.py`

**Current Implementation:**
- Inherits from `Content`
- Additional attribute: `normalized_by`
- Overrides: `to_dict()`

**Refactored as Pydantic Model:**
```python
class NormalizedContent(Content):
    normalized_by: List[str] = Field(default_factory=list)
```

**Rationale:**
- Inherits from Content, so Pydantic's inheritance model is appropriate
- Benefits from validation for the `normalized_by` list
- Serialization/deserialization with proper inheritance

### 3. `ValidationResult` (New class from validation functionality)

Multiple files contain validation logic that could be encapsulated in a Pydantic model:

**Implemented as Pydantic Model:**
```python
class ValidationResult(BaseModel):
    is_valid: bool
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    validation_context: Dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str) -> None:
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        self.warnings.append(warning)
```

**Rationale:**
- Multiple components perform validation but lack a structured result object
- Could standardize validation results across the system
- Pydantic's validation would help enforce the structure

## Benefits of Refactoring

### Dataclasses
1. **Reduced Boilerplate**: Eliminates repetitive `__init__` methods
2. **Automatic Methods**: Provides `__repr__`, `__eq__`, and other special methods
3. **Type Safety**: Integrates well with type hints for better IDE support
4. **Cleaner Code**: More readable class definitions that highlight data structure
5. **Default Values**: Simple syntax for default values with `field(default_factory=list)`

### Pydantic Models
1. **Validation**: Automatic validation of data with clear error messages
2. **Serialization**: Built-in JSON serialization/deserialization
3. **Documentation**: Ability to generate OpenAPI documentation
4. **Schema Definition**: Clear schema of data models for documentation
5. **Inheritance**: Clean model inheritance that maintains validation
6. **Config Options**: Fine-grained control over model behavior

## Implementation Strategy

1. Start with standalone data containers like `ProcessingResult` and `FormattedOutput`
2. Then tackle the `Content` model and its derivatives
3. Gradually refactor data-oriented parts of the codebase
4. Add appropriate unit tests for the refactored components
5. Consider introducing a shared base model for common functionality

## Required Imports

For dataclasses:
```python
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from datetime import datetime
```

For Pydantic models:
```python
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime
```