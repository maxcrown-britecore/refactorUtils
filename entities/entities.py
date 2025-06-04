#!/usr/bin/env python3
"""
Python Code Extractor

A tool to extract functions and classes from a Python file into separate modules.
Follows clean architecture principles with separation of concerns.
"""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class CodeEntity:
    """Represents a function or class extracted from source code."""
    name: str
    source_code: str
    entity_type: str  # 'function' or 'class'
    line_start: int
    line_end: int
    internal_dependencies: List[str] = field(default_factory=list)
    
    @property
    def internal_dependencies_count(self) -> int:
        return len(self.internal_dependencies)


@dataclass
class ImportStatement:
    """Represents a single import statement with its metadata."""
    module: str
    names: List[str]  # Empty for "import module", populated for "from module import name1, name2"
    alias: Optional[str] = None
    level: int = 0  # For relative imports
    original_line: str = ""


@dataclass
class UsedName:
    """Represents a name used in code that might need an import."""
    name: str
    context: str  # 'attribute', 'function_call', 'class_instantiation', etc.
    line_number: int