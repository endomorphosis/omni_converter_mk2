
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
from core.processing_pipeline import processing_pipeline


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
    parser.add_argument("--no-normalize", action="store_true",
                        help="Skip text normalization")
    parser.add_argument("--normalizers", 
                        help="Comma-separated list of normalizers to apply")
    
    # Information options
    parser.add_argument("-l", "--list-formats", action="store_true",
                        help="List supported formats and exit")
    parser.add_argument("--list-normalizers", action="store_true",
                        help="List available text normalizers and exit")
    parser.add_argument("--list-output-formats", action="store_true",
                        help="List available output formats and exit")
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
        # Get output format from args, config, or default to txt
        output_format = output_path.split('.')[-1] if output_path and '.' in output_path else None
        if not output_format:
            output_format = config_manager.get_config_value('output.format', 'txt')
        
        # Set processing options
        options = {
            'format': output_format,
            'normalizers': ['whitespace', 'line_endings', 'empty_lines', 'unicode'],
            'verbose': config_manager.get_config_value('output.verbose', False)
        }
        
        # Process the file using the processing pipeline
        result = processing_pipeline.process_file(input_path, output_path, options)
        
        # Handle the processing result
        if result.success:
            if output_path:
                print(f"Converted {input_path} to {output_path}")
            else:
                # If no output path was provided, print the content to stdout
                print(f"=== Content from {input_path} ({result.format}) ===")
                
                # Extract content directly from the result's metadata
                # This avoids the need to read from a file that may not exist
                content_obj = format_registry.extract_content(input_path)
                print(content_obj.text)
                
                print("=== End of content ===")
            
            # Log processing metadata if verbose
            if options.get('verbose'):
                print("Processing metadata:")
                for key, value in result.metadata.items():
                    print(f"  {key}: {value}")
            
            return True
        else:
            logger.error(f"Error processing {input_path}", {'errors': result.errors})
            print(f"Error processing {input_path}:", file=sys.stderr)
            for error in result.errors:
                print(f"  - {error}", file=sys.stderr)
            
            return False
    
    except Exception as e:
        logger.error(f"Error processing {input_path}", {'error': str(e)})
        print(f"Error processing {input_path}: {str(e)}", file=sys.stderr)
        return False


def list_normalizers() -> None:
    """List all available text normalizers."""
    print("Omni-Converter Text Normalizers:")
    print("===============================")
    print()
    
    normalizers = processing_pipeline.normalizer.get_applied_normalizers()
    
    for normalizer in sorted(normalizers):
        print(f"- {normalizer}")
    
    print("\nUse --normalizers option to specify which normalizers to apply.")
    print("Example: --normalizers whitespace,line_endings")


def list_output_formats() -> None:
    """List all available output formats."""
    print("Omni-Converter Output Formats:")
    print("============================")
    print()
    
    formats = processing_pipeline.formatter.get_available_formats()
    
    for fmt in sorted(formats):
        print(f"- {fmt}")
    
    print("\nUse -f or --format option to specify the output format.")
    print("Example: -f json")


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
    
    if args.list_normalizers:
        list_normalizers()
        return 0
    
    if args.list_output_formats:
        list_output_formats()
        return 0
    
    # Check for input file or directory
    if not args.input:
        print("Error: No input file or directory specified", file=sys.stderr)
        return 1
    
    # Set configuration based on command-line arguments
    if args.format:
        config_manager.set_config_value('output.format', args.format)
    
    if args.verbose:
        config_manager.set_config_value('output.verbose', True)
    
    # Process input
    if os.path.isfile(args.input):
        # Process a single file
        output_path = args.output
        
        # Set processing options
        options = {
            'format': args.format,
            'verbose': args.verbose
        }
        
        # Handle normalizers
        if args.no_normalize:
            options['normalizers'] = []
        elif args.normalizers:
            options['normalizers'] = args.normalizers.split(',')
        
        # Store options in config
        for key, value in options.items():
            config_manager.set_config_value(f'processing.{key}', value)
        
        # Process the file
        success = process_file(args.input, output_path)
        
        if not success:
            # Try a test run with different format if original failed
            logger.debug("Attempting to process with default format")
            try_options = options.copy()
            try_options['format'] = 'txt'  # Use plain text as fallback
            success = process_file(args.input, None)  # Output to stdout
        
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
