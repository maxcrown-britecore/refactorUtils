from typing import List
from entities import ImportStatement, UsedName
import ast
from typing import Set


class DependencyResolver:
    """
    Resolves which imports are actually needed for a code entity.
    
    This is like a smart packing assistant that only packs what you'll actually use.
    """

    def find_entity_dependencies(self, entity_name: str|None, entity_code: str, all_entity_names: List[str]) -> List[str]:
        """
        Given the source code of an entity, return a list of other entity names
        (functions or classes) it references from the same file.
        This is used for internal function or class dependencies.
        """
        try:
            tree = ast.parse(entity_code)
        except SyntaxError:
            return []

        class NameCollector(ast.NodeVisitor):
            def __init__(self):
                self.used_names: Set[str] = set()

            def visit_Name(self, node: ast.Name):
                self.used_names.add(node.id)
                self.generic_visit(node)

        collector = NameCollector()
        collector.visit(tree)

        # Return only names that are other known entities
        dependencies = [
            name for name in collector.used_names
            if name in all_entity_names and name != entity_name
        ]
        return sorted(dependencies)
    
    def find_used_names(self, entity_code: str) -> List[UsedName]:
        """Find all names used in the entity code that might require imports."""
        tree = ast.parse(entity_code)
        used_names = []
        
        for node in ast.walk(tree):
            # Function calls: func_name() or module.func_name()
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    used_names.append(UsedName(
                        name=node.func.id,
                        context="function_call",
                        line_number=getattr(node, 'lineno', 0)
                    ))
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        used_names.append(UsedName(
                            name=node.func.value.id,
                            context="module_reference",
                            line_number=getattr(node, 'lineno', 0)
                        ))
            
            # Name references: variable names, class names, etc.
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Load):
                used_names.append(UsedName(
                    name=node.id,
                    context="name_reference",
                    line_number=getattr(node, 'lineno', 0)
                ))
            
            # Attribute access: module.attribute
            elif isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    used_names.append(UsedName(
                        name=node.value.id,
                        context="attribute_access",
                        line_number=getattr(node, 'lineno', 0)
                    ))
        
        return used_names
    
    def resolve_required_imports(self, 
                               used_names: List[UsedName], 
                               available_imports: List[ImportStatement]) -> List[ImportStatement]:
        """Determine which imports are actually needed."""
        required_imports = []
        used_name_set = {name.name for name in used_names}
        
        for import_stmt in available_imports:
            if self._is_import_needed(import_stmt, used_name_set):
                required_imports.append(import_stmt)
        
        return required_imports
    
    def _is_import_needed(self, import_stmt: ImportStatement, used_names: Set[str]) -> bool:
        """Check if an import statement is needed based on used names."""
        # Handle "import module" or "import module as alias"
        if not import_stmt.names:
            check_name = import_stmt.alias or import_stmt.module.split('.')[-1]
            return check_name in used_names
        
        # Handle "from module import name1, name2"
        for name in import_stmt.names:
            if name in used_names or name == '*':  # Star imports are tricky
                return True
        
        return False