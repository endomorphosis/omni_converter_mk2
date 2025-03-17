
#!/usr/bin/env python
"""
Omni-Converter: Convert various file formats to plaintext.

This is the main entry point for the Omni-Converter application.
"""

import os
import sys
import argparse
from typing import List, Optional

from utils.config import config_manager
from utils.logger import logger
from format_handlers.text_handler import text_handler
from format_handlers.image_handler import image_handler
from format_handlers.application_handler import application_handler
from format_handlers.format_registry import format_registry


def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments.
    
    Returns:
        The parsed arguments.
    """
    parser = argparse.ArgumentParser(description="Convert files to plaintext")
    
    # Input options
    parser.add_argument("input", nargs="?", help="Input file or directory")
    parser.add_argument("-r", "--recursive", action="store_true", 
                        help="Process directories recursively")
    
    # Output options
    parser.add_argument("-o", "--output", help="Output file or directory")
    parser.add_argument("-f", "--format", choices=["txt", "json", "md"],
                        default="txt", help="Output format (default: txt)")
    
    # Processing options
    parser.add_argument("--batch-size", type=int, 
                        help="Maximum number of files to process at once")
    
    # Information options
    parser.add_argument("-l", "--list-formats", action="store_true",
                        help="List supported formats and exit")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="Enable verbose output")
    parser.add_argument("--version", action="store_true",
                        help="Show version information and exit")
    
    return parser.parse_args()


def list_supported_formats() -> None:
    """List all supported formats."""
    # Format the handler capabilities
    print("Omni-Converter Supported Formats:")
    print("=================================")
    print()
    
    # Get formats grouped by category from the registry
    categories = format_registry.get_formats_by_category()
    
    # Print formats by category
    for category, formats in sorted(categories.items()):
        print(f"{category.capitalize()} Formats ({len(formats)}):")
        for fmt in sorted(formats):
            print(f"  - {fmt}")
        print()
    
    # List categories that aren't implemented yet
    if "audio" not in categories:
        print("Audio Formats (0): Not implemented yet")
    if "video" not in categories:
        print("Video Formats (0): Not implemented yet")


def show_version() -> None:
    """Show version information."""
    from __version__ import __version__
    print(f"Omni-Converter version {__version__}")
    print("Copyright 2025")
    print("\nImplementation Status:")
    print("- Text formats: Fully implemented (HTML, XML, Plain text, CSV, Calendar)")
    print("- Image formats: Fully implemented (JPEG, PNG, GIF, WebP, SVG)")
    print("- Application formats: Fully implemented (PDF, JSON, DOCX, XLSX, ZIP)")
    print("- Audio formats: Not implemented")
    print("- Video formats: Not implemented")
    print("\nSee IMPLEMENTATION_STATUS.md for detailed status report.")


def process_file(input_path: str, output_path: Optional[str] = None) -> bool:
    """
    Process a single file.
    
    Args:
        input_path: The path to the input file.
        output_path: The path to the output file. If None, print to stdout.
        
    Returns:
        True if successful, False otherwise.
    """
    try:
        # Use the format registry to extract content
        content = format_registry.extract_content(input_path)
        
        # Output the content
        if output_path:
            # Create output directory if it doesn't exist
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            # Write to file
            with open(output_path, 'w') as f:
                f.write(content.text)
            
            print(f"Converted {input_path} to {output_path}")
        else:
            # Print to stdout
            print(f"=== Content from {input_path} ({content.source_format}) ===")
            print(content.text)
            print("=== End of content ===")
        
        return True
    
    except Exception as e:
        logger.error(f"Error processing {input_path}", {'error': str(e)})
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)
        return False


def main() -> int:
    """
    Main entry point.
    
    Returns:
        Exit code.
    """
    # Parse arguments
    args = parse_arguments()
    
    # Set verbose logging if requested
    if args.verbose:
        logger.set_log_level("DEBUG")
    
    # Show information if requested
    if args.version:
        show_version()
        return 0
    
    if args.list_formats:
        list_supported_formats()
        return 0
    
    # Check for input file or directory
    if not args.input:
        print("Error: No input file or directory specified", file=sys.stderr)
        return 1
    
    # Process input
    if os.path.isfile(args.input):
        # Process a single file
        output_path = args.output
        success = process_file(args.input, output_path)
        return 0 if success else 1
    
    elif os.path.isdir(args.input):
        # Process a directory
        print("Directory processing not implemented yet")
        return 1
    
    else:
        print(f"Error: {args.input} does not exist", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
