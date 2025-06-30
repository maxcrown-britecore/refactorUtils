#!/usr/bin/env python3
"""
Python Code Extractor

A tool to extract functions and classes from a Python file into separate modules.
Follows clean architecture principles with separation of concerns.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any


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
    names: Tuple[str, ...]  # Empty for "import module", populated for "from module import name1, name2"
    alias: Optional[str] = None
    level: int = 0  # For relative imports
    original_line: str = ""


@dataclass
class UsedName:
    """Represents a name used in code that might need an import."""
    name: str
    context: str  # 'attribute', 'function_call', 'class_instantiation', etc.
    line_number: int


@dataclass
class DependencyNode:
    """Represents a single node in the dependency tree."""
    name: str
    entity_type: str  # 'function', 'class', 'module'
    file_path: str
    line_start: int
    line_end: int
    dependency_type: str  # 'import', 'call', 'inheritance', 'attribute_access'
    depth: int = 0


@dataclass
class DependencyTree:
    """Container for dependency tree analysis results."""
    target: DependencyNode
    upstream: Dict[str, Any] = field(default_factory=dict)
    downstream: Dict[str, Any] = field(default_factory=dict)
    
    def to_pretty_string(self, show_upstream: bool = True, 
                         show_downstream: bool = True) -> str:
        """Generate a visual tree representation."""
        result = []
        target_info = (f"📦 Dependency Tree for: {self.target.name} "
                       f"({self.target.entity_type})")
        result.append(target_info)
        
        file_info = (f"   📁 {self.target.file_path}:"
                     f"{self.target.line_start}-{self.target.line_end}")
        result.append(file_info)
        result.append("")
        
        if show_upstream and self.upstream:
            result.append("⬆️  UPSTREAM DEPENDENCIES (what this depends on):")
            result.extend(self._format_tree_branch(self.upstream, "   "))
            result.append("")
        
        if show_downstream and self.downstream:
            result.append("⬇️  DOWNSTREAM DEPENDENCIES (what depends on this):")
            result.extend(self._format_tree_branch(self.downstream, "   "))
        
        return "\n".join(result)
    
    def _format_tree_branch(self, tree_dict: Dict[str, Any], indent: str) -> List[str]:
        """Recursively format a tree branch."""
        result = []
        
        if 'direct' in tree_dict:
            for node in tree_dict['direct']:
                result.append(f"{indent}├── {node.name} ({node.entity_type}) [{node.dependency_type}]")
                result.append(f"{indent}    📁 {node.file_path}:{node.line_start}")
        
        if 'indirect' in tree_dict:
            for key, subtree in tree_dict['indirect'].items():
                result.append(f"{indent}└── {key} (depth {subtree.get('depth', 0)})")
                result.extend(self._format_tree_branch(subtree, indent + "    "))
        
        return result
    
    def to_graph(self):
        """Convert to networkx graph object for visualization."""
        try:
            import networkx as nx
        except ImportError:
            msg = ("networkx is required for graph functionality. "
                   "Install with: pip install networkx")
            raise ImportError(msg)
        
        G = nx.DiGraph()
        
        # Add target node
        target_id = f"{self.target.name}@{self.target.file_path}"
        G.add_node(target_id, 
                  name=self.target.name,
                  type=self.target.entity_type,
                  file_path=self.target.file_path,
                  is_target=True)
        
        # Add upstream dependencies
        self._add_graph_nodes(G, self.upstream, target_id, direction='upstream')
        
        # Add downstream dependencies  
        self._add_graph_nodes(G, self.downstream, target_id, direction='downstream')
        
        return G
    
    def _add_graph_nodes(self, graph, tree_dict: Dict[str, Any], parent_id: str, direction: str):
        """Recursively add nodes to the graph."""
        if 'direct' in tree_dict:
            for node in tree_dict['direct']:
                node_id = f"{node.name}@{node.file_path}"
                graph.add_node(node_id,
                             name=node.name,
                             type=node.entity_type,
                             file_path=node.file_path,
                             dependency_type=node.dependency_type)
                
                if direction == 'upstream':
                    graph.add_edge(node_id, parent_id, type=node.dependency_type)
                else:
                    graph.add_edge(parent_id, node_id, type=node.dependency_type)
        
        if 'indirect' in tree_dict:
            for key, subtree in tree_dict['indirect'].items():
                self._add_graph_nodes(graph, subtree, parent_id, direction)
    
    def get_all_dependencies(self, direction: Optional[str] = None) -> List[DependencyNode]:
        """Get flattened list of all dependencies."""
        result = []
        
        if direction is None or direction == 'upstream':
            result.extend(self._flatten_dependencies(self.upstream))
        
        if direction is None or direction == 'downstream':
            result.extend(self._flatten_dependencies(self.downstream))
        
        # Remove duplicates while preserving order
        seen = set()
        unique_result = []
        for node in result:
            node_key = f"{node.name}@{node.file_path}"
            if node_key not in seen:
                seen.add(node_key)
                unique_result.append(node)
        
        return unique_result
    
    def _flatten_dependencies(self, tree_dict: Dict[str, Any]) -> List[DependencyNode]:
        """Recursively flatten dependency tree to list."""
        result = []
        
        if 'direct' in tree_dict:
            result.extend(tree_dict['direct'])
        
        if 'indirect' in tree_dict:
            for subtree in tree_dict['indirect'].values():
                result.extend(self._flatten_dependencies(subtree))
        
        return result
