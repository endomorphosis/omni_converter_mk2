import ast
from pathlib import Path
from typing import Any, Callable, Self


from pydantic import BaseModel, DirectoryPath, Field, ValidationError


from configs import Configs, configs
from logger import logger

def name(x):
    return type(x).__name__

def _get_item(self: BaseModel, item: Any) -> Any:
    """
    Get the attribute value from the model.

    Args:
        self (Self): The instance of the model.
        item (Any): The name of the attribute to retrieve.

    Returns:
        Any: The value of the requested attribute.
    """
    try:
        return getattr(self, item)
    except AttributeError as e:
        raise KeyError(f"Attribute '{item}' not found.") from e


def _set_item(self: BaseModel, key: str, value: Any) -> None:
    """
    Set the attribute value in the model.

    Args:
        self (BaseModel): The instance of the model.
        key (str): The name of the attribute to set.
        value (Any): The value to set for the attribute.

    Raises:
        ValidationError: If the value does not pass validation.
        AttributeError: If the attribute does not exist.
    """
    try:
        setattr(self, key, value)
        # Re-validate the new value
        self.model_validate()
    except ValidationError as e:
        raise ValidationError(f"Validation error setting '{key}' to '{value}': {e.errors()}")
    except AttributeError as e:
        raise KeyError(f"Attribute '{key}' not found.") from e

def _get(self, key: str, default: Any = None) -> Any:
    """
    Get the attribute value from the model.

    Args:
        self (BaseModel): The instance of the model.
        key (str): The name of the attribute to retrieve.

    Returns:
        Any: The value of the requested attribute.
    """
    try:
        return getattr(self, key)
    except Exception:
        return default


def assign_dict_funcs(self: BaseModel) -> BaseModel:
    self.__getitem__ = _get_item
    self.__setitem__ = _set_item
    self.get = _get
    return self


class Imports(BaseModel):
    """
    A model to represent import statements in a Python file.

    This class is used to store information about the imports found in a
    Python file, including the module name and the imported names.

    Attributes:
        imported_names (list): A list of names imported from the module.
    """
    imported_names: list[str] = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)

class Functions(BaseModel):
    """
    A model to represent functions in a Python file.

    This class is used to store information about the functions found in a
    Python file, including the function name, arguments, docstring, and
    return type.

    Attributes:
        name (str): The name of the function.
        args (list): A list of argument names for the function.
        docstring (str): The docstring of the function.
        returns (str): The return type of the function.
    """
    name: str
    args: list[str] = Field(default_factory=list)
    docstring: str = None
    returns: str = None
    decorators: list[str] = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)

class ModelInfo(BaseModel):
    """
    A base model for the test file generator.

    This class defines the structure of the configuration and resources
    used in the test file generation process.

    Attributes:
        configs (Configs): Configuration settings for the application.
        resources (dict): Resources needed for generating test files.
    """
    path: DirectoryPath = Field(default_factory=list)
    imports: Imports = Field(default_factory=list)
    functions: list = Field(default_factory=list)
    coroutines: list = Field(default_factory=list)
    classes: list = Field(default_factory=list)

    def __init__(self, **data) -> Self:
        super().__init__(**data)
        self = assign_dict_funcs(self)


def _get_docstring_as_list(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef) -> list[str]:
    """
    Convert a docstring into a list of lines.

    Args:
        node (astnode): The node where the docstring is.

    Returns:
        list[str]: A list of lines from the docstring.
    """
    docstring = ast.get_docstring(node)
    if not docstring:
        return []
    return [line for line in docstring.splitlines() if line.strip()]

def _get_args(node: ast.FunctionDef | ast.AsyncFunctionDef | ast.arguments | ast.arg) -> list[str]:
    """
    Get the arguments from the function definition.

    Args:
        node (ast.FunctionDef): The AST node representing a function definition.

    Returns:
        list[str]: A list of argument names for the function.
    """
    return [arg.arg for arg in node.args.args]

def _get_returns(node: ast.FunctionDef | ast.AsyncFunctionDef) -> str:
    """
    Get the return type from the function definition.

    Args:
        node (ast.FunctionDef): The AST node representing a function definition.

    Returns:
        str: The return type of the function.
    """
    if node.returns:
        return ast.unparse(node.returns)
    return None

class _AstFileParser:
    """
    A class to parse Python files and extract information about their callables.
    
    This class uses the Abstract Syntax Tree (AST) module to analyze Python code
    and extract information about functions, classes, and their attributes.
    """
    _MODULE_KEYS = ['imports', 'functions', 'coroutines', 'classes']
    _CLASS_KEYS = ['attribute', 'classmethod', 'coroutine', 'dunder', 
                    'method', 'property', 'staticmethod', 'unknown']

    def __init__(self, file_path: str):
        self.file_path = file_path

        # Initialize collections for different types of callables
        self.module_info: dict[str, list] = {key: [] for key in self._MODULE_KEYS}
        self.module_info["module_name"] = Path(file_path).stem

        self.file_content: str = self._open_file()

    def _open_file(self) -> str:
        """Open the file and read its content."""
        with open(self.file_path, 'r') as file:
            return file.read()

    @property
    def nodes(self):
        # Use ast.parse().body to get only top-level nodes, not nested ones
        for node in ast.parse(self.file_content).body:
            yield node

    def extract_imports_from(self, node: ast.Import | ast.ImportFrom) -> None:
        """Extract import statements from the AST node.
        
        Args:
            node (ast.Import | ast.ImportFrom): The AST node representing an import statement.
        """
        import_str = ast.unparse(node)
        
        # Handle future imports separately - they must be at the top
        if isinstance(node, ast.ImportFrom) and node.module == "__future__":
            if "future_imports" not in self.module_info:
                self.module_info["future_imports"] = []
            # Avoid duplicates
            if import_str not in self.module_info["future_imports"]:
                self.module_info["future_imports"].append(import_str)
        else:
            # Avoid duplicates
            if import_str not in self.module_info["imports"]:
                self.module_info["imports"].append(import_str)

    def extract_standalone_functions_and_coroutines(self, node: ast.FunctionDef) -> None:
        """Extract standalone functions and coroutines from the AST node."""
        is_coroutine = any(isinstance(decorator, ast.Name) and decorator.id == "coroutine" for decorator in node.decorator_list)
        key = "coroutines" if is_coroutine else "functions"
        self.module_info[key].append({
            "name": node.name,
            "args": _get_args(node),
            "docstring": _get_docstring_as_list(node),
            "returns": ast.unparse(node.returns) if node.returns else None,
            "decorators": [ast.unparse(decorator) for decorator in node.decorator_list],
        })

    def _extract_class_methods(self, item: ast.FunctionDef, class_info: dict[str, list]) -> dict[str, Any]:
        method_info = {
            "name": item.name,
            "args": _get_args(item),
            "docstring": _get_docstring_as_list(item),
            "returns": ast.unparse(item.returns) if item.returns else None,
        }
        # Identify method type - default to "methods"
        method_name = "method"
        for dec in item.decorator_list:
            decorator_name = dec.id if isinstance(dec, ast.Name) else "unknown"
            if isinstance(dec, ast.Name):
                if decorator_name in self._CLASS_KEYS:
                    method_name = decorator_name
                elif item.name.startswith("__") and item.name.endswith("__"):
                    method_name = "dunder"
                logger.debug(f"Found {decorator_name} decorator: {dec.id}")
            else:
                logger.warning(f"Unknown decorator: {ast.unparse(dec)}")
                continue
        
        # Special case for dunder methods without decorators
        if not item.decorator_list and item.name.startswith("__") and item.name.endswith("__"):
            method_name = "dunder"

        # Put the method info in the appropriate list
        #logger.debug(f"method_name: {method_name}\nclass_info: {class_info}")
        class_info[method_name].append(method_info)
        
        # Also add to a unified 'methods' list for template compatibility
        if "methods" not in class_info:
            class_info["methods"] = []
        class_info["methods"].append(method_info)
        
        return class_info

    def _extract_init_attributes(self, item: ast.FunctionDef) -> list[str]:
        """
        Extract the final assignment values for all attributes in the __init__ method.
        
        Args:
            item (ast.FunctionDef): The AST node representing the __init__ function definition.
            
        Returns:
            list[str]: A list of strings representing the final value assigned to each attribute.
        """
        # Verify this is the __init__ method
        if not (isinstance(item, ast.FunctionDef) and item.name == "__init__"):
            return []

        init_method = item
        
        # Track the final assignment for each attribute
        attribute_assignments = {}  # attr_name -> value_string
        
        for stmt in init_method.body:
            if isinstance(stmt, ast.Assign):
                # Check if any target is a self attribute assignment
                for target in stmt.targets:
                    if (isinstance(target, ast.Attribute) and 
                        isinstance(target.value, ast.Name) and 
                        target.value.id == "self"):
                        
                        # Convert the value AST node back to string
                        attribute_assignments[target.attr] = ast.unparse(target).replace("self.", "") # So we don't get self.self.attr
                        break
        
        # Return list of final values for each attribute
        return list(attribute_assignments.values())


    def _extract_class_attributes(self, item: ast.FunctionDef) -> list[dict[str, Any]]:
        """
        Extract class attributes from assignment statements in the class body.
        
        Args:
            item (ast.Assign): The AST node representing an assignment statement.
            
        Returns:
            list[dict[str, Any]]: A list of dictionaries containing attribute names and values.
        """
        return [
            {"name": target.id, "value": ast.unparse(item.value), "type": name(item.value)}
            for target in item.targets 
            if isinstance(target, ast.Attribute)
        ]

    def extract_classes_from(self, node: ast.ClassDef) -> None:
        """Extract class information from the AST node."""

        class_info = {key: [] for key in self._CLASS_KEYS}
        class_info.update({"docstring": _get_docstring_as_list(node),})

        for item in node.body:
            #logger.debug(f"Processing class body item {name(item)}: {ast.unparse(item)}")
            match item:
                case ast.FunctionDef():
                    # logger.debug(f"Found function in class body '{name(item)}': {ast.unparse(item)}")
                    class_info['method'].append(self._extract_class_methods(item, class_info))
                    if item.name == "__init__":
                        class_info["attribute"].extend(self._extract_init_attributes(item))
                case ast.Attribute() | ast.Assign():
                    #logger.debug(f"Found attribute in class body: {ast.unparse(item)}")
                    #class_info["attribute"].extend(self._extract_class_attributes(item))
                    continue
                case ast.Import() | ast.ImportFrom():
                    logger.debug(f"Found import in class body: {ast.unparse(item)}")
                case ast.Expr() if isinstance(item.value, ast.Constant):
                    if not isinstance(item.value.value, str):
                        logger.warning(f"Unexpected constant in class body {name(item)}: {ast.unparse(item)}")
                    else: # Skip docstrings in the class body. They're assigned to the class_info['docstring'] already.
                        continue
                case _:
                    logger.warning(f"Unknown class body item: '{name(item)}' {ast.unparse(item)}")
                    continue

        class_info["name"] = node.name
        self.module_info["classes"].append(class_info)

    def extract_exceptions_from(self, node: ast.ExceptHandler) -> None:
        """Extract exception information from the AST node."""
        raise NotImplementedError("Exception extraction not implemented yet.")

    def extract_resources_and_configs_from(self, node: ast.Assign) -> None:
        """
        Extract the resources dictionary and configs pydantic base model from a file.
        The return values should be the last time they are changed in the file.

        Since many classes work via dependency injection, we need to extract the
        resources and configs from the file, so that we can use or mock them in tests.

        Args:
            node (ast.Assign): The AST node representing assignments.
        """
        for target in node.targets:
            if isinstance(target, ast.Name):
                match target.id:
                    case 'configs':
                        # Get all the values of the attributes of the configs pydantic base model.
                        # If there are any nested attributes, they should be included as well.

                        # Try to extract the actual configuration attributes if it's a variable assignment
                        try:
                            if isinstance(node.value, ast.Name):
                                # It's referencing an existing variable
                                self.module_info['configs_reference'] = node.value.id
                            elif isinstance(node.value, (ast.Dict, ast.Call)):
                                # It's either a dictionary or a model instantiation
                                self.module_info['configs_type'] = 'direct_assignment'
                        except Exception as e:
                            logger.warning(f"Failed to extract configs details: {str(e)}")

                    case 'resources' if isinstance(node.value, ast.Dict):
                        # Get the keys and values of the resources dictionary.
                        self.module_info['resources'] = {
                            ast.unparse(key): ast.unparse(value)
                            for key, value in zip(node.value.keys, node.value.values)
                        }
                    case _:
                        pass  # Ignore other assignments


def parse_file(file_path: str) -> dict[str, Any]:
    """
    Parse a Python file to extract information about its callables.
    
    Args:
        file_path (str): Path to the Python file.
        
    Returns:
        dict: A dictionary containing information about the file's callables.
    """
    # Initialize the parser
    parser = _AstFileParser(file_path)

    # Get any variables called 'configs' or 'resources' that are not defined in classes or functions.
    # It should be the last time they are changed in the file.
    
    # Track assignments to 'configs' and 'resources' at module level
    try:
        # Parse the file content into an AST, then iterate through all nodes.
        for node in parser.nodes:
            match node:
                case ast.Import() | ast.ImportFrom():
                    parser.extract_imports_from(node)

                case ast.FunctionDef():
                    parser.extract_standalone_functions_and_coroutines(node)

                case ast.ClassDef():
                    parser.extract_classes_from(node)

                case ast.Assign():
                    parser.extract_resources_and_configs_from(node)

                case ast.Expr() if isinstance(name(node), str):
                    # Skip docstrings at the module level
                    #logger.debug(f"Found module-level docstring: {ast.unparse(node)}")
                    continue

                case _:
                    logger.warning(f"Unknown AST node '{name(node)}': {ast.unparse(node)}")
                    continue
        return parser.module_info

    except (SyntaxError, Exception) as e:
        msg = f"{name(e)} parsing file {file_path}: {e}"
        logger.exception(msg)
        return {
            "module_name": Path(file_path).stem,
            "error": msg,
        }