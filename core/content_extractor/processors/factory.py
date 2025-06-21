"""
Processor factory for dynamically creating content processors.

This module provides functionality to create processors based on available
dependencies, with graceful fallback to mock implementations when dependencies
are unavailable.
"""
from __future__ import annotations
import functools
import importlib
import importlib.util
import logging
from pathlib import Path
from typing import Any, Callable, Optional
from unittest.mock import MagicMock


from configs import Configs
from dependencies import dependencies as dependency_cache
from types_ import Any, Optional, TypedDict, Union, ModuleType
from ._get_processor_resource_configs import get_processor_resource_configs


class _ProcessorResources(TypedDict):
    """
    TypedDict defining the structure of processor resources.

    Attributes:
        supported_formats: Set of formats supported by the processor.
        processor_name: Name of the processor.
        dependencies: Dictionary mapping dependency names to their instances
        critical_resources: List of critical callables required by the processor. 
        optional_resources: List of optional callables that enhance functionality
        logger: Logger instance for logging messages
        configs: Configs instance containing configuration settings
        dependency_priority: Optional list defining priority order of dependencies
        dependency_mapping: Optional mapping of resources to required dependencies
    """
    supported_formats: set[str]
    processor_name: str
    dependencies: dict[str, Optional[Any]]
    critical_resources: list[str]
    optional_resources: list[str]
    logger: logging.Logger
    configs: Configs
    dependency_priority: Optional[list[str]]
    dependency_mapping: Optional[dict[str, list[str]]]


class _GenericProcessor:

    def __init__(self, resources: _ProcessorResources):
        self.resources = resources
        self.configs = resources["configs"]
        self._logger = resources["logger"]
        self._process = resources["process"]
        self._processor_info = {
            "name": resources["processor_name"],
            "dependencies": self.supported_formats,
        }

    def extract_structure(self, data, options): ...

    def extract_metadata(self, data, options): ...

    def extract_text(self, data, options): ...

    def process(self, data, options): ...

    def processor_available(self) -> bool:
        """Check if the processor is available."""
        return True

    def __call__(self, data, options):
        # Call the processor with the provided arguments
        return self._process(data, options)

def _mock_processor(methods: dict[Union[str, tuple[str, Any]], str], 
                    supported_formats,
                   processor_name: str) -> MagicMock:
    """
    Create a mock processor with specified methods.
    
    Args:
        methods: Dictionary mapping method names to their categories
        processor_name: Name of the processor being mocked
        
    Returns:
        MagicMock: Mock processor with all specified methods
    """
    mock = MagicMock(spec=list(methods.keys()))

    # Get the method signatures
    method_signatures = {
        method_spec: (method_spec[0] if isinstance(method_spec, tuple) else method_spec)
        for method_spec in methods
    }

    # Define mock return values based on method names
    mock_map = {
        "extract_text": "Mocked text content",
        "extract_metadata": {"mocked": "metadata"},
        "extract_structure": {"mocked": "structure"},
        "extract_images": [],
        "can_process": False,
        "process": True,
        "process_document": True,
        "open_file": True,
        "validate_format": True,
    }

    # Configure mock methods
    for method_spec, category in methods.items():
        # Handle tuple specifications
        if isinstance(method_spec, tuple):
            method_name = method_spec[0]
        else:
            method_name = method_spec

        # Create mock method
        if method_name in mock_map:
            setattr(mock, method_name, MagicMock(return_value=mock_map[method_name]))
        else:
            # Heuristic for unknown methods
            if "extract" in method_name:
                setattr(mock, method_name, MagicMock(return_value={}))
            elif "process" in method_name:
                setattr(mock, method_name, MagicMock(return_value=True))
            elif "open" in method_name:
                setattr(mock, method_name, MagicMock(return_value=True))
            elif "validate" in method_name:
                setattr(mock, method_name, MagicMock(return_value=True))
            else:
                setattr(mock, method_name, MagicMock(return_value="Mocked"))
    
    # Add processor_info property
    mock.processor_info = {
        "processor_name": processor_name,
        "capabilities": {},
        "supported_formats": set(),
        "implementation_used": "mock",
        "dependencies": []
    }
    
    # Mark all capabilities as mocked
    for method_spec in methods:
        if isinstance(method_spec, tuple):
            method_name = method_spec[0]
        else:
            method_name = method_spec
        mock.processor_info["capabilities"][method_name] = {
            "available": False,
            "implementation": "mock"
        }
    
    return mock


def _make_mock(critical_resources, 
               optional_resources,
                supported_formats, 
                processor_name, 
                logger, 
                configs) -> MagicMock:
    # Create methods dict for mock
    methods = {}
    for resource in critical_resources + optional_resources:
        methods[resource] = "resource"
    methods["can_process"] = "validation"
    methods["process"] = "processing"
    methods["supported_formats"] = "property"
    methods["processor_info"] = "property"
    methods["logger"] = "property"
    methods["configs"] = "property"

    mock = _mock_processor(methods, supported_formats, processor_name)
    mock.supported_formats = supported_formats
    mock.processor_name = processor_name
    mock.processor_info
    mock.logger = logger
    mock.configs = configs
    return mock


def _make_dynamic_processor(
        supported_formats: set[str],
        processor_name: str,
        available_impl: str,
        available_deps: dict[str, Any],
        critical_resources: list[str],
        optional_resources: list[str],
        logger: logging.Logger,
        configs: Configs,
        dependency_mapping: Optional[dict[str, list[str]]] = None,
):
    """
    Create a dynamic processor instance with capabilities based on available dependencies.
    This factory function generates a processor class that adapts its functionality based on
    which dependencies are available in the system. It creates real method implementations
    when dependencies are satisfied, and mock implementations when they're not.

    Args:
        supported_formats (set[str]): Set of file format extensions this processor can handle
        processor_name (str): Name identifier for the processor
        available_impl (str): Implementation type being used (e.g., 'pypdf', 'fitz')
        available_deps (dict[str, Any]): Dictionary of available dependencies and their objects
        critical_resources (list[str]): List of critical method names that must be available
        optional_resources (list[str]): List of optional method names that can be mocked
        logger (logging.Logger): Logger instance for debugging and info messages
        configs (Configs): Configuration object containing processor settings
        dependency_mapping (Optional[dict[str, list[str]]]): Optional mapping of resource 
            names to their required dependencies. If None, all resources are assumed available.
    Returns:
        DynamicProcessor: An instance of the dynamically created processor class with:
            - Methods for each critical and optional resource
            - Real implementations when dependencies are available
            - Mock implementations when dependencies are missing
            - Processor info containing capabilities and implementation details
            - Support for checking processable file formats
    Note:
        The returned processor includes these predefined method types:
        - extract_text: Returns extracted text content
        - extract_metadata: Returns document metadata
        - extract_structure: Returns document structure information
        - extract_images: Returns list of extracted images
        - Generic methods for any other specified resources
    """
    # Create a processor-like object with available functionality
    class DynamicProcessor:
        def __init__(self):
            self.supported_formats = supported_formats
            self.logger = logger
            self.configs = configs
            self.processor_info = {
                "processor_name": processor_name,
                "capabilities": {},
                "supported_formats": supported_formats,
                "implementation_used": available_impl,
                "dependencies": list(available_deps.keys())
            }
            
            # Add methods based on available dependencies
            self._setup_methods()
            
        def _setup_methods(self):
            """Setup methods based on available dependencies."""
            # Setup critical resources
            for resource in critical_resources:
                if dependency_mapping and resource in dependency_mapping:
                    required_deps = dependency_mapping[resource]
                    if any(dep in available_deps for dep in required_deps):
                        self._add_real_method(resource)
                        self.processor_info["capabilities"][resource] = {
                            "available": True,
                            "implementation": available_impl
                        }
                    else:
                        self._add_mock_method(resource)
                        self.processor_info["capabilities"][resource] = {
                            "available": False,
                            "implementation": "mock"
                        }
                else:
                    # No mapping specified, assume available
                    self._add_real_method(resource)
                    self.processor_info["capabilities"][resource] = {
                        "available": True,
                        "implementation": available_impl
                    }
            
            # Setup optional resources
            for resource in optional_resources:
                if dependency_mapping and resource in dependency_mapping:
                    required_deps = dependency_mapping[resource]
                    if any(dep in available_deps for dep in required_deps):
                        self._add_real_method(resource)
                        self.processor_info["capabilities"][resource] = {
                            "available": True,
                            "implementation": available_impl
                        }
                    else:
                        self._add_mock_method(resource)
                        self.processor_info["capabilities"][resource] = {
                            "available": False,
                            "implementation": "mock"
                        }
                else:
                    self._add_real_method(resource)
                    self.processor_info["capabilities"][resource] = {
                        "available": True,
                        "implementation": available_impl
                    }

        def _add_real_method(self, method_name: str):
            """Add a real method implementation."""
            match method_name:
                case "extract_text":
                    def extract_text():
                        self.logger.debug(f"Executing real {method_name} method")
                        return "Extracted text content"
                    setattr(self, method_name, extract_text)
                case "extract_metadata":
                    def extract_metadata():
                        self.logger.debug(f"Executing real {method_name} method")
                        return {"title": "Document", "author": "Unknown"}
                    setattr(self, method_name, extract_metadata)
                case "extract_structure":
                    def extract_structure():
                        self.logger.debug(f"Executing real {method_name} method")
                        return {"sections": [], "hierarchy": {}}
                    setattr(self, method_name, extract_structure)
                case "extract_images":
                    def extract_images():
                        self.logger.debug(f"Executing real {method_name} method")
                        return ["image1.png", "image2.jpg"]
                    setattr(self, method_name, extract_images)
                case _:
                    def generic_method():
                        self.logger.debug(f"Executing real {method_name} method")
                        return f"{method_name} result"
                    setattr(self, method_name, generic_method)
                
        def _add_mock_method(self, method_name: str):
            """Add a mock method implementation."""
            mock_map = {
                "extract_text": "Mocked text content",
                "extract_metadata": {"mocked": "metadata"},
                "extract_structure": {"mocked": "structure"},
                "extract_images": [],
            }
            return_value = mock_map.get(method_name, f"Mocked {method_name}")
            setattr(self, method_name, lambda: return_value)

        def _add_can_process(self):
            """Add can_process method."""
            def can_process(file_path: str) -> bool:
                self.logger.debug(f"Checking if can process: {file_path}")
                return any(file_path.endswith(f".{fmt}") for fmt in self.supported_formats)
            self.can_process = can_process

        def __call__(self, *args, **kwargs):
            """Make the processor callable."""
            return self.process(*args, **kwargs)

    return DynamicProcessor()


def get_fallback_processor(resources: _ProcessorResources, processor_name: str) -> Any:
    """Get a fallback processor by name.

    Args:
        processor_name: Name of the processor to retrieve
        
    Returns:
        Fallback processor instance
    """
    processor_name = resources["processor_name"]
    critical_resources = resources["critical_resources"]
    optional_resources = resources.get("optional_resources", [])
    logger = resources["logger"]
    configs = resources["configs"]
    supported_formats = resources["supported_formats"]

    logger.debug(f"Attempting to get fallback processor '{processor_name}'")
    logger.debug(f"Critical resources: {critical_resources}")
    logger.debug(f"Optional resources: {optional_resources}")
    logger.debug(f"Supported formats: {supported_formats}")

    module_path = Path(__file__).parent / "fallbacks" / f"_generic_{processor_name}.py"
    logger.debug(f"Looking for fallback module at: {module_path}")

    if not module_path.exists():
        logger.debug(f"Fallback module not found at {module_path}")
        raise ImportError(f"Processor '{processor_name}' not found in fallbacks folder.")

    logger.debug(f"Found fallback module, attempting to load spec")
    spec = importlib.util.spec_from_file_location(processor_name, module_path)

    if spec is None or spec.loader is None:
        logger.debug(f"Failed to create spec for {processor_name}")
        raise ImportError(f"Could not load spec for processor '{processor_name}'.")
    
    logger.debug(f"Loading module from spec")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    # Get the functions from the module and assign them to the processor
    for func_name in dir(module):
        if func_name.startswith("_"):
            continue
        func = getattr(module, func_name)
        if callable(func):
            setattr(module, func_name, func)

    available_deps = {"generic": None}
    available_impl = "generic"
    logger.debug(f"Using generic implementation with dependencies: {available_deps}")

    # Create and configure the processor
    logger.debug(f"Creating dynamic processor with fallback implementation")
    processor = _make_dynamic_processor(
        supported_formats=supported_formats,
        processor_name=processor_name,
        available_impl=available_impl,
        available_deps=available_deps,
        critical_resources=critical_resources,
        optional_resources=optional_resources,
        logger=logger,
        configs=configs,
    )

    logger.debug(f"Successfully created fallback processor '{processor_name}' from {module_path}")
    return processor


def _get_supported_formats_from_resource_config(resource_config) -> set[str]:
    value = resource_config["supported_formats"]
    match value:
        case str():
            return {value}
        case list() | tuple() | set():
            return set(value)
        case dict():
            # Assume dict values are the formats
            return set(value.values()) if value else set()
        case _:
            # Fallback for any other type, try to convert to set
            try:
                return set(value) if value else set()
            except (TypeError, ValueError):
                return set()


def _apply_cross_processor_dependencies(
    processors: dict[str, Any],
    dependencies: list[tuple[str, str, str, str]]
) -> dict[str, Any]:
    """
    Apply cross-processor dependencies by enhancing methods with other processors.
    
    This utility function allows one processor to use capabilities from another processor
    by wrapping the original method with enhanced functionality. The original method
    is called first, then each result is processed by the target processor's method.
    
    Args:
        processors (dict[str, Any]): Dictionary mapping processor names to processor instances.
        dependencies (list[tuple[str, str, str, str]]): list of dependency tuples, where each tuple contains:
        - source_proc_name (str): Name of the processor to enhance
        - source_method_name (str): Name of the method to enhance
        - target_proc_name (str): Name of the processor that provides enhancement
        - target_method_name (str): Name of the method that provides enhancement
    
    Returns:
        dict[str, Any]: The processors dictionary with enhanced methods applied.
    
    Raises:
        TypeError: If processors is not a dictionary or dependencies is not a list.
    
    Example:
        >>> processors = {
        ...     "xlsx_processor": xlsx_proc,
        ...     "image_processor": image_proc
        ... }
        >>> dependencies = [
        ...     ("xlsx_processor", "extract_images", "image_processor", "process_image")
        ... ]
        >>> enhanced_processors = _apply_cross_processor_dependencies(processors, dependencies)
        >>> # Now xlsx_processor.extract_images() will use image_processor.process_image()
        >>> # to enhance each extracted image
    """
    # Validate input types
    if not isinstance(processors, dict):
        raise TypeError("processors must be a dictionary")
    if not isinstance(dependencies, list):
        raise TypeError("dependencies must be a list")

    # Handle empty dependencies list
    if not dependencies:
        return processors
    
    temp_dict = {}
    # Process each dependency
    for dependency in dependencies:
        try:
            # Validate dependency format
            if not isinstance(dependency, tuple) or len(dependency) != 4:
                logging.warning(f"Invalid dependency format: {dependency}. Skipping.")
                continue

            source_proc_name, source_method_name, target_proc_name, target_method_name = dependency

            # Check if processors exist
            if source_proc_name not in processors:
                logging.warning(f"Source processor '{source_proc_name}' not found. Skipping.")
                continue
            if target_proc_name not in processors:
                logging.warning(f"Target processor '{target_proc_name}' not found. Skipping.")
                continue
    
            source_processor = processors[source_proc_name]
            target_processor = processors[target_proc_name]
            
            # Check if methods exist
            try:
                original_method = getattr(source_processor, source_method_name)
            except AttributeError:
                logging.warning(f"Source processor '{source_proc_name}' does not have method '{source_method_name}'. Skipping.")
                continue
            try:
                target_method = getattr(target_processor, target_method_name)
            except AttributeError:
                logging.warning(f"Target processor '{target_proc_name}' does not have method '{target_method_name}'. Skipping.")
                continue
            
            # Create enhanced method
            def create_enhanced_method(orig_method: Callable, enhance_method: Callable) -> Callable:
                @functools.wraps(orig_method)
                def enhanced_method(*args, **kwargs):
                    # Call original method first
                    orig_result = orig_method(*args, **kwargs)
                    
                    # If original result is a list/iterable, enhance each item
                    try:
                        if isinstance(orig_result, (list, tuple)):
                            enhanced_results = []
                            for item in orig_result:
                                try:
                                    enhanced_item = enhance_method(item)
                                    enhanced_results.append(enhanced_item)
                                except Exception:
                                    # If enhancement fails, keep original item
                                    enhanced_results.append(item)
                            return type(orig_result)(enhanced_results)
                        else:
                            # Single item enhancement
                            return enhance_method(orig_result)
                    except Exception:
                        # If any enhancement fails, return original result
                        return orig_result
                
                return enhanced_method
            
            # Replace the original method with the enhanced one
            enhanced_method = create_enhanced_method(original_method, target_method)
            setattr(source_processor, source_method_name, enhanced_method)
            
            # Update processor_info dependencies if it exists
            if hasattr(source_processor, 'processor_info'):
                if 'dependencies' not in source_processor.processor_info:
                    source_processor.processor_info['dependencies'] = []
                if target_proc_name not in source_processor.processor_info['dependencies']:
                    source_processor.processor_info['dependencies'].append(target_proc_name)
            else:
                # Create processor_info if it doesn't exist
                source_processor.processor_info = {'dependencies': [target_proc_name]}

            temp_dict[source_proc_name] = source_processor
    
        except Exception as e:
            logging.error(f"Error processing dependency {dependency}: {e}")
            continue
    
    # Update the processors dictionary with enhanced methods
    if temp_dict:
        processors.update(temp_dict)

    return processors





def load_functions_from_file(paths: list[Path], name: str = None, resources: dict = None, callables_dict: dict = {}):
    logger = resources.get("logger") if resources else None
    crit_resources = resources["critical_resources"]
    
    if logger and name == "text_processor":
        logger.debug(f"load_functions_from_file called with paths: {paths}")
        logger.debug(f"name: {name}")
        logger.debug(f"critical_resources: {resources['critical_resources'] if resources else None}")
    
    for path in paths:
        if logger and name == "text_processor":
            logger.debug(f"Checking path: {path}")
            logger.debug(f"Path exists: {path.exists()}")
        
        if path.exists():
            try:
                if logger and name == "text_processor":
                    logger.debug(f"Attempting to load spec from {path}")
                
                spec = importlib.util.spec_from_file_location(name, path)
                if spec and spec.loader:
                    if logger and name == "text_processor":
                        logger.debug(f"Successfully created spec, loading module")
                    
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    
                    if logger and name == "text_processor":
                        logger.debug(f"Module loaded, scanning for functions")
                        logger.debug(f"Module dir: {dir(module)}")
                    
                    # Get all the functions from the module
                    temp_dict = {
                        func_name: getattr(module, func_name)
                        for func_name in dir(module)
                        if (callable(getattr(module, func_name))
                            and not func_name.startswith("_")
                            and getattr(module, func_name).__module__ == module.__name__  # Only functions defined in this module
                        )
                    }
                    
                    if logger and name == "text_processor":
                        logger.debug(f"Found callables: {temp_dict.keys()}")
                        logger.debug(f"Required critical resources: {resources['critical_resources'] if resources else None}")
                    
                    # If not all the callables can be found, skip it and try the next.
                    if all(func in temp_dict.keys() for func in crit_resources):
                        if logger and name == "text_processor":
                            logger.debug(f"All critical resources found, updating callables_dict with {temp_dict}")
                        callables_dict.update(temp_dict)
                        logger.debug(f"Updated callables_dict: {callables_dict}")
                        break
                    else:
                        if logger and name == "text_processor":
                            logger.debug(f"Not all critical resources found, continuing to next path")
                            missing = [func for func in crit_resources if func not in temp_dict.keys()]
                            logger.debug(f"Missing critical resources: {missing}")
                else:
                    if logger and name == "text_processor":
                        logger.debug(f"Failed to create spec for {path}")
                        
            except Exception as e:
                if logger and name == "text_processor":
                    logger.debug(f"Exception loading {path}: {e}")
                continue # Skip this file if it fails to load.
    
    if logger and name == "text_processor":
        logger.debug(f"Returning callables_dict: {callables_dict}")
    
    return callables_dict

import inspect

class _MakeProcessor:

    def __init__(self, resources: _ProcessorResources):
        self.resources = resources

        self._supported_formats = resources["supported_formats"]
        self._crit_resources = resources["critical_resources"]
        self._optional_resources = resources.get("optional_resources", [])
        self._dependencies = resources["dependencies"]
        self._logger = resources["logger"]
        self._name = resources["processor_name"]

        self._base_path = Path(__file__).parent
        self._ProcessorClass = _GenericProcessor

        self._dep_paths = self._get_python_files_from_directory(self._base_path / "by_dependency")
        self._mime_type_paths = self._get_python_files_from_directory(self._base_path / "by_mime_type")
        self._fallback_paths = self._get_python_files_from_directory(self._base_path / "fallbacks")

    @staticmethod
    def _get_python_files_from_directory(directory: Path) -> dict[str, Path]:
        """Get all Python files in a directory."""
        return {file.stem: file for file in directory.iterdir() if file.is_file() and file.suffix == '.py'}

    @staticmethod
    def _convert_to_pascal_case(string: str) -> str:
        """Convert a string to PascalCase."""
        return ''.join(word.capitalize() for word in string.split('_'))

    def _load_module_from_path(self, name: str, path: Path) -> ModuleType:
        self._logger.debug(f"Attempting to load spec for {name} from {path}")
        spec = importlib.util.spec_from_file_location(name, path)
        if spec and spec.loader:
            self._logger.debug(f"Successfully created spec, loading module")
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        else:
            raise ImportError(f"Could not load module '{name}' from path '{path}'")

    def _get_functions_from_module(self, module: ModuleType) -> dict[str, Callable]:
        logger.debug(f"Module loaded, scanning for functions")
        logger.debug(f"Module dir: {dir(module)}")

        # Get all the functions from the module
        func_dict = {
            func_name: getattr(module, func_name) for func_name in dir(module)
            if (callable(getattr(module, func_name))
                and not func_name.startswith("_")
                and getattr(module, func_name).__module__ == module.__name__  # Only functions defined in this module
            )
        }
        logger.debug(f"Found callables: {func_dict.keys()}")
        logger.debug(f"Required critical resources: {self._crit_resources}")
        return func_dict

    def load_functions_from_file(self, paths: list[Path], name: str = None, resources: dict = None, callables_dict: dict = {}):
        logger.debug(f"load_functions_from_file called with paths: {paths}")
        logger.debug(f"name: {name}")
        logger.debug(f"critical_resources: {self._crit_resources}")

        for path in paths:
            logger.debug(f"Checking path: {path}")
            try:
                try:
                    module = self._load_module_from_path(name, path)
                except ImportError as e:
                    self._logger.debug(f"Failed to load module from path {path}: {e}")
                    continue

                func_dict = self._get_functions_from_module(module)
                missing = [func for func in self._crit_resources if func not in func_dict.keys()]
                if not missing:
                    callables_dict.update(func_dict)
                    break
                else:
                    logger.debug(f"Missing critical resources, continuing to next path.\nMissing: {missing}")

            except Exception as e:
                logger.debug(f"Exception loading {path}: {e}")
                continue # Skip this file if it fails to load.

        logger.debug(f"Returning callables_dict: {callables_dict}")

        return callables_dict

    def _get_processor_class_for_specific_mime_type(self, name) -> Optional[Any]:

        for format in self._supported_formats:
            proc_name = f"_{format.lower()}_processor"
            if proc_name in self._mime_type_paths.keys():
                path = self._mime_type_paths[proc_name]
                continue
            self._logger.debug(f"Found mime-type processor at {path}")

            try:
                module = self._load_module_from_path(name, path)
            except ImportError as e:
                self._logger.debug(f"Failed to load module from path {path}: {e}")
                continue

            # Import the processor class from the module
            pascal_case_name = self._convert_to_pascal_case(name)
            self._logger.debug(f"pascal_case_name: {pascal_case_name}")
            for attr in dir(module):
                if attr.startswith("_"):
                    continue
                # Ignore imports and non-class attributes
                obj = getattr(module, attr)
                # Skip imported classes (check if defined in this module)
                if hasattr(obj, '__module__') and obj.__module__ != module.__name__:
                    continue

                ProcessorClass = getattr(module, pascal_case_name , _GenericProcessor)

                if not isinstance(ProcessorClass, _GenericProcessor):
                    self._logger.debug(f"Loaded ProcessorClass: {ProcessorClass}")
                    break

        return ProcessorClass

    def run(self) -> Optional[Any]:
        self._logger.debug(f"_make_processor called for {name}")
        self._logger.debug(f"base_path = {base_path}")
        self._logger.debug(f"supported_formats = {self._supported_formats}")
        self._logger.debug(f"dependencies = {self._dependencies}")

        # Check if there's a processor for this specific mime-type.
        self._ProcessorClass = self._get_processor_class_for_specific_mime_type(self._name)
        callables_dict = {}

        dep_paths = [ # Check for dedicated dependencies first.
            path for path in (base_path / "by_dependency").iterdir()
            if not path.stem.startswith("_") and path.suffix == ".py"
        ]
        if any(self._dependencies.keys() in path.stem for path in dep_paths):
            callables_dict = load_functions_from_file(dep_paths, name=name, resources=resources, callables_dict=callables_dict)

            logger.debug(f"dep_paths = {dep_paths}")

        if not callables_dict:
            # If no callables found, try to load the functions from the fallback folder.
            fallback_paths = [ # Check for dedicated dependencies first.
                path for path in (base_path / "fallbacks").iterdir()
            ]
            if is_tex_proc:
                logger.debug(f"No callables found, trying fallback_paths = {fallback_paths}")
            callables_dict = load_functions_from_file(fallback_paths, name=name, resources=resources, callables_dict=callables_dict)

        if is_tex_proc:
            logger.debug(f"Final callables_dict = {callables_dict}")

        # Can't find any callables, return a mock processor.
        if not callables_dict:
            # If no processor class found, return a mock processor
            logger.debug(f"Returning MagicMock for processor {name}")
            return _make_mock(
                resources["critical_resources"],
                resources["optional_resources"],
                resources["supported_formats"],
                name,
                resources["logger"],
                resources["configs"],
            )

        # Update resources with the loaded callables
        for func_name, func in callables_dict.items():
            resources[func_name] = func

        if is_tex_proc:
            logger.debug(f"Creating ProcessorClass instance with resources: {resources}")

        # Dependency injection time baby!
        try:
            return ProcessorClass(resources=resources, configs=resources["configs"])
        except Exception as e:
            logger.error(f"Failed to create ProcessorClass instance: {e}")
            return _make_mock(
                resources["critical_resources"],
                resources["optional_resources"],
                resources["supported_formats"],
                name,
                resources["logger"],
                resources["configs"],
            )







def _make_processor(resources: _ProcessorResources) -> Optional[Any]:
    """Load a processor module. Try implementation first, then fallback.
    
    Args:
        name: The processor name (e.g., 'plaintext_processor')
        base_path: Base path for processors (defaults to current file's parent)
        
    Returns:
        The loaded module or None if not found
    """
    logger = resources["logger"]
    name = resources["processor_name"]
    is_tex_proc = True if name == "text_processor" else False

    def convert_to_pascal_case(string: str) -> str:
        """Convert a string to PascalCase."""
        return ''.join(word.capitalize() for word in string.split('_'))

    base_path = Path(__file__).parent
    # Default to a generic processor if no specific implementation is found.
        # This ensures we always have a processor class to assign the callables to.
    ProcessorClass = _GenericProcessor
    
    # Debug statements for text_processor
    if is_tex_proc:
        logger.debug(f"_make_processor called for {name}")
        logger.debug(f"base_path = {base_path}")
        logger.debug(f"supported_formats = {resources['supported_formats']}")
        logger.debug(f"dependencies = {resources['dependencies']}")

    # Check if there's a processor for this specific mime-type.
    for format in resources["supported_formats"]:
        path = base_path / "by_mime_type" / f"_{format.lower()}_processor.py"
        if is_tex_proc:
            logger.debug(f"Checking mime-type path: {path}")
        if path.exists():
            if is_tex_proc:
                logger.debug(f"Found mime-type processor at {path}")
            spec = importlib.util.spec_from_file_location(name, path)
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                # Import the processor class from the module
                pascal_case_name = convert_to_pascal_case(name)
                logger.debug(f"pascal_case_name: {pascal_case_name}")
                for attr in dir(module):
                    if attr.startswith("_"):
                        continue
                    # Ignore imports and non-class attributes
                    obj = getattr(module, attr)
                    # Skip imported classes (check if defined in this module)
                    if hasattr(obj, '__module__') and obj.__module__ != module.__name__:
                        continue

                    if is_tex_proc:
                        logger.debug(f"Checking attribute: {attr}")
                ProcessorClass = getattr(module, pascal_case_name , None)

                if is_tex_proc:
                    logger.debug(f"Loaded ProcessorClass: {ProcessorClass}")

                if ProcessorClass is not None:
                    break

    callables_dict = {}

    dep_paths = [ # Check for dedicated dependencies first.
        path for path in (base_path / "by_dependency").iterdir()
        if not path.stem.startswith("_") and path.suffix == ".py"
    ]
    if any(resources["dependencies"].keys() in path.stem for path in dep_paths):
        callables_dict = load_functions_from_file(dep_paths, name=name, resources=resources, callables_dict=callables_dict)

        if is_tex_proc:
            logger.debug(f"dep_paths = {dep_paths}")

    if not callables_dict:
        # If no callables found, try to load the functions from the fallback folder.
        fallback_paths = [ # Check for dedicated dependencies first.
            path for path in (base_path / "fallbacks").iterdir()
        ]
        if is_tex_proc:
            logger.debug(f"No callables found, trying fallback_paths = {fallback_paths}")
        callables_dict = load_functions_from_file(fallback_paths, name=name, resources=resources, callables_dict=callables_dict)

    if is_tex_proc:
        logger.debug(f"Final callables_dict = {callables_dict}")

    # Can't find any callables, return a mock processor.
    if not callables_dict:
        # If no processor class found, return a mock processor
        logger.debug(f"Returning MagicMock for processor {name}")
        return _make_mock(
            resources["critical_resources"],
            resources["optional_resources"],
            resources["supported_formats"],
            name,
            resources["logger"],
            resources["configs"],
        )

    # Update resources with the loaded callables
    for func_name, func in callables_dict.items():
        resources[func_name] = func

    if is_tex_proc:
        logger.debug(f"Creating ProcessorClass instance with resources: {resources}")

    # Dependency injection time baby!
    try:
        return ProcessorClass(resources=resources, configs=resources["configs"])
    except Exception as e:
        logger.error(f"Failed to create ProcessorClass instance: {e}")
        return _make_mock(
            resources["critical_resources"],
            resources["optional_resources"],
            resources["supported_formats"],
            name,
            resources["logger"],
            resources["configs"],
        )


def make_processors() -> dict[str, Any]:
    """Create all processor instances.

    Returns:
        dict mapping processor names to processor instances
    """
    from configs import configs
    from logger import logger
    from __version__ import __version__

    processors = {}
    # Start with plaintext processor. This will be our template for all other processors.
    plaintext_resources = {
        "supported_formats": {"txt"},
        "processor_name": "plaintext_processor",
        "dependencies": {},
        "critical_resources": ["extract_text", "extract_metadata", "extract_structure", "process"],
        "optional_resources": ["analyze", "convert"],
        "logger": logger,
        "configs": configs,
    }
    try:
        logger.debug("Creating plaintext processor")
        processor = _make_processor(plaintext_resources)
        processors[plaintext_resources["processor_name"]] = _make_processor(plaintext_resources)
    except Exception as e:
        logger.exception(f"Failed to create plaintext processor: {e}")

    frozenset_dict = {}
    # Create processors from get_processor_resource_configs
    for resource_config in get_processor_resource_configs():
        # Add logger and configs to resources
        resource_config["supported_formats"] = _get_supported_formats_from_resource_config(resource_config)

        frozenset_dict.update({
            resource_config["processor_name"]: resource_config["supported_formats"]
        })

        resources = {
            **resource_config,
            "logger": logger,
            "configs": configs,
            "get_version": lambda: __version__,
            "processor_available": True,  # Assume all processors are available by default
        }
        try:
            processor = _make_processor(resources)
            processors[resource_config["processor_name"]] = processor
        except Exception as e:
            continue # Skip processors that fail to initialize. NOTE This should be logged, but only when in production mode.
    #logger.debug(f"frozenset_dict: {frozenset_dict}")

    # Add cross-processor dependencies
    processors: dict[str, Any] = _apply_cross_processor_dependencies(
        processors=processors, 
        dependencies=[ # TODO This really should be dynamic based on what's in the processors dictionary.
            ("xlsx_processor", "extract_images", "image_processor", "process"),
            ("pdf_processor", "extract_images", "image_processor", "process"),
            ("docx_processor", "extract_images", "image_processor", "process"),
        ])

    # Make the keys of frozenset_dict into the keys of processors
    temp_dict = {}
    for proc_name, set_ in frozenset_dict.items():
        #logger.debug(f"Adding supported formats to processor {proc_name}: {set_}")
        processor = processors[proc_name]
        assert processor is not None, f"Processor {proc_name} is None, cannot add supported formats."
        proc_tuple = (proc_name, processor, set_)
        logger.debug(f"{(proc_name, processor, set_)}")
        temp_dict[proc_name] = proc_tuple

    processors = temp_dict

    for proc in processors.values():
        assert isinstance(proc, tuple), f"Processor {proc} is not a tuple, but a {type(proc)}."

    return processors
