#!/usr/bin/env python3
"""
Python Code Extractor

A tool to extract functions and classes from a Python file into separate modules.
Follows clean architecture principles with separation of concerns.
"""
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any
import pandas as pd

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
    """Represents a single node in the dependency tree with path tracking."""
    name: str
    entity_type: str  # 'function', 'class', 'module'
    file_path: str
    line_start: int
    line_end: int
    dependency_type: str  # 'import', 'call', 'inheritance', 'attribute_access'
    depth: int = 0
    
    # NEW: Parent-child relationship tracking
    parent_node_id: Optional[str] = None
    dependency_path: List[str] = field(default_factory=list)
    children_node_ids: List[str] = field(default_factory=list)
    
    @property
    def node_id(self) -> str:
        """Unique identifier for this node."""
        return f"{self.name}@{self.file_path}:{self.line_start}"
    
    @property
    def path_string(self) -> str:
        """Human-readable dependency path from root."""
        if not self.dependency_path:
            return self.name
        return " → ".join(self.dependency_path + [self.name])
    
    @property
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        base_dict = self.__dict__
        base_dict['node_id'] = self.node_id
        return base_dict


@dataclass
class DependencyTree:
    """Container for dependency tree analysis results with path tracking."""
    target: DependencyNode
    upstream: Dict[str, Any] = field(default_factory=dict)
    downstream: Dict[str, Any] = field(default_factory=dict)
    
    # NEW: Node registry for path reconstruction
    node_registry: Dict[str, DependencyNode] = field(default_factory=dict)
    
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
    
    def get_all_dependencies_df(self) -> pd.DataFrame:
        """Get all dependencies as a DataFrame."""
        affected_dependencies = self.get_all_dependencies()
        list_of_dicts = [node.to_dict for node in affected_dependencies]
        return pd.DataFrame(list_of_dicts)
    
    def _flatten_dependencies(self, tree_dict: Dict[str, Any]) -> List[DependencyNode]:
        """Recursively flatten dependency tree to list."""
        result = []
        
        if 'direct' in tree_dict:
            result.extend(tree_dict['direct'])
        
        if 'indirect' in tree_dict:
            for subtree in tree_dict['indirect'].values():
                result.extend(self._flatten_dependencies(subtree))
        
        return result
    
    def dependency_depths_grouped(self) -> Dict[int, List[DependencyNode]]:
        """Group dependencies by depth."""
        grouped = {}
        for node in self.node_registry.values():
            depth = node.depth
            if depth not in grouped:
                grouped[depth] = []
            grouped[depth].append(node)
        return grouped
    
    def get_dependency_path(self, node_id: str) -> List[str]:
        """Get the complete dependency path from root to specified node."""
        if node_id not in self.node_registry:
            return []
        
        node = self.node_registry[node_id]
        return node.dependency_path + [node.name]
    
    def get_dependency_chain(self, node_id: str) -> List[DependencyNode]:
        """Get the complete chain of nodes from root to specified node."""
        if node_id not in self.node_registry:
            return []
        
        chain = []
        
        # Start with target
        chain.append(self.target)
        
        # Build chain by following parent relationships
        current_node_id = node_id
        path_nodes = []
        
        while current_node_id in self.node_registry:
            node = self.node_registry[current_node_id]
            path_nodes.append(node)
            current_node_id = node.parent_node_id
            if not current_node_id:
                break
        
        # Reverse to show root → target path
        chain.extend(reversed(path_nodes))
        return chain
    
    def get_children_of_node(self, node_id: str) -> List[DependencyNode]:
        """Get all direct children of a specific node."""
        if node_id not in self.node_registry:
            return []
        
        node = self.node_registry[node_id]
        return [self.node_registry[child_id] for child_id in node.children_node_ids 
                if child_id in self.node_registry]
    
    def to_path_report(self) -> str:
        """Generate a report showing dependency paths."""
        result = []
        result.append(f"📊 Dependency Path Analysis for: {self.target.name}")
        result.append("=" * 60)
        result.append("")
        
        # Group nodes by depth
        depth_groups = {}
        for node in self.node_registry.values():
            depth = node.depth
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(node)
        
        # Show paths for each depth level
        for depth in sorted(depth_groups.keys()):
            nodes = depth_groups[depth]
            result.append(f"🔍 Depth {depth} Dependencies ({len(nodes)} nodes):")
            result.append("")
            
            for node in nodes[:10]:  # Show first 10 per depth
                result.append(f"   📍 {node.name} [{node.dependency_type}]")
                result.append(f"      Path: {node.path_string}")
                result.append(f"      File: {node.file_path}:{node.line_start}")
                result.append("")
            
            if len(nodes) > 10:
                result.append(f"   ... and {len(nodes) - 10} more at depth {depth}")
                result.append("")
        
        return "\n".join(result)
