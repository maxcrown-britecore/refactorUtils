from pathlib import Path
from typing import Dict, List, Optional, Set, Any
import ast
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
        self._codebase_cache: Dict[str, List[CodeEntity]] = {}
        self._visited_entities: Set[str] = set()
        self._node_registry: Dict[str, DependencyNode] = {}
    
    def build_dependency_tree(self, 
                            file_path: Path, 
                            entity_name: str, 
                            entity_type: str,
                            max_depth: Optional[int] = None,
                            codebase_root: Optional[Path] = None) -> DependencyTree:
        """
        Build a complete dependency tree for a target entity.
        
        Args:
            file_path: Path to the file containing the target entity
            entity_name: Name of the target entity
            entity_type: Type of entity ('function', 'class', 'module')
            max_depth: Maximum depth to traverse (None for unlimited)
            codebase_root: Root directory to scan for dependencies (default: parent of file_path)
        
        Returns:
            DependencyTree object with upstream and downstream dependencies
        """
        if codebase_root is None:
            codebase_root = file_path.parent
        
        # Clear caches for fresh analysis
        self._codebase_cache.clear()
        self._visited_entities.clear()
        self._node_registry.clear()
        
        # Find target entity
        target_entity = self._find_target_entity(file_path, entity_name, entity_type)
        if not target_entity:
            raise ValueError(f"Entity '{entity_name}' of type '{entity_type}' not found in {file_path}")
        
        # Create enhanced target node with path tracking
        target_node = DependencyNode(
            name=target_entity.name,
            entity_type=target_entity.entity_type,
            file_path=str(file_path),
            line_start=target_entity.line_start,
            line_end=target_entity.line_end,
            dependency_type='target',
            depth=0,
            dependency_path=[]  # Root has empty path
        )
        
        # Register target node
        self._node_registry[target_node.node_id] = target_node
        
        # Build upstream dependencies (what target depends on)
        upstream = self._build_upstream_tree(target_entity, file_path, codebase_root, max_depth)
        
        # Reset visited entities for downstream analysis
        self._visited_entities.clear()
        
        # Build downstream dependencies with path tracking
        downstream = self._build_downstream_tree(
            target_entity, file_path, codebase_root, max_depth, 0,
            target_node.node_id, [target_node.name]
        )
        
        return DependencyTree(
            target=target_node,
            upstream=upstream,
            downstream=downstream,
            node_registry=self._node_registry.copy()
        )
    
    def _find_target_entity(self, file_path: Path, entity_name: str, entity_type: str) -> Optional[CodeEntity]:
        """Find the target entity in the specified file."""
        entities = self._get_file_entities(file_path)
        
        for entity in entities:
            if entity.name == entity_name and entity.entity_type == entity_type:
                return entity
        
        return None
    
    def _get_file_entities(self, file_path: Path) -> List[CodeEntity]:
        """Get cached entities for a file or parse if not cached."""
        file_key = str(file_path)
        
        if file_key not in self._codebase_cache:
            try:
                self._codebase_cache[file_key] = self.parser.parse(file_path)
            except Exception:
                self._codebase_cache[file_key] = []
        
        return self._codebase_cache[file_key]
    
    def _build_upstream_tree(self, 
                           target_entity: CodeEntity, 
                           current_file: Path,
                           codebase_root: Path, 
                           max_depth: Optional[int],
                           current_depth: int = 0) -> Dict[str, Any]:
        """Build upstream dependency tree (what target depends on)."""
        entity_key = f"{target_entity.name}@{current_file}"
        
        if entity_key in self._visited_entities:
            return {'cyclic_reference': entity_key}
        
        if max_depth is not None and current_depth >= max_depth:
            return {'max_depth_reached': current_depth}
        
        self._visited_entities.add(entity_key)
        
        # Find direct dependencies
        direct_deps = self._find_direct_dependencies(target_entity, current_file, codebase_root)
        
        result = {
            'direct': direct_deps,
            'indirect': {},
            'depth': current_depth
        }
        
        # Recursively build indirect dependencies
        for dep_node in direct_deps:
            dep_file = Path(dep_node.file_path)
            dep_entity = self._find_target_entity(dep_file, dep_node.name, dep_node.entity_type)
            
            if dep_entity:
                indirect_key = f"{dep_node.name}@{dep_node.file_path}"
                result['indirect'][indirect_key] = self._build_upstream_tree(
                    dep_entity, dep_file, codebase_root, max_depth, current_depth + 1
                )
        
        self._visited_entities.remove(entity_key)
        return result
    
    def _build_downstream_tree(self, 
                             target_entity: CodeEntity, 
                             current_file: Path,
                             codebase_root: Path, 
                             max_depth: Optional[int],
                             current_depth: int = 0,
                             parent_node_id: Optional[str] = None,
                             current_path: Optional[List[str]] = None) -> Dict[str, Any]:
        """Build downstream dependency tree (what depends on target) with path tracking."""
        entity_key = f"{target_entity.name}@{current_file}"
        
        if current_path is None:
            current_path = []
        
        if entity_key in self._visited_entities:
            return {'cyclic_reference': entity_key}
        
        if max_depth is not None and current_depth >= max_depth:
            return {'max_depth_reached': current_depth}
        
        self._visited_entities.add(entity_key)
        
        # Find direct dependents with path tracking
        direct_deps = self._find_direct_dependents(
            target_entity, current_file, codebase_root, current_depth,
            parent_node_id, current_path
        )
        
        result = {
            'direct': direct_deps,
            'indirect': {},
            'depth': current_depth
        }
        
        # Recursively build indirect dependencies with path tracking
        for dep_node in direct_deps:
            dep_file = Path(dep_node.file_path)
            dep_entity = self._find_target_entity(dep_file, dep_node.name, dep_node.entity_type)
            
            if dep_entity:
                # Update parent's children list
                if parent_node_id and parent_node_id in self._node_registry:
                    parent = self._node_registry[parent_node_id]
                    if dep_node.node_id not in parent.children_node_ids:
                        parent.children_node_ids.append(dep_node.node_id)
                
                # Build next level with extended path
                next_path = current_path + [dep_node.name]
                indirect_key = f"{dep_node.name}@{dep_node.file_path}"
                result['indirect'][indirect_key] = self._build_downstream_tree(
                    dep_entity, dep_file, codebase_root, max_depth, current_depth + 1,
                    dep_node.node_id, next_path
                )
        
        self._visited_entities.remove(entity_key)
        return result
    
    def _find_direct_dependencies(self, 
                                entity: CodeEntity, 
                                current_file: Path, 
                                codebase_root: Path) -> List[DependencyNode]:
        """Find direct dependencies for an entity."""
        dependencies = []
        
        # Get internal dependencies (within same file)
        internal_deps = self.dependency_resolver.find_entity_dependencies(
            entity.name, entity.source_code, [e.name for e in self._get_file_entities(current_file)]
        )
        
        for dep_name in internal_deps:
            dep_entity = self._find_target_entity(current_file, dep_name, 'function')
            if not dep_entity:
                dep_entity = self._find_target_entity(current_file, dep_name, 'class')
            
            if dep_entity:
                dependencies.append(DependencyNode(
                    name=dep_entity.name,
                    entity_type=dep_entity.entity_type,
                    file_path=str(current_file),
                    line_start=dep_entity.line_start,
                    line_end=dep_entity.line_end,
                    dependency_type='internal_reference'
                ))
        
        # Find external dependencies (imports and cross-file references)
        external_deps = self._find_external_dependencies(entity, current_file, codebase_root)
        dependencies.extend(external_deps)
        
        return dependencies
    
    def _find_direct_dependents(self, 
                              target_entity: CodeEntity, 
                              target_file: Path, 
                              codebase_root: Path,
                              current_depth: int = 0,
                              parent_node_id: Optional[str] = None,
                              current_path: Optional[List[str]] = None) -> List[DependencyNode]:
        """Find entities that directly depend on the target entity with path tracking."""
        dependents = []
        
        if current_path is None:
            current_path = []
        
        # Scan all Python files in codebase
        for py_file in codebase_root.rglob("*.py"):
            if py_file == target_file:
                continue
            
            file_entities = self._get_file_entities(py_file)
            
            for entity in file_entities:
                # Enhanced dependency type detection
                dependency_info = self._analyze_dependency_relationship(
                    entity, target_entity, target_file
                )
                
                if dependency_info:
                    # Create enhanced node with path tracking
                    enhanced_node = DependencyNode(
                        name=entity.name,
                        entity_type=entity.entity_type,
                        file_path=str(py_file),
                        line_start=entity.line_start,
                        line_end=entity.line_end,
                        dependency_type=dependency_info['type'],
                        depth=current_depth,
                        parent_node_id=parent_node_id,
                        dependency_path=current_path.copy()  # Path to this node
                    )
                    
                    # Register node for path lookup
                    self._node_registry[enhanced_node.node_id] = enhanced_node
                    dependents.append(enhanced_node)
        
        return dependents
    
    def _find_external_dependencies(self, 
                                  entity: CodeEntity, 
                                  current_file: Path, 
                                  codebase_root: Path) -> List[DependencyNode]:
        """Find dependencies in other files."""
        dependencies = []
        
        # Parse the entity's AST to find references
        try:
            tree = ast.parse(entity.source_code)
        except SyntaxError:
            return dependencies
        
        # Collect all name references
        class ExternalReferenceCollector(ast.NodeVisitor):
            def __init__(self):
                self.references = []
            
            def visit_Name(self, node):
                if isinstance(node.ctx, ast.Load):
                    self.references.append(node.id)
                self.generic_visit(node)
            
            def visit_Call(self, node):
                if isinstance(node.func, ast.Name):
                    self.references.append(node.func.id)
                elif isinstance(node.func, ast.Attribute) and isinstance(node.func.value, ast.Name):
                    self.references.append(node.func.value.id)
                self.generic_visit(node)
        
        collector = ExternalReferenceCollector()
        collector.visit(tree)
        
        # Search for these references in other files
        for ref_name in set(collector.references):
            found_deps = self._search_codebase_for_entity(ref_name, current_file, codebase_root)
            dependencies.extend(found_deps)
        
        return dependencies
    
    def _search_codebase_for_entity(self, 
                                  entity_name: str, 
                                  exclude_file: Path, 
                                  codebase_root: Path) -> List[DependencyNode]:
        """Search the codebase for entities with the given name."""
        found_entities = []
        
        for py_file in codebase_root.rglob("*.py"):
            if py_file == exclude_file:
                continue
            
            file_entities = self._get_file_entities(py_file)
            
            for entity in file_entities:
                if entity.name == entity_name:
                    found_entities.append(DependencyNode(
                        name=entity.name,
                        entity_type=entity.entity_type,
                        file_path=str(py_file),
                        line_start=entity.line_start,
                        line_end=entity.line_end,
                        dependency_type='external_reference'
                    ))
        
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
    
    def create_interactive_dependency_graph(self, 
                                          tree: DependencyTree,
                                          output_filename: str = "dependency_graph.html",
                                          height: str = "900px",
                                          width: str = "100%") -> str:
        """
        Create an interactive dependency graph using NetworkX and Pyvis.
        
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
        
        # Get all dependencies as DataFrame
        df = tree.get_all_dependencies_df()
        
        # === Build Graph from parent-child relationships ===
        edges_df = df.dropna(subset=["parent_node_id"])
        edges = list(zip(edges_df["parent_node_id"], edges_df["node_id"]))
        
        # Build directed graph
        G = nx.DiGraph()
        G.add_edges_from(edges)
        
        # === Set up interactive Pyvis graph ===
        net = Network(notebook=True, height=height, width=width, directed=True)
        
        # Simplified label: just entity name (could also truncate path if needed)
        label_map = dict(zip(df["node_id"], df["name"]))
        
        # Add nodes with optional depth-based color
        depth_map = dict(zip(df["node_id"], df["depth"]))
        for node in G.nodes:
            label = label_map.get(node, node.split('/')[-1][:30])
            depth = depth_map.get(node, 0)
            net.add_node(node, label=label, title=node, level=depth)
        
        # Add edges
        for source, target in G.edges:
            net.add_edge(source, target)
        
        net.show_buttons(filter_=['physics']) 
        
        # === Show or Save to HTML ===
        net.show(output_filename)
        
        return output_filename 