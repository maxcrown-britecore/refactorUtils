from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Optional, Tuple
import ast
from ..entities import CodeEntity


class CodeParser(ABC):
    """Abstract base class for code parsing strategies."""
    
    @abstractmethod
    def parse(
        self, file_path: Path, **kwargs
    ) -> Tuple[List[CodeEntity], ast.AST]:
        """Parse a file and extract code entities."""
        pass


class PythonASTParser(CodeParser):
    """Concrete parser implementation using Python's AST module."""
    
    def parse(
        self, file_path: Path, entity_names: Optional[List[str]] = None
    ) -> Tuple[List[CodeEntity], ast.AST]:
        """
        Parse a Python file using AST and extract functions and classes.
        
        This is like a detective examining a crime scene - the AST helps
        us identify and locate each 'suspect' (function/class) precisely.
        """
        with open(file_path, 'r', encoding='utf-8') as file:
            source_code = file.read()
            source_lines = source_code.splitlines()
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in {file_path}: {e}")
        
        entities = []
        
        # Walk through the AST looking for top-level functions and classes
        for node in ast.walk(tree):
            if isinstance(
                node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)
            ):
                # Only extract top-level entities (not nested ones)
                if self._is_top_level(node, tree):
                    
                    # If entity_names is provided, only extract the entities
                    # with the given names.
                    if (
                        entity_names
                        and node.name not in entity_names
                    ):
                        continue
                    
                    entity = self._extract_entity(node, source_lines)
                    entities.append(entity)
        
        return entities, tree
    
    def _is_top_level(self, node: ast.AST, tree: ast.AST) -> bool:
        """Check if a node is at the top level of the module."""
        # For module-level nodes, check if they're directly
        # in the module's body
        if hasattr(tree, "body") and isinstance(
            tree.body, list
        ):
            return node in tree.body
        return False
    
    def _extract_entity(
        self, node: ast.AST, source_lines: List[str]
    ) -> CodeEntity:
        """Extract source code for a given AST node."""
        # Get the complete source code including decorators
        start_line = node.lineno - 1  # AST uses 1-based indexing
        
        # Handle decorators by finding the actual start
        if hasattr(node, 'decorator_list') and node.decorator_list:
            start_line = node.decorator_list[0].lineno - 1
        
        # Find the end line by looking for the next top-level construct or EOF
        end_line = getattr(node, 'end_lineno', len(source_lines)) - 1
        
        # Extract the source code
        entity_source = '\n'.join(source_lines[start_line:end_line + 1])
        
        entity_type = 'class' if isinstance(node, ast.ClassDef) else 'function'
        
        return CodeEntity(
            name=node.name,
            source_code=entity_source,
            entity_type=entity_type,
            line_start=start_line + 1,
            line_end=end_line + 1,
        )
