# Codebase Services - Usage Guide

Complete guide for using `codebase_services` both as a Python library and CLI tools.

## 📦 Installation

### From PyPI (Recommended)
```bash
pip install codebase_services
```

### Development Installation
```bash
git clone https://github.com/maxcrown-britecore/codebase_services.git
cd codebase_services
pip install -e .
```

## 🐍 Python Library Usage

### Basic Import
```python
from codebase_services import (
    create_extractor, 
    create_report_service, 
    create_dependency_tree_service
)
```

### 1. Code Extraction Service

#### Basic Extraction (Separate Files)
```python
from pathlib import Path
from codebase_services import create_extractor

# Create the service
extractor = create_extractor()

# Extract all entities to separate files
result = extractor.extract_code_entities(
    source_file=Path("large_module.py")
)

print(f"Created {len(result['files_created'])} files")
print(f"Extracted {len(result['extracted_entities'])} entities")
```

#### Selective Extraction
```python
# Extract only specific entities
result = extractor.extract_code_entities(
    source_file=Path("my_module.py"),
    entity_names=["MyClass", "helper_function", "CONSTANT"]
)
```

#### Target File Mode (Consolidation)
```python
# Move entities to a specific target file
result = extractor.extract_code_entities(
    source_file=Path("large_module.py"),
    entity_names=["UtilClass", "helper_func"],
    target_file=Path("utils/consolidated.py")
)

print(f"Modified target file: {result['target_file_modified']}")
```

#### Advanced Options
```python
# Full-featured extraction
result = extractor.extract_code_entities(
    source_file=Path("legacy_code.py"),
    entity_names=["ImportantClass", "critical_function"],
    target_file=Path("refactored/new_module.py"),
    cut_entities=True,  # Remove from source after extraction
    py2_top_most_import=True,  # Add Python 2 compatibility
    top_custom_block="# Refactored from legacy code\n# Date: 2024-06-30",
    root_path_prefix="myproject"
)

# Check results
if result['source_file_modified']:
    print(f"Cut {len(result['entities_cut'])} entities from source")
```

### 2. Code Report Service

#### Single File Analysis
```python
from codebase_services import create_report_service
import pandas as pd

# Create the service
reporter = create_report_service()

# Generate report for a single file
df = reporter.generate_code_report(Path("my_module.py"))

# Display the data
print(df[['name', 'entity_type', 'line_start', 'code_length', 'has_docstring']])

# Get summary statistics
stats = reporter.get_summary_statistics(df)
print(f"Total entities: {stats['total_entities']}")
print(f"Documentation coverage: {stats['docstring_percentage']}%")
```

#### Multi-File Analysis
```python
# Analyze multiple files
file_paths = [
    Path("src/module1.py"),
    Path("src/module2.py"),
    Path("src/utils.py")
]

df = reporter.generate_multi_file_report(file_paths)

# Find files with poor documentation
poorly_documented = df[df['has_docstring'] == False]
print(f"Files needing documentation: {len(poorly_documented)}")

# Export to CSV
df.to_csv("code_analysis_report.csv", index=False)
```

#### Directory Analysis
```python
# Analyze entire directory
from pathlib import Path

src_dir = Path("src")
python_files = list(src_dir.rglob("*.py"))

df = reporter.generate_multi_file_report(python_files)
stats = reporter.get_summary_statistics(df)

print(f"Analyzed {stats['files_analyzed']} files")
print(f"Found {stats['total_entities']} entities")
print(f"Functions: {stats['functions_count']}")
print(f"Classes: {stats['classes_count']}")
```

### 3. Enhanced Dependency Tree Service with Path Tracking

#### Basic Dependency Analysis
```python
from codebase_services import create_dependency_tree_service

# Create the service
dependency_service = create_dependency_tree_service()

# Analyze a specific class
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/services/my_service.py"),
    entity_name="MyServiceClass",
    entity_type="class"
)

# Print the dependency tree
print(tree.to_pretty_string())
```

#### 🆕 Enhanced Path Tracking Features
```python
# Get complete dependency paths (NEW!)
all_deps = tree.get_all_dependencies()
for dep in all_deps[:5]:
    path = tree.get_dependency_path(dep.node_id)
    print(f"Path to {dep.name}: {' → '.join(path)}")

# Get dependency chain with full node objects (NEW!)
chain = tree.get_dependency_chain(some_node_id)
print("Complete dependency chain:")
for i, node in enumerate(chain):
    print(f"  {i+1}. {node.name} ({node.entity_type})")

# Find children of any node (NEW!)
children = tree.get_children_of_node(parent_node_id)
print(f"Direct children: {[child.name for child in children]}")

# Group dependencies by depth (NEW!)
depth_groups = tree.dependency_depths_grouped()
for depth, nodes in depth_groups.items():
    print(f"Depth {depth}: {len(nodes)} dependencies")

# Generate enhanced path report (NEW!)
path_report = tree.to_path_report()
print(path_report)
```

#### Advanced Dependency Analysis
```python
# Analyze with depth limit and custom codebase root
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/models/user.py"),
    entity_name="User",
    entity_type="class",
    max_depth=3,  # Limit analysis depth
    codebase_root=Path("src")  # Scan only src directory
)

# Get all dependencies as a list
all_deps = tree.get_all_dependencies()
print(f"Total dependencies found: {len(all_deps)}")

for dep in all_deps[:5]:  # Show first 5
    print(f"  {dep.name} ({dep.entity_type}) in {dep.file_path}")
```

#### Network Graph Export
```python
# Export to NetworkX graph for advanced analysis
graph = tree.to_graph()

# Use with visualization libraries
import matplotlib.pyplot as plt
import networkx as nx

plt.figure(figsize=(12, 8))
pos = nx.spring_layout(graph, k=1, iterations=50)
nx.draw(graph, pos, with_labels=True, node_color='lightblue', 
        node_size=1000, font_size=8, arrows=True)
plt.title("Code Dependency Graph")
plt.savefig("dependency_graph.png", dpi=300, bbox_inches='tight')
plt.show()

# Analyze graph properties
print(f"Nodes: {graph.number_of_nodes()}")
print(f"Edges: {graph.number_of_edges()}")
print(f"Strongly connected components: {len(list(nx.strongly_connected_components(graph)))}")
```

#### 🆕 Interactive Graph Visualization
```python
# Create interactive HTML dependency graph with Pyvis
html_file = dependency_service.create_interactive_dependency_graph(
    tree=tree,
    output_filename="my_dependency_graph.html",
    height="900px",
    width="100%"
)

print(f"🎯 Interactive graph saved to: {html_file}")
print("🌐 Open in your browser for interactive exploration!")

# Advanced interactive graph with custom styling
html_file = dependency_service.create_interactive_dependency_graph(
    tree=tree,
    output_filename="custom_graph.html",
    height="1200px",  # Larger height
    width="100%"
)

# Features of the interactive graph:
# - Drag and zoom functionality
# - Click on nodes to see details
# - Physics simulation for natural layout
# - Depth-based node positioning
# - Hover tooltips with full node information
# - Directed edges showing dependency flow
```

## 🖥️ CLI Usage

### 1. Code Extraction (`codebase-extract`)

#### Basic Usage
```bash
# Extract all entities to separate files
codebase-extract my_module.py

# Extract specific entities
codebase-extract my_module.py --entities MyClass helper_function

# Extract to a target file
codebase-extract large_file.py --entities Utils Helper --target-file utils/new_module.py
```

#### Advanced Options
```bash
# Full-featured extraction with all options
codebase-extract legacy_code.py \
  --entities "ImportantClass" "critical_function" \
  --target-file refactored/new_module.py \
  --cut \
  --py2-import \
  --custom-block "# Refactored legacy code" \
  --root-prefix myproject
```

### 2. Code Reports (`codebase-report`)

#### File Analysis
```bash
# Analyze a single file
codebase-report my_module.py

# Get summary statistics only
codebase-report my_module.py --summary-only

# Analyze a directory
codebase-report src/
```

#### Export Options
```bash
# Export to CSV
codebase-report src/ --format csv --output analysis.csv

# Export to JSON
codebase-report my_module.py --format json --output report.json

# Table format (default)
codebase-report src/ --format table
```

### 3. Dependency Analysis (`codebase-deps`)

#### Basic Analysis
```bash
# Analyze a class
codebase-deps src/models/user.py User class

# Analyze a function
codebase-deps src/utils.py helper_function function
```

#### Advanced Analysis
```bash
# With depth limit and custom root
codebase-deps src/services/payment.py PaymentService class \
  --max-depth 3 \
  --codebase-root src/

# Different output formats
codebase-deps src/models/user.py User class --format tree
codebase-deps src/models/user.py User class --format graph
codebase-deps src/models/user.py User class --format list
codebase-deps src/models/user.py User class --format df

# 🆕 NEW: Enhanced path tracking formats
codebase-deps src/models/user.py User class --format paths
codebase-deps src/models/user.py User class --format depths

# 🆕 NEW: Interactive graph visualization
codebase-deps src/models/user.py User class --format interactive
```

#### Output Options
```bash
# Save to file
codebase-deps src/models/user.py User class --output user_dependencies.txt

# Show only upstream dependencies
codebase-deps src/models/user.py User class --upstream-only

# Show only downstream dependencies
codebase-deps src/models/user.py User class --downstream-only

# 🆕 Interactive graph generation
codebase-deps src/models/user.py User class --format interactive
codebase-deps src/models/user.py User class --format interactive --output my_graph.html
```

## 🆕 Enhanced Path Tracking Features

### Understanding Dependency Paths

The enhanced dependency tree service now provides **complete path tracking**, allowing you to see exactly how dependencies are connected through multiple levels. This solves the common problem of knowing a dependency exists at a certain depth but not knowing the complete path to reach it.

#### Key Capabilities

1. **Complete Dependency Paths**: See the full chain from root to any dependency
2. **Parent-Child Relationships**: Navigate the dependency tree bidirectionally  
3. **Fast Node Lookup**: O(1) access to any node by unique ID
4. **Path Reconstruction**: Get complete dependency chains as node objects
5. **Children Discovery**: Find all direct dependents of any node

#### CLI Format Options

```bash
# Generate detailed path report
codebase-deps src/models/user.py User class --format paths

# Show dependencies grouped by depth with paths
codebase-deps src/models/user.py User class --format depths

# 🆕 Generate interactive HTML graph (NEW!)
codebase-deps src/models/user.py User class --format interactive

# Save path analysis for review
codebase-deps src/core/payment.py PaymentProcessor class \
  --format paths \
  --output payment_processor_paths.txt

# 🆕 Interactive graph with custom filename (NEW!)
codebase-deps src/core/payment.py PaymentProcessor class \
  --format interactive \
  --output payment_processor_dependencies.html
```

#### Real-World Path Tracking Example

```python
from pathlib import Path
from codebase_services import create_dependency_tree_service

# Analyze a critical business class
dependency_service = create_dependency_tree_service()
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/billing/invoice.py"),
    entity_name="InvoiceProcessor", 
    entity_type="class",
    max_depth=3,
    codebase_root=Path("src")
)

print(f"📊 Found {len(tree.node_registry)} nodes with complete path tracking")

# Find specific dependencies and their paths
depth_groups = tree.dependency_depths_grouped()
for depth, nodes in depth_groups.items():
    print(f"\n🔍 Depth {depth}: {len(nodes)} dependencies")
    
    for node in nodes[:3]:  # Show first 3 per depth
        print(f"   📍 {node.name}")
        print(f"   🗺️  Path: {node.path_string}")
        
        # Get complete dependency chain
        chain = tree.get_dependency_chain(node.node_id)
        if len(chain) > 1:
            chain_names = [n.name for n in chain]
            print(f"   🔗 Chain: {' → '.join(chain_names)}")
        
        # Show children (what depends on this node)
        children = tree.get_children_of_node(node.node_id)
        if children:
            child_names = [child.name for child in children[:3]]
            print(f"   👶 Children: {', '.join(child_names)}")

# Generate comprehensive path report
with open("invoice_processor_impact.txt", "w") as f:
    f.write(tree.to_path_report())

print("✅ Complete impact analysis saved to invoice_processor_impact.txt")
```

#### Business Value of Path Tracking

**Before Enhancement:**
- ❓ "I know `calculate_tax` is at depth 2, but how is it connected?"
- ❓ "Which specific path will my changes follow?"
- ❓ "What's the complete chain of dependencies?"

**After Enhancement:**
- ✅ **Complete Visibility**: `InvoiceProcessor → BillingService → TaxCalculator → calculate_tax`
- ✅ **Impact Planning**: See exact paths changes will propagate through
- ✅ **Risk Assessment**: Identify critical dependency chains
- ✅ **Refactoring Guidance**: Understand complete dependency structure

## 🎨 Interactive Dependency Visualization

### New Interactive Graph Feature

The latest enhancement includes **interactive HTML dependency graphs** using Pyvis for beautiful, explorable visualizations that work in any web browser.

#### Key Features of Interactive Graphs

1. **🖱️ Interactive Exploration**: Drag, zoom, and click on nodes
2. **🎯 Node Details**: Hover tooltips with complete node information
3. **🔄 Physics Simulation**: Natural layout with force-directed positioning
4. **📊 Depth Visualization**: Color-coded or level-based node positioning
5. **🔗 Directed Edges**: Clear dependency flow visualization
6. **💻 Browser-based**: Works offline in any modern web browser

#### Python Library Usage

```python
from pathlib import Path
from codebase_services import create_dependency_tree_service

# Create the dependency service
dependency_service = create_dependency_tree_service()

# Build dependency tree
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/services/payment_service.py"),
    entity_name="PaymentService",
    entity_type="class",
    max_depth=3
)

# Generate interactive graph
html_file = dependency_service.create_interactive_dependency_graph(
    tree=tree,
    output_filename="payment_service_graph.html",
    height="900px",
    width="100%"
)

print(f"🎯 Interactive dependency graph created: {html_file}")
print("🌐 Open this file in your browser to explore dependencies!")
```

#### CLI Usage Examples

```bash
# Basic interactive graph
codebase-deps src/models/user.py User class --format interactive

# Custom filename and deep analysis
codebase-deps src/core/processor.py DataProcessor class \
  --format interactive \
  --max-depth 4 \
  --output data_processor_visualization.html

# Focus on specific dependency direction
codebase-deps src/api/routes.py UserRoutes class \
  --format interactive \
  --downstream-only \
  --output user_routes_impact.html
```

#### What Gets Generated

The interactive graph includes:
- **Target Entity**: Highlighted center node
- **All Dependencies**: Connected with directed edges
- **Depth Information**: Visual hierarchy
- **File Paths**: Clickable node details
- **Dependency Types**: Color-coded or labeled edges
- **Interactive Controls**: Pan, zoom, drag functionality

#### Business Value

**Perfect for:**
- 📋 **Stakeholder Reviews**: Share visual dependency analysis with non-technical team members
- 🎯 **Impact Presentations**: Show the scope of proposed changes visually
- 🔍 **Code Exploration**: Interactive discovery of unfamiliar codebases
- 📚 **Documentation**: Include in technical documentation and architecture guides
- 🤝 **Team Collaboration**: Share dependency insights across development teams
- 🎓 **Onboarding**: Help new developers understand code structure visually

## 🚀 Real-World Examples

### Example 1: Legacy Code Refactoring

```python
from pathlib import Path
from codebase_services import create_extractor, create_report_service

# Step 1: Analyze the legacy file
reporter = create_report_service()
df = reporter.generate_code_report(Path("legacy_monster.py"))

# Find large, complex entities
large_entities = df[df['code_length'] > 1000]
print("Large entities to extract:")
print(large_entities[['name', 'entity_type', 'code_length']])

# Step 2: Extract entities to separate modules
extractor = create_extractor()

# Extract data models
result = extractor.extract_code_entities(
    source_file=Path("legacy_monster.py"),
    entity_names=["User", "Product", "Order"],
    target_file=Path("models/entities.py"),
    cut_entities=True
)

# Extract utility functions
result = extractor.extract_code_entities(
    source_file=Path("legacy_monster.py"),
    entity_names=["validate_email", "format_currency", "sanitize_input"],
    target_file=Path("utils/helpers.py"),
    cut_entities=True
)

print("Refactoring complete!")
```

### Example 2: Impact Analysis Before Changes

```bash
# Before modifying a critical class, understand its impact
codebase-deps src/core/payment_processor.py PaymentProcessor class \
  --max-depth 2 \
  --downstream-only \
  --output impact_analysis.txt

echo "⚠️  Files that will be affected by PaymentProcessor changes:"
grep "📁" impact_analysis.txt | head -10
```

### Example 3: Documentation Audit

```python
from pathlib import Path
from codebase_services import create_report_service

# Analyze entire codebase for documentation coverage
reporter = create_report_service()
src_files = list(Path("src").rglob("*.py"))
df = reporter.generate_multi_file_report(src_files)

# Find files with poor documentation
undocumented = df[df['has_docstring'] == False]
by_file = undocumented.groupby('source_file').size().sort_values(ascending=False)

print("Files needing documentation (worst first):")
for file_path, count in by_file.head(10).items():
    print(f"  {file_path}: {count} undocumented entities")

# Export detailed report
df.to_csv("documentation_audit.csv", index=False)
```

### Example 4: Dependency Cleanup

```bash
# Find all dependencies of a module you want to remove
codebase-deps src/deprecated/old_module.py OldClass class \
  --downstream-only \
  --format list \
  --output dependencies_to_fix.txt

echo "Files that need updating before removing old_module.py:"
cat dependencies_to_fix.txt
```

### Example 5: Enhanced Impact Analysis with Path Tracking

```python
from pathlib import Path
from codebase_services import create_dependency_tree_service

# Before making breaking changes to a critical class
dependency_service = create_dependency_tree_service()
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/core/base_event.py"),
    entity_name="BaseEvent", 
    entity_type="class",
    max_depth=3,
    codebase_root=Path("src")
)

print("🚨 IMPACT ANALYSIS: BaseEvent Changes")
print("=" * 50)

# Use new path tracking to understand complete impact
depth_groups = tree.dependency_depths_grouped()

critical_paths = []
for depth, nodes in depth_groups.items():
    if depth > 0:  # Skip the target itself
        print(f"\n📊 Depth {depth} Impact: {len(nodes)} affected components")
        
        for node in nodes:
            path = tree.get_dependency_path(node.node_id)
            path_str = " → ".join(path)
            
            # Identify critical business components
            if any(keyword in node.name.lower() for keyword in 
                   ['payment', 'billing', 'user', 'auth', 'policy']):
                critical_paths.append({
                    'component': node.name,
                    'path': path_str,
                    'file': node.file_path,
                    'type': node.dependency_type
                })

print(f"\n🚨 CRITICAL BUSINESS COMPONENTS AFFECTED:")
print("-" * 40)
for item in critical_paths[:10]:  # Show top 10 critical
    print(f"⚠️  {item['component']}")
    print(f"   📍 Path: {item['path']}")
    print(f"   📁 File: {Path(item['file']).name}")
    print(f"   🔗 Type: {item['type']}")
    print()

# Generate detailed path report for stakeholders
report_path = "base_event_impact_analysis.txt"
with open(report_path, "w") as f:
    f.write("🚨 BaseEvent Impact Analysis Report\n")
    f.write("=" * 50 + "\n\n")
    f.write(f"Total affected components: {len(tree.get_all_dependencies())}\n")
    f.write(f"Critical business components: {len(critical_paths)}\n\n")
    f.write(tree.to_path_report())

print(f"✅ Detailed impact analysis saved to: {report_path}")
print(f"📋 Share this report with your team before making changes!")
```

### Example 6: CLI-Based Path Analysis

```bash
# Quick path analysis for critical components
echo "🔍 Analyzing payment processor dependencies..."
codebase-deps src/billing/payment_processor.py PaymentProcessor class \
  --format paths \
  --max-depth 2 \
  --output payment_paths.txt

echo "📊 Depth-grouped analysis..."  
codebase-deps src/billing/payment_processor.py PaymentProcessor class \
  --format depths \
  --max-depth 2

echo "💾 Results saved to payment_paths.txt for team review"

# Before refactoring - understand the complete dependency structure
echo "📋 Pre-refactoring dependency audit..."
codebase-deps src/legacy/old_service.py LegacyService class \
  --format paths \
  --downstream-only \
  --output legacy_service_dependencies.txt

echo "✅ Review legacy_service_dependencies.txt before refactoring"
```

### Example 7: Interactive Graph Generation for Stakeholders 🆕

```bash
# Generate interactive graphs for different audiences

echo "🎯 Creating interactive graph for technical review..."
codebase-deps src/core/authentication.py AuthManager class \
  --format interactive \
  --max-depth 3 \
  --output auth_manager_technical.html

echo "📋 Creating focused graph for security audit..."
codebase-deps src/security/validator.py SecurityValidator class \
  --format interactive \
  --downstream-only \
  --output security_impact_audit.html

echo "🎨 Creating comprehensive graph for architecture documentation..."
codebase-deps src/api/main_router.py MainRouter class \
  --format interactive \
  --max-depth 4 \
  --output api_architecture_overview.html

echo "✅ Interactive graphs generated!"
echo "🌐 Share these HTML files with:"
echo "   • auth_manager_technical.html - Engineering team"
echo "   • security_impact_audit.html - Security team"  
echo "   • api_architecture_overview.html - Architecture documentation"
```

### Example 8: Python Library Interactive Workflow 🆕

```python
from pathlib import Path
from codebase_services import create_dependency_tree_service

# Multi-purpose interactive graph generation workflow
dependency_service = create_dependency_tree_service()

def generate_interactive_analysis(entity_info, audience="technical"):
    """Generate interactive graphs for different audiences."""
    
    tree = dependency_service.build_dependency_tree(
        file_path=Path(entity_info['file']),
        entity_name=entity_info['name'],
        entity_type=entity_info['type'],
        max_depth=entity_info.get('depth', 3)
    )
    
    # Generate appropriate filename
    base_name = f"{entity_info['name'].lower()}_{audience}"
    html_file = f"{base_name}_dependencies.html"
    
    # Create interactive graph
    result_file = dependency_service.create_interactive_dependency_graph(
        tree=tree,
        output_filename=html_file,
        height="1000px" if audience == "detailed" else "800px",
        width="100%"
    )
    
    # Get summary stats
    all_deps = tree.get_all_dependencies()
    depth_groups = tree.dependency_depths_grouped()
    max_depth = max(depth_groups.keys()) if depth_groups else 0
    
    return {
        'file': result_file,
        'stats': {
            'total_dependencies': len(all_deps),
            'max_depth': max_depth,
            'depth_distribution': {d: len(nodes) for d, nodes in depth_groups.items()}
        }
    }

# Generate graphs for different components and audiences
components = [
    {'file': 'src/models/user.py', 'name': 'User', 'type': 'class', 'depth': 2},
    {'file': 'src/services/payment.py', 'name': 'PaymentService', 'type': 'class', 'depth': 3},
    {'file': 'src/core/database.py', 'name': 'DatabaseManager', 'type': 'class', 'depth': 2}
]

print("🎯 Generating interactive dependency analysis suite...")
print("=" * 60)

for component in components:
    for audience in ['technical', 'overview', 'detailed']:
        result = generate_interactive_analysis(component, audience)
        
        print(f"\n📊 {component['name']} - {audience.title()} Analysis")
        print(f"   📄 File: {result['file']}")
        print(f"   📈 Dependencies: {result['stats']['total_dependencies']}")
        print(f"   📏 Max Depth: {result['stats']['max_depth']}")
        print(f"   🔍 Distribution: {result['stats']['depth_distribution']}")

print(f"\n✅ Interactive analysis suite complete!")
print(f"🌐 Open the HTML files in your browser to explore dependencies")
print(f"📋 Share appropriate graphs with different stakeholders:")
print(f"   • technical_* - For developers and code reviews")
print(f"   • overview_* - For managers and quick impact assessment")  
print(f"   • detailed_* - For architecture reviews and documentation")
```

## 🎯 Best Practices

### For Code Extraction
1. **Always analyze first**: Use `codebase-report` to understand the code structure
2. **Start small**: Extract a few entities at a time
3. **Use target files**: For related entities, consolidate into logical modules
4. **Test thoroughly**: Always test after extraction/cutting
5. **Version control**: Commit before major extractions

### For Dependency Analysis
1. **Limit depth**: Use `--max-depth` for large codebases to avoid overwhelming output
2. **Focus scope**: Use `--codebase-root` to analyze specific directories
3. **Save results**: Use `--output` for complex analyses you'll reference later
4. **Regular audits**: Check dependencies before making breaking changes

### 🆕 For Enhanced Path Tracking
1. **Use path reports**: `--format paths` for stakeholder reviews before major changes
2. **Depth analysis**: `--format depths` to understand impact distribution
3. **Critical path identification**: Focus on business-critical dependency chains
4. **Pre-refactoring analysis**: Always generate path reports before structural changes
5. **Team communication**: Share path analysis reports with affected teams
6. **Documentation**: Include dependency paths in architectural documentation

### 🎨 For Interactive Graph Visualization
1. **Stakeholder presentations**: Use `--format interactive` for visual impact demonstrations
2. **Browser-based sharing**: Share HTML files with non-technical team members
3. **Architecture documentation**: Include interactive graphs in project documentation
4. **Code exploration**: Use interactive graphs to understand unfamiliar codebases
5. **Custom filenames**: Use `--output custom_name.html` for organized graph collections
6. **Audience-specific graphs**: Generate different depth/scope graphs for different audiences
7. **Offline accessibility**: Interactive graphs work without internet connection

### For Reporting
1. **Automate**: Include reports in CI/CD pipelines
2. **Track trends**: Export to CSV and track metrics over time
3. **Set goals**: Aim for specific documentation coverage percentages
4. **Review regularly**: Monthly code quality reviews using reports

## 🔧 Integration Examples

### Git Pre-commit Hook
```bash
#!/bin/bash
# Check documentation coverage before commit
codebase-report src/ --summary-only | grep "Docstring Percentage" | awk '{if ($3 < 80) exit 1}'
```

### CI/CD Pipeline
```yaml
# GitHub Actions example
- name: Code Quality Report
  run: |
    pip install codebase_services
    codebase-report src/ --format json --output quality_report.json
    # Upload report as artifact
```

### Jupyter Notebook Analysis
```python
# In a Jupyter notebook for interactive analysis
%matplotlib inline
import pandas as pd
from codebase_services import create_report_service

reporter = create_report_service()
df = reporter.generate_multi_file_report(Path("src").rglob("*.py"))

# Interactive visualizations
df['code_length'].hist(bins=30, title='Code Length Distribution')
df.groupby('entity_type').size().plot(kind='bar', title='Entity Types')
```

## 📚 Additional Resources

- **GitHub Repository**: https://github.com/maxcrown-britecore/codebase_services
- **PyPI Package**: https://pypi.org/project/codebase_services/
- **Issues & Support**: https://github.com/maxcrown-britecore/codebase_services/issues

## 🤝 Contributing

See the main README.md for contribution guidelines and development setup instructions. 