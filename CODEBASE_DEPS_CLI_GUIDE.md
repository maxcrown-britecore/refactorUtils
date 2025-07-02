# 🔍 Codebase Dependencies CLI Guide (`codebase-deps`)

A comprehensive command-line tool for analyzing and visualizing dependencies in Python codebases. The `codebase-deps` CLI helps you understand how your code entities (functions, classes, modules) are interconnected through dependency relationships.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Command Syntax](#-command-syntax)
- [Arguments](#-arguments)
- [Output Formats](#-output-formats)
- [Usage Examples](#-usage-examples)
- [Advanced Use Cases](#-advanced-use-cases)
- [Output Interpretation](#-output-interpretation)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

```bash
# Analyze dependencies for a function
codebase-deps src/mymodule.py calculate_total function

# Generate an interactive HTML graph
codebase-deps src/mymodule.py UserManager class --format interactive

# Show only what depends ON your target (downstream)
codebase-deps src/utils.py helper_function function --downstream-only

# Limit analysis depth and save to file
codebase-deps src/core.py DatabaseManager class --max-depth 3 --output deps_report.txt
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- `codebase_services` package installed

### Install Package
```bash
# From Git repository
pip install git+ssh://git@github.com/maxcrown-britecore/codebase_services.git

# For development
git clone https://github.com/maxcrown-britecore/codebase_services.git
cd codebase_services
pip install -e .
```

### Verify Installation
```bash
codebase-deps --help
```

## 📝 Command Syntax

```bash
codebase-deps <file_path> <entity_name> <entity_type> [OPTIONS]
```

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `file_path` | Path to Python file containing the target entity | `src/models.py` |
| `entity_name` | Name of the entity to analyze | `UserManager` |
| `entity_type` | Type of entity: `function`, `class`, or `module` | `class` |

### Optional Arguments

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--max-depth` | `-d` | Maximum depth to traverse | Unlimited |
| `--codebase-root` | `-r` | Root directory to scan for dependencies | Parent of file_path |
| `--format` | `-f` | Output format (see formats below) | `tree` |
| `--output` | `-o` | Output file to save results | Print to console |
| `--upstream-only` | | Show only upstream dependencies (what target depends on) | Show both |
| `--downstream-only` | | Show only downstream dependencies (what depends on target) | Show both |

## 📊 Output Formats

### 1. `tree` (Default)
Hierarchical tree view showing dependency relationships.

```bash
codebase-deps src/models.py UserManager class --format tree
```

**Output Example:**
```
🎯 DEPENDENCY TREE FOR: UserManager (class)
📁 File: src/models.py:45-120

🔼 UPSTREAM DEPENDENCIES (what UserManager depends on):
├── DatabaseConnection (class) [internal_reference]
│   📁 src/database.py:15-45
├── validate_email (function) [external_reference]
│   📁 src/validators.py:10-25
└── logging (module) [import]
    📁 <built-in>

🔽 DOWNSTREAM DEPENDENCIES (what depends on UserManager):
├── UserService (class) [instantiation]
│   📁 src/services.py:30-80
│   └── APIController (class) [function_call]
│       📁 src/api.py:100-150
└── test_user_manager (function) [import]
    📁 tests/test_models.py:5-25
```

### 2. `graph`
NetworkX graph representation with nodes and edges.

```bash
codebase-deps src/models.py UserManager class --format graph
```

**Output Example:**
```
📊 Dependency Graph for: UserManager (class)
Nodes: 8
Edges: 12

Edges:
  UserManager -> DatabaseConnection
  UserManager -> validate_email
  UserService -> UserManager
  APIController -> UserService
```

### 3. `list`
Simple numbered list of all dependencies.

```bash
codebase-deps src/models.py UserManager class --format list
```

**Output Example:**
```
📋 All Dependencies for: UserManager (class)
==================================================
 1. DatabaseConnection (class) - internal_reference
    📁 src/database.py:15
 2. validate_email (function) - external_reference
    📁 src/validators.py:10
 3. UserService (class) - instantiation
    📁 src/services.py:30
```

### 4. `df`
Pandas DataFrame format (useful for data analysis).

```bash
codebase-deps src/models.py UserManager class --format df --output deps.csv
```

**Output:** CSV file with columns:
- `name`, `entity_type`, `file_path`, `line_start`, `line_end`
- `dependency_type`, `depth`, `parent_node_id`, `node_id`

### 5. `paths`
Detailed path analysis showing dependency chains.

```bash
codebase-deps src/models.py UserManager class --format paths
```

**Output Example:**
```
🛤️ DEPENDENCY PATHS for UserManager:

Path 1: UserManager → DatabaseConnection → ConnectionPool
  Depth: 2, Type: internal_reference → external_reference

Path 2: UserManager ← UserService ← APIController ← WebApp
  Depth: 3, Type: instantiation ← function_call ← inheritance
```

### 6. `depths`
Analysis grouped by dependency depth levels.

```bash
codebase-deps src/models.py UserManager class --format depths
```

**Output Example:**
```
📊 Dependency Depth Analysis for: UserManager (class)
============================================================

🔍 Depth 0: 1 dependencies
   1. UserManager [target]
      Path: 
      File: src/models.py:45

🔍 Depth 1: 3 dependencies
   1. DatabaseConnection [internal_reference]
      Path: UserManager
      File: src/database.py:15
   2. validate_email [external_reference]
      Path: UserManager
      File: src/validators.py:10
   ... and 1 more at depth 1

🔍 Depth 2: 5 dependencies
   1. ConnectionPool [external_reference]
      Path: UserManager → DatabaseConnection
      File: src/pool.py:20
   ... and 4 more at depth 2
```

### 7. `interactive`
Generates an interactive HTML graph visualization.

```bash
codebase-deps src/models.py UserManager class --format interactive --output user_deps.html
```

**Output Example:**
```
🎯 Interactive dependency graph generated!
📄 File: user_deps.html
🌐 Open in browser to view interactive visualization

Graph includes:
  • Target: UserManager (class)
  • Total dependencies: 15
  • Maximum depth: 4
```

## 💡 Usage Examples

### Basic Analysis

```bash
# Analyze a function's dependencies
codebase-deps src/utils.py calculate_tax function

# Analyze a class with limited depth
codebase-deps src/models.py User class --max-depth 2

# Analyze from a different root directory
codebase-deps lib/core.py Parser class --codebase-root /path/to/project
```

### Directional Analysis

```bash
# What does my function depend on? (upstream only)
codebase-deps src/services.py process_payment function --upstream-only

# What depends on my class? (downstream only)
codebase-deps src/models.py User class --downstream-only

# Full bidirectional analysis (default)
codebase-deps src/core.py Engine class
```

### Output Management

```bash
# Save tree view to file
codebase-deps src/api.py APIHandler class --output api_deps.txt

# Generate CSV for data analysis
codebase-deps src/models.py User class --format df --output user_deps.csv

# Create interactive visualization
codebase-deps src/core.py MainEngine class --format interactive --output engine_graph.html
```

### Complex Analysis

```bash
# Deep analysis with path tracking
codebase-deps src/complex.py Algorithm class --max-depth 5 --format paths

# Depth-based analysis for large codebases
codebase-deps src/main.py Application class --format depths --max-depth 3

# Upstream-only analysis with graph format
codebase-deps src/db.py DatabaseManager class --upstream-only --format graph
```

## 🎯 Advanced Use Cases

### 1. Refactoring Planning
```bash
# Find what will break if you change a core class
codebase-deps src/core.py BaseModel class --downstream-only --format list

# Understand dependencies before extracting a function
codebase-deps src/utils.py complex_calculation function --format tree --max-depth 2
```

### 2. Code Review and Architecture Analysis
```bash
# Generate interactive graph for code review
codebase-deps src/services.py PaymentService class --format interactive

# Analyze coupling depth
codebase-deps src/models.py User class --format depths --max-depth 4
```

### 3. Testing Strategy
```bash
# Find all code that needs testing when you change a function
codebase-deps src/core.py validate_input function --downstream-only --format list

# Understand test dependencies
codebase-deps tests/test_models.py TestUser class --format tree
```

### 4. Documentation Generation
```bash
# Generate dependency documentation
codebase-deps src/api.py RestAPI class --format df --output api_dependencies.csv

# Create visual documentation
codebase-deps src/main.py Application class --format interactive --output app_architecture.html
```

### 5. Migration and Modernization
```bash
# Analyze legacy code dependencies
codebase-deps legacy/old_system.py LegacyProcessor class --format paths --max-depth 3

# Plan microservice extraction
codebase-deps src/monolith.py UserModule class --downstream-only --format tree
```

## 📖 Output Interpretation

### Dependency Types

| Type | Description | Example |
|------|-------------|---------|
| `target` | The entity you're analyzing | Your specified function/class |
| `internal_reference` | Reference within the same file | Function calls same-file function |
| `external_reference` | Reference in different file | Imports from another module |
| `inheritance` | Class inheritance relationship | `class Child(Parent)` |
| `import` | Direct import statement | `import module` or `from module import name` |
| `function_call` | Function/method call | `my_function()` |
| `instantiation` | Class instantiation | `obj = MyClass()` |
| `attribute_access` | Attribute or method access | `obj.method()` or `obj.attribute` |
| `name_reference` | General name reference | Variable usage |

### Depth Levels

- **Depth 0**: Your target entity
- **Depth 1**: Direct dependencies/dependents
- **Depth 2**: Dependencies of dependencies
- **Depth N**: N levels of separation from target

### Direction Indicators

- **🔼 UPSTREAM**: What your target depends on (imports, calls, etc.)
- **🔽 DOWNSTREAM**: What depends on your target (is imported by, called by, etc.)

## 🔧 Troubleshooting

### Common Issues

#### 1. Entity Not Found
```bash
❌ Error: Entity 'MyClass' of type 'class' not found in src/models.py
```

**Solutions:**
- Check entity name spelling and case sensitivity
- Verify the entity type (`function`, `class`, `module`)
- Ensure the file path is correct
- Check if entity is nested (not supported for top-level analysis)

#### 2. No Dependencies Found
```bash
# Output shows empty dependency tree
```

**Possible Causes:**
- Entity has no dependencies (rare)
- Codebase root is too narrow
- Entity uses only built-in functions
- Syntax errors in source files

**Solutions:**
```bash
# Expand codebase root
codebase-deps src/models.py MyClass class --codebase-root /entire/project

# Check for syntax errors
python -m py_compile src/models.py
```

#### 3. Visualization Dependencies Missing
```bash
❌ ImportError: networkx and pyvis are required for graph visualization
```

**Solution:**
```bash
pip install networkx pyvis
```

#### 4. Large Output / Performance Issues
```bash
# Very large dependency trees
```

**Solutions:**
```bash
# Limit depth
codebase-deps src/models.py MyClass class --max-depth 3

# Focus on one direction
codebase-deps src/models.py MyClass class --upstream-only

# Use more efficient formats
codebase-deps src/models.py MyClass class --format list
```

### File Permission Issues
```bash
# If output file cannot be created
codebase-deps src/models.py MyClass class --output /readonly/path/deps.txt
```

**Solution:**
- Ensure write permissions for output directory
- Use relative paths or home directory
- Check disk space

### Syntax Error Handling
The tool gracefully handles files with syntax errors by:
- Skipping problematic files
- Continuing analysis with remaining files
- Reporting which files were skipped

### Performance Tips

1. **Use appropriate depth limits** for large codebases
2. **Specify narrow codebase roots** when possible
3. **Use `--upstream-only` or `--downstream-only`** to reduce analysis scope
4. **Save large outputs to files** instead of printing to console

## 📚 Integration Examples

### With Other Tools

#### Git Hooks
```bash
#!/bin/bash
# Pre-commit hook to check critical dependencies
codebase-deps src/core.py CriticalClass class --downstream-only --format list > deps_check.txt
```

#### CI/CD Pipeline
```bash
# Generate dependency documentation
codebase-deps src/main.py Application class --format interactive --output docs/architecture.html
```

#### Code Review Process
```bash
# Analyze impact of changes
codebase-deps src/modified_file.py ChangedClass class --downstream-only --format tree
```

---

## 🎉 Conclusion

The `codebase-deps` CLI is a powerful tool for understanding code relationships and planning refactoring efforts. Use it to:

- **🔍 Analyze** dependencies before making changes
- **📊 Visualize** code architecture
- **📋 Document** system relationships
- **🛠️ Plan** refactoring and modernization efforts
- **🧪 Design** comprehensive testing strategies

For more advanced usage and Python library integration, see the main [USAGE.md](USAGE.md) documentation.

**Happy dependency analysis!** 🚀