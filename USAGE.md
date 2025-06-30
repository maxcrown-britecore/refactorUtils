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

### 3. Dependency Tree Service

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
```

#### Output Options
```bash
# Save to file
codebase-deps src/models/user.py User class --output user_dependencies.txt

# Show only upstream dependencies
codebase-deps src/models/user.py User class --upstream-only

# Show only downstream dependencies
codebase-deps src/models/user.py User class --downstream-only
```

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