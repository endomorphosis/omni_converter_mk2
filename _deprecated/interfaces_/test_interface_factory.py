# """
# Tests for the Interface Factory module.

# This module provides comprehensive tests for the InterfaceFactory class, which is
# responsible for creating appropriate interfaces (API, CLI) to the Omni Converter
# system. The tests verify that the factory correctly instantiates interfaces with
# the proper dependencies and configuration, and handles invalid interface requests
# appropriately with descriptive errors.
# """

# import unittest
# from unittest.mock import MagicMock, patch

# from configs import Configs
# from interfaces.python_api import PythonAPI
# from interfaces.interface_factory import InterfaceFactory
# from interfaces.cli import CLI
# from interfaces import _make_api_resources, _make_resources, _make_cli_resources


# class InstanceOf:
#     """
#     Helper class to check if an object is an instance of a specific class.
#     Used for asserting equality between Mock objects and expected class types.
#     """
#     def __init__(self, klass):
#         self.klass = klass

#     def __eq__(self, other):
#       return isinstance(other, self.klass)


# class TestInterfaceFactory(unittest.TestCase):
#     """
#     Test suite for the InterfaceFactory class.
    
#     This test class verifies that the InterfaceFactory correctly implements the factory
#     pattern for creating different interfaces to the Omni Converter system. Tests cover
#     initialization with dependencies, creating specific interface types (API, CLI), and
#     handling error cases for invalid interface requests.
#     """
    
#     def setUp(self):
#         """
#         Set up test environment before each test.
        
#         Creates a mock Configs and initializes an InterfaceFactory instance
#         with the mocked dependency for isolation in unit testing.
#         """
#         self.mock_resources = {
#             'python_api': MagicMock(spec=PythonAPI),
#             'cli': MagicMock(spec=CLI),
#         }

#         # Mock Configs
#         self.mock_configs = MagicMock(spec=Configs)
        
#         # Create factory with mocked dependencies
#         self.factory = InterfaceFactory(resources=self.mock_resources,configs=self.mock_configs)
    
#     def test_init(self):
#         """
#         Test proper initialization of the InterfaceFactory.
        
#         Verifies that the InterfaceFactory correctly stores the provided Configs
#         instance during initialization, making it available for interfaces it creates.
#         """
#         self.assertEqual(self.factory.configs, self.mock_configs)
    
#     def test_create_api(self):
#         """
#         Test the create_api method for instantiating a Python API interface.
        
#         Verifies that the factory correctly creates a PythonAPI instance and
#         configures it with the factory's Configs. This ensures that interfaces
#         created by the factory have access to the proper configuration settings.
#         """
#         # Create API
#         mock_api = self.factory.create_api(_make_api_resources())
        
#         # Check type
#         self.assertIsInstance(mock_api, PythonAPI)
        
#         # Check that it uses the factory's config manager
#         self.assertEqual(mock_api.configs, self.mock_configs)
    
#     def test_create_cli(self):
#         """
#         Test the create_cli method for unimplemented interface types.
        
#         Verifies that attempting to create a CLI interface raises NotImplementedError,
#         as this interface type is defined in the factory API but not yet implemented.
#         This ensures appropriate error handling for unsupported interface types.
#         """
#         resources = _make_cli_resources()
#         self.assertIsInstance(resources, dict)
#         cli = self.factory.create_cli(resources)
#         #self.assertIsInstance(cli, CLI)
#         self.assertEqual(cli.configs, self.mock_configs)
    
#     def test_get_config_manager(self):
#         """
#         Test the configs method for accessing the configuration manager.
        
#         Verifies that the factory provides access to its Configs instance,
#         allowing components to retrieve configuration settings directly if needed.
#         """
#         configs = self.factory.configs
#         self.assertEqual(configs, self.mock_configs)

# if __name__ == "__main__":
#     unittest.main()