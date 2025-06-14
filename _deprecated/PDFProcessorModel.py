from pydantic import BaseModel, Field
from typing import List, Any, Union, Optional, Dict

class PDFProcessorModel(BaseModel):
    class_name: Optional[str] = Field(default=None)
    format_name: Optional[str] = Field(default=None)
    class_docstring: Optional[str] = Field(default=None)
    type_vars: Optional[None] = Field(default=None)
    imports: Optional[None] = Field(default=None)
    required_resources: Optional[None] = Field(default=None)
    resource_assignments: Optional[None] = Field(default=None)
    optional_resources: Optional[None] = Field(default=None)
    example_output: Optional[str] = Field(default=None)
    methods: Optional[None] = Field(default=None)