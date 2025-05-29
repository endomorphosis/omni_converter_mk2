"""
Factory functions for creating and configuring LLM components.
Provides a unified API for initializing LLM interfaces and resources.
"""
import os
from pathlib import Path
from typing import Any, Optional

from logger import logger
from ..dependency_modules.openai_processor import (
    check_openai_available,
    create_async_openai_client,
    calculate_cost,
    generate_text,
    generate_embeddings
)
from .refactored_async_interface import AsyncLLMInterface, create_async_llm_interface
from .refactored_embeddings import EmbeddingsManager, create_embeddings_manager
from .refactored_prompt_loader import load_prompt_by_name


def create_llm_resources(
    api_key: Optional[str] = None,
    model: str = "gpt-3.5-turbo",
    embedding_model: str = "text-embedding-ada-002",
    embedding_dimensions: int = 1536
) -> dict[str, Any]:
    """
    Create a resources dictionary with LLM components.
    
    Args:
        api_key: OpenAI API key (uses environment variable if not provided)
        model: Model to use for text generation
        embedding_model: Model to use for embeddings
        embedding_dimensions: Dimensions of embedding vectors
        
    Returns:
        Dictionary of LLM resources
    """
    resources = {}
    
    # Check if OpenAI is available
    if not check_openai_available():
        logger.warning("OpenAI library not available. LLM functionality will be limited.")
        return resources
    
    # Use provided API key or get from environment
    key = api_key or os.environ.get("OPENAI_API_KEY")
    if not key:
        logger.warning("OpenAI API key not provided and not found in environment. LLM functionality will be limited.")
        return resources
    
    # Create async client
    async_client = create_async_openai_client(key)
    if not async_client:
        logger.error("Failed to create AsyncOpenAI client. LLM functionality will be limited.")
        return resources
    
    # Add resources to dictionary
    resources["async_client"] = async_client
    resources["generate_text"] = generate_text
    resources["generate_embeddings"] = generate_embeddings
    resources["calculate_cost"] = calculate_cost
    
    return resources


def create_llm_interface(
    configs: Optional[dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Optional[AsyncLLMInterface]:
    """
    Create a configured AsyncLLMInterface instance.
    
    Args:
        configs: Configuration parameters
        api_key: OpenAI API key (uses environment variable if not provided)
        
    Returns:
        Configured AsyncLLMInterface instance or None if creation failed
    """
    # Use default configs if none provided
    config_params = configs or {}
    
    # Get model configurations
    model = config_params.get("model", "gpt-3.5-turbo")
    embedding_model = config_params.get("embedding_model", "text-embedding-ada-002")
    embedding_dimensions = config_params.get("embedding_dimensions", 1536)
    
    # Create resources
    resources = create_llm_resources(
        api_key=api_key,
        model=model,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions
    )
    
    # Check if required resources are available
    if "async_client" not in resources or "generate_text" not in resources:
        logger.error("Required LLM resources not available. Cannot create interface.")
        return None
    
    try:
        # Create interface with resources and configs
        interface = create_async_llm_interface(
            resources=resources,
            configs=config_params
        )
        return interface
    except Exception as e:
        logger.error(f"Error creating LLM interface: {e}")
        return None


def create_embeddings_manager_instance(
    configs: Optional[dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> Optional[EmbeddingsManager]:
    """
    Create a configured EmbeddingsManager instance.
    
    Args:
        configs: Configuration parameters
        api_key: OpenAI API key (uses environment variable if not provided)
        
    Returns:
        Configured EmbeddingsManager instance or None if creation failed
    """
    # Use default configs if none provided
    config_params = configs or {}
    
    # Get embedding configurations
    embedding_model = config_params.get("embedding_model", "text-embedding-ada-002")
    embedding_dimensions = config_params.get("embedding_dimensions", 1536)
    
    # Create resources
    resources = create_llm_resources(
        api_key=api_key,
        embedding_model=embedding_model,
        embedding_dimensions=embedding_dimensions
    )
    
    try:
        # Create embeddings manager with resources and configs
        manager = create_embeddings_manager(
            resources=resources,
            configs=config_params
        )
        return manager
    except Exception as e:
        logger.error(f"Error creating embeddings manager: {e}")
        return None


def initialize_llm_components(
    configs: Optional[dict[str, Any]] = None,
    api_key: Optional[str] = None
) -> dict[str, Any]:
    """
    Initialize and return all LLM components.
    
    Args:
        configs: Configuration parameters
        api_key: OpenAI API key (uses environment variable if not provided)
        
    Returns:
        Dictionary with initialized LLM components
    """
    config_params = configs or {}
    
    # Create interface and embeddings manager
    interface = create_llm_interface(config_params, api_key)
    embeddings_manager = create_embeddings_manager_instance(config_params, api_key)
    
    # Return components dictionary
    return {
        "llm_interface": interface,
        "embeddings_manager": embeddings_manager,
        "resources": create_llm_resources(api_key)
    }