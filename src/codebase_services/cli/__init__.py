"""
CLI entry points for codebase_services.
"""

from .extractor_cli import main as extractor_main
from .report_cli import main as report_main  
from .dependency_cli import main as dependency_main

__all__ = ["extractor_main", "report_main", "dependency_main"] 