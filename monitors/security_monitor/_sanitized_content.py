from typing import Any


from types_ import Content


try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Pydantic is required for this module. Please install it with 'pip install pydantic'.")


class SanitizedContent:
    """
    Sanitized content from a file.
    
    This class extends the base Content class with sanitization information.
    
    Attributes:
        sanitization_applied (list[str]): list of sanitization techniques applied.
        removed_content (dict[str, Any]): Information about content that was removed.
    """
    content: Content
    sanitization_applied: list[str] = Field(default_factory=list)
    removed_content: dict[str, Any] = Field(default_factory=dict)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.

        Returns:
            A dictionary representation of the sanitized content.
        """
        result = Content.to_dict()
        result["sanitization_applied"] = self.sanitization_applied
        result["removed_content"] = self.removed_content
        return result