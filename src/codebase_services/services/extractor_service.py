from ..core import (
    CodeParser, FileWriter, ImportAnalyzer, 
    DependencyResolver, ImportOptimizer
)
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import replace


class CodeExtractorService:
    """
    Main service class that orchestrates the extraction process.
    
    This follows the Service Layer pattern - it coordinates between different
    components without handling the low-level details itself.
    """
    
    def __init__(
        self, 
        parser: CodeParser, 
        file_writer: FileWriter, 
        import_analyzer: ImportAnalyzer, 
        dependency_resolver: DependencyResolver, 
        import_optimizer: ImportOptimizer
    ):
        self.parser = parser
        self.file_writer = file_writer
        self.import_analyzer = import_analyzer
        self.dependency_resolver = dependency_resolver
        self.import_optimizer = import_optimizer
    
    def _validate_target_file(self, target_file: Path) -> None:
        """Validate and create target file if needed."""
        if not target_file.suffix == '.py':
            raise ValueError(
                f"Target file must be a Python file, got: {target_file}"
            )
        
        # Create the target file if it doesn't exist
        if not target_file.exists():
            target_file.parent.mkdir(parents=True, exist_ok=True)
            target_file.write_text('')
    
    def _merge_imports(
        self, existing_content: str, new_imports: str
    ) -> str:
        """Merge existing imports with new ones, with deduplication."""
        if not existing_content.strip():
            return new_imports
        
        lines = existing_content.split('\n')
        
        # Find where imports end 
        import_end_idx = 0
        for i, line in enumerate(lines):
            stripped = line.strip()
            if (stripped and 
                    not stripped.startswith('from ') and 
                    not stripped.startswith('import ') and
                    not stripped.startswith('#')):
                import_end_idx = i
                break
        else:
            import_end_idx = len(lines)
        
        # Extract existing import lines (excluding comments)
        existing_imports = set()
        for line in lines[:import_end_idx]:
            stripped = line.strip()
            if (stripped and 
                    (stripped.startswith('from ') or stripped.startswith('import ')) and
                    not stripped.startswith('#')):
                existing_imports.add(stripped)
        
        # Extract new import lines
        new_import_lines = []
        if new_imports.strip():
            for line in new_imports.split('\n'):
                stripped = line.strip()
                if (stripped and 
                        (stripped.startswith('from ') or stripped.startswith('import ')) and
                        stripped not in existing_imports):
                    new_import_lines.append(line)
                    existing_imports.add(stripped)  # Prevent future duplicates
        
        # Reconstruct the file
        result_lines = lines[:import_end_idx]
        if new_import_lines:
            result_lines.extend(['', '# Additional imports from extraction'])
            result_lines.extend(new_import_lines)
        result_lines.extend(lines[import_end_idx:])
        
        return '\n'.join(result_lines)
    
    def _append_entities_to_target(
        self, 
        target_file: Path, 
        entities, 
        combined_imports: str
    ) -> None:
        """Append entities to target file with proper import handling."""
        existing_content = ''
        if target_file.exists() and target_file.stat().st_size > 0:
            existing_content = target_file.read_text()
        
        # Merge imports
        merged_content = self._merge_imports(
            existing_content, combined_imports
        )
        
        # Append entities
        for entity in entities:
            merged_content += f'\n\n\n{entity.source_code}'
        
        target_file.write_text(merged_content)
    
    def _cut_entities_from_source(
        self, source_file: Path, entities
    ) -> bool:
        """Remove entities from source file and clean up empty lines."""
        try:
            source_content = source_file.read_text()
            lines = source_content.split('\n')
            
            # Sort entities by line_start in reverse order 
            # (remove from bottom to top to preserve line numbers)
            sorted_entities = sorted(
                entities, key=lambda e: e.line_start, reverse=True
            )
            
            # Remove each entity's lines
            for entity in sorted_entities:
                # Convert to 0-based indexing
                start_idx = entity.line_start - 1
                end_idx = entity.line_end - 1
                
                # Remove the entity lines
                del lines[start_idx:end_idx + 1]
                
                # Clean up consecutive empty lines around the removed entity
                # Remove empty lines before the cut point
                while (start_idx > 0 and start_idx < len(lines) and 
                       not lines[start_idx - 1].strip()):
                    del lines[start_idx - 1]
                    start_idx -= 1
                
                # Remove empty lines after the cut point  
                while (start_idx < len(lines) and 
                       not lines[start_idx].strip()):
                    del lines[start_idx]
            
            # Write the modified content back to source file
            modified_content = '\n'.join(lines)
            source_file.write_text(modified_content)
            return True
            
        except Exception as e:
            print(f"Warning: Failed to cut entities from source: {e}")
            return False
    
    def extract_code_entities(
        self, 
        source_file: Path, 
        entity_names: Optional[List[str]] = None, 
        py2_top_most_import: bool = True, 
        top_custom_block: str = None, 
        root_path_prefix: str = None,
        target_file: Optional[Path] = None,
        cut_entities: bool = False
    ) -> Dict[str, Any]:
        """
        Main method to extract functions and classes from a Python file.

        If entity_names is provided, only extract the entities with the 
        given names. If target_file is provided, all entities will be moved
        to that single file instead of creating separate files.
        If cut_entities is True, entities will be removed from source file.
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
            base_result = {
                'source_file': str(source_file),
                'extracted_entities': [],
                'files_created': [],
                'init_file_updated': False
            }
            if target_file:
                base_result['target_file_modified'] = None
            return base_result
        
        # TARGET FILE MODE: Move all entities to single target file
        if target_file:
            self._validate_target_file(target_file)
            
            # Collect all imports and dependencies for all entities
            all_used_names = set()
            all_dependencies = set()
            
            for entity in entities:
                used_names = self.dependency_resolver.find_used_names(
                    entity.source_code
                )
                all_used_names.update(used_names)
                
                dependencies = (
                    self.dependency_resolver.find_entity_dependencies(
                        entity.name, 
                        entity.source_code, 
                        [e.name for e in all_entities]
                    )
                )
                all_dependencies.update(dependencies)
            
            # Resolve combined imports
            required_imports = (
                self.dependency_resolver.resolve_required_imports(
                    all_used_names, imports
                )
            )
            optimized_imports = (
                self.import_optimizer.generate_import_statements(
                    required_imports
                )
            )
            
            # Add py2 import if needed
            if py2_top_most_import:
                py2_import = (
                    'from __future__ import print_function, '
                    'division, absolute_import'
                )
            else:
                py2_import = ''
            
            # Add internal imports
            internal_imports = '\n'.join(
                f'from .{dep} import {dep}' for dep in all_dependencies
            )
            
            # Combine all imports
            import_parts = [py2_import, optimized_imports, internal_imports]
            combined_imports = '\n\n'.join(
                part for part in import_parts if part
            )
            
            # Add custom block to each entity if provided
            if top_custom_block:
                entities = [
                    replace(entity, source_code=f'{top_custom_block}\n\n{entity.source_code}')
                    for entity in entities
                ]
            
            # Append entities to target file
            self._append_entities_to_target(
                target_file, entities, combined_imports
            )
            
            # CUT MODE: Remove entities from source file if requested
            source_modified = False
            entities_cut = []
            if cut_entities:
                source_modified = self._cut_entities_from_source(
                    source_file, entities
                )
                if source_modified:
                    entities_cut = [entity.name for entity in entities]
            
            result = {
                'source_file': str(source_file),
                'extracted_entities': [
                    {'name': entity.name, 'type': entity.entity_type} 
                    for entity in entities
                ],
                'files_created': [],
                'init_file_updated': False,
                'target_file_modified': str(target_file)
            }
            
            # Add cut mode specific fields
            if cut_entities:
                result['source_file_modified'] = source_modified
                result['entities_cut'] = entities_cut
            
            return result
        
        # ORIGINAL MODE: Create separate files for each entity
        target_dir = source_file.parent
        created_files = []
        entity_names_list = []
        
        for entity in entities:
            try:
                # Resolve imports for the entity
                used_names = self.dependency_resolver.find_used_names(
                    entity.source_code
                )
                required_imports = (
                    self.dependency_resolver.resolve_required_imports(
                        used_names, imports
                    )
                )
                optimized_imports = (
                    self.import_optimizer.generate_import_statements(
                        required_imports
                    )
                )

                # Resolve internal dependencies
                dependencies = (
                    self.dependency_resolver.find_entity_dependencies(
                        entity.name, 
                        entity.source_code, 
                        [e.name for e in all_entities]
                    )
                )

                if py2_top_most_import:
                    py2_import = (
                        'from __future__ import print_function, '
                        'division, absolute_import'
                    )
                else:
                    py2_import = ''

                internal_imports = '\n'.join(
                    f'from .{dep} import {dep}' for dep in dependencies
                )
                
                # Combine imports
                import_parts = [
                    py2_import, optimized_imports, internal_imports
                ]
                combined_imports = '\n\n'.join(
                    part for part in import_parts if part
                )

                # Write the entity to a file
                if top_custom_block:
                    modified_entity = replace(
                        entity,
                        source_code=combined_imports + "\n\n" + top_custom_block + "\n\n" + entity.source_code
                    )    
                else:
                    modified_entity = replace(
                        entity,
                        source_code=combined_imports + "\n\n\n" + entity.source_code
                    )

                created_file = self.file_writer.write_entity_file(
                    modified_entity, target_dir
                )
                created_files.append(str(created_file))
                entity_names_list.append(entity.name)
            except IOError as e:
                print(f"Warning: Failed to create file for {entity.name}: {e}")
        
        # Update __init__.py file
        init_updated = False
        if entity_names_list:
            try:
                self.file_writer.create_init_file(
                    target_dir, entity_names_list, root_path_prefix
                )
                init_updated = True
            except IOError as e:
                print(f"Warning: Failed to update __init__.py: {e}")
        
        # CUT MODE: Remove entities from source file if requested  
        source_modified = False
        entities_cut = []
        if cut_entities and created_files:  # Only cut if files were created
            source_modified = self._cut_entities_from_source(
                source_file, entities
            )
            if source_modified:
                entities_cut = [entity.name for entity in entities]
        
        result = {
            'source_file': str(source_file),
            'extracted_entities': [
                {'name': entity.name, 'type': entity.entity_type} 
                for entity in entities
            ],
            'files_created': created_files,
            'init_file_updated': init_updated
        }
        
        # Add cut mode specific fields
        if cut_entities:
            result['source_file_modified'] = source_modified
            result['entities_cut'] = entities_cut
        
        return result

