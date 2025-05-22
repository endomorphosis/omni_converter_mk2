"""
Tests for the Interface Factory module.

This module provides comprehensive tests for the InterfaceFactory class, which is
responsible for creating appropriate interfaces (API, CLI) to the Omni Converter
system. The tests verify that the factory correctly instantiates interfaces with
the proper dependencies and configuration, and handles invalid interface requests
appropriately with descriptive errors.
"""

import unittest
from unittest.mock import MagicMock, patch

from utils.configs import Configs
from interfaces.python_api import PythonAPI
from interfaces.interface_factory import InterfaceFactory


class TestInterfaceFactory(unittest.TestCase):
    """
    Test suite for the InterfaceFactory class.
    
    This test class verifies that the InterfaceFactory correctly implements the factory
    pattern for creating different interfaces to the Omni Converter system. Tests cover
    initialization with dependencies, creating specific interface types (API, CLI), and
    handling error cases for invalid interface requests.
    """
    
    def setUp(self):
        """
        Set up test environment before each test.
        
        Creates a mock Configs and initializes an InterfaceFactory instance
        with the mocked dependency for isolation in unit testing.
        """
        self.resources = {
            'python_api': MagicMock(spec=PythonAPI),
            'cli': None,
        }

        # Mock Configs
        self.configs = MagicMock(spec=Configs)
        
        # Create factory with mocked dependencies
        self.factory = InterfaceFactory(resources=self.resources,configs=self.configs)
    
    def test_init(self):
        """
        Test proper initialization of the InterfaceFactory.
        
        Verifies that the InterfaceFactory correctly stores the provided Configs
        instance during initialization, making it available for interfaces it creates.
        """
        self.assertEqual(self.factory.configs, self.configs)
    
    def test_create_api(self):
        """
        Test the create_api method for instantiating a Python API interface.
        
        Verifies that the factory correctly creates a PythonAPI instance and
        configures it with the factory's Configs. This ensures that interfaces
        created by the factory have access to the proper configuration settings.
        """
        # Create API
        api = self.factory.create_api()
        
        # Check type
        self.assertIsInstance(api, PythonAPI)
        
        # Check that it uses the factory's config manager
        self.assertEqual(api.configs, self.configs)
    
    def test_create_cli(self):
        """
        Test the create_cli method for unimplemented interface types.
        
        Verifies that attempting to create a CLI interface raises NotImplementedError,
        as this interface type is defined in the factory API but not yet implemented.
        This ensures appropriate error handling for unsupported interface types.
        """
        with self.assertRaises(NotImplementedError):
            self.factory.create_cli()
    
    def test_get_config_manager(self):
        """
        Test the configs method for accessing the configuration manager.
        
        Verifies that the factory provides access to its Configs instance,
        allowing components to retrieve configuration settings directly if needed.
        """
        configs = self.factory.configs
        self.assertEqual(configs, self.configs)
    
    def test_create_interface_api(self):
        """
        Test creating an API via the generic create_interface method.
        
        Verifies that the factory's create_interface method correctly instantiates
        a PythonAPI when requested with the 'api' interface type. This ensures the
        generic interface creation method properly delegates to specific creation methods.
        """
        api = self.factory.create_interface('api')
        self.assertIsInstance(api, PythonAPI)
    
    def test_create_interface_cli(self):
        """
        Test creating a CLI via the generic create_interface method.
        
        Verifies that the factory's create_interface method correctly raises NotImplementedError
        when attempting to create a 'cli' interface type that is not yet implemented.
        This ensures the generic interface creation method properly delegates to specific
        creation methods and maintains consistent error handling.
        """
        with self.assertRaises(NotImplementedError):
            self.factory.create_interface('cli')
    
    def test_create_interface_invalid(self):
        """
        Test error handling when requesting an invalid interface type.
        
        Verifies that the factory's create_interface method correctly raises ValueError
        when requested to create an interface type that is not defined in the factory's
        supported types. This ensures proper validation of interface type parameters.
        """
        with self.assertRaises(ValueError):
            self.factory.create_interface('invalid')


if __name__ == "__main__":
    unittest.main()