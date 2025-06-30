import sys
import ast
from collections import defaultdict
from pathlib import Path
from typing import List, Dict, Set

# Core utilities
from ..core import ImportAnalyzer, DependencyResolver
from ..entities.entities import ImportStatement


def move_imports_to_functions(file_path: str):
    """
    Move top-level imports to the functions where they are used.
    This function reads a Python file, analyzes its imports and functions,
    and modifies the file to move imports into the functions that use them.
    Args:
        file_path (str): Path to the Python file to be modified.
    Returns:
    """
    # Read source
    source_path = Path(file_path)
    source_code = source_path.read_text(encoding='utf-8')
    dest_path = source_path.with_suffix('.moved_imports.py')
    tree = ast.parse(source_code)

    # 1. Extract all top-level imports
    import_analyzer = ImportAnalyzer()
    all_imports: List[ImportStatement] = import_analyzer.extract_imports(source_code)

    # 2. Find all top-level function definitions
    func_nodes = [node for node in tree.body if isinstance(node, ast.FunctionDef)]
    func_name_to_node = {fn.name: fn for fn in func_nodes}

    # Find all other entities that are not functions in the file
    non_functions = [node for node in tree.body
                     if not isinstance(node, (ast.FunctionDef, ast.Import, ast.ImportFrom, ast.Expr))]

    # 3. For each function, find which imports it uses
    dep_resolver = DependencyResolver()
    func_to_used_imports: Dict[str, Set[str]] = {fn.name: set() for fn in func_nodes}
    import_name_map = {}  # name/alias -> ImportStatement
    # Do the same for non-function entities
    non_func_to_used_imports: Dict[str, Set[str]] = defaultdict(set)

    for imp in all_imports:
        if imp.names:
            for n in imp.names:
                import_name_map[n] = imp
        else:
            # import module or import module as alias
            import_name_map[imp.alias or imp.module.split('.')[-1]] = imp

    for fn in func_nodes:
        fn_code = ast.get_source_segment(source_code, fn)
        used_names = dep_resolver.find_used_names(fn_code)
        for used in used_names:
            if used.name in import_name_map:
                func_to_used_imports[fn.name].add(used.name)

        # add symbols imported inside the function's decorators
        for decorator in fn.decorator_list:
            if isinstance(decorator, ast.Call):
                decorator_code = ast.get_source_segment(source_code, decorator)
                used_names_in_decorator = dep_resolver.find_used_names(decorator_code)
                for used in used_names_in_decorator:
                    if used.name in import_name_map:
                        non_func_to_used_imports[fn.name].add(used.name)

    for node in non_functions:
        # Does not work for classes, just functions and variables
        # For other non-function entities (e.g., global variables)
        entity_code = ast.get_source_segment(source_code, node)
        used_names = dep_resolver.find_entity_dependencies(None, entity_code, list(func_name_to_node.keys()))
        for used in used_names:
            if used.name in import_name_map:
                non_func_to_used_imports[node.name].add(used.name)

    all_non_func_imports = set([name for names in non_func_to_used_imports.values() for name in names])

    # 4. Remove all top-level imports from the AST unless they are used in non-function entities
    new_body = [node for node in tree.body
                if not isinstance(node, (ast.Import, ast.ImportFrom))
                    or (isinstance(node, ast.Import) or node.names[0].name in all_non_func_imports)]


    # 5. Insert needed imports at the top of each function
    for fn in func_nodes:
        needed_imports = set()
        for name in func_to_used_imports[fn.name]:
            needed_imports.add(import_name_map[name])
        # Remove duplicates
        def make_hashable_names(names):
            if isinstance(names, list):
                return tuple(names)
            return names
        needed_imports = list({(imp.module, make_hashable_names(imp.names), imp.alias, imp.level): imp for imp in needed_imports}.values())
        # Create AST import nodes
        import_nodes = []
        used_names_in_fn = func_to_used_imports[fn.name]
        for imp in needed_imports:
            if imp.names:
                # Only import the names actually used in this function
                filtered_names = [n for n in imp.names if n in used_names_in_fn]
                if filtered_names:
                    import_nodes.append(ast.ImportFrom(module=imp.module, names=[ast.alias(name=n) for n in filtered_names], level=imp.level))
            else:
                import_nodes.append(ast.Import(names=[ast.alias(name=imp.module, asname=imp.alias)]))
        # Insert at top of function body
        fn.body = import_nodes + fn.body

    tree.body = new_body
    tree.body.extend(func_nodes)  # Re-add functions with updated bodies

    # 6. Write back the modified code
    new_code = ast.unparse(tree)
    dest_path.write_text(new_code, encoding='utf-8')

    # 7. Print summary
    for fn in func_nodes:
        print(f"Function '{fn.name}': imports moved: {[import_name_map[n].original_line for n in func_to_used_imports[fn.name]]}")


def main():
    if len(sys.argv) != 2:
        print("Usage: python top_level_imports_detection.py <python_file>")
        sys.exit(1)
    move_imports_to_functions(sys.argv[1])


if __name__ == "__main__":
    main()
