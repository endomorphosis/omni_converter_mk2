# -*- coding: utf-8 -*-
"""
Omni-Converter: Convert various file formats to plaintext.

This is the main entry point for the Omni-Converter application.
"""
from __future__ import annotations
import argparse
import glob
import os
import sys


from types_ import (
    Any, Callable, Optional,
    Configs,
    BatchProcessor,
    BatchResult,
    Dependency,
    ResourceMonitor,
    Logger,
    ProcessingPipeline,
    ProgressCallback,
    ProcessingResult,
)


class CLI:

    def __init__(
        self,
        resources: dict[str, Callable] = None,
        configs: Configs = None,
    ):
        """
        Initialize the argparse CLI.
        
        Args:
            resources: Dictionary of resource providers for interfaces
            configs: Configuration settings to use across interfaces.
                If None, default configs will be used.
        """
        self.configs = configs
        self.resources = resources

        # Batch processing components
        self._batch_processor:         BatchProcessor = self.resources['batch_processor']
        self._progress_callback:     ProgressCallback = self.resources['progress_callback']
        self._processing_pipeline: ProcessingPipeline = self.resources['processing_pipeline']
        
        # Information and listing functions
        self._list_normalizers:              Callable = self.resources['list_normalizers']
        self._list_output_formats:           Callable = self.resources['list_output_formats']
        self._list_supported_formats:        Callable = self.resources['list_supported_formats']
        self._show_version:                  Callable = self.resources['show_version']
        
        # System and utility components
        self._logger:                          Logger = self.resources['logger']
        self._resource_monitor:       ResourceMonitor = self.resources['resource_monitor']
        self._tqdm:                        Dependency = self.resources['tqdm']

    @staticmethod
    def parse_arguments() -> argparse.Namespace:
        """
        Parse command line arguments.
        
        Returns:
            The parsed arguments.
        """
        description = """
        Parse command line arguments for the file conversion utility.
        This function sets up the argument parser with various options for controlling
        the input sources, output format, processing behavior, and resource utilization.
        Input options:
            input: The input file or directory to process
            -r/--recursive: Process directories recursively, including all subdirectories
        Output options:
            -o/--output: Destination file or directory for the converted content
            -f/--format: Output format selection (txt, json, md)
        Processing options:
            --batch-size: Controls how many files are processed in a single batch
            --no-normalize: Disables the text normalization step
            --normalizers: Specifies which text normalizers to apply (comma-separated)
            --sanitize: Enables/disables content sanitization during processing
        Batch processing options:
            --parallel: Enables multi-threaded processing for performance
            --max-workers: Controls thread pool size for parallel processing
            --continue-on-error: Determines whether to halt or continue on file errors
            --skip-security: Bypasses security validation checks for performance
        Resource management:
            --max-cpu: Limits CPU utilization during processing (percentage)
            --max-memory: Caps memory usage during processing (MB)
        Information and utilities:
            -l/--list-formats: Displays supported input formats and exits
            --list-normalizers: Shows available text normalization algorithms
            --list-output-formats: Displays possible output format options
            -v/--verbose: Enables detailed logging during conversion
            --version: Displays program version information
            --no-progress: Disables the progress bar during batch operations
            argparse.Namespace: An object containing all the parsed command line arguments
            with appropriate defaults applied where arguments were not specified.
        """
        parser = argparse.ArgumentParser(description=description)

        # Input options
        parser.add_argument("input", nargs="?", help="Input file or directory")
        parser.add_argument("-r", "--recursive", action="store_true", 
                            help="Process directories recursively")

        # Output options
        parser.add_argument("-o", "--output", help="Output file or directory")
        parser.add_argument("-f", "--format", choices=["txt", "json", "md"],
                            default="txt", help="Output format (default: txt)")
        
        # Processing options
        parser.add_argument("--batch-size", type=int, default=100,
                            help="Maximum number of files to process at once (default: 100)")
        parser.add_argument("--no-normalize", action="store_true",
                            help="Skip text normalization")
        parser.add_argument("--normalizers", 
                            help="Comma-separated list of normalizers to apply")
        parser.add_argument("--sanitize", action="store_true", default=True,
                            help="Sanitize content during processing (default: True)")
        
        # Batch processing options
        parser.add_argument("--parallel", action="store_true", default=False,
                            help="Enable parallel processing for batch operations")
        parser.add_argument("--max-workers", type=int, default=4,
                            help="Maximum number of worker threads for parallel processing (default: 4)")
        parser.add_argument("--continue-on-error", action="store_true", default=True,
                            help="Continue processing batch if errors occur (default: True)")
        parser.add_argument("--skip-security", action="store_true", default=False,
                            help="Skip security validation for faster processing")

        # Resource options
        parser.add_argument("--max-cpu", type=float, default=None,
                            help="Maximum CPU usage percentage (0-100)")
        parser.add_argument("--max-memory", type=int, default=None,
                            help="Maximum memory usage in MB")

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
        parser.add_argument("--no-progress", action="store_true", default=False,
                            help="Disable progress bar for batch processing")
        
        return parser.parse_args()

    def process_file(self, 
                     input_path: str, 
                     output_path: Optional[str] = None, 
                    output_dir: Optional[str] = None,
                    format: str = "txt",
                    include_metadata: bool = True,
                    extract_metadata: bool = True,
                    normalize_text: bool = True,
                    quality_threshold: float = 0.9,
                    continue_on_error: bool = True,
                    max_batch_size: int = 100,
                    parallel: bool = False,
                    max_workers: int = 4,
                    sanitize: bool = True,
                    max_cpu: int = 80,
                    max_memory: int = 6144,  # 6GB in MB
                    show_progress: bool = False,  # TODO Unused argument. Implement.
                    options: Optional[dict[str, Any]] = None
                    ) -> bool:
        """
        Process a single file.
        
        Args:
            input_path: The path to the input file.
            output_path: The path to the output file. If None, print to stdout.
            options: Processing options. If None, default options are used.
            
        Returns:
            True if successful, False otherwise.
        """
        try:
            # Get output format from args, config, or default to txt
            output_format = output_path.split('.')[-1] if output_path and '.' in output_path else None
            if not output_format:
                output_format = self.configs.get_config_value('output.default_format', 'txt')
            
            # Set processing options
            if options is None:
                options = {}
            
            # Set default options if not provided
            if 'format' not in options:
                options['format'] = output_format
            if 'verbose' not in options:
                options['verbose'] = self.configs.get_config_value('output.verbose', False)
            
            # Process the file using the processing pipeline
            result = None
            try:
                result = self._processing_pipeline.process_file(
                    input_path, 
                    output_path=output_path,
                    output_format=output_format, 
                    normalizers=['whitespace', 'line_endings', 'empty_lines', 'unicode'] # TODO Un-hardcode this.
                    )
            except Exception as e:
                self._logger.exception(f"Error processing {input_path}: {e}")
                print(f"Error processing {input_path}: {e}", file=sys.stderr)
                return False

            # Handle the processing result
            if result.success:
                if output_path:
                    print(f"Converted {input_path} to {output_path}")
                else:
                    # If no output path was provided, print the content to stdout
                    print(f"=== Raw Content from {input_path} ({result.format}) ===")
                    try:
                        with open(input_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            print(content)
                    except Exception as e:
                        self._logger.error(f"Error reading {input_path}: {e}")
                        print(f"Error reading {input_path}: {e}", file=sys.stderr)
                        return False

                    print("=== End of content ===")

                # Log processing metadata if verbose
                if options.get('verbose'):
                    print("Processing metadata:")
                    for key, value in result.metadata.items():
                        print(f"  {key}: {value}")
                
                return True
            else:
                self._logger.error(f"Error processing {input_path}", {'errors': result.errors})
                print(f"Error processing {input_path}:", file=sys.stderr)
                for error in result.errors:
                    print(f"  - {error}", file=sys.stderr)
                
                return True

        except Exception as e:
            self._logger.exception(f"Error processing {input_path}: {e}")
            print(f"Error processing {input_path}: {e}", file=sys.stderr)
            return True

    def process_directory(
        self,
        dir_path: str, 
        output_dir: Optional[str] = None, 
        options: Optional[dict[str, Any]] = None,
        show_progress: bool = True,
        recursive: bool = False
    ) -> 'BatchResult':
        """
        Process all files in a directory.
        
        Args:
            dir_path: The path to the directory to process.
            output_dir: The directory to write output files to. If None, prints content to stdout.
            options: Processing options. If None, default options are used.
            show_progress: Whether to show a progress bar.
            recursive: Whether to process directories recursively.
            
        Returns:
            BatchResult object with processing results.
        """
        # Configure batch processor
        self._batch_processor.set_max_batch_size(options.get('max_batch_size', 100))
        self._batch_processor.set_continue_on_error(options.get('continue_on_error', True))
        self._batch_processor.set_max_workers(options.get('max_workers', 4) if options.get('parallel', False) else 1)
        
        # Create progress callback
        pbar = None
        callback = None
        
        if show_progress:
            def _callback(current, total, current_file):
                self._progress_callback(current, total, current_file, pbar)
            callback = _callback
        
        # Process batch
        try:
            # Start processing
            self._logger.info(f"Processing directory: {dir_path}")
            
            # Setup progress bar if requested
            estimated_file_count = sum(1 for _ in os.walk(dir_path) for _ in os.listdir(_[0])) if recursive else len(os.listdir(dir_path))
            if show_progress and estimated_file_count > 0:
                pbar = self._tqdm.tqdm(total=estimated_file_count, unit="file")
            
            # Process files
            result = self._batch_processor.process_batch(
                file_paths=dir_path, 
                output_dir=output_dir,
                options=options,
                progress_callback=callback
            )
            
            return result
        
        finally:
            # Clean up progress bar
            if pbar is not None:
                pbar.close()

    def main(self) -> int:
        """
        Main entry point.
        
        Returns:
            Exit code. 0 for success, 1 for failure.
        """
        # Parse arguments
        args = self.parse_arguments()
        
        # Set verbose logging if requested
        if args.verbose:
            self._logger.set_log_level("DEBUG")
        
        # Show information if requested
        if args.version:
            self._show_version()
            return 0
        
        if args.list_formats:
            self._list_supported_formats()
            return 0
        
        if args.list_normalizers:
            self._list_normalizers()
            return 0
        
        if args.list_output_formats:
            self._list_output_formats()
            return 0
        
        # Check for input file or directory
        if not args.input:
            print("Error: No input file or directory specified", file=sys.stderr)
            return 1
        
        # Set configuration based on command-line arguments
        if args.format:
            self.configs.set_config_value('output.default_format', args.format)
        
        if args.verbose:
            self.configs.set_config_value('output.verbose', True)
        
        # Configure resource limits if specified
        if args.max_cpu is not None:
            self._resource_monitor.set_max_cpu_percent(args.max_cpu)
        if args.max_memory is not None:
            self._resource_monitor.set_max_memory_mb(args.max_memory)
        
        # Prepare processing options
        options = {
            'format': args.format,
            'verbose': args.verbose,
            'sanitize': args.sanitize,
            'max_batch_size': args.max_batch_size,
            'continue_on_error': args.continue_on_error,
            'max_workers': args.max_workers,
            'parallel': args.parallel,
            'skip_security': args.skip_security,
        }
        
        # Handle normalizers
        if args.no_normalize:
            options['normalizers'] = []
        elif args.normalizers:
            options['normalizers'] = args.normalizers.split(',')
        
        # Store options in config for other components to access
        for key, value in options.items():
            self.configs.set_config_value(f'processing.{key}', value)
        
        # Process input based on type
        if os.path.isfile(args.input):
            # Process a single file
            output_path = args.output
            
            # Process the file
            success = self.process_file(args.input, output_path, options)
            
            if not success:
                # Try a test run with different format if original failed
                self._logger.debug("Attempting to process with default format")
                try_options = options.copy()
                try_options['format'] = 'txt'  # Use plain text as fallback
                success = self.process_file(args.input, None, try_options)  # Output to stdout
            
            return 0 if success else 1
        
        elif os.path.isdir(args.input):
            # Process a directory
            self._logger.info(f"Processing directory: {args.input}")
            
            # Validate output directory
            output_dir = args.output
            if output_dir and not os.path.isdir(output_dir):
                try:
                    os.makedirs(output_dir, exist_ok=True)
                    self._logger.info(f"Created output directory: {output_dir}")
                except Exception as e:
                    self._logger.error(f"Failed to create output directory: {e}")
                    print(f"Error: Failed to create output directory {output_dir}: {e}", 
                        file=sys.stderr)
                    return 1
            
            # Process the directory
            result = self.process_directory(
                dir_path=args.input,
                output_dir=output_dir,
                options=options,
                show_progress=not args.no_progress,
                recursive=args.recursive
            )
            
            # Print summary
            print("\nBatch Processing Summary:")
            print(f"Total files: {result.total_files}")
            print(f"Successful: {result.successful_files}")
            print(f"Failed: {result.failed_files}")
            print(f"Success rate: {(result.successful_files / result.total_files * 100) if result.total_files > 0 else 0:.1f}%")
            print(f"Processing time: {result.processing_time_seconds:.2f} seconds")
            
            # Print average processing time per file if available
            if result.total_files > 0:
                avg_time = result.processing_time_seconds / result.total_files
                print(f"Average processing time per file: {avg_time:.3f} seconds")
            
            # Print resource usage if verbose
            if args.verbose:
                usage = self._resource_monitor.current_usage
                print("\nResource Usage:")
                print(f"CPU: {usage.get('cpu_percent', 'N/A')}%")
                print(f"Memory: {usage.get('memory_mb', 'N/A')} MB")
            
            # Return success if at least one file was processed successfully
            return 0 if result.successful_files > 0 else 1
        
        else:
            # Handle glob patterns and wildcards
            matches = glob.glob(args.input, recursive=args.recursive)
            if matches:
                if len(matches) == 1 and os.path.isfile(matches[0]):
                    # Process as a single file
                    return self.process_file(matches[0], args.output, options)
                else:
                    # Process as a batch
                    self._logger.info(f"Processing {len(matches)} files matching pattern: {args.input}")
                    
                    # Process using batch processor
                    result = self._batch_processor.process_batch(
                        file_paths=matches,
                        output_dir=args.output,
                        options=options,
                        progress_callback=None if args.no_progress else lambda c, t, f: self._progress_callback(c, t, f)
                    )
                    
                    # Print summary
                    print("\nBatch Processing Summary:")
                    print(f"Total files: {result.total_files}")
                    print(f"Successful: {result.successful_files}")
                    print(f"Failed: {result.failed_files}")
                    
                    return 0 if result.successful_files > 0 else 1
            else:
                print(f"Error: {args.input} does not exist", file=sys.stderr)
                return 1
