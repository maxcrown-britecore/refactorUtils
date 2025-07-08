import ast
import networkx as nx
from ..core import CodeParser, DependencyResolver, ImportAnalyzer
from pathlib import Path
import pandas as pd
from typing import List, Dict, Any, Optional


class CodeReportService:
    """
    Service for generating DataFrame reports of code entities.
    
    This is like having a data analyst examine your codebase - instead of
    reorganizing files, it creates a structured report showing what's inside.
    Perfect for code analysis, documentation, or understanding large codebases.
    """
    
    def __init__(self, parser: CodeParser,
                 dependency_resolver: DependencyResolver,
                 import_analyzer: ImportAnalyzer):
        self.parser = parser
        self.dependency_resolver = dependency_resolver
        self.import_analyzer = import_analyzer
    
    def generate_code_report(
            self, 
            source_file: Path, 
            entity_names: Optional[List[str]] = None
    ) -> 'pd.DataFrame':
        """
        Generate a DataFrame report of all functions and classes in a file.
        
        Think of this as creating a detailed inventory of your code warehouse -
        you get a neat table showing what's in stock, where it's located, and
        what type of item it is.
        
        Args:
            source_file: Path to the Python file to analyze
            entity_names: Optional list of entity names to filter by
        
        Returns:
            pandas.DataFrame with columns: name, entity_type, line_start, 
            line_end, source_file, code_length, has_docstring
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not source_file.suffix == '.py':
            raise ValueError(f"Expected a Python file, got: {source_file}")
        
        # Parse all entities in the source file
        all_entities, _ = self.parser.parse(source_file)
        all_entity_names = [e.name for e in all_entities]

        # Filter entities if entity_names is provided
        entities = all_entities
        if entity_names:
            entities = [e for e in all_entities if e.name in entity_names]
        if not entities:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'name', 'entity_type', 'line_start', 'line_end', 
                'source_file', 'code_length', 'has_docstring'
            ])
        # Resolve internal dependencies
        for entity in entities:
            entity.internal_dependencies = (
                self.dependency_resolver.find_entity_dependencies(
                    entity.name, entity.source_code, 
                    all_entity_names
                )
            )
        
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
                'internal_dependencies_count': (
                    entity.internal_dependencies_count
                )
            }
            report_data.append(row)
        
        df = pd.DataFrame(report_data)
        
        # Sort by line number for logical ordering
        df = df.sort_values('line_start').reset_index(drop=True)
        
        return df
    
    def generate_multi_file_report(
            self, 
            file_paths: List[Path],
            entity_names: Optional[List[str]] = None
    ) -> 'pd.DataFrame':
        """
        Generate a consolidated report for multiple Python files.
        
        Like having a master catalog that spans multiple warehouses - you get
        a unified view of all your code assets across different files.
        
        Args:
            file_paths: List of Python file paths to analyze
            entity_names: Optional list of entity names to filter by
        """
        all_reports = []
        
        for file_path in file_paths:
            try:
                file_report = self.generate_code_report(
                    file_path, entity_names
                )
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
        combined_df = (
            combined_df.sort_values(['source_file', 'line_start'])
            .reset_index(drop=True)
        )
        
        return combined_df
    
    def cluster_code_entities(self, df: 'pd.DataFrame') -> 'pd.DataFrame':
        """
        Cluster code entities by similarity.
        """
        # Create the graph
        G = nx.Graph()
        df['name'].apply(G.add_node)

        # Build dependency map
        dependency_map = {}
        for _, row in df.iterrows():
            for dep in row['internal_dependencies']:
                dependency_map.setdefault(dep, set()).add(row['name'])

        # Add edges between entities that share dependencies
        for entities in dependency_map.values():
            entities = list(entities)
            for i in range(len(entities)):
                for j in range(i + 1, len(entities)):
                    G.add_edge(entities[i], entities[j])

        # Identify connected components (clusters)
        clusters = list(nx.connected_components(G))
        entity_to_cluster = {
            entity: idx 
            for idx, cluster in enumerate(clusters) 
            for entity in cluster
        }

        # Assign cluster_id to each entity
        df['cluster_id'] = (
            df['name'].map(entity_to_cluster).fillna(-1).astype(int)
        )

        df.sort_values(by='cluster_id', ascending=False)

        return df
    
    def get_summary_statistics(
            self, 
            df: 'pd.DataFrame',
            entity_names: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Generate summary statistics from a code report DataFrame.
        
        This is like getting executive summary metrics from your code 
        inventory - quick insights without diving into the details.
        
        Args:
            df: DataFrame containing code entity information
            entity_names: Optional list of entity names to filter by
        """
        # Filter DataFrame if entity_names is provided
        if entity_names:
            df = df[df['name'].isin(entity_names)]
        
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
            'total_lines': int(df['total_lines'].sum()),
            'entities_with_docstrings': int(df['has_docstring'].sum()),
            'docstring_percentage': round(
                float(df['has_docstring'].sum() / len(df)) * 100, 2
            )
        }
    
    def _has_docstring(self, source_code: str) -> bool:
        """Check if the source code contains a docstring."""
        try:
            tree = ast.parse(source_code)
            # Look for the first statement being a string literal
            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, 
                                     ast.ClassDef)):
                    if (node.body and 
                            isinstance(node.body[0], ast.Expr) and 
                            isinstance(node.body[0].value, ast.Constant) and 
                            isinstance(node.body[0].value.value, str)):
                        return True
                    break
        except (SyntaxError, AttributeError):
            pass
        return False

    def analyze_missing_imports(self, source_file: Path) -> 'pd.DataFrame':
        """
        Analyze a Python file and identify missing imports.
        
        Returns a DataFrame with missing symbol names and line numbers where
        they are used but not imported or defined locally.
        
        Args:
            source_file: Path to the Python file to analyze
        
        Returns:
            pandas.DataFrame with columns: symbol_name, line_numbers, 
            usage_context, symbol_type, suggested_import
        """
        if not source_file.exists():
            raise FileNotFoundError(f"Source file not found: {source_file}")
        
        if not source_file.suffix == '.py':
            raise ValueError(f"Expected a Python file, got: {source_file}")
        
        # Read source code
        source_code = source_file.read_text(encoding='utf-8')
        
        try:
            tree = ast.parse(source_code)
        except SyntaxError as e:
            raise ValueError(f"Invalid Python syntax in {source_file}: {e}")
        
        # Get existing imports
        existing_imports = self.import_analyzer.extract_imports(source_file)
        imported_names = self._extract_imported_names(existing_imports)
        
        # Get locally defined names
        local_names = self._extract_local_names(tree)
        
        # Get all used names in the file
        used_names = self.dependency_resolver.find_used_names(source_code)
        
        # Get built-in names
        builtin_names = self._get_builtin_names()
        
        # Find missing imports
        available_names = imported_names | local_names | builtin_names
        missing_data = []
        
        for used_name in used_names:
            if used_name.name not in available_names:
                # Skip if it looks like a string literal or number
                if self._is_likely_literal(used_name.name):
                    continue
                
                missing_data.append({
                    'symbol_name': used_name.name,
                    'line_number': used_name.line_number,
                    'usage_context': used_name.context,
                    'symbol_type': self._categorize_symbol_type(used_name),
                    'suggested_import': self._suggest_import(used_name.name)
                })
        
        # Group by symbol name and aggregate line numbers
        if missing_data:
            df = pd.DataFrame(missing_data)
            grouped = df.groupby('symbol_name').agg({
                'line_number': lambda x: sorted(list(set(x))),
                'usage_context': 'first',
                'symbol_type': 'first', 
                'suggested_import': 'first'
            }).reset_index()
            
            # Sort by first occurrence line number
            grouped['first_line'] = grouped['line_number'].apply(min)
            grouped = grouped.sort_values('first_line').drop('first_line', axis=1)
            
            return grouped
        else:
            # Return empty DataFrame with expected columns
            return pd.DataFrame(columns=[
                'symbol_name', 'line_number', 'usage_context', 
                'symbol_type', 'suggested_import'
            ])

    def analyze_multi_file_missing_imports(
            self, file_paths: List[Path]) -> 'pd.DataFrame':
        """
        Analyze multiple Python files for missing imports.
        
        Args:
            file_paths: List of Python file paths to analyze
            
        Returns:
            pandas.DataFrame with missing imports across all files
        """
        all_reports = []
        
        for file_path in file_paths:
            try:
                file_report = self.analyze_missing_imports(file_path)
                if not file_report.empty:
                    file_report['source_file'] = str(file_path)
                    all_reports.append(file_report)
            except (FileNotFoundError, ValueError) as e:
                print(f"Warning: Skipping {file_path}: {e}")
        
        if not all_reports:
            return pd.DataFrame(columns=[
                'symbol_name', 'line_number', 'usage_context', 
                'symbol_type', 'suggested_import', 'source_file'
            ])
        
        # Concatenate all reports
        combined_df = pd.concat(all_reports, ignore_index=True)
        
        # Sort by source file, then by first line number
        combined_df['first_line'] = (
            combined_df['line_number'].apply(min)
        )
        combined_df = (
            combined_df.sort_values(['source_file', 'first_line'])
            .drop('first_line', axis=1)
            .reset_index(drop=True)
        )
        
        return combined_df

    def get_missing_imports_summary(self, df: 'pd.DataFrame') -> Dict[str, Any]:
        """
        Generate summary statistics for missing imports analysis.
        
        Args:
            df: DataFrame from analyze_missing_imports or 
                analyze_multi_file_missing_imports
        """
        if df.empty:
            return {
                'total_missing_symbols': 0,
                'files_with_missing_imports': 0,
                'most_common_missing': [],
                'symbols_by_type': {}
            }
        
        stats = {
            'total_missing_symbols': len(df),
            'most_common_missing': (
                df['symbol_name'].value_counts().head(5).to_dict()
            ),
            'symbols_by_type': (
                df['symbol_type'].value_counts().to_dict()
            )
        }
        
        # Add file count if available
        if 'source_file' in df.columns:
            stats['files_with_missing_imports'] = (
                df['source_file'].nunique()
            )
        else:
            stats['files_with_missing_imports'] = 1
            
        return stats

    def _extract_imported_names(self, imports: List) -> set:
        """Extract all names made available by import statements."""
        names = set()
        
        for import_stmt in imports:
            if import_stmt.names:
                # from module import name1, name2
                for name in import_stmt.names:
                    if name != '*':  # Skip star imports
                        names.add(name)
            else:
                # import module or import module as alias
                if import_stmt.alias:
                    names.add(import_stmt.alias)
                else:
                    # Add the module name and its parts
                    module_parts = import_stmt.module.split('.')
                    names.add(module_parts[0])
        
        return names

    def _extract_local_names(self, tree: ast.AST) -> set:
        """Extract all names defined locally in the file."""
        names = set()
        
        for node in ast.walk(tree):
            # Function definitions
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
                # Extract function parameters
                param_names = self._extract_function_parameters(node)
                names.update(param_names)
            # Class definitions  
            elif isinstance(node, ast.ClassDef):
                names.add(node.name)
            # Variable assignments
            elif isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        names.add(target.id)
            # Other name bindings (for loops, with statements, etc.)
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                names.add(node.id)
        
        return names

    def _extract_function_parameters(self, func_node) -> set:
        """Extract all parameter names from a function definition."""
        param_names = set()
        
        # Regular positional arguments
        for arg in func_node.args.args:
            param_names.add(arg.arg)
        
        # Positional-only arguments (Python 3.8+)
        if hasattr(func_node.args, 'posonlyargs'):
            for arg in func_node.args.posonlyargs:
                param_names.add(arg.arg)
        
        # Keyword-only arguments
        for arg in func_node.args.kwonlyargs:
            param_names.add(arg.arg)
        
        # *args parameter
        if func_node.args.vararg:
            param_names.add(func_node.args.vararg.arg)
        
        # **kwargs parameter
        if func_node.args.kwarg:
            param_names.add(func_node.args.kwarg.arg)
        
        return param_names

    def _get_builtin_names(self) -> set:
        """Get Python built-in names."""
        import builtins
        return set(dir(builtins))

    def _is_likely_literal(self, name: str) -> bool:
        """Check if a name is likely a string literal or number."""
        # Skip very short names or obvious non-identifiers
        if len(name) <= 1:
            return True
        
        # Skip if it contains non-identifier characters
        if not name.isidentifier():
            return True
            
        # Skip common string-like patterns
        string_patterns = ['__', 'self', 'cls']
        if any(pattern in name for pattern in string_patterns):
            return True
            
        return False

    def _categorize_symbol_type(self, used_name) -> str:
        """Categorize the type of symbol based on usage context."""
        context = used_name.context.lower()
        
        if 'function_call' in context:
            return 'function'
        elif 'module_reference' in context:
            return 'module'
        elif 'attribute_access' in context:
            return 'attribute'
        else:
            return 'variable'

    def _suggest_import(self, symbol_name: str) -> str:
        """Suggest an import statement for a missing symbol."""
        # Common standard library modules
        stdlib_suggestions = {
            'os': 'import os',
            'sys': 'import sys', 
            'json': 'import json',
            'datetime': 'from datetime import datetime',
            'Path': 'from pathlib import Path',
            'defaultdict': 'from collections import defaultdict',
            'Counter': 'from collections import Counter',
            'pd': 'import pandas as pd',
            'np': 'import numpy as np',
            'plt': 'import matplotlib.pyplot as plt',
            're': 'import re',
            'math': 'import math',
            'random': 'import random',
            'uuid': 'import uuid',
            'logging': 'import logging'
        }
        
        return stdlib_suggestions.get(symbol_name, f"# import {symbol_name}")  