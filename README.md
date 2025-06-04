# Codebase Services

A comprehensive Python tool for **codebase analysis and code extraction** that helps you refactor large Python files and generate insightful reports about your code structure.

## 🚀 Main Features

Based on the factory functions in `main.py`, this project provides two core services:

### 1. **Code Extraction Service** (`create_extractor()`)
Intelligently extracts functions and classes from Python files into separate, well-organized modules.

**Key Capabilities:**
- 🔍 **AST-based parsing** - Uses Python's Abstract Syntax Tree for accurate code analysis
- 📦 **Smart import resolution** - Automatically determines and includes required imports
- 🔗 **Dependency management** - Resolves internal dependencies between extracted entities
- ⚡ **Import optimization** - Generates clean, optimized import statements
- 📁 **File organization** - Creates properly structured modules with `__init__.py` files

**Perfect for:**
- Breaking down large, monolithic Python files
- Modularizing legacy codebases
- Creating clean, maintainable code structure

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

## 🎯 Use Cases

### **Code Refactoring**
```python
extractor = create_extractor()
result = extractor.extract_code_entities(
    source_file=Path("large_file.py"),
    entity_names=["MyClass", "helper_function"]
)
```

### **Codebase Analysis**
```python
reporter = create_report_service()
df = reporter.generate_code_report(Path("my_module.py"))
stats = reporter.get_summary_statistics(df)
```

## 🔧 Core Philosophy

This tool treats code transformation like a **well-organized kitchen**:
- **Extraction Service** = The chef who carefully separates ingredients into organized containers
- **Report Service** = The inventory manager who provides detailed reports about what's in stock
- **Core Components** = The specialized tools that make both processes efficient and reliable

Each service is assembled from specialized components, ensuring reliability, maintainability, and extensibility.
