from ..core import (
    CodeParser, FileWriter, ImportAnalyzer, 
    DependencyResolver, ImportOptimizer
)
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import replace
import ast


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
    
    def _extract_function_signature(self, entity) -> str:
        """Extract function signature from entity source code."""
        try:
            tree = ast.parse(entity.source_code)
        except SyntaxError:
            return f"def {entity.name}(*args, **kwargs):"
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name == entity.name:
                # Build argument list
                args = []
                
                # Regular arguments
                for arg in node.args.args:
                    args.append(arg.arg)
                
                # Default arguments
                defaults_offset = len(node.args.args) - len(node.args.defaults)
                for i, default in enumerate(node.args.defaults):
                    arg_index = defaults_offset + i
                    if arg_index < len(node.args.args):
                        arg_name = node.args.args[arg_index].arg
                        # For safety, use a placeholder for default values
                        args[arg_index] = f"{arg_name}=None"
                
                # *args
                if node.args.vararg:
                    args.append(f"*{node.args.vararg.arg}")
                
                # **kwargs  
                if node.args.kwarg:
                    args.append(f"**{node.args.kwarg.arg}")
                
                return f"def {entity.name}({', '.join(args)}):"
        
        # Fallback for classes or if function not found
        if entity.entity_type == "class":
            return f"class {entity.name}:"
        else:
            return f"def {entity.name}(*args, **kwargs):"

    def _calculate_relative_import(self, source_file: Path, target_file: Path) -> str:
        """Calculate relative import path from source to target file."""
        try:
            # Convert to absolute paths
            source_abs = source_file.resolve()
            target_abs = target_file.resolve()
            
            # Get relative path from source directory to target file
            source_dir = source_abs.parent
            rel_path = target_abs.relative_to(source_dir.parent)
            
            # Convert path to module notation
            module_parts = rel_path.with_suffix('').parts
            
            # Calculate dots for relative import
            # Count how many directories we need to go up
            try:
                # Try to find common parent
                common = source_abs.parent
                target_parent = target_abs.parent
                
                dots = 1  # Start with one dot for same level
                while not target_parent.is_relative_to(common):
                    common = common.parent
                    dots += 1
                
                # Build module path
                if target_parent == common:
                    module_path = target_abs.stem
                else:
                    rel_to_common = target_parent.relative_to(common)
                    module_path = '.'.join(rel_to_common.parts + (target_abs.stem,))
                
                return f"{'.' * dots}{module_path}"
                
            except ValueError:
                # Fallback to simple relative import
                module_path = '.'.join(module_parts)
                return f".{module_path}"
                
        except Exception:
            # Fallback to absolute import using target filename
            return target_file.stem

    def _detect_indentation(self, entity) -> str:
        """Detect the indentation level of an entity."""
        lines = entity.source_code.split('\n')
        if not lines:
            return ""
        
        # Find the first non-empty line (should be the entity definition)
        for line in lines:
            if line.strip():
                # Count leading spaces
                return line[:len(line) - len(line.lstrip())]
        
        return ""

    def _generate_safe_wrapper(self, entity, source_file: Path, target_file: Path) -> str:
        """Generate safe wrapper code for an entity."""
        import_path = self._calculate_relative_import(source_file, target_file)
        base_indent = self._detect_indentation(entity)
        
        if entity.entity_type == "function":
            signature = self._extract_function_signature(entity)
            
            # Extract function name and arguments
            func_name = entity.name
            
            # Parse arguments from signature for call
            try:
                tree = ast.parse(entity.source_code)
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == func_name:
                        call_args = []
                        
                        # Regular arguments
                        for arg in node.args.args:
                            call_args.append(arg.arg)
                        
                        # *args
                        if node.args.vararg:
                            call_args.append(f"*{node.args.vararg.arg}")
                        
                        # **kwargs
                        if node.args.kwarg:
                            call_args.append(f"**{node.args.kwarg.arg}")
                        
                        call_signature = ', '.join(call_args)
                        break
                else:
                    call_signature = "*args, **kwargs"
            except Exception:
                call_signature = "*args, **kwargs"
            
            # Remove 'def ' prefix if present in signature for consistency
            if signature.startswith('def '):
                signature = signature[4:]
            
            return f'''{base_indent}def {signature}
{base_indent}    from {import_path} import {func_name}
{base_indent}    return {func_name}({call_signature})'''
        
        elif entity.entity_type == "class":
            class_name = entity.name
            return f'''{base_indent}class {class_name}:
{base_indent}    def __new__(cls, *args, **kwargs):
{base_indent}        from {import_path} import {class_name}
{base_indent}        return {class_name}(*args, **kwargs)'''
        
        else:
            # Fallback for other entity types
            return f'''{base_indent}# {entity.name} moved to {target_file.name}
{base_indent}from {import_path} import {entity.name}'''

    def _handle_entity_mode(
        self, source_file: Path, entities, mode: str, target_file: Path = None
    ) -> bool:
        """Handle entities based on extraction mode (copy/cut/safe)."""
        if mode == "copy":
            # Copy mode: no changes to source file
            return False
        
        try:
            source_content = source_file.read_text()
            lines = source_content.split('\n')
            
            # Sort entities by line_start in reverse order 
            # (modify from bottom to top to preserve line numbers)
            sorted_entities = sorted(
                entities, key=lambda e: e.line_start, reverse=True
            )
            
            # Handle each entity based on mode
            for entity in sorted_entities:
                # Convert to 0-based indexing
                start_idx = entity.line_start - 1
                end_idx = entity.line_end - 1
                
                if mode == "cut":
                    # Cut mode: remove the entity lines
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
                
                elif mode == "safe" and target_file:
                    # Safe mode: replace with wrapper
                    wrapper_code = self._generate_safe_wrapper(
                        entity, source_file, target_file
                    )
                    wrapper_lines = wrapper_code.split('\n')
                    
                    # Replace entity lines with wrapper
                    lines[start_idx:end_idx + 1] = wrapper_lines
            
            # Write the modified content back to source file
            modified_content = '\n'.join(lines)
            source_file.write_text(modified_content)
            return True
            
        except Exception as e:
            print(f"Warning: Failed to modify entities in source: {e}")
            return False
    
    def extract_code_entities(
        self, 
        source_file: Path, 
        entity_names: Optional[List[str]] = None, 
        py2_top_most_import: bool = True, 
        top_custom_block: str = None, 
        root_path_prefix: str = None,
        target_file: Optional[Path] = None,
        mode: str = "copy"
    ) -> Dict[str, Any]:
        """
        Main method to extract functions and classes from a Python file.

        If entity_names is provided, only extract the entities with the 
        given names. If target_file is provided, all entities will be moved
        to that single file instead of creating separate files.
        Mode controls source handling: 'copy' leaves intact, 'cut' removes,
        'safe' replaces with import wrapper.
        Returns a summary of the extraction process for transparency.
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not source_file.suffix == '.py':
            raise ValueError(f"Expected a Python file, got: {source_file}")
        
        # Parse the source file
        all_entities, _ = self.parser.parse(source_file)

        # Filtered entities
        entities, _ = self.parser.parse(source_file, entity_names)

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
            all_used_names = []
            all_dependencies = set()
            
            for entity in entities:
                used_names = self.dependency_resolver.find_used_names(
                    entity.source_code
                )
                all_used_names.extend(used_names)
                
                dependencies = (
                    self.dependency_resolver.find_entity_dependencies(
                        entity.name, 
                        entity.source_code, 
                        [e.name for e in all_entities]
                    )
                )
                all_dependencies.update(dependencies)
            
            # Filter out extracted entities from internal imports
            if entity_names:
                all_dependencies = {dep for dep in all_dependencies if dep not in entity_names}
            
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
            
            # Add custom block after imports if provided
            if top_custom_block:
                if combined_imports:
                    combined_imports = (
                        combined_imports + "\n\n" + top_custom_block
                    )
                else:
                    combined_imports = top_custom_block
            
            # Append entities to target file
            self._append_entities_to_target(
                target_file, entities, combined_imports
            )
            
            # Handle source file based on mode
            source_modified = False
            entities_cut = []
            if mode in ["cut", "safe"]:
                source_modified = self._handle_entity_mode(
                    source_file, entities, mode, target_file
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
            
            # Add mode specific fields
            if mode in ["cut", "safe"]:
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
                modified_entity = replace(
                    entity,
                    source_code=(
                        combined_imports + "\n\n\n" + entity.source_code
                    )
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
        
        # Handle source file based on mode
        source_modified = False
        entities_cut = []
        if mode in ["cut", "safe"] and created_files:  # Only modify if files were created
            source_modified = self._handle_entity_mode(
                source_file, entities, mode, target_file
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
        
        # Add mode specific fields
        if mode in ["cut", "safe"]:
            result['source_file_modified'] = source_modified
            result['entities_cut'] = entities_cut
        
        return result

