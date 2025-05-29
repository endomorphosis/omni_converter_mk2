from dataclasses import dataclass, field
from typing import Any


from types_ import Content


@dataclass
class NormalizedContent:
    """
    Normalized content from a file.
    
    This class represents normalized content with normalization metadata.
    
    Attributes:
        text (str): The normalized text content.
        metadata (dict[str, Any]): Metadata about the content.
        normalized_by (list[str]): list of normalizers applied to the content.
    """
    content: Content
    normalized_by: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """
        Convert to a dictionary.
        
        Returns:
            A dictionary representation of the normalized content.
        """
        content = self.content.to_dict()
        content.update({
            'normalized_by': self.normalized_by
        })
        return content
