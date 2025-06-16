# Implementation for infer_type_from_expression
def infer_type_from_expression(expr: ast.expr) -> str:
    """
    Infer Python type annotation from an AST expression.
    
    Analyzes an AST expression node to determine the appropriate Python
    type annotation string. Handles basic types, containers, and complex expressions.
    
    Args:
        expr: AST expression node to analyze for type inference.
        
    Returns:
        str: String representation of the inferred type annotation.
        
    Raises:
        TypeError: If expr is not a valid AST expression node.
        
    Example:
        >>> # For ast.Constant(value=42)
        >>> type_str = infer_type_from_expression(constant_node)
        >>> type_str
        'int'
    """
    if not isinstance(expr, ast.expr):
        raise TypeError(f"Expected ast.expr, got {type(expr)}")
    
    # Handle Constant nodes (Python 3.8+)
    if isinstance(expr, ast.Constant):
        value = expr.value
        if isinstance(value, bool):
            return 'bool'
        elif isinstance(value, int):
            return 'int'
        elif isinstance(value, float):
            return 'float'
        elif isinstance(value, str):
            return 'str'
        elif value is None:
            return 'None'
        else:
            return 'Any'
    
    # Handle older AST nodes (Python < 3.8 compatibility)
    elif isinstance(expr, ast.Num):
        if isinstance(expr.n, int):
            return 'int'
        elif isinstance(expr.n, float):
            return 'float'
        else:
            return 'Any'
    
    elif isinstance(expr, ast.Str):
        return 'str'
    
    elif isinstance(expr, ast.NameConstant):
        if expr.value is True or expr.value is False:
            return 'bool'
        elif expr.value is None:
            return 'None'
        else:
            return 'Any'
    
    # Handle containers
    elif isinstance(expr, ast.List):
        if not expr.elts:
            return 'List[Any]'
        # Try to infer element type from first element
        try:
            elem_type = infer_type_from_expression(expr.elts[0])
            return f'List[{elem_type}]'
        except:
            return 'List[Any]'
    
    elif isinstance(expr, ast.Dict):
        if not expr.keys:
            return 'Dict[Any, Any]'
        # Try to infer key and value types from first pair
        try:
            key_type = infer_type_from_expression(expr.keys[0])
            val_type = infer_type_from_expression(expr.values[0])
            return f'Dict[{key_type}, {val_type}]'
        except:
            return 'Dict[Any, Any]'
    
    elif isinstance(expr, ast.Set):
        if not expr.elts:
            return 'Set[Any]'
        try:
            elem_type = infer_type_from_expression(expr.elts[0])
            return f'Set[{elem_type}]'
        except:
            return 'Set[Any]'
    
    elif isinstance(expr, ast.Tuple):
        if not expr.elts:
            return 'Tuple[()]'
        try:
            elem_types = [infer_type_from_expression(e) for e in expr.elts]
            return f'Tuple[{", ".join(elem_types)}]'
        except:
            return 'Tuple[Any, ...]'
    
    # Handle Name nodes (variables)
    elif isinstance(expr, ast.Name):
        # Common patterns
        if expr.id in ('True', 'False'):
            return 'bool'
        elif expr.id == 'None':
            return 'None'
        else:
            return 'Any'
    
    # Default case
    else:
        return 'Any'
