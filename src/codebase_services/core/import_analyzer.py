from typing import List, Union
from pathlib import Path
from ..entities import ImportStatement
import ast


class ImportAnalyzer:
    """
    Analyzes import statements from Python source code.
    
    Follows Single Responsibility Principle - only handles import parsing.
    """
    
    def extract_imports(self, source: Union[str, Path]) -> List[ImportStatement]:
            """Extract all import statements from source code or file."""
            if isinstance(source, Path):
                source_code = source.read_text(encoding='utf-8')
            else:
                source_code = source
                
            tree = ast.parse(source_code)
            imports = []
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(ImportStatement(
                            module=alias.name,
                            names=(),
                            alias=alias.asname,
                            original_line=ast.get_source_segment(source_code, node) or ""
                        ))
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:  # Skip relative imports without module name
                        names = tuple(alias.name for alias in node.names) if node.names else ()
                        imports.append(ImportStatement(
                            module=node.module,
                            names=names,
                            level=node.level,
                            original_line=ast.get_source_segment(source_code, node) or ""
                        ))
            
            return imports