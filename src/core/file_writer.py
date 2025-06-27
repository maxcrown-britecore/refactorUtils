from abc import ABC, abstractmethod
from pathlib import Path
from typing import List
import ast
from codebase_services.entities import CodeEntity


class FileWriter:
    """Handles file writing operations with proper error handling."""
    
    def write_entity_file(self, entity: CodeEntity, target_dir: Path) -> Path:
        """
        Write a code entity to its own file.
        
        Like a librarian organizing books - each function/class gets its own
        dedicated space with a clear label (filename).
        """
        filename = f"{entity.name}.py"
        file_path = target_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(entity.source_code)
            return file_path
        except IOError as e:
            raise IOError(f"Failed to write {file_path}: {e}")
    
    def create_init_file(self, target_dir: Path, entity_names: List[str], root_path_prefix: str = None) -> Path:
        """
        Create or update __init__.py file with imports.
        
        This is like creating a master index that tells Python where to find
        all the extracted components - similar to a table of contents.
        """
        init_path = target_dir / "__init__.py"
        
        # Read existing content if file exists
        existing_content = ""
        if init_path.exists():
            with open(init_path, 'r', encoding='utf-8') as file:
                existing_content = file.read()
        
        # Generate import statements
        import_statements = []
        for name in entity_names:  # Not Sorting to avoid issues with the order of imports
            if root_path_prefix:
                import_statement = f"from {root_path_prefix}.{name} import {name}"
            else:
                import_statement = f"from .{name} import {name}"
            # Avoid duplicate imports
            if import_statement not in existing_content:
                import_statements.append(import_statement)
        
        # Write the file
        if import_statements:
            content_to_add = "\n".join(import_statements) + "\n"
            mode = 'a' if existing_content else 'w'
            
            with open(init_path, mode, encoding='utf-8') as file:
                if existing_content and not existing_content.endswith('\n'):
                    file.write('\n')
                file.write(content_to_add)

            # Add the __all__ variable
            with open(init_path, 'a', encoding='utf-8') as file:
                file.write("__all__ = ['" + "', '".join(entity_names) + "']\n")
        
        return init_path
