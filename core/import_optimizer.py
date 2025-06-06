from typing import List
from entities import ImportStatement

class ImportOptimizer:
    """
    Generates optimized import statements for extracted entities.
    
    This is like a professional organizer who arranges your imports cleanly.
    """
    
    def generate_import_statements(self, required_imports: List[ImportStatement]) -> str:
        """Generate clean, PEP8-compliant import statements."""
        if not required_imports:
            return ""
        
        # Group imports by type (standard library, third-party, local)
        stdlib_imports = []
        thirdparty_imports = []
        local_imports = []
        
        for import_stmt in required_imports:
            category = self._categorize_import(import_stmt.module)
            target_list = {
                'stdlib': stdlib_imports,
                'thirdparty': thirdparty_imports,
                'local': local_imports
            }[category]
            target_list.append(import_stmt)
        
        # Generate import blocks
        import_blocks = []
        for imports, block_name in [
            (stdlib_imports, "Standard Library"),
            (thirdparty_imports, "Third Party"),
            (local_imports, "Local")
        ]:
            if imports:
                block = self._format_import_block(imports)
                import_blocks.append(block)
        
        return "\n\n".join(import_blocks)
    
    def _categorize_import(self, module_name: str) -> str:
        """Categorize import as stdlib, thirdparty, or local."""
        # Simplified categorization - in practice, you might use importlib or other tools
        stdlib_modules = {
            'os', 'sys', 'json', 'datetime', 'collections', 'typing', 'pathlib',
            'functools', 'itertools', 'ast', 'logging', 're', 'math'
        }
        
        base_module = module_name.split('.')[0]
        if base_module in stdlib_modules:
            return 'stdlib'
        elif module_name.startswith('.'):
            return 'local'
        else:
            return 'thirdparty'
    
    def _format_import_block(self, imports: List[ImportStatement]) -> str:
        """Format a block of imports according to PEP8."""
        lines = []
        for import_stmt in imports:
            if not import_stmt.names:  # import module
                if import_stmt.alias:
                    lines.append(f"import {import_stmt.module} as {import_stmt.alias}")
                else:
                    lines.append(f"import {import_stmt.module}")
            else:  # from module import names
                names_str = ", ".join(import_stmt.names)
                if import_stmt.level > 0:
                    dots = "." * import_stmt.level
                    lines.append(f"from {dots}{import_stmt.module} import {names_str}")
                else:
                    lines.append(f"from {import_stmt.module} import {names_str}")
        
        return "\n".join(sorted(list(set(lines))))