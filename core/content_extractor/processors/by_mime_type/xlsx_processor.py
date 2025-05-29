from typing import Any, Callable, TypeVar
from unittest.mock import MagicMock


Workbook = TypeVar('Workbook') # For type-hinting


from logger import logger


class XLSXProcessor:
    """
    XLSX processor framework.
    
    This class provides functionality to extract text, metadata, and structure from XLSX files.

    Attributes:
        configs: Configuration settings for the processor.
        resources: Dictionary containing callable functions and metadata to implement processing.
        NOTE resources must include:
            _supported_formats: set of supported file formats. See `format_handlers.constants.Constants`.
            _processor_available: Boolean indicating if the processor is available.
            _processor_name: Name of the processor.
            _get_version: Callable function to get version information.
            _extract_structure: Callable function to extract structure from XLSX files. This includes:
            _extract_text: Callable function to extract text from XLSX files.
            _extract_metadata: Callable function to extract metadata from XLSX files.
            _open_xlsx_file: Callable function to open XLSX files.
            _extract_images: Callable function to extract images from XLSX files.

    Example Output:
        ```
        # example.xlsx
        ## Metadata
        - XLSX Document: Sales Report Q4 2023
        - Creator: Jane Smith
        - Subject: Quarterly Sales Analysis
        - Created: 2023-12-15T10:30:00
        - Total Sheets: 3
        - Sheet Names: Summary, Sales Data, Charts

        ## Content
        ### Sheet: Summary
        #### Spreadsheet Data
        |---------|----------|--------|
        | Quarter | Revenue  | Growth |
        |---------|----------|--------|
        | Q1      | $125,000 | 5.2%   |
        | Q2      | $132,000 | 8.1%   |
        | Q3      | $145,000 | 12.3%  |
        | Q4      | $158,000 | 15.8%  |
        |---------|----------|--------|

        #### Computed Fields
        |----------------|----------------------------------------|-------------------------------|
        | Quarter        | Revenue                                | Growth                        |
        |----------------|----------------------------------------|-------------------------------|
        | `="Q"&ROW()-1` | `=SUM(B2:B5)*0.25+RAND()*10000+120000` | `=(B2-110000)/110000*100&"%"` |
        | `="Q"&ROW()-1` | `=SUM(B2:B5)*0.28+RAND()*8000+125000`  | `=(B3-B2)/B2*100&"%"`         |
        | `="Q"&ROW()-1` | `=SUM(B2:B5)*0.31+RAND()*12000+130000` | `=(B4-B2)/B2*100&"%"`         |
        | `="Q"&ROW()-1` | `=SUM(B2:B5)*0.35+RAND()*15000+135000` | `=(B5-B2)/B2*100&"%"`         |
        |----------------|----------------------------------------|-------------------------------|

        #### Named Ranges
        - SalesData: Sheet1!$A$1:$E$100

        #### Images
        - Image: Chart1.png
        - Sheet: Charts
        - Dimensions: 800x600 pixels
        - Summary: This is a pie chart that shows the quarterly sales growth as compared with the previous year. The largest growth is in Q4.
        - Text: "Sales Growth by Quarter", "Q1", "Q2", "Q3", "Q4", "2023", "Sales Growth", "Revenue", "125,000", "132,000", "145,000", "158,000", "Growth", "5.2%", "8.1%", "12.3%", "15.8%"

        ### Sheet: Sales Data
        #### Spreadsheet Data
        ...
        ```
    """
    
    def __init__(self, resources: dict[str, Callable] = None, configs=None) -> None:
        """Initialize the XLSX processor."""
        self.configs = configs
        self.resources = resources

        self._supported_formats: set[str] = self.resources["supported_formats"]
        self._processor_available: bool = self.resources["processor_available"]
        self._processor_name: str = self.resources["processor_name"]

        self._get_version: Callable = self.resources["get_version"]
        self._extract_structure: Callable = self.resources["extract_structure"]
        self._extract_text: Callable = self.resources["extract_text"]
        self._extract_metadata: Callable = self.resources["extract_metadata"]
        self._open_xlsx_file: Callable = self.resources["open_xlsx_file"]

        # Optional image extraction function
        self._extract_images: Callable | MagicMock = self.resources["extract_images"]

    def can_process(self, format_name: str) -> bool:
        """
        Check if this processor can handle the given format.
        
        Args:
            format_name: The name of the format to check.
            
        Returns:
            True if this processor can handle the format and openpyxl is available,
            False otherwise.
        """
        return self._processor_available and format_name.lower() in self._supported_formats
    
    @property
    def supported_formats(self) -> list[str]:
        """
        Get the list of formats supported by this processor.
        
        Returns:
            A list of format names supported by this processor.
        """
        return self._supported_formats if self._processor_available else []
    
    def get_processor_info(self) -> dict[str, Any]:
        """
        Get information about this processor.
        
        Returns:
            A dictionary containing information about this processor.
        """
        info = {
            "name": self._processor_name,
            "supported_formats": self._supported_formats,
            "available": self._processor_available
        }
        
        if self._processor_available:
            info["version"] = self._get_version()
        
        return info

    def open_xlsx_file(self, data: bytes) -> 'Workbook':
        """
        Open an XLSX file and return the Workbook object.
        
        Args:
            data: The binary data of the XLSX document.
            
        Returns:
            An openpyxl Workbook object.
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            return self._open_xlsx_file(data)
        except Exception as e:
            logger.error(f"Error opening XLSX file: {e}")
            raise ValueError(f"Error opening XLSX file: {e}")

    def extract_text(self, data: bytes, options: dict[str, Any]) -> str:
        """
        Extract plain text from an XLSX document.
        
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.
                include_empty_cells: Whether to include empty cells (default: False)
                max_rows: Maximum number of rows to extract per sheet (default: 1000)
                
        Returns:
            Extracted text from the XLSX document.
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            return self._extract_text(data, options)
        except Exception as e:
            logger.error(f"Error extracting text from XLSX: {e}")
            raise ValueError(f"Error extracting text from XLSX: {e}")
    
    def extract_metadata(self, data: bytes, options: dict[str, Any]) -> dict[str, Any]:
        """
        Extract metadata from an XLSX document.
        
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.
            
        Returns:
            Metadata extracted from the XLSX document.
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            return self._extract_metadata(data, options)
        except Exception as e:
            logger.error(f"Error extracting metadata from XLSX: {e}")
            raise ValueError(f"Error extracting metadata from XLSX: {e}")
    
    def extract_structure(self, data: bytes, options: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract structural elements from an XLSX document.
        
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.
            
        Returns:
            A list of structural elements extracted from the XLSX document.
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            return self._extract_structure(data, options)
        except Exception as e:
            logger.error(f"Error extracting structure from XLSX: {e}")
            raise ValueError(f"Error extracting structure from XLSX: {e}")
        
    def extract_computed_fields(self, data: bytes, options: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract computed fields from an XLSX document.
        
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.
            
        Returns:
            A list of dictionaries containing computed fields extracted from the XLSX document.
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            return self._extract_structure(data, options, include_computed_fields=True)
        except Exception as e:
            logger.error(f"Error extracting computed fields from XLSX: {e}")
            raise ValueError(f"Error extracting computed fields from XLSX: {e}")

    def extract_images(self, data: bytes, options: dict[str, Any]) -> list[dict[str, Any]]:
        """
        Extract images from an XLSX document.
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.

        Returns:
            A list of dictionaries containing the following.
                - name: The name of the image file.
                - sheet_name: The name of the sheet where the image is located.
                - dimensions: The dimensions of the image (width x height) in pixels.
                - summary: A brief summary of the image content.
                - text: A list of text extracted from the image, if applicable.
        """
        try:
            return self._extract_images(data, options)
        except Exception as e:
            logger.error(f"Error extracting images from XLSX: {e}")
            raise ValueError(f"Error extracting images from XLSX: {e}")

    def process(self, data: bytes, options: dict[str, Any]) -> tuple[str, dict[str, Any], list[dict[str, Any]]]:
        """
        Process an XLSX document completely, extracting text, metadata, and structure.
        
        Args:
            data: The binary data of the XLSX document.
            options: Processing options.
            
        Returns:
            A tuple of (text content, metadata, sections).
            
        Raises:
            ValueError: If openpyxl is not available or the data cannot be processed as an XLSX.
        """
        try:
            # Open the XLSX file
            wb = self.open_xlsx_file(data)

            # Extract text, metadata, and structure
            metadata: dict[str, Any] = self.extract_metadata(wb, options)
            text = self.extract_text(wb, options)
            sections: list[dict[str, Any]] = self.extract_structure(wb, options)

            images = None
            if not isinstance(self._extract_images, MagicMock):
                images = self.extract_images(wb, options)

            # Create a human-readable text version
            text_content = [f"XLSX Document: {metadata.get('title', 'Untitled')}"]
            
            if "creator" in metadata:
                text_content.append(f"Creator: {metadata['creator']}")
            
            if "subject" in metadata:
                text_content.append(f"Subject: {metadata['subject']}")
            
            if "creation_date" in metadata:
                text_content.append(f"Created: {metadata['creation_date']}")
            
            if "sheet_count" in metadata:
                text_content.append(f"Total Sheets: {metadata['sheet_count']}")
                text_content.append(f"Sheet Names: {', '.join(metadata['sheets'])}")
            
            text_content.append("\n## Content\n")
            text_content.append(text)
            
            if images:
                text_content.append("\n## Images\n")
                for img in images:
                    text_content.append(f"Image: {img['name']}")
                    text_content.append(f"Sheet Name: {img['sheet_name']}")
                    text_content.append(f"Dimensions: {img['dimensions']} pixels")
                    text_content.append(f"Summary: {img['summary']}")
                    text_content.append(f"Text: {', '.join(img['text'])}")

            return "\n".join(text_content), metadata, sections

        except Exception as e:
            logger.error(f"Error processing XLSX document: {e}")
            raise ValueError(f"Error processing XLSX document: {e}")

