"""
Tests for the Interface Factory module.
"""

import unittest
from unittest.mock import MagicMock, patch

from utils.config import ConfigManager
from interfaces.python_api import PythonAPI
from interfaces.interface_factory import InterfaceFactory


class TestInterfaceFactory(unittest.TestCase):
    """Test the InterfaceFactory class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Mock ConfigManager
        self.mock_config_manager = MagicMock(spec=ConfigManager)
        
        # Create factory with mocked dependencies
        self.factory = InterfaceFactory(custom_config_manager=self.mock_config_manager)
    
    def test_init(self):
        """Test initialization."""
        self.assertEqual(self.factory.config_manager, self.mock_config_manager)
    
    def test_create_api(self):
        """Test creating a Python API."""
        # Create API
        api = self.factory.create_api()
        
        # Check type
        self.assertIsInstance(api, PythonAPI)
        
        # Check that it uses the factory's config manager
        self.assertEqual(api.config_manager, self.mock_config_manager)
    
    def test_create_cli(self):
        """Test creating a CLI (which should raise NotImplementedError)."""
        with self.assertRaises(NotImplementedError):
            self.factory.create_cli()
    
    def test_get_config_manager(self):
        """Test getting the config manager."""
        config_manager = self.factory.get_config_manager()
        self.assertEqual(config_manager, self.mock_config_manager)
    
    def test_create_interface_api(self):
        """Test creating an API via create_interface."""
        api = self.factory.create_interface('api')
        self.assertIsInstance(api, PythonAPI)
    
    def test_create_interface_cli(self):
        """Test creating a CLI via create_interface."""
        with self.assertRaises(NotImplementedError):
            self.factory.create_interface('cli')
    
    def test_create_interface_invalid(self):
        """Test creating an invalid interface type."""
        with self.assertRaises(ValueError):
            self.factory.create_interface('invalid')


if __name__ == "__main__":
    unittest.main()