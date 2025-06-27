# Codebase Services

A comprehensive Python tool for **codebase analysis and code extraction** that helps you refactor large Python files and generate insightful reports about your code structure.

## 🚀 Main Features

Based on the factory functions in `main.py`, this project provides two core services:

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
- **Core Components** = The specialized tools that make both processes efficient and reliable

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
