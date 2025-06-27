from core import CodeParser, DependencyResolver
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any
import ast

class CodeReportService:
    """
    Service for generating DataFrame reports of code entities.
    
    This is like having a data analyst examine your codebase - instead of
    reorganizing files, it creates a structured report showing what's inside.
    Perfect for code analysis, documentation, or understanding large codebases.
    """
    
    def __init__(self, parser: CodeParser, dependency_resolver: DependencyResolver):
        self.parser = parser
        self.dependency_resolver = dependency_resolver
    
    def generate_code_report(self, source_file: Path) -> 'pd.DataFrame':
        """
        Generate a DataFrame report of all functions and classes in a Python file.
        
        Think of this as creating a detailed inventory of your code warehouse -
        you get a neat table showing what's in stock, where it's located, and
        what type of item it is.
        
        Returns:
            pandas.DataFrame with columns: name, entity_type, line_start, line_end,
            source_file, code_length, has_docstring
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not source_file.suffix == '.py':
            raise ValueError(f"Expected a Python file, got: {source_file}")
        
        # Parse the source file
        entities = self.parser.parse(source_file)
        
        if not entities:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'name', 'entity_type', 'line_start', 'line_end', 
                'source_file', 'code_length', 'has_docstring'
            ])
        
        # Resolve internal dependencies
        for entity in entities:
            entity.internal_dependencies = self.dependency_resolver.find_entity_dependencies(entity.name, entity.source_code, [e.name for e in entities])
        
        # Convert entities to DataFrame
        report_data = []
        for entity in entities:
            row = {
                'name': entity.name,
                'entity_type': entity.entity_type,
                'line_start': entity.line_start,
                'line_end': entity.line_end,
                'total_lines': entity.line_end - entity.line_start + 1,
                'source_file': str(source_file),
                'code_length': len(entity.source_code),
                'has_docstring': self._has_docstring(entity.source_code),
                'internal_dependencies': entity.internal_dependencies,
                'internal_dependencies_count': entity.internal_dependencies_count
            }
            report_data.append(row)
        
        df = pd.DataFrame(report_data)
        
        # Sort by line number for logical ordering
        df = df.sort_values('line_start').reset_index(drop=True)
        
        return df
    
    def generate_multi_file_report(self, file_paths: List[Path]) -> 'pd.DataFrame':
        """
        Generate a consolidated report for multiple Python files.
        
        Like having a master catalog that spans multiple warehouses - you get
        a unified view of all your code assets across different files.
        """
        all_reports = []
        
        for file_path in file_paths:
            try:
                file_report = self.generate_code_report(file_path)
                if not file_report.empty:
                    all_reports.append(file_report)
            except (FileNotFoundError, ValueError) as e:
                print(f"Warning: Skipping {file_path}: {e}")
        
        if not all_reports:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'name', 'entity_type', 'line_start', 'line_end', 
                'source_file', 'code_length', 'has_docstring'
            ])
        
        # Concatenate all reports
        combined_df = pd.concat(all_reports, ignore_index=True)
        
        # Sort by source file, then by line number
        combined_df = combined_df.sort_values(['source_file', 'line_start']).reset_index(drop=True)
        
        return combined_df
    
    def get_summary_statistics(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """
        Generate summary statistics from a code report DataFrame.
        
        This is like getting executive summary metrics from your code inventory -
        quick insights without diving into the details.
        """
        if df.empty:
            return {
                'total_entities': 0,
                'functions_count': 0,
                'classes_count': 0,
                'files_analyzed': 0,
                'avg_code_length': 0,
                'entities_with_docstrings': 0
            }
        
        return {
            'total_entities': len(df),
            'functions_count': len(df[df['entity_type'] == 'function']),
            'classes_count': len(df[df['entity_type'] == 'class']),
            'files_analyzed': int(df['source_file'].nunique()),
            'avg_code_length': float(df['code_length'].mean()),
            'entities_with_docstrings': int(df['has_docstring'].sum()),
            'docstring_percentage': round(float(df['has_docstring'].sum() / len(df)) * 100, 2)
        }
    
    def _has_docstring(self, source_code: str) -> bool:
        """Check if the source code contains a docstring."""
        try:
            tree = ast.parse(source_code)
            # Look for the first statement being a string literal
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                    if (node.body and 
                        isinstance(node.body[0], ast.Expr) and 
                        isinstance(node.body[0].value, ast.Constant) and 
                        isinstance(node.body[0].value.value, str)):
                        return True
                    break
        except (SyntaxError, AttributeError):
            pass
        return False