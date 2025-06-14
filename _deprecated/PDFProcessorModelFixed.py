from pydantic import BaseModel, Field
from typing import List, Any, Union, Optional, Dict

class PDFProcessorModelFixed(BaseModel):
    class_name: str = Field()
    format_name: str = Field()
    class_docstring: str = Field()
    type_vars: None = Field()
    imports: None = Field()
    required_resources: None = Field()
    resource_assignments: None = Field()
    optional_resources: None = Field()
    example_output: str = Field()
    methods: None = Field()