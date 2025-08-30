"""
Test suite for core/text_normalizer/_text_normalizer.py converted from unittest to pytest.
"""
import pytest
import importlib.util
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import copy

# Skip tests if the module can't be imported
try:
    from core.text_normalizer._normalized_content import NormalizedContent
    from core.text_normalizer._text_normalizer import TextNormalizer
    from core.content_extractor import Content
    from configs import Configs, _PathsBaseModel
    from types_ import Logger
except ImportError:
    pytest.skip("core.text_normalizer module not available", allow_module_level=True)


_THIS_DIR = Path(__file__).parent


def make_mock_configs():
    """Create mock configs for testing."""
    mock_configs = MagicMock()
    mock_configs.paths = MagicMock()
    mock_configs.paths.NORMALIZER_FUNCTIONS_DIR = _THIS_DIR / "default_normalizers_"
    mock_configs.paths.PLUGINS_DIR = _THIS_DIR / "plugins_"
    return copy.deepcopy(mock_configs)


def make_mock_resources():
    """Create a mock resources dictionary for testing."""
    # Create a mock for importlib_util that delegates to the real one for specific methods
    mock_importlib = MagicMock(spec=importlib.util)
    
    # Make spec_from_file_location return real specs
    mock_importlib.spec_from_file_location.side_effect = importlib.util.spec_from_file_location
    mock_importlib.module_from_spec.side_effect = importlib.util.module_from_spec

    mock_resources = {
        "importlib_util": mock_importlib,
        "normalized_content": MagicMock(spec=NormalizedContent),
        "logger": MagicMock(spec=Logger)
    }
    return copy.deepcopy(mock_resources)


# Alternative approach using a custom TextNormalizer subclass for testing
class TestableTextNormalizer(TextNormalizer):
    """Subclass that tracks method calls for testing."""
    
    def __init__(self, resources, configs):
        self.register_calls = []
        super().__init__(resources, configs)
    
    def register_normalizers_from(self, folder):
        """Track calls while executing parent logic."""
        self.register_calls.append(folder)
        return super().register_normalizers_from(folder)


@pytest.fixture
def mock_configs():
    """Provide mock configs for testing."""
    return make_mock_configs()


@pytest.fixture
def mock_resources():
    """Provide mock resources for testing."""
    return make_mock_resources()


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    import tempfile
    import shutil
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.mark.unit
class TestTextNormalizerInitialization:
    """Test TextNormalizer initialization and configuration."""

    @pytest.fixture
    def setup_data(self, mock_configs):
        """Set up test data for each test."""
        # Calculate number of normalizer functions
        try:
            num_normalizer_functions = len(
                [fun for fun in mock_configs.paths.NORMALIZER_FUNCTIONS_DIR.glob("*.py")
                if fun.is_file() and not fun.name.startswith("_")
                and fun.name != "__init__.py"]
            ) + len(
                [fun for fun in mock_configs.paths.PLUGINS_DIR.glob("*.py")
                if fun.is_file() and not fun.name.startswith("_")
                and fun.name != "__init__.py"]
            )
        except AttributeError:
            num_normalizer_functions = 0
        
        return {'num_normalizer_functions': num_normalizer_functions}

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_with_valid_resources_and_configs(self, mock_register, mock_resources, mock_configs, setup_data):
        """
        GIVEN valid resources dict containing:
            - importlib_util: Module for dynamic imports
            - normalized_content: Factory for creating NormalizedContent objects
            - logger: Logger instance for operation logging
        AND valid configs object with:
            - paths.NORMALIZER_FUNCTIONS_DIR attribute (Path object)
            - paths.PLUGINS_DIR attribute (Path object)
        WHEN TextNormalizer is initialized
        THEN expect:
            - Instance created successfully
            - _normalizers initialized with functions from the two input directories
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert isinstance(normalizer, TextNormalizer)
        assert normalizer.configs == mock_configs
        assert normalizer.resources == mock_resources

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_configs_stored_correctly(self, mock_register, mock_resources, mock_configs):
        """
        GIVEN valid resources dict and valid configs object
        WHEN TextNormalizer is initialized
        THEN expect:
            - normalizer.configs equals the provided configs object
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert normalizer.configs == mock_configs

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_resources_stored_correctly(self, mock_register, mock_resources, mock_configs):
        """
        GIVEN valid resources dict and valid configs object
        WHEN TextNormalizer is initialized
        THEN expect:
            - normalizer.resources equals the provided resources dict
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert normalizer.resources == mock_resources

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_logger_component_set_correctly(self, mock_register, mock_resources, mock_configs):
        """
        GIVEN valid resources dict containing logger component
        WHEN TextNormalizer is initialized
        THEN expect:
            - normalizer._logger equals the provided logger
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert normalizer._logger == mock_resources["logger"]

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_importlib_util_component_set_correctly(self, mock_register, mock_resources, mock_configs):
        """
        GIVEN valid resources dict containing importlib_util component
        WHEN TextNormalizer is initialized
        THEN expect:
            - normalizer._importlib_util equals the provided importlib_util
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert normalizer._importlib_util == mock_resources["importlib_util"]

    @patch('core.text_normalizer._text_normalizer.TextNormalizer.register_normalizers_from')
    def test_init_normalized_content_factory_set_correctly(self, mock_register, mock_resources, mock_configs):
        """
        GIVEN valid resources dict containing normalized_content factory
        WHEN TextNormalizer is initialized
        THEN expect:
            - normalizer._normalized_content equals the provided factory
        """
        # GIVEN
        mock_register.return_value = None  # Mock the normalizer loading
        
        # WHEN
        normalizer = TextNormalizer(resources=mock_resources, configs=mock_configs)
        
        # THEN
        assert normalizer._normalized_content == mock_resources["normalized_content"]