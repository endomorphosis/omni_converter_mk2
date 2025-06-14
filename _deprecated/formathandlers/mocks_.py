# import importlib
# from typing import Any, Callable, TypeVar
# from unittest.mock import MagicMock

# Dataclass = TypeVar('Dataclass')



# # class LoggingMock(MagicMock):
# #     """A MagicMock that logs access to its methods."""
    
# #     def __init__(self, name: str, *args, **kwargs):
# #         super().__init__(*args, **kwargs)
# #         self._mock_name = name
# #         logger.warning(f"Using mocked version of {name}")
    
# #     def __getattr__(self, name):
# #         if name.startswith('_'):
# #             return super().__getattr__(name)
        
# #         logger.warning(f"{self._mock_name}.{name} accessed on mock")
# #         return super().__getattr__(name)





# from logger import logger


# class Mocks:
#     """
#     Make mock classes for external libraries and external programs.
#     """

#     def __new__(cls, resources=None, configs=None): # Enforce singleton pattern
#         if not hasattr(cls, 'instance'):
#             cls.instance = super(Mocks, cls).__new__(cls)
#         return cls.instance


#     def __init__(self, 
#                  resources: dict[str, Callable] = None, 
#                  configs: Dataclass = None
#                  ) -> None:
#         self.configs = configs
#         self.resources = resources

#         self._force_mocks = self.configs.resources.force_mocks
#         self._libraries: dict[str, bool] = self.resources['libraries']
#         self._external_programs: dict[str, bool] = self.resources['external_programs']


#     def make_mocks_from_libraries_and_external_programs(self) -> None:
#         """
#         Create a mock instance of the given class.

#         Args:
#             name: The name of the mock instance.
#             mock_class: The class to create a mock instance of.

#         Returns:
#             A mock instance of the given class.
#         """
#         # Make mocks of all the third-party libraries
#         for key, value in self._libraries.items():
#             if value is False or self._force_mocks:
#                 logger.warning(f'Using mocked version of {key}')
#                 if not hasattr(self, key):
#                     try:
#                         module = importlib.import_module(key)
#                         setattr(self, key, MagicMock(spec=module)) # TODO Errors happen with external API keys (e.g. OpenAI). Find out how to handle this.
#                     except Exception as e:
#                         logger.warning(f"{type(e).__name__} creating mock for {key}: {e}\nReturning generic MagicMock instead.")
#                         setattr(self, key, MagicMock())
#             else:
#                 module = importlib.import_module(key)
#                 setattr(self, key, module)

#         # Make mocks of all the external programs
#         for key, value in self._external_programs.items():
#             if not hasattr(self, key):
#                 setattr(self, key, MagicMock())


# def make_mocks() -> Mocks:
#     """
#     Create a mock instance of the Mocks class.
#     """
#     # Get all the properties in the Constants class.
#     from ...format_handlers.constants import libraries, external_programs
#     from configs import configs

#     resources = {
#         "libraries": libraries,
#         "external_programs": external_programs,
#     }
#     mocks = Mocks(resources=resources,configs=configs)
#     mocks.make_mocks_from_libraries_and_external_programs()
#     return mocks

# mocks = make_mocks()
