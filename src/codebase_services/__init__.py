"""
Codebase Services - A comprehensive Python tool for codebase analysis and code extraction.

This package provides three main services:
- Code Extraction Service: Extract and refactor Python code entities
- Code Report Service: Generate analytical reports about code structure  
- Dependency Tree Service: Map dependencies and relationships across codebases
"""

from .main import (
    create_extractor,
    create_report_service, 
    create_dependency_tree_service
)

__version__ = "0.1.0"
__all__ = [
    "create_extractor",
    "create_report_service", 
    "create_dependency_tree_service"
]
