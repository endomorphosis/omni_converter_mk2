"""
Output formatter module for the Omni-Converter.

This module provides the OutputFormatter class for formatting extracted content
into different output formats.
"""
import json
import os
from typing import Any, Optional


from types_ import Configs, Content, FormatterFunc, FormattedOutput, Logger


class OutputFormatter:
    """
    Output formatter for the Omni-Converter.
    
    This class formats extracted content into different output formats.
    
    Attributes:
        output_formats (dict[str, FormatterFunc]): Dictionary of formatter functions.
        default_format (str): The default output format.
    """
    
    def __init__(self, resources: dict[str, Any], configs: Configs):
        """
        Initialize an output formatter.
        
        Args:
            resources: A dictionary of callable objects and dependencies.
            configs: A pydantic model containing configuration settings.
        """
        self.resources = resources
        self.configs = configs
        
        # Extract required resources
        self._normalized_content = self.resources["normalized_content"]
        self._formatted_output = self.resources["formatted_output"]
        self._logger: Logger = self.resources["logger"]
        
        # Get default format from config or use 'txt' as fallback
        self.default_format = self.configs.get_config_value('output.default_format', 'txt')
        
        self.output_formats: dict[str, FormatterFunc] = {}
        
        # Register default formatters
        self._register_default_formatters()
    
    def _register_default_formatters(self) -> None:
        """Register the default output formatters."""
        self._logger.debug("Registering default output formatters")
        
        # Clear existing formatters to avoid duplicates
        self.output_formats = {}
        
        # Register standard formats
        self.output_formats["txt"] = self._format_as_txt
        self.output_formats["json"] = self._format_as_json
        self.output_formats["md"] = self._format_as_markdown
        
        # Log the registered formats
        self._logger.info(f"Registered output formats: {', '.join(self.output_formats.keys())}")
    
    def _format_as_txt(self, content: Content) -> str:
        """
        Format content as plain text.
        
        Args:
            content: The content to format.
            
        Returns:
            The formatted content as plain text.
        """
        return content.text
    
    def _format_as_json(self, content: Content) -> str:
        """
        Format content as JSON.
        
        Args:
            content: The content to format.
            
        Returns:
            The formatted content as JSON.
        """
        return json.dumps(content.to_dict(), indent=2)
    
    def _format_as_markdown(self, content: Content) -> str:
        """
        Format content as Markdown.
        
        Args:
            content: The content to format.
            
        Returns:
            The formatted content as Markdown.
        """
        # Start with a header including the source file
        md = f"# Content from {os.path.basename(content.source_path)}\n\n"
        
        # Add metadata section
        if content.metadata:
            md += "## Metadata\n\n"
            for key, value in content.metadata.items():
                md += f"- **{key}**: {value}\n"
            md += "\n"
        
        # Add normalization info if available
        if isinstance(content, self.normalized_content) and content.normalized_by:
            md += "## Normalization\n\n"
            md += "Applied normalizers:\n\n"
            for normalizer in content.normalized_by:
                md += f"- {normalizer}\n"
            md += "\n"
        
        # Add content sections if available
        if content.sections:
            md += "## Sections\n\n"
            for section in content.sections:
                section_type = section.get('type', 'Section')
                section_title = section.get('title', section_type)
                section_content = section.get('content', '')
                
                md += f"### {section_title}\n\n"
                md += f"{section_content}\n\n"
        
        # Add main content
        md += "## Content\n\n"
        md += content.text
        
        return md
    
    def format_output(
        self,
        content: Content,
        format: Optional[str] = None,
        options: Optional[dict[str, Any]] = None,
        output_path: Optional[str] = None
    ) -> FormattedOutput:
        """
        Format content for output.
        
        Args:
            content: The content to format.
            format: The output format. If None, the default format is used.
            options: Optional formatting options.
            output_path: The path where the output will be written.
            
        Returns:
            The formatted output.
            
        Raises:
            ValueError: If the specified format is not supported.
        """
        # Use the default format if none is specified
        output_format = format or self.default_format
        self._logger.debug(f"Formatting output for {content.source_path}", {'format': output_format})
        
        # Try to get from options if not directly specified
        if output_format not in self.output_formats and options and 'format' in options:
            output_format = options['format']
        
        # If still not valid, default to txt
        if output_format not in self.output_formats:
            self._logger.warning(f"Unsupported format: {output_format}, defaulting to {self.default_format}")
            output_format = self.default_format
        
        # Format the content
        formatter = self.output_formats[output_format]
        formatted_content = formatter(content)
        
        # Create formatted output
        return  self._formatted_output(
            content=formatted_content,
            format=output_format,
            metadata={
                'source_format': content.source_format,
                'source_path': content.source_path,
                'extraction_time': content.extraction_time.isoformat(),
                **(options or {})
            },
            output_path=output_path
        )
    
    def register_format(self, format_name: str, formatter: FormatterFunc) -> None:
        """
        Register an output format.
        
        Args:
            format_name: The name of the format.
            formatter: The formatter function.
            
        Raises:
            ValueError: If a formatter for the format already exists.
        """
        if format_name in self.output_formats:
            raise ValueError(f"A formatter for '{format_name}' already exists")
        
        self.output_formats[format_name] = formatter
        self._logger.debug(f"Registered output format: {format_name}")

    @property
    def available_formats(self) -> list[str]:
        """
        Get the available output formats.
        
        Returns:
            List of available output formats.
        """
        return list(self.output_formats.keys())
