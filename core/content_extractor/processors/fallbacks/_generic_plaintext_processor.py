
from typing import Any, Tuple

def process_plaintext(
        file_content: Any, 
        options: dict[str, Any]
        ) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
    """
    Process a plain text file and extract content.
    
    Args:
        file_content: The file content to process (text).
        options: Processing options including format information.
            Must contain:
            - file_path: Path to the text file
            
    Returns:
        Tuple of (text content, metadata, sections).
        
    Raises:
        Exception: If an error occurs during processing.
    """
    # Get text content
    if hasattr(file_content, 'get_as_text'):
        text = file_content.get_as_text()
    else:
        text = file_content
    
    # Plain text is already in the desired format
    metadata = {
        'format': 'plain',
        'line_count': text.count('\n') + 1,
        'character_count': len(text),
        'word_count': len(text.split())
    }
    
    # Create a single section
    sections = [{
        'type': 'text',
        'content': text
    }]
    
    return text, metadata, sections
