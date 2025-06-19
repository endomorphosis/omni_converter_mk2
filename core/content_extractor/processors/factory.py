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
from types_ import Any, Optional, TypedDict, Union
from ._get_processor_resource_configs import get_processor_resource_configs


class _ProcessorResources(TypedDict):
    """
    TypedDict defining the structure of processor resources.

    Attributes:
        supported_formats: Set of formats supported by the processor
        processor_name: Name of the processor
        dependencies: Dictionary mapping dependency names to their instances
        critical_resources: list of critical resources required by the processor
        optional_resources: list of optional resources that enhance functionality
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


def _make_mock(critical_resources, optional_resources,
                supported_formats, processor_name, logger, configs) -> MagicMock:
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
    Create a dynamic processor based on available dependencies.
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


def _make_processor(resources: _ProcessorResources) -> Any:
    """
    Create a processor based on available dependencies.

    Args:
        resources: _ProcessorResources dict with processor configuration
        
    Returns:
        Processor instance or mock if dependencies unavailable
    """
    processor_name = resources["processor_name"]
    dependencies = resources["dependencies"]
    critical_resources = resources["critical_resources"]
    optional_resources = resources.get("optional_resources", [])
    logger = resources["logger"]
    configs = resources["configs"]
    supported_formats = resources["supported_formats"]

    # If it's specifically an empty dictionary, check the fallbacks folder
    # for a processor with the same name.
    if not dependencies:
        # Check if the processor exists in fallbacks folder
        logger.debug(f"Processor '{processor_name}' not found in dependencies, checking fallbacks folder.")
        try:
            processor = get_fallback_processor(resources, processor_name)
            return processor
        except ImportError:
            logger.warning(f"Processor '{processor_name}' not found in fallbacks folder.")

    # Check dependency priority if specified
    dependency_priority = resources.get("dependency_priority", list(dependencies.keys()))
    dependency_mapping = resources.get("dependency_mapping", {})

    # Try to create processor with available dependencies
    available_impl = None
    available_deps = {}
    degraded_capabilities = []

    # Check which dependencies are available
    for name in dependency_priority:
        if name in dependencies and dependencies[name] is not None:

            # Check if dependency can be loaded from the cache
            try:
                dep = dependency_cache[name]
                logger.debug(f"Found cached dependency '{dep}'")
            except Exception as e:
                logger.warning(f"Could not load dependency '{name}'. Checking builtins")
                continue

            available_deps[name] = dependencies[name]
            if available_impl is None:
                available_impl = name

    # Check if we can provide all critical resources
    can_provide_all_critical = True
    if dependency_mapping:
        for critical_resource in critical_resources:
            if critical_resource in dependency_mapping:
                required_deps = dependency_mapping[critical_resource]
                if not any(dep in available_deps for dep in required_deps):
                    can_provide_all_critical = False
                    degraded_capabilities.append(critical_resource)

    # Check for degraded optional resources
    degraded_optional = []
    if dependency_mapping:
        for optional_resource in optional_resources:
            if optional_resource in dependency_mapping:
                required_deps = dependency_mapping[optional_resource]
                if not any(dep in available_deps for dep in required_deps):
                    degraded_optional.append(optional_resource)

    # If no dependencies available or can't provide critical resources, return mock
    if not available_deps or (not can_provide_all_critical and dependency_mapping):
        #logger.warning(f"'{processor_name}' processor not available, returning mock instead.")
        mock = _make_mock(
                critical_resources, 
                optional_resources,
                supported_formats, 
                processor_name, 
                logger, 
                configs
            )
        return mock

    # Create and configure the processor
    processor = _make_dynamic_processor(
        supported_formats=supported_formats,
        processor_name=processor_name,
        available_impl=available_impl,
        available_deps=available_deps,
        critical_resources=critical_resources,
        optional_resources=optional_resources,
        logger=logger,
        configs=configs,
        dependency_mapping=dependency_mapping,
    )

    # Log if we have degraded capabilities
    if degraded_capabilities:
        logger.warning(f"{processor_name} has degraded capabilities: {degraded_capabilities}")

    # Log if we have degraded optional capabilities
    if degraded_optional:
        logger.warning(f"{processor_name} has degraded optional capabilities: {degraded_optional}")

    # Also add a warning when partial dependencies are detected:
    if available_deps and not can_provide_all_critical and dependency_mapping:
        logger.warning(f"{processor_name} has partial dependency availability - some capabilities will be mocked")

    # Log fallback if not using first priority
    if available_impl != dependency_priority[0]:
        logger.warning(f"{processor_name} using fallback implementation: {available_impl}")
        
    return processor

# Resource configurations for different processors
# TODO get_processor_resource_configs import resource_list can likely be defined in a JSON file and loaded at runtime. This can also probably be used to define a jinja template to make processors en-masse.


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
        - source_processor_name (str): Name of the processor to enhance
        - source_method_name (str): Name of the method to enhance
        - target_processor_name (str): Name of the processor that provides enhancement
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
    
    # Process each dependency
    for dependency in dependencies:
        try:
            # Validate dependency format
            if not isinstance(dependency, tuple) or len(dependency) != 4:
                logging.warning(f"Invalid dependency format: {dependency}. Skipping.")
                continue
            
            source_processor_name, source_method_name, target_processor_name, target_method_name = dependency
            
            # Check if processors exist
            if source_processor_name not in processors:
                logging.warning(f"Source processor '{source_processor_name}' not found. Skipping.")
                continue
            if target_processor_name not in processors:
                logging.warning(f"Target processor '{target_processor_name}' not found. Skipping.")
                continue
    
            source_processor = processors[source_processor_name]
            target_processor = processors[target_processor_name]
            
            # Check if methods exist
            try:
                original_method = getattr(source_processor, source_method_name)
            except AttributeError:
                logging.warning(f"Source processor '{source_processor_name}' does not have method '{source_method_name}'. Skipping.")
                continue
            try:
                target_method = getattr(target_processor, target_method_name)
            except AttributeError:
                logging.warning(f"Target processor '{target_processor_name}' does not have method '{target_method_name}'. Skipping.")
                continue
            
            # Create enhanced method
            def create_enhanced_method(orig_method: Callable, enhance_method: Callable) -> Callable:
                @functools.wraps(orig_method)
                def enhanced_method(*args, **kwargs):
                    # Call original method first
                    original_result = orig_method(*args, **kwargs)
                    
                    # If original result is a list/iterable, enhance each item
                    try:
                        if isinstance(original_result, (list, tuple)):
                            enhanced_results = []
                            for item in original_result:
                                try:
                                    enhanced_item = enhance_method(item)
                                    enhanced_results.append(enhanced_item)
                                except Exception:
                                    # If enhancement fails, keep original item
                                    enhanced_results.append(item)
                            return type(original_result)(enhanced_results)
                        else:
                            # Single item enhancement
                            return enhance_method(original_result)
                    except Exception:
                        # If any enhancement fails, return original result
                        return original_result
                
                return enhanced_method
            
            # Replace the original method with the enhanced one
            enhanced_method = create_enhanced_method(original_method, target_method)
            setattr(source_processor, source_method_name, enhanced_method)
            
            # Update processor_info dependencies if it exists
            if hasattr(source_processor, 'processor_info'):
                if 'dependencies' not in source_processor.processor_info:
                    source_processor.processor_info['dependencies'] = []
                if target_processor_name not in source_processor.processor_info['dependencies']:
                    source_processor.processor_info['dependencies'].append(target_processor_name)
            else:
                # Create processor_info if it doesn't exist
                source_processor.processor_info = {'dependencies': [target_processor_name]}
                
        except Exception as e:
            logging.error(f"Error processing dependency {dependency}: {e}")
            continue
    
    return processors



def make_processors() -> dict[str, Any]:
    """Create all processor instances.

    Returns:
        dict mapping processor names to processor instances
    """
    from configs import configs
    from logger import logger

    processors = {}
    # Start with plaintext processor. This will be our template for all other processors.
    plaintext_resources = {
        "supported_formats": {"txt"},
        "processor_name": "plaintext_processor",
        "dependencies": {},
        "critical_resources": ["extract_text", "extract_metadata", "extract_sections", "process"],
        "optional_resources": ["analyze", "convert"],
        "logger": logger,
        "configs": configs,
    }
    try:
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
        }
        try:
            processor = _make_processor(resources)
            processors[resource_config["processor_name"]] = processor
        except Exception as e:
            continue # Skip processors that fail to initialize. NOTE This should be logged, but only when in production mode.
    logger.debug(f"frozenset_dict: {frozenset_dict}")

    # Add cross-processor dependencies
    processors: dict[str, Any] = _apply_cross_processor_dependencies(
        processors=processors, 
        dependencies=[ # TODO This really should be dynamic based on what's in the processors dictionary.
            ("xlsx_processor", "extract_images", "image_processor", "process"),
            ("pdf_processor", "extract_images", "image_processor", "process"),
            ("docx_processor", "extract_images", "image_processor", "process"),
        ])

    # Make the keys of frozenset_dict into the keys of processors
    for proc_name, set_ in frozenset_dict.items():
        logger.debug(f"Adding supported formats to processor {proc_name}: {set_}")
        processor = processors.get(proc_name)
        proc_tuple = (proc_name, processor, set_)
        logger.debug(f"{(proc_name, processor, set_)}")
        processors[proc_name] = proc_tuple

    return processors


def add_cross_processor_dependencies(processors: dict[str, Any]) -> None:
    """
    Add cross-processor dependencies dynamically.
    
    This function allows processors to use functionality from other processors,
    creating a dependency chain where one processor can delegate certain tasks
    to another more specialized processor.
    
    Args:
        processors: Dictionary of processor instances
    """
    # Define cross-processor dependency configurations
    dependency_configs = [
        {
            "dependent_processor": "xlsx_processor",
            "provider_processor": "image_processor", 
            "method_name": "extract_images",
            "delegate_method": "extract_images"
        },
        {
            "dependent_processor": "pdf_processor",
            "provider_processor": "image_processor",
            "method_name": "extract_images", 
            "delegate_method": "extract_images"
        },
        {
            "dependent_processor": "docx_processor",
            "provider_processor": "image_processor",
            "method_name": "extract_images",
            "delegate_method": "extract_images"
        }
    ]
    
    # Apply each dependency configuration
    for config in dependency_configs:
        dependent_name = config["dependent_processor"]
        provider_name = config["provider_processor"]
        method_name = config["method_name"]
        delegate_method = config["delegate_method"]
        
        # Check if both processors exist
        if dependent_name not in processors or provider_name not in processors:
            continue
            
        dependent_proc = processors[dependent_name]
        provider_proc = processors[provider_name]
        
        # Check if dependent processor has the method to replace
        if not hasattr(dependent_proc, method_name):
            continue
            
        # Check if provider processor has the delegate method
        if not hasattr(provider_proc, delegate_method):
            continue
            
        # Store original method
        original_method = getattr(dependent_proc, method_name)
        
        # Create enhanced method that uses provider processor
        def create_enhanced_method(original, provider, delegate_name):
            def enhanced_method(*args, **kwargs):
                try:
                    # First try the provider processor
                    provider_method = getattr(provider, delegate_name)
                    return provider_method(*args, **kwargs)
                except Exception:
                    # Fallback to original method if provider fails
                    return original(*args, **kwargs)
            return enhanced_method
        
        # Replace the method
        enhanced_method = create_enhanced_method(original_method, provider_proc, delegate_method)
        setattr(dependent_proc, method_name, enhanced_method)
        
        # Update processor info if available
        if hasattr(dependent_proc, "processor_info"):
            dependencies = dependent_proc.processor_info.get("dependencies", [])
            if provider_name not in dependencies:
                dependent_proc.processor_info["dependencies"].append(provider_name)


def generate_capability_report(processors: dict[str, Any]) -> str:
    """
    Generate a human-readable capability report.
    
    Args:
        processors: Dictionary of processor instances
        
    Returns:
        Formatted capability report string
    """
    lines = ["=" * 60, "PROCESSOR CAPABILITY REPORT", "=" * 60, ""]
    
    for processor_name, processor in sorted(processors.items()):
        lines.append(f"{processor_name}:")
        lines.append("-" * 40)
        
        if hasattr(processor[1], "processor_info"):
            info = processor[1].processor_info
            capabilities = info.get("capabilities", {})
            
            for cap_name, cap_info in sorted(capabilities.items()):
                if cap_info["available"]:
                    status = "✓"
                    impl = cap_info["implementation"]
                else:
                    status = "✗"
                    impl = "mock"
                lines.append(f"  {status} {cap_name} ({impl})")
                
            formats = info.get("supported_formats", set())
            if formats:
                lines.append(f"  Supported formats: {', '.join(sorted(formats))}")
        else:
            lines.append("  No processor info available")
            
        lines.append("")
    
    return "\n".join(lines)


def generate_startup_report(processors: dict[str, tuple[str, Any, set]]) -> str:
    """
    Generate a startup summary report.
    
    Args:
        processors: Dictionary of processor instances
        
    Returns:
        Formatted startup report string
    """
    from logger import logger
    lines = ["", "=" * 60, "CONTENT PROCESSOR STARTUP REPORT", "=" * 60, ""]
    
    # Sort by alphabetical order
    processors = dict(sorted(processors.items()))
    total_processors = len(processors)
    fully_functional_count = 0
    fully_functional = []
    degraded = []
    missing_deps = set()

    for processor_name, processor in processors.items():
        if hasattr(processor[1], "processor_info"):
            info = processor[1].processor_info
            capabilities = info.get("capabilities", {})

            # Check if all capabilities are available
            all_available = all(cap["available"] for cap in capabilities.values())
            if all_available and capabilities:
                fully_functional_count += 1
                fully_functional.append(processor_name)
            elif any(not cap["available"] for cap in capabilities.values()):
                degraded.append(processor_name)

            # Track missing dependencies
            if info.get("implementation_used") == "mock":
                missing_deps.add(processor_name)

    lines.append(f"Total processors loaded: {total_processors}")
    lines.append(f"Fully functional: {fully_functional_count}")
    lines.append(f"DEGRADED: {len(degraded)}")

    if fully_functional_count == total_processors:
        lines.append("\nAll processors are fully functional.")
        lines.append("\n" + "=" * 60)
        return "\n".join(lines)

    if fully_functional:
        lines.append("\nProcessors with FULL capabilities:")
        for proc in fully_functional:
            lines.append(f"  {proc}")

    if degraded:
        lines.append("\nProcessors with DEGRADED capabilities:")
        for proc in degraded:
            lines.append(f"  WARNING: {proc}")

    if missing_deps:
        lines.append("\nTo restore full functionality, install missing dependencies:")
        lines.append("  pip install pillow opencv-python pydub beautifulsoup4 lxml")
        lines.append("  pip install pandas pypdf2 python-docx openpyxl")

    lines.append("\n" + "=" * 60)

    return "\n".join(lines)
