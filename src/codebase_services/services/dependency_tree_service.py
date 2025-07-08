from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
import ast
import pandas as pd
try:
    import networkx as nx
    from pyvis.network import Network
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False
from ..core.parser import CodeParser
from ..core.dependency_resolver import DependencyResolver
from ..entities.entities import CodeEntity, DependencyNode, DependencyTree


class DependencyTreeService:
    """
    Service for building comprehensive dependency trees across a codebase.
    
    This is like creating a family tree for your code - showing how different
    functions, classes, and modules are related through dependencies.
    """
    
    def __init__(self, parser: CodeParser, dependency_resolver: DependencyResolver):
        self.parser = parser
        self.dependency_resolver = dependency_resolver
        self._codebase_cache: Dict[str, Tuple[List[CodeEntity], ast.AST]] = {}
        self._upstream_visited: Set[str] = set()
        self._downstream_visited: Set[str] = set()
        self._node_registry: Dict[str, DependencyNode] = {}
        self._max_total_nodes = 10000  # Safety limit
    
    def build_dependency_tree(
        self, 
        file_path: Path, 
        entity_name: str, 
        entity_type: str,
        max_depth: Optional[int] = None,
        codebase_root: Optional[Path] = None
    ) -> DependencyTree:
        """
        Build a complete dependency tree for a target entity.
        
        Args:
            file_path: Path to the file containing the target entity
            entity_name: Name of the target entity
            entity_type: Type of entity ('function', 'class', 'module')
            max_depth: Maximum depth to traverse (None for unlimited)
            codebase_root: Root directory to scan for dependencies
        
        Returns:
            DependencyTree object with upstream and downstream dependencies
        """
        if codebase_root is None:
            codebase_root = file_path.parent
        
        # Clear caches for fresh analysis
        self._codebase_cache.clear()
        self._upstream_visited.clear()
        self._downstream_visited.clear()
        self._node_registry.clear()
        
        # Find target entity
        target_entity = self._find_target_entity(file_path, entity_name, entity_type)
        if not target_entity:
            raise ValueError(
                f"Entity '{entity_name}' of type '{entity_type}' "
                f"not found in {file_path}"
            )
        
        # Create target node at depth 0
        target_node = DependencyNode(
            name=target_entity.name,
            entity_type=target_entity.entity_type,
            file_path=str(file_path),
            line_start=target_entity.line_start,
            line_end=target_entity.line_end,
            dependency_type='target',
            depth=0,
            dependency_path=[],
            root_node_id=None  # Will be set after node_id is available
        )
        
        # Set target node as root of its own tree
        target_node.root_node_id = target_node.node_id
        
        # Register target node
        self._node_registry[target_node.node_id] = target_node
        
        # Build upstream dependencies (negative depths)
        upstream_nodes = self._build_upstream_tree_nodes(
            target_entity, file_path, codebase_root, 
            target_node.node_id, target_node.node_id, -1, max_depth
        )
        
        # Build downstream dependencies (positive depths)
        downstream_nodes = self._build_downstream_tree_nodes(
            target_entity, file_path, codebase_root, 
            target_node.node_id, target_node.node_id, 1, max_depth
        )
        
        # Convert nodes back to nested dict format for backward compatibility
        upstream_dict = self._nodes_to_nested_dict(upstream_nodes, 'upstream')
        downstream_dict = self._nodes_to_nested_dict(downstream_nodes, 'downstream')
        
        return DependencyTree(
            target=target_node,
            upstream=upstream_dict,
            downstream=downstream_dict,
            node_registry=self._node_registry.copy()
        )
    
    def _find_target_entity(self, file_path: Path, entity_name: str, entity_type: str) -> Optional[CodeEntity]:
        """Find the target entity in the specified file."""
        entities, _ = self._get_file_analysis(file_path)
        
        for entity in entities:
            if entity.name == entity_name and entity.entity_type == entity_type:
                return entity
        
        return None
    
    def _get_file_analysis(self, file_path: Path) -> Tuple[List[CodeEntity], ast.AST]:
        """Get cached entities for a file or parse if not cached."""
        file_key = str(file_path)
        
        if file_key not in self._codebase_cache:
            try:
                entities, tree = self.parser.parse(file_path)
                self._codebase_cache[file_key] = (entities, tree)
            except Exception:
                self._codebase_cache[file_key] = ([], ast.parse(""))
        
        return self._codebase_cache[file_key]
    
    def _build_upstream_tree_nodes(self, 
                                    target_entity: CodeEntity, 
                                    current_file: Path,
                                    codebase_root: Path, 
                                    parent_node_id: str,
                                    root_node_id: str,
                                    current_depth: int,
                                    max_depth: Optional[int]) -> List[DependencyNode]:
        """Build upstream dependency tree (negative depths: what target depends on)."""
        entity_key = f"{target_entity.name}@{current_file}"
        
        if entity_key in self._upstream_visited:
            return []
        
        if max_depth is not None and current_depth >= max_depth:
            return []
        
        self._upstream_visited.add(entity_key)
        
        # Find direct dependencies
        direct_deps = self._find_direct_dependencies(
            target_entity, current_file, codebase_root, parent_node_id, root_node_id, current_depth
        )
        
        result = direct_deps.copy()  # Include direct dependencies in result
        
        # Recursively build indirect dependencies
        for dep_node in direct_deps:
            dep_file = Path(dep_node.file_path)
            dep_entity = self._find_target_entity(dep_file, dep_node.name, dep_node.entity_type)
            
            if dep_entity:
                indirect_nodes = self._build_upstream_tree_nodes(
                    dep_entity, dep_file, codebase_root, dep_node.node_id, root_node_id, current_depth - 1, max_depth
                )
                result.extend(indirect_nodes)
        
        self._upstream_visited.remove(entity_key)
        return result
    
    def _build_downstream_tree_nodes(self, 
                                    target_entity: CodeEntity, 
                                    current_file: Path,
                                    codebase_root: Path, 
                                    parent_node_id: str,
                                    root_node_id: str,
                                    current_depth: int,
                                    max_depth: Optional[int]) -> List[DependencyNode]:
        """Build downstream dependency tree (positive depths: what depends on target)."""
        entity_key = f"{target_entity.name}@{current_file}"
        
        if entity_key in self._downstream_visited:
            return []
        
        if max_depth is not None and current_depth >= max_depth:
            return []
        
        self._downstream_visited.add(entity_key)
        
        # Find direct dependents
        direct_deps = self._find_direct_dependents(
            target_entity, current_file, codebase_root, current_depth,
            parent_node_id, root_node_id
        )
        
        result = direct_deps.copy()  # Include direct dependencies in result
        
        # Recursively build indirect dependencies
        for dep_node in direct_deps:
            dep_file = Path(dep_node.file_path)
            dep_entity = self._find_target_entity(dep_file, dep_node.name, dep_node.entity_type)
            
            if dep_entity:
                # Build next level
                next_nodes = self._build_downstream_tree_nodes(
                    dep_entity, dep_file, codebase_root, dep_node.node_id, root_node_id, current_depth + 1, max_depth
                )
                result.extend(next_nodes)
        
        self._downstream_visited.remove(entity_key)
        return result
    
    def _find_direct_dependencies(self, 
                                entity: CodeEntity, 
                                current_file: Path, 
                                codebase_root: Path,
                                parent_node_id: str,
                                root_node_id: str,
                                current_depth: int) -> List[DependencyNode]:
        """Find direct dependencies for an entity."""
        dependencies = []
        
        # Get internal dependencies (within same file)
        file_entities, _ = self._get_file_analysis(current_file)
        internal_deps = self.dependency_resolver.find_entity_dependencies(
            entity.name, 
            entity.source_code, 
            [e.name for e in file_entities]
        )
        
        for dep_name in internal_deps:
            dep_entity = self._find_target_entity(current_file, dep_name, 'function')
            if not dep_entity:
                dep_entity = self._find_target_entity(current_file, dep_name, 'class')
            
            if dep_entity:
                dep_node = DependencyNode(
                    name=dep_entity.name,
                    entity_type=dep_entity.entity_type,
                    file_path=str(current_file),
                    line_start=dep_entity.line_start,
                    line_end=dep_entity.line_end,
                    dependency_type='internal_reference',
                    depth=current_depth,
                    parent_node_id=parent_node_id,
                    root_node_id=root_node_id
                )
                self._node_registry[dep_node.node_id] = dep_node
                dependencies.append(dep_node)
        
        # Find external dependencies (imports and cross-file references)
        external_deps = self._find_external_dependencies(
            entity, current_file, codebase_root, parent_node_id, root_node_id, current_depth
        )
        dependencies.extend(external_deps)
        
        return dependencies
    
    def _find_direct_dependents(self, 
                              target_entity: CodeEntity, 
                              target_file: Path, 
                              codebase_root: Path,
                              current_depth: int = 0,
                              parent_node_id: Optional[str] = None,
                              root_node_id: Optional[str] = None) -> List[DependencyNode]:
        """Find entities that directly depend on the target entity."""
        dependents = []
        
        # Scan all Python files in codebase
        for py_file in codebase_root.rglob("*.py"):
            if py_file == target_file:
                continue
            
            entities, _ = self._get_file_analysis(py_file)
            
            for entity in entities:
                # Enhanced dependency type detection
                dependency_info = self._analyze_dependency_relationship(
                    entity, target_entity, target_file
                )
                
                if dependency_info:
                    # Create enhanced node
                    enhanced_node = DependencyNode(
                        name=entity.name,
                        entity_type=entity.entity_type,
                        file_path=str(py_file),
                        line_start=entity.line_start,
                        line_end=entity.line_end,
                        dependency_type=dependency_info['type'],
                        depth=current_depth,
                        parent_node_id=parent_node_id,
                        root_node_id=root_node_id
                    )
                    
                    # Register node
                    self._node_registry[enhanced_node.node_id] = enhanced_node
                    dependents.append(enhanced_node)
        
        return dependents
    
    def _find_external_dependencies(self, 
                                  entity: CodeEntity, 
                                  current_file: Path, 
                                  codebase_root: Path,
                                  parent_node_id: str,
                                  root_node_id: str,
                                  current_depth: int) -> List[DependencyNode]:
        """Find dependencies in other files."""
        dependencies = []
        
        # Parse the entity's AST to find references
        try:
            tree = ast.parse(entity.source_code)
        except SyntaxError:
            return dependencies
        
        # Collect only meaningful references (function calls, imports, inheritance)
        class MeaningfulReferenceCollector(ast.NodeVisitor):
            def __init__(self):
                self.references = set()
                self.imports = set()
            
            def visit_Import(self, node):
                for alias in node.names:
                    self.imports.add(alias.name.split('.')[0])
                self.generic_visit(node)
            
            def visit_ImportFrom(self, node):
                if node.module:
                    self.imports.add(node.module.split('.')[0])
                for alias in node.names:
                    self.imports.add(alias.name)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.references.add(node.func.id)
                elif isinstance(node.func, ast.Attribute):
                    if isinstance(node.func.value, ast.Name):
                        self.references.add(node.func.value.id)
                self.generic_visit(node)
            
            def visit_ClassDef(self, node):
                for base in node.bases:
                    if isinstance(base, ast.Name):
                        self.references.add(base.id)
                self.generic_visit(node)
        
        collector = MeaningfulReferenceCollector()
        collector.visit(tree)
        
        # Only include references that are imported or meaningfully used
        meaningful_refs = collector.references.intersection(collector.imports)
        meaningful_refs.update(collector.imports)
        
        # Search for these references in other files
        for ref_name in meaningful_refs:
            found_deps = self._search_codebase_for_entity(
                ref_name, current_file, codebase_root, parent_node_id, root_node_id, current_depth
            )
            dependencies.extend(found_deps)
        
        return dependencies
    
    def _search_codebase_for_entity(self, 
                                  entity_name: str, 
                                  exclude_file: Path, 
                                  codebase_root: Path,
                                  parent_node_id: str,
                                  root_node_id: str,
                                  current_depth: int) -> List[DependencyNode]:
        """Search the codebase for entities with the given name."""
        found_entities = []
        
        for py_file in codebase_root.rglob("*.py"):
            if py_file == exclude_file:
                continue
            
            entities, _ = self._get_file_analysis(py_file)
            
            for entity in entities:
                if entity.name == entity_name:
                    dep_node = DependencyNode(
                        name=entity.name,
                        entity_type=entity.entity_type,
                        file_path=str(py_file),
                        line_start=entity.line_start,
                        line_end=entity.line_end,
                        dependency_type='external_reference',
                        depth=current_depth,
                        parent_node_id=parent_node_id,
                        root_node_id=root_node_id
                    )
                    self._node_registry[dep_node.node_id] = dep_node
                    found_entities.append(dep_node)
        
        return found_entities
    
    def _analyze_dependency_relationship(self, 
                                       entity: CodeEntity, 
                                       target_entity: CodeEntity, 
                                       target_file: Path) -> dict:
        """Analyze the specific type of dependency relationship."""
        
        if not target_entity.name in entity.source_code:
            return None
        
        try:
            tree = ast.parse(entity.source_code)
        except SyntaxError:
            return {'type': 'unknown_reference'}
        
        # Check for inheritance
        inheritance_info = self._check_inheritance(tree, target_entity.name)
        if inheritance_info:
            return {'type': 'inheritance', 'details': inheritance_info}
        
        # Check for imports
        import_info = self._check_imports(tree, target_entity.name, target_file)
        if import_info:
            return {'type': 'import', 'details': import_info}
        
        # Check for function calls
        call_info = self._check_function_calls(tree, target_entity.name)
        if call_info:
            return {'type': 'function_call', 'details': call_info}
        
        # Check for instantiation
        instantiation_info = self._check_instantiation(tree, target_entity.name)
        if instantiation_info:
            return {'type': 'instantiation', 'details': instantiation_info}
        
        # Check for attribute access
        attr_info = self._check_attribute_access(tree, target_entity.name)
        if attr_info:
            return {'type': 'attribute_access', 'details': attr_info}
        
        # Default to name reference
        return {'type': 'name_reference'}
    
    def _check_inheritance(self, tree: ast.AST, target_name: str) -> dict:
        """Check if target is used as a base class."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for base in node.bases:
                    if isinstance(base, ast.Name) and base.id == target_name:
                        return {
                            'inheriting_class': node.name,
                            'base_class': target_name,
                            'line': node.lineno
                        }
        return None
    
    def _check_imports(self, tree: ast.AST, target_name: str, target_file: Path) -> dict:
        """Check if target is imported."""
        for node in ast.walk(tree):
            # Direct import: import module
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name == target_name or alias.name.endswith(f'.{target_name}'):
                        return {
                            'import_type': 'direct_import',
                            'module': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        }
            
            # From import: from module import name
            elif isinstance(node, ast.ImportFrom):
                for alias in node.names:
                    if alias.name == target_name:
                        return {
                            'import_type': 'from_import',
                            'module': node.module,
                            'name': alias.name,
                            'alias': alias.asname,
                            'line': node.lineno
                        }
        return None
    
    def _check_function_calls(self, tree: ast.AST, target_name: str) -> dict:
        """Check if target is called as a function."""
        calls = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                # Direct call: target_name()
                if isinstance(node.func, ast.Name) and node.func.id == target_name:
                    calls.append({
                        'call_type': 'direct_call',
                        'line': node.lineno
                    })
                # Method call: obj.target_name()
                elif isinstance(node.func, ast.Attribute) and node.func.attr == target_name:
                    calls.append({
                        'call_type': 'method_call',
                        'line': node.lineno
                    })
        
        return {'calls': calls} if calls else None
    
    def _check_instantiation(self, tree: ast.AST, target_name: str) -> dict:
        """Check if target is instantiated as a class."""
        instantiations = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == target_name:
                    instantiations.append({
                        'instantiation_type': 'direct_instantiation',
                        'line': node.lineno,
                        'args_count': len(node.args)
                    })
        
        return {'instantiations': instantiations} if instantiations else None
    
    def _check_attribute_access(self, tree: ast.AST, target_name: str) -> dict:
        """Check if target is accessed as an attribute."""
        accesses = []
        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                # obj.target_name
                if node.attr == target_name:
                    accesses.append({
                        'access_type': 'attribute_access',
                        'line': node.lineno
                    })
            elif isinstance(node, ast.Name) and node.id == target_name:
                # Direct name reference
                accesses.append({
                    'access_type': 'name_reference',
                    'line': node.lineno
                })
        
        return {'accesses': accesses} if accesses else None
    
    def _entity_references_target(self, 
                                entity: CodeEntity, 
                                target_entity: CodeEntity, 
                                target_file: Path) -> bool:
        """Check if an entity references the target entity."""
        # Simple name-based check (can be enhanced)
        return target_entity.name in entity.source_code
    
    def create_interactive_dependency_graph(
        self, 
        tree: DependencyTree,
        output_filename: str = "dependency_graph.html",
        height: str = "900px",
        width: str = "100%"
    ) -> str:
        """
        Create an interactive dependency graph using NetworkX and Pyvis.
        Simplified version to avoid JavaScript container errors.
        
        Args:
            tree: DependencyTree object to visualize
            output_filename: Name of the HTML file to generate
            height: Height of the visualization
            width: Width of the visualization
        
        Returns:
            Path to the generated HTML file
        
        Raises:
            ImportError: If networkx or pyvis are not installed
        """
        if not VISUALIZATION_AVAILABLE:
            raise ImportError(
                "networkx and pyvis are required for graph visualization. "
                "Install with: pip install networkx pyvis"
            )
        
        # Create a very simple network with minimal configuration
        net = Network(height=height, width=width, bgcolor="#ffffff")
        
        # Add the target node as the center
        target_id = tree.target.node_id
        net.add_node(
            target_id,
            label=f"🎯 {tree.target.name}",
            color="#FF6B6B",
            size=30,
            title=f"{tree.target.name} ({tree.target.entity_type})"
        )
        
        # Get connected nodes only - start with target and follow connections
        connected_nodes = self._get_connected_nodes(tree, max_nodes=50)
        
        # Keep track of which nodes we actually add to the network
        added_node_ids = {target_id}  # Target is always added
        
        # Add all connected nodes
        for node in connected_nodes:
            node_id = node.node_id
            if node_id != target_id:  # Don't duplicate target
                # Clean, readable labels without depth indicators
                label = node.name
                
                # Color based on depth and direction
                if node.depth < 0:
                    color = "#4ECDC4"  # Upstream (what target depends on)
                elif node.depth > 0:
                    color = "#45B7D1"  # Downstream (what depends on target)
                else:
                    color = "#96CEB4"  # Same level
                
                # Create detailed tooltip
                file_name = Path(node.file_path).name
                tooltip = f"{node.name} ({node.entity_type})\nFile: {file_name}\nDepth: {node.depth}\nType: {node.dependency_type}"
                
                net.add_node(
                    node_id,
                    label=label,
                    color=color,
                    size=25,  # Slightly larger for better visibility
                    title=tooltip,
                    font={'size': 14}  # Larger font for readability
                )
                added_node_ids.add(node_id)
        
        # Add edges only between nodes that actually exist in the network
        for node in connected_nodes:
            if (node.parent_node_id and 
                node.parent_node_id in added_node_ids and 
                node.node_id in added_node_ids):
                
                parent_id = node.parent_node_id
                child_id = node.node_id
                
                # Color edges based on direction
                if node.depth < 0:
                    edge_color = "#4ECDC4"  # Upstream
                else:
                    edge_color = "#45B7D1"  # Downstream
                
                net.add_edge(parent_id, child_id, color=edge_color)
        
        # Configuration for better connected graph layout
        net.set_options("""
        var options = {
          "physics": {
            "enabled": true,
            "stabilization": {"iterations": 100},
            "barnesHut": {
              "gravitationalConstant": -8000,
              "centralGravity": 0.3,
              "springLength": 95,
              "springConstant": 0.04,
              "damping": 0.09
            }
          },
          "nodes": {
            "font": {"size": 14},
            "borderWidth": 2
          },
          "edges": {
            "width": 2,
            "smooth": {"type": "continuous"}
          }
        }
        """)
        
        # Generate HTML file
        net.write_html(output_filename, open_browser=False, notebook=False)
        
        return output_filename
    
    def _get_connected_nodes(self, tree: DependencyTree, max_nodes: int = 50) -> List[DependencyNode]:
        """
        Get nodes that are connected to the target, prioritizing closer relationships.
        This prevents disconnected clusters in the visualization.
        """
        connected = []
        visited = set()
        
        # Start with target node
        target = tree.target
        connected.append(target)
        visited.add(target.node_id)
        
        # Use BFS to find connected nodes, prioritizing by depth
        queue = [(target, 0)]  # (node, distance_from_target)
        
        while queue and len(connected) < max_nodes:
            current_node, distance = queue.pop(0)
            
            # Find all nodes that have this node as parent (children)
            for node in tree.node_registry.values():
                if (node.node_id not in visited and 
                    node.parent_node_id == current_node.node_id):
                    connected.append(node)
                    visited.add(node.node_id)
                    queue.append((node, distance + 1))
                    
                    if len(connected) >= max_nodes:
                        break
            
            # Also find parent of current node
            if current_node.parent_node_id and current_node.parent_node_id not in visited:
                parent_node = tree.node_registry.get(current_node.parent_node_id)
                if parent_node:
                    connected.append(parent_node)
                    visited.add(parent_node.node_id)
                    queue.append((parent_node, distance + 1))
        
        # Sort by depth for better layout (target at center, then by depth)
        connected.sort(key=lambda n: (abs(n.depth), n.depth))
        
        return connected[:max_nodes]

    def _nodes_to_nested_dict(self, nodes: List[DependencyNode], direction: str) -> Dict[str, any]:
        """Convert flat list of nodes back to nested dict format for backward compatibility."""
        if not nodes:
            return {}
        
        # Group nodes by depth
        depth_groups = {}
        for node in nodes:
            depth = abs(node.depth)  # Use absolute value for grouping
            if depth not in depth_groups:
                depth_groups[depth] = []
            depth_groups[depth].append(node)
        
        # Build nested structure
        result = {
            'direct': depth_groups.get(1, []),
            'indirect': {},
            'depth': 0 if direction == 'upstream' else 0
        }
        
        # Add deeper levels as indirect
        for depth in sorted(depth_groups.keys()):
            if depth > 1:
                for node in depth_groups[depth]:
                    key = f"{node.name}@{node.file_path}"
                    result['indirect'][key] = {
                        'direct': [node],
                        'indirect': {},
                        'depth': depth
                    }
        
        return result 