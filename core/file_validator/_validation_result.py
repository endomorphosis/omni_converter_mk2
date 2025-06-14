"""
Validation result module for the Omni-Converter.

This module provides the ValidationResult class for tracking the result of validation operations.
"""
from typing import Any, Callable


from dependencies import dependencies
BaseModel: Callable = dependencies.pydantic.BaseModel
Field: Callable = dependencies.pydantic.Field


class ValidationResult(BaseModel):
    """
    Result of validation operations.
    
    This class represents the result of validating a file or content, including
    validity status, errors, warnings, and context information.
    
    Attributes:
        is_valid (bool): Whether the validation was successful.
        errors (list[str]): list of errors encountered during validation.
        warnings (list[str]): list of warnings encountered during validation.
        validation_context (dict[str, Any]): Additional context about the validation.
    """
    is_valid: bool = True
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    validation_context: dict[str, Any] = Field(default_factory=dict)
    
    def add_error(self, error: str) -> None:
        """
        Add an error to the result.
        
        Args:
            error: The error message to add.
        """
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """
        Add a warning to the result.
        
        Args:
            warning: The warning message to add.
        """
        self.warnings.append(warning)
    
    def add_context(self, key: str, value: Any) -> None:
        """
        Add validation context to the result.
        
        Args:
            key: The context key.
            value: The context value.
        """
        self.validation_context[key] = value
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the validation result.
        """
        return self.model_dump()