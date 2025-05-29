from typing import Any


try:
    from pydantic import BaseModel, Field
except ImportError:
    raise ImportError("Pydantic is required for this module. Please install it with 'pip install pydantic'.")


class SecurityResult(BaseModel):
    """
    Result of security validation.
    
    This class represents the result of security validation for a file.
    
    Attributes:
        is_safe (bool): Whether the file is considered safe.
        issues (list[str]): list of security issues found.
        risk_level (str): Risk level assessment ('low', 'medium', 'high').
        metadata (dict[str, Any]): Additional metadata about the security check.
    """
    is_safe: bool
    issues: list[str] = Field(default_factory=list)
    risk_level: str = "low"
    metadata: dict[str, Any] = Field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.

        Returns:
            A dictionary representation of the security result.
        """
        return self.model_dump()