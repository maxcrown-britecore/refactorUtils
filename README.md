# Codebase Services

A comprehensive Python tool for **codebase analysis and code extraction** that helps you refactor large Python files and generate insightful reports about your code structure.

## 📦 Installation

### Quick Install
```bash
pip install git+ssh://git@github.com/maxcrown-britecore/codebase_services.git
```

### Prerequisites
- Python 3.8+
- Git access to this repository

### Dependencies
The package automatically installs:
- `pandas>=1.3.0` - For data analysis and reporting
- `networkx>=2.5` - For graph analysis and visualization
- `pyvis>=0.3.0` - For interactive HTML graph generation

### Verify Installation
```bash
# Test CLI commands
codebase-extract --help
codebase-report --help  
codebase-deps --help
```

## 🚀 Main Features

### 1. **Code Extraction** (`codebase-extract`)
Break down large Python files into well-organized, modular structures.

**Key Capabilities:**
- ✂️ **Extract functions and classes** to separate files or consolidate into target files
- 🔍 **AST-based parsing** for accurate code analysis
- 📦 **Smart import resolution** with automatic dependency management
- 🔄 **Cut mode** to remove entities from source after extraction
- 🐍 **Python 2 compatibility** imports when needed

### 2. **Code Analysis** (`codebase-report`)
Generate detailed analytical reports about your codebase structure and quality.

**Key Capabilities:**
- 📊 **Structured reports** using pandas DataFrames
- 📈 **Code metrics** including line counts, complexity, and documentation coverage
- 🔍 **Multi-file analysis** for entire projects
- 📋 **Summary statistics** for executive-level insights
- 💾 **Export formats** (CSV, JSON, table)

### 3. **Dependency Analysis** (`codebase-deps`)
Visualize and understand code relationships across your entire codebase.

**Key Capabilities:**
- 🌳 **Bidirectional dependency trees** (upstream and downstream)
- 🎨 **Interactive HTML graphs** with drag-and-zoom functionality
- 📊 **Multiple output formats** (tree, graph, list, paths, depths)
- 🔄 **Cycle detection** and safe handling of circular dependencies
- 🎯 **Impact analysis** for refactoring planning

## 📚 CLI Documentation

### Comprehensive Guides

Each CLI tool has a detailed guide with examples, workflows, and best practices:

- **[📊 `codebase-report` CLI Guide](CODEBASE_REPORT_CLI_GUIDE.md)** - Complete guide for code analysis and quality metrics
- **[🔍 `codebase-deps` CLI Guide](CODEBASE_DEPS_CLI_GUIDE.md)** - Complete guide for dependency analysis and visualization  
- **[✂️ `codebase-extract` CLI Guide](CODEBASE_EXTRACT_CLI_GUIDE.md)** - Complete guide for code extraction and refactoring

### Quick Examples

```bash
# Extract specific entities to separate files
codebase-extract src/models.py --entities UserModel ProductModel

# Generate project quality report
codebase-report src/ --format csv --output project_analysis.csv

# Analyze dependencies with interactive visualization
codebase-deps src/core.py DatabaseManager class --format interactive
```

## 🐍 Python Library Usage

For advanced programmatic usage, see [USAGE.md](USAGE.md) for complete Python library documentation.

```python
from codebase_services import create_extractor, create_report_service, create_dependency_tree_service

# Extract code entities
extractor = create_extractor()
result = extractor.extract_code_entities(source_file=Path("large_file.py"))

# Generate reports
reporter = create_report_service()
df = reporter.generate_code_report(Path("my_module.py"))

# Analyze dependencies
dependency_service = create_dependency_tree_service()
tree = dependency_service.build_dependency_tree(
    file_path=Path("src/models.py"),
    entity_name="UserModel", 
    entity_type="class"
)
```

## 🎯 Common Use Cases

- **🔄 Refactoring** - Break down monolithic files into manageable modules
- **📊 Quality Assessment** - Analyze code metrics and documentation coverage
- **🔍 Impact Analysis** - Understand what will break before making changes
- **📚 Code Documentation** - Generate architectural insights and dependency maps
- **🚀 Legacy Modernization** - Safely extract and reorganize legacy codebases
- **🏗️ Architecture Planning** - Visualize and plan code structure improvements

## 🏗️ Architecture

Built with **clean architecture principles**:
- **Factory Pattern** for service creation
- **AST-based parsing** for accurate code analysis
- **Dependency injection** for component coordination
- **Modular design** with clear separation of concerns

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.
