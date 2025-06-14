"""
XLSX processor implementation using openpyxl.

This module provides a concrete implementation of DocumentProcessor for XLSX files
using the openpyxl library.
"""
import io
from typing import Any, Callable, Optional, BinaryIO
from datetime import datetime

from logger import logger
from dependencies import dependencies

# #### Pictures
# - Image: Chart1.png
# - Sheet Name: Charts
# - Dimensions: A1:D10
# - Summary: This is a pie chart that shows the quarterly sales growth as compared with the previous year. The largest growth is in Q4.
# - Text: "Sales Growth by Quarter", "Q1", "Q2", "Q3", "Q4", "2023", "Sales Growth", "Revenue", "125,000", "132,000", "145,000", "158,000", "Growth", "5.2%", "8.1%", "12.3%", "15.8%"
# ```

def open_xlsx_file(data: bytes) -> Optional[BinaryIO]:
    # Create a file-like object from the bytes
    xlsx_file = io.BytesIO(data)

    # Open the XLSX file
    wb = dependencies.openpyxl.load_workbook(xlsx_file, read_only=True, data_only=True)

    return wb


def extract_text(data: bytes, options: dict[str, Any]) -> str:
    """
    Extract text from an XLSX document using openpyxl.

    Args:
        data: The binary data of the XLSX document.
        options: Processing options.
            - include_empty_cells: Whether to include empty cells (default: False)
            - max_rows: Maximum number of rows to extract per sheet (default: 1000)
    Returns:
        Extracted text from the XLSX document.

    Example Output:
    ```python
    {
        "include_empty_cells": False,
        "max_rows": 1000
    }
    ```

    Example of Formatted Output:
    ## Content
    ### Sheet: Cells
    ```markdown
        ## Content
        ### Sheet: Cells
        |---------|---------|--------|
        | Quarter | Revenue | Growth |
        |---------|---------|--------|
        | Q1      | $125,000| 5.2%   |
        | Q2      | $132,000| 8.1%   |
        | Q3      | $145,000| 12.3%  |
        | Q4      | $158,000| 15.8%  |
        |---------|---------|--------|
    ```
    """
    wb = open_xlsx_file(data)

    # Get options
    # TODO Make these values explicit in higher up in the dependency chain.
    include_empty_cells = options.get('include_empty_cells', False)
    max_rows = options.get('max_rows', 1000)
    
    # Extract text from each sheet
    sheet_texts = []
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]

        # Add the markdown headers
        sheet_texts.append(f"## Content")
        sheet_texts.append(f"### Sheet: {sheet_name}")

        # Extract data from cells
        rows = []
        row_count = 0
        
        for row in ws.iter_rows(max_row=max_rows):
            row_count += 1
            cells = []
            
            for cell in row:
                value = cell.value
                
                # Format the value as a string
                match value:
                    case None:
                        if include_empty_cells:
                            cells.append("")
                    case datetime():
                        cells.append(value.strftime("%Y-%m-%d %H:%M:%S"))
                    case str():
                        cells.append(str(value))
                    case _:
                        pass

            # Only add non-empty rows or rows with at least some content
            if any(cell.strip() for cell in cells):
                rows.append(cells)
        
        # Format as markdown table if we have data
        if rows:
            # Create table header separator
            if rows:
                num_cols = len(rows[0]) if rows else 0
                separator = "|" + "|".join(["-" * 9 for _ in range(num_cols)]) + "|"
                
                # Format rows as table
                table_rows = []
                for i, row in enumerate(rows):
                    # Pad row to match column count
                    padded_row = row + [""] * (num_cols - len(row))
                    formatted_row = "| " + " | ".join(f"{cell:<8}" for cell in padded_row) + " |"
                    table_rows.append(formatted_row)
                    
                    # Add separator after first row (header)
                    if i == 0:
                        table_rows.append(separator)
                
                sheet_texts.extend(table_rows)
        
        # Add notice if we hit the row limit
        if row_count >= max_rows:
            sheet_texts.append(f"\n[Row limit of {max_rows} reached. Additional rows not shown.]")
    
    # Join all sheets
    return "\n".join(sheet_texts)


def extract_metadata(data: bytes) -> dict[str, Any]:
    """
    Example of Formatted Output:
    ```markdown
        ## Metadata
        - XLSX Document: Sales Report Q4 2023
        - Creator: Jane Smith
        - Subject: Quarterly Sales Analysis
        - Created: 2023-12-15T10:30:00
        - Total Sheets: 3
        - Sheet Names: Summary, Sales Data, Charts
        - Number of Images: 2
    ```
    """
    wb = open_xlsx_file(data)

    # Extract document info
    metadata = {
        "file_size_bytes": len(data),
        "sheet_count": len(wb.sheetnames),
        "sheets": wb.sheetnames
    }

    # Extract document properties
    if hasattr(wb, "properties"):
        props = wb.properties
        prop_mappings = {
            "title": "title",
            "creator": "creator", 
            "subject": "subject",
            "keywords": "keywords",
            "category": "category",
            "description": "description",
            "lastModifiedBy": "last_modified_by",
            "revision": "revision"
        }
        
        # Map properties to metadata keys
        for prop_attr, meta_key in prop_mappings.items():
            if hasattr(props, prop_attr) and getattr(props, prop_attr):
                metadata[meta_key] = getattr(props, prop_attr)
        
        # Handle date properties separately
        for date_attr, meta_key in [("created", "creation_date"), ("modified", "modification_date")]:
            if hasattr(props, date_attr) and getattr(props, date_attr):
                date_val = getattr(props, date_attr)
                metadata[meta_key] = date_val.isoformat() if hasattr(date_val, "isoformat") else str(date_val)

    # Extract sheet statistics
    sheet_stats = []
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Get dimensions if available
        dimensions = "Unknown"
        if hasattr(ws, "calculate_dimension") and callable(getattr(ws, "calculate_dimension")):
            try:
                dimensions = ws.calculate_dimension()
            except:
                # Some sheets may not have data
                dimensions = "Empty or Error"
        
        sheet_stats.append({
            "name": sheet_name,
            "dimensions": dimensions,
            "sheet_state": ws.sheet_state
        })
    
    metadata["sheet_statistics"] = sheet_stats
    return metadata

def extract_structure(data: bytes, options: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Example of Formatted Output:
    ## Structure
    - Sheet: Summary
        - Dimensions: A1:C5
        - Sample Data:
            - Q1    $125,000    5.2%
            - Q2    $132,000    8.1%
            - Q3    $145,000    12.3%
    - Sheet: Sales Data
        - Dimensions: A1:E100
        - Sample Data:
            - 2023-10-01    Widget A    John Doe    $2,500    North
            - 2023-10-02    Widget B    Jane Smith    $3,200    South
            - 2023-10-03    Widget C    Bob Johnson    $1,800    East
    - Named Ranges:
        - SalesData: Sheet1!$A$1:$E$100
    """
    wb = open_xlsx_file(data)
    
    # Extract structure
    structure = []
    
    # Add workbook as a section
    structure.append({
        "type": "workbook",
        "content": "XLSX Workbook"
    })
    
    # Extract sheets and sample data
    max_rows = options.get('structure_max_rows', 20) # TODO 20 is magic number. Make this configurable
    max_columns = options.get('structure_max_cols', 10) # TODO 10 is magic number. Make this configurable
    
    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        
        # Sample data for display
        sample_data = []
        
        row_count = 0
        for row in ws.iter_rows(max_row=max_rows, max_col=max_columns):
            row_data = []
            for cell in row:
                value = cell.value
                if isinstance(value, datetime):
                    value = value.strftime("%Y-%m-%d %H:%M:%S")
                row_data.append(str(value) if value is not None else "")
            
            sample_data.append(row_data)
            row_count += 1
        
        # Add sheet structure
        sheet_structure = {
            "type": "sheet",
            "name": sheet_name,
            "content": {
                "sample_data": sample_data
            }
        }
        
        # Add dimensions if available
        if hasattr(ws, "calculate_dimension") and callable(getattr(ws, "calculate_dimension")):
            try:
                sheet_structure["content"]["dimensions"] = ws.calculate_dimension()
            except:
                sheet_structure["content"]["dimensions"] = "Empty or Error"
        
        # Add sample size information
        if row_count >= max_rows:
            sheet_structure["content"]["note"] = f"Showing {max_rows} rows, {max_columns} columns (sample)"
        
        structure.append(sheet_structure)
        
        # Add named ranges if any are defined
        if hasattr(wb, "defined_names") and wb.defined_names:
            defined_names = []
            for name in wb.defined_names:
                if name.name.startswith('_'):  # Internal name
                    continue
                defined_names.append({
                    "name": name.name,
                    "destinations": list(name.destinations)
                })
            
            if defined_names:
                structure.append({
                    "type": "named_ranges",
                    "content": defined_names
                })
    
    return structure


def get_version() -> str:
    """
    Get the version of openpyxl library.
    
    Returns:
        Version string of openpyxl.
    """
    try:
        return dependencies.openpyxl.__version__
    except AttributeError:
        return "unknown"
