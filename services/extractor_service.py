from codebase_services.core import CodeParser, FileWriter, ImportAnalyzer, DependencyResolver, ImportOptimizer
from pathlib import Path
from typing import Dict, Any, List, Optional


class CodeExtractorService:
    """
    Main service class that orchestrates the extraction process.
    
    This follows the Service Layer pattern - it coordinates between different
    components without handling the low-level details itself.
    """
    
    def __init__(self, parser: CodeParser, file_writer: FileWriter, import_analyzer: ImportAnalyzer, dependency_resolver: DependencyResolver, import_optimizer: ImportOptimizer):
        self.parser = parser
        self.file_writer = file_writer
        self.import_analyzer = import_analyzer
        self.dependency_resolver = dependency_resolver
        self.import_optimizer = import_optimizer
    
    def extract_code_entities(self, source_file: Path, entity_names: Optional[List[str]] = None, py2_top_most_import: bool = True, top_custom_block: str = None, root_path_prefix: str = None) -> Dict[str, Any]:
        """
        Main method to extract functions and classes from a Python file.

        If entity_names is provided, only extract the entities with the given names.
        Returns a summary of the extraction process for transparency.
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not source_file.suffix == '.py':
            raise ValueError(f"Expected a Python file, got: {source_file}")
        
        # Parse the source file
        all_entities = self.parser.parse(source_file)

        # Filtered entities
        entities = self.parser.parse(source_file, entity_names)

        # All imports
        imports = self.import_analyzer.extract_imports(source_file)
        
        if not entities:
            return {
                'source_file': str(source_file),
                'extracted_entities': [],
                'files_created': [],
                'init_file_updated': False
            }
        
        # Prepare target directory (same as source file)
        target_dir = source_file.parent
        
        # Extract entities to separate files
        created_files = []
        entity_names = []
        
        for entity in entities:
            try:
                # Resolve imports for the entity
                used_names = self.dependency_resolver.find_used_names(entity.source_code)
                required_imports = self.dependency_resolver.resolve_required_imports(used_names, imports)
                optimized_imports = self.import_optimizer.generate_import_statements(required_imports)

                # Resolve internal dependencies
                dependencies = self.dependency_resolver.find_entity_dependencies(
                    entity.name, entity.source_code, [e.name for e in all_entities]
                )

                if py2_top_most_import:
                    py2_top_most_import = 'from __future__ import print_function, division, absolute_import'
                else:
                    py2_top_most_import = ''

                internal_imports = '\n'.join(f'from .{dep} import {dep}' for dep in dependencies)
                
                # Combine imports
                combined_imports = '\n\n'.join(part for part in [py2_top_most_import, optimized_imports, internal_imports] if part)

                # Write the entity to a file
                if top_custom_block:
                    entity.source_code = combined_imports + "\n\n" + top_custom_block + "\n\n" + entity.source_code    
                else:
                    entity.source_code = combined_imports + "\n\n\n" + entity.source_code

                created_file = self.file_writer.write_entity_file(entity, target_dir)
                created_files.append(str(created_file))
                entity_names.append(entity.name)
            except IOError as e:
                print(f"Warning: Failed to create file for {entity.name}: {e}")
        
        # Update __init__.py file
        init_updated = False
        if entity_names:
            try:
                self.file_writer.create_init_file(target_dir, entity_names, root_path_prefix)
                init_updated = True
            except IOError as e:
                print(f"Warning: Failed to update __init__.py: {e}")
        
        return {
            'source_file': str(source_file),
            'extracted_entities': [
                {'name': entity.name, 'type': entity.entity_type} 
                for entity in entities
            ],
            'files_created': created_files,
            'init_file_updated': init_updated
        }

