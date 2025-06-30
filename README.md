# Codebase Services

A comprehensive Python tool for **codebase analysis and code extraction** that helps you refactor large Python files and generate insightful reports about your code structure.

## 📦 Installation

### Prerequisites
- Python 3.8+
- Git access to this repository

### Install from Git Repository

#### Latest Version
```bash
pip install git+ssh://git@github.com/maxcrown-britecore/codebase_services.git
```

#### Specific Version/Tag
```bash
# Install specific version tag
pip install git+ssh://git@github.com/maxcrown-britecore/codebase_services.git@v0.1.0

# Install from specific branch
pip install git+ssh://git@github.com/maxcrown-britecore/codebase_services.git@main
```

### Add to Project Dependencies

#### requirements.txt
```txt
# requirements.txt
pandas>=1.3.0
git+ssh://git@github.com/maxcrown/codebase_services.git@v0.1.0
```

#### pyproject.toml
```toml
[project]
dependencies = [
    "pandas>=1.3.0",
    "codebase_services @ git+ssh://git@github.com/maxcrown/codebase_services.git@v0.1.0"
]
```

### Verify Installation

#### Test Python Library
```python
# Test package import
from codebase_services import create_extractor, create_report_service, create_dependency_tree_service
print("✅ Library installation successful!")
```

#### Test CLI Commands
```bash
# Verify CLI tools are available
codebase-extract --help
codebase-report --help  
codebase-deps --help
```

### Development Installation

For development work on this package:
```bash
# Clone and install in editable mode
git clone git@github.com:maxcrown-britecore/codebase_services.git
cd codebase_services
pip install -e .
```


## 🚀 Main Features

Based on the factory functions in `main.py`, this project provides three core services:

### 1. **Code Extraction Service** (`create_extractor()`)
Intelligently extracts functions and classes from Python files with **two flexible extraction modes**.

**Key Capabilities:**
- 🔍 **AST-based parsing** - Uses Python's Abstract Syntax Tree for accurate code analysis
- 📦 **Smart import resolution** - Automatically determines and includes required imports
- 🔗 **Dependency management** - Resolves internal dependencies between extracted entities
- ⚡ **Import optimization** - Generates clean, optimized import statements
- 📁 **Dual extraction modes** - Create separate files OR consolidate into a target file
- 🔄 **Import merging** - Intelligently merges imports when appending to existing files

**Two Extraction Modes:**

#### **Mode 1: Separate File Creation** (Default)
Creates individual files for each extracted entity with proper `__init__.py` management.

#### **Mode 2: Target File Consolidation** (New!)
Moves multiple entities into a single existing target file, perfect for:
- Consolidating related functionality
- Moving entities to existing modules
- Building feature-specific files
- Refactoring without creating new module structure

**Perfect for:**
- Breaking down large, monolithic Python files
- Modularizing legacy codebases
- Creating clean, maintainable code structure
- Consolidating related functionality into existing modules

### 2. **Code Report Service** (`create_report_service()`)
Generates detailed analytical reports about your Python codebase structure and metrics.

**Key Capabilities:**
- 📊 **DataFrame reports** - Structured data analysis using pandas
- 📈 **Code metrics** - Line counts, complexity analysis, docstring coverage
- 🔍 **Multi-file analysis** - Analyze entire projects or directories
- 📋 **Summary statistics** - Executive-level insights about your codebase
- 🎯 **Dependency tracking** - Understand internal code relationships

**Perfect for:**
- Code quality assessments
- Technical debt analysis
- Project documentation
- Understanding large codebases

### 3. **Dependency Tree Service** (`create_dependency_tree_service()`)
Creates comprehensive dependency maps showing how functions, classes, and modules are interconnected across your entire codebase.

**Key Capabilities:**
- 🌳 **Bidirectional dependency trees** - Shows both upstream (what it depends on) and downstream (what depends on it) relationships
- 🔍 **Multi-file analysis** - Traces dependencies across your entire codebase, not just single files
- 🎯 **Precise entity targeting** - Analyze specific functions, classes, or modules by name and type
- 🔄 **Cycle detection** - Safely handles circular dependencies without infinite loops
- 📊 **Multiple output formats** - Visual trees, NetworkX graphs, and flattened dependency lists
- ⚡ **Smart caching** - Efficiently reuses parsed file data for performance
- 🎚️ **Depth limiting** - Control analysis depth with optional maximum depth parameter
- 🏷️ **Dependency classification** - Distinguishes between different types of dependencies (internal references, external references, etc.)

**Perfect for:**
- Impact analysis before refactoring ("What will break if I change this?")
- Understanding code architecture and relationships
- Finding unused or orphaned code
- Planning refactoring strategies
- Onboarding new team members to complex codebases
- Identifying tightly coupled components

## 🏗️ Architecture

The project follows **clean architecture principles** with clear separation of concerns:

### Core Components (from `main.py` factory functions):

- **`PythonASTParser`** - Parses Python source code into analyzable entities
- **`FileWriter`** - Handles file creation and organization
- **`ImportAnalyzer`** - Extracts and analyzes import statements
- **`DependencyResolver`** - Resolves internal and external dependencies
- **`ImportOptimizer`** - Generates clean, optimized import statements

### Factory Pattern
The `main.py` uses the **Factory Pattern** to create fully configured service instances:

```python
# Create a complete extraction toolkit
extractor = create_extractor()

# Create a complete analysis toolkit  
reporter = create_report_service()

# Create a complete dependency analysis toolkit
dependency_service = create_dependency_tree_service()
```

This ensures all components are properly wired together and ready to use.

## 🎯 Use Cases & Examples

### **1. Code Refactoring - Separate Files Mode**
Extract entities into individual files (original behavior):

```python
extractor = create_extractor()
result = extractor.extract_code_entities(
    source_file=Path("large_file.py"),
    entity_names=["MyClass", "helper_function"]
)
# Creates: MyClass.py, helper_function.py, and updates __init__.py
```

### **2. Code Consolidation - Target File Mode** 🆕
Move multiple entities to an existing target file:

```python
extractor = create_extractor()
result = extractor.extract_code_entities(
    source_file=Path("large_file.py"),
    entity_names=["UtilClass", "process_data", "validate_input"],
    target_file=Path("utils/data_processing.py")  # Existing or new file
)
# Appends all entities to data_processing.py with smart import merging
```

### **3. Advanced Target File Usage**
Complete example with all options:

```python
extractor = create_extractor()
result = extractor.extract_code_entities(
    source_file=Path("legacy_module.py"),
    entity_names=["DatabaseHelper", "query_builder"],
    target_file=Path("database/helpers.py"),
    py2_top_most_import=True,  # Add Python 2 compatibility
    top_custom_block="# Database utility functions\n# Added via extraction",
    root_path_prefix="myproject"
)

# Result structure for target file mode:
{
    'source_file': 'legacy_module.py',
    'extracted_entities': [
        {'name': 'DatabaseHelper', 'type': 'class'},
        {'name': 'query_builder', 'type': 'function'}
    ],
    'files_created': [],  # Empty in target file mode
    'init_file_updated': False,
    'target_file_modified': 'database/helpers.py'  # Path to modified file
}
```

### **4. Codebase Analysis**
```python
reporter = create_report_service()
df = reporter.generate_code_report(Path("my_module.py"))
stats = reporter.get_summary_statistics(df)
```

### **5. Dependency Tree Analysis** 🆕
Build comprehensive dependency maps for better code understanding:

```python
dependency_service = create_dependency_tree_service()

# Analyze a specific class and its relationships
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/services/report_service.py"),
    entity_name="CodeReportService",
    entity_type="class",
    max_depth=3,  # Optional depth limiting
    codebase_root=Path("src")  # Scan this directory for dependencies
)

# Get a beautiful visual representation
print(tree.to_pretty_string())
# Output:
# 📦 Dependency Tree for: CodeReportService (class)
#    📁 src/services/report_service.py:7-150
# 
# ⬆️  UPSTREAM DEPENDENCIES (what this depends on):
#    ├── CodeParser (class) [external_reference]
#        📁 src/core/parser.py:8
#    ├── DependencyResolver (class) [external_reference]
#        📁 src/core/dependency_resolver.py:7
# 
# ⬇️  DOWNSTREAM DEPENDENCIES (what depends on this):
#    ├── MainController (class) [external_reference]
#        📁 src/controllers/main.py:15
```

### **6. Impact Analysis Workflow**
Perfect for understanding change impact before refactoring:

```python
# Before modifying a critical function, understand its impact
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/core/parser.py"),
    entity_name="parse",
    entity_type="function"
)

# Get all entities that would be affected by changes
affected_entities = tree.get_all_dependencies('downstream')
print(f"⚠️  Changing this function affects {len(affected_entities)} other entities")

# Get detailed breakdown
for entity in affected_entities:
    print(f"   • {entity.name} in {entity.file_path}:{entity.line_start}")
```

### **7. Advanced Graph Analysis**
Export to NetworkX for sophisticated analysis and visualization:

```python
# Get NetworkX graph for advanced analysis
graph = tree.to_graph()

# Use with visualization libraries
import matplotlib.pyplot as plt
import networkx as nx

# Create a visual dependency graph
plt.figure(figsize=(12, 8))
pos = nx.spring_layout(graph)
nx.draw(graph, pos, with_labels=True, node_color='lightblue', 
        node_size=1000, font_size=8, arrows=True)
plt.title("Code Dependency Graph")
plt.show()

# Analyze graph properties
print(f"Total nodes: {graph.number_of_nodes()}")
print(f"Total edges: {graph.number_of_edges()}")
print(f"Strongly connected components: {len(list(nx.strongly_connected_components(graph)))}")
```

## 📋 **Target File Mode Behavior**

When using `target_file` parameter:

**✅ What happens:**
- Validates target file (.py extension required)
- Creates target file and directories if they don't exist
- Preserves existing content in target file
- Merges imports intelligently (existing + new)
- Appends all specified entities to the end of the file
- Returns info about the modified target file

**🔧 Import Handling:**
- **Smart Merging**: Preserves existing imports, adds new ones in separate section
- **Deduplication**: Avoids import conflicts
- **Organization**: Maintains clean import structure

**📁 File Management:**
- No new individual files created
- No `__init__.py` updates
- Target file is created if missing
- Existing target file content is preserved

## 🔧 Core Philosophy

This tool treats code transformation like a **well-organized kitchen**:
- **Extraction Service** = The chef who carefully separates ingredients into organized containers OR consolidates them into feature-specific containers
- **Report Service** = The inventory manager who provides detailed reports about what's in stock
- **Dependency Tree Service** = The architect who maps out how all the ingredients and recipes are connected and depend on each other
- **Core Components** = The specialized tools that make all processes efficient and reliable

Each service is assembled from specialized components, ensuring reliability, maintainability, and extensibility.

## 📚 Using This Project in iPython/Jupyter Notebooks

If you want to use this project from an iPython or Jupyter notebook in the root directory, and your source code is now inside the `src/` subdirectory, add the following lines at the top of your notebook:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path().resolve() / "src"))
```

This allows you to import your packages as before, for example:

```python
from services.report_service import CodeReportService
```

No need to change your import statements to include `src.` as a prefix.
