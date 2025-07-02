# 📊 Codebase Report CLI Guide (`codebase-report`)

A powerful command-line tool for generating analytical reports about Python code structure and metrics. The `codebase-report` CLI helps you understand your codebase composition, documentation coverage, code complexity, and overall project health through detailed data analysis.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Command Syntax](#-command-syntax)
- [Arguments](#-arguments)
- [Output Formats](#-output-formats)
- [Usage Examples](#-usage-examples)
- [Report Data Columns](#-report-data-columns)
- [Analysis Scenarios](#-analysis-scenarios)
- [Data Analysis Workflows](#-data-analysis-workflows)
- [Integration Examples](#-integration-examples)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

```bash
# Analyze a single Python file
codebase-report src/models.py

# Analyze an entire directory
codebase-report src/

# Get just summary statistics
codebase-report src/ --summary-only

# Export detailed report to CSV
codebase-report src/ --format csv --output project_analysis.csv

# Generate JSON report for data processing
codebase-report src/services/ --format json --output services_report.json
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- `codebase_services` package installed
- `pandas` library (automatically installed with the package)

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
codebase-report --help
```

## 📝 Command Syntax

```bash
codebase-report <source> [OPTIONS]
```

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `source` | Python file or directory to analyze | `src/models.py` or `src/` |

### Optional Arguments

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--output` | `-o` | Output file for the report | Print to console |
| `--summary-only` | `-s` | Show only summary statistics | Show full report |
| `--format` | `-f` | Output format: `table`, `csv`, `json` | `table` |

## 📊 Output Formats

### 1. `table` (Default)
Human-readable table format with summary statistics.

```bash
codebase-report src/models.py --format table
```

**Output Example:**
```
📋 Code Structure Report
==================================================
        name entity_type  line_start  line_end  total_lines                source_file  code_length  has_docstring internal_dependencies  internal_dependencies_count
   UserModel       class           5        45           41  /path/to/src/models.py          892           True         [validate_email]                            1
validate_email    function          47        55            9  /path/to/src/models.py          156           True                     []                            0
   save_user    function          57        75           19  /path/to/src/models.py          324          False            [UserModel]                            1

📊 Summary Statistics:
------------------------------
Total Entities: 3
Functions Count: 2
Classes Count: 1
Files Analyzed: 1
Avg Code Length: 457.3
Entities With Docstrings: 2
Docstring Percentage: 66.67
```

### 2. `csv`
Comma-separated values format for data analysis.

```bash
codebase-report src/ --format csv --output analysis.csv
```

**Output:** CSV file with all entity data suitable for Excel, pandas, or other data analysis tools.

### 3. `json`
JSON format for programmatic processing.

```bash
codebase-report src/ --format json --output report.json
```

**Output Example:**
```json
[
  {
    "name": "UserModel",
    "entity_type": "class",
    "line_start": 5,
    "line_end": 45,
    "total_lines": 41,
    "source_file": "/path/to/src/models.py",
    "code_length": 892,
    "has_docstring": true,
    "internal_dependencies": ["validate_email"],
    "internal_dependencies_count": 1
  }
]
```

## 💡 Usage Examples

### Single File Analysis

```bash
# Basic analysis of a Python file
codebase-report src/utils.py

# Get only summary for quick overview
codebase-report src/models.py --summary-only

# Export detailed analysis to CSV
codebase-report src/services.py --format csv --output services_analysis.csv
```

### Directory Analysis

```bash
# Analyze entire source directory
codebase-report src/

# Analyze with specific output file
codebase-report src/ --output project_report.csv

# Get project overview with summary only
codebase-report . --summary-only

# Analyze subdirectory
codebase-report src/core/ --format json --output core_analysis.json
```

### Comparative Analysis

```bash
# Analyze different modules separately
codebase-report src/models/ --output models_report.csv
codebase-report src/services/ --output services_report.csv
codebase-report src/utils/ --output utils_report.csv

# Analyze entire project
codebase-report src/ --output full_project_report.csv
```

### Quick Health Checks

```bash
# Quick project health check
codebase-report src/ --summary-only

# Check specific module documentation
codebase-report src/api/ --summary-only

# Verify test coverage structure
codebase-report tests/ --summary-only
```

## 📋 Report Data Columns

The generated reports include the following columns:

| Column | Type | Description |
|--------|------|-------------|
| `name` | string | Name of the function or class |
| `entity_type` | string | Type: `function` or `class` |
| `line_start` | integer | Starting line number in source file |
| `line_end` | integer | Ending line number in source file |
| `total_lines` | integer | Total lines of code for the entity |
| `source_file` | string | Full path to the source file |
| `code_length` | integer | Character count of the entity's source code |
| `has_docstring` | boolean | Whether the entity has a docstring |
| `internal_dependencies` | list | Names of other entities this one depends on |
| `internal_dependencies_count` | integer | Count of internal dependencies |

### Summary Statistics

| Statistic | Description |
|-----------|-------------|
| `total_entities` | Total number of functions and classes found |
| `functions_count` | Number of functions |
| `classes_count` | Number of classes |
| `files_analyzed` | Number of Python files processed |
| `avg_code_length` | Average character count per entity |
| `entities_with_docstrings` | Number of documented entities |
| `docstring_percentage` | Percentage of entities with documentation |

## 🎯 Analysis Scenarios

### 1. Code Quality Assessment

```bash
# Get overall project health
codebase-report src/ --summary-only

# Detailed analysis for quality metrics
codebase-report src/ --format csv --output quality_assessment.csv
```

**What to look for:**
- **Documentation coverage** < 70% indicates poor documentation
- **Average code length** > 500 characters may indicate complex functions
- **High dependency counts** suggest tight coupling

### 2. Documentation Audit

```bash
# Check documentation coverage
codebase-report src/ --summary-only

# Export for detailed documentation analysis
codebase-report src/ --format csv --output doc_audit.csv
```

**Analysis workflow:**
1. Check `docstring_percentage` in summary
2. Filter CSV for `has_docstring == False`
3. Prioritize documenting classes and long functions

### 3. Refactoring Planning

```bash
# Analyze before refactoring
codebase-report src/legacy/ --format csv --output before_refactor.csv

# Analyze after refactoring
codebase-report src/refactored/ --format csv --output after_refactor.csv
```

**Metrics to compare:**
- Reduction in average code length
- Decrease in internal dependencies
- Improvement in documentation coverage

### 4. Module Complexity Analysis

```bash
# Compare complexity across modules
codebase-report src/models/ --output models_complexity.csv
codebase-report src/services/ --output services_complexity.csv
codebase-report src/utils/ --output utils_complexity.csv
```

**Complexity indicators:**
- High `total_lines` per entity
- High `internal_dependencies_count`
- Low `docstring_percentage`

### 5. Technical Debt Assessment

```bash
# Generate comprehensive technical debt report
codebase-report src/ --format json --output tech_debt_analysis.json
```

**Technical debt indicators:**
- Functions > 50 lines
- Classes > 200 lines
- Entities without docstrings
- High coupling (many dependencies)

## 📈 Data Analysis Workflows

### Workflow 1: Project Health Dashboard

```bash
# Step 1: Generate comprehensive report
codebase-report src/ --format csv --output project_health.csv

# Step 2: Get summary metrics
codebase-report src/ --summary-only > health_summary.txt

# Step 3: Analyze specific modules
codebase-report src/core/ --summary-only
codebase-report src/api/ --summary-only
codebase-report src/utils/ --summary-only
```

**Analysis with pandas:**
```python
import pandas as pd

# Load the report
df = pd.read_csv('project_health.csv')

# Find large functions (potential refactoring candidates)
large_functions = df[(df['entity_type'] == 'function') & (df['total_lines'] > 50)]

# Find undocumented entities
undocumented = df[df['has_docstring'] == False]

# Calculate complexity metrics
complexity_by_file = df.groupby('source_file').agg({
    'total_lines': 'mean',
    'internal_dependencies_count': 'mean',
    'has_docstring': 'mean'
})
```

### Workflow 2: Documentation Coverage Analysis

```bash
# Generate documentation report
codebase-report src/ --format json --output doc_coverage.json
```

**Analysis script:**
```python
import json
import pandas as pd

# Load JSON report
with open('doc_coverage.json', 'r') as f:
    data = json.load(f)

df = pd.DataFrame(data)

# Documentation coverage by file
doc_by_file = df.groupby('source_file')['has_docstring'].agg(['count', 'sum', 'mean'])
doc_by_file.columns = ['total_entities', 'documented', 'coverage_rate']

# Find files with poor documentation
poor_docs = doc_by_file[doc_by_file['coverage_rate'] < 0.5]
print("Files needing documentation attention:")
print(poor_docs)
```

### Workflow 3: Complexity Trend Analysis

```bash
# Analyze different versions or branches
git checkout main
codebase-report src/ --format csv --output main_analysis.csv

git checkout feature-branch
codebase-report src/ --format csv --output feature_analysis.csv
```

**Comparison analysis:**
```python
import pandas as pd

main_df = pd.read_csv('main_analysis.csv')
feature_df = pd.read_csv('feature_analysis.csv')

# Compare metrics
main_stats = {
    'avg_lines': main_df['total_lines'].mean(),
    'avg_deps': main_df['internal_dependencies_count'].mean(),
    'doc_coverage': main_df['has_docstring'].mean()
}

feature_stats = {
    'avg_lines': feature_df['total_lines'].mean(),
    'avg_deps': feature_df['internal_dependencies_count'].mean(),
    'doc_coverage': feature_df['has_docstring'].mean()
}

print("Complexity changes:")
for metric in main_stats:
    change = feature_stats[metric] - main_stats[metric]
    print(f"{metric}: {change:+.2f}")
```

### Workflow 4: Code Review Preparation

```bash
# Analyze changed files for code review
codebase-report src/modified_module.py --format table
codebase-report src/new_feature/ --summary-only
```

**Review checklist generation:**
```python
import pandas as pd

df = pd.read_csv('review_analysis.csv')

# Generate review checklist
checklist = []

# Check for large functions
large_funcs = df[(df['entity_type'] == 'function') & (df['total_lines'] > 30)]
if not large_funcs.empty:
    checklist.append(f"Review {len(large_funcs)} large functions for complexity")

# Check documentation
undocumented = df[df['has_docstring'] == False]
if not undocumented.empty:
    checklist.append(f"Add documentation to {len(undocumented)} entities")

# Check coupling
high_coupling = df[df['internal_dependencies_count'] > 3]
if not high_coupling.empty:
    checklist.append(f"Review {len(high_coupling)} highly coupled entities")

print("Code Review Checklist:")
for item in checklist:
    print(f"- {item}")
```

## 🔗 Integration Examples

### CI/CD Pipeline Integration

#### GitHub Actions Example
```yaml
name: Code Quality Analysis
on: [push, pull_request]

jobs:
  code-analysis:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: 3.9
    
    - name: Install dependencies
      run: |
        pip install codebase_services
    
    - name: Generate code report
      run: |
        codebase-report src/ --format json --output code_analysis.json
        codebase-report src/ --summary-only > code_summary.txt
    
    - name: Upload analysis results
      uses: actions/upload-artifact@v2
      with:
        name: code-analysis
        path: |
          code_analysis.json
          code_summary.txt
```

#### Quality Gate Script
```bash
#!/bin/bash
# quality_gate.sh - Fail build if quality metrics are below threshold

codebase-report src/ --format json --output quality_check.json

# Extract metrics using jq
TOTAL_ENTITIES=$(jq length quality_check.json)
DOCUMENTED=$(jq '[.[] | select(.has_docstring == true)] | length' quality_check.json)
DOC_PERCENTAGE=$(echo "scale=2; $DOCUMENTED * 100 / $TOTAL_ENTITIES" | bc)

echo "Documentation coverage: $DOC_PERCENTAGE%"

# Fail if documentation coverage is below 70%
if (( $(echo "$DOC_PERCENTAGE < 70" | bc -l) )); then
    echo "❌ Documentation coverage below 70% threshold"
    exit 1
fi

echo "✅ Quality gate passed"
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Analyze staged Python files
STAGED_FILES=$(git diff --cached --name-only --diff-filter=ACM | grep '\.py$')

if [ ! -z "$STAGED_FILES" ]; then
    echo "🔍 Analyzing staged Python files..."
    
    for file in $STAGED_FILES; do
        echo "Analyzing $file..."
        codebase-report "$file" --summary-only
    done
    
    echo "📊 Full project analysis:"
    codebase-report src/ --summary-only
fi
```

### Development Workflow Integration

#### VS Code Task
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Analyze Current File",
            "type": "shell",
            "command": "codebase-report",
            "args": ["${file}", "--format", "table"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            }
        },
        {
            "label": "Project Health Check",
            "type": "shell",
            "command": "codebase-report",
            "args": ["src/", "--summary-only"],
            "group": "build"
        }
    ]
}
```

#### Makefile Integration
```makefile
.PHONY: analyze analyze-summary analyze-export

analyze:
	@echo "📊 Generating code analysis report..."
	codebase-report src/ --format table

analyze-summary:
	@echo "📋 Project health summary:"
	codebase-report src/ --summary-only

analyze-export:
	@echo "💾 Exporting detailed analysis..."
	codebase-report src/ --format csv --output reports/code_analysis_$(shell date +%Y%m%d).csv
	codebase-report src/ --format json --output reports/code_analysis_$(shell date +%Y%m%d).json
	@echo "✅ Reports saved to reports/ directory"

quality-check: analyze-summary
	@echo "🔍 Running quality checks..."
	@python scripts/quality_gate.py reports/code_analysis_$(shell date +%Y%m%d).json
```

## 🔧 Troubleshooting

### Common Issues

#### 1. No Python Files Found
```bash
❌ Error: No Python files found in directory
```

**Causes & Solutions:**
- **Empty directory**: Verify the directory contains `.py` files
- **Wrong path**: Check the directory path is correct
- **Hidden files**: Ensure Python files aren't hidden or in subdirectories

```bash
# Check directory contents
ls -la src/
find src/ -name "*.py" -type f
```

#### 2. Source Path Does Not Exist
```bash
❌ Error: Source path does not exist
```

**Solutions:**
```bash
# Verify path exists
ls -la src/models.py

# Use absolute path if needed
codebase-report /full/path/to/src/models.py

# Check current directory
pwd
ls -la
```

#### 3. Permission Denied for Output File
```bash
❌ Error: Permission denied: /readonly/path/report.csv
```

**Solutions:**
```bash
# Use writable directory
codebase-report src/ --output ~/reports/analysis.csv

# Check permissions
ls -la /path/to/output/directory/

# Create directory if needed
mkdir -p reports/
codebase-report src/ --output reports/analysis.csv
```

#### 4. Syntax Errors in Source Files
```bash
Warning: Skipping /path/to/file.py: Invalid Python syntax
```

**Handling:**
- The tool automatically skips files with syntax errors
- Check which files were skipped in the output
- Fix syntax errors in problematic files

```bash
# Check syntax manually
python -m py_compile src/problematic_file.py

# Use Python's AST to validate
python -c "import ast; ast.parse(open('src/file.py').read())"
```

#### 5. Large Output Truncation
```bash
# Very large reports may be truncated in terminal
```

**Solutions:**
```bash
# Always save large reports to files
codebase-report large_project/ --format csv --output large_analysis.csv

# Use summary for quick overview
codebase-report large_project/ --summary-only

# Analyze subdirectories separately
codebase-report src/module1/ --output module1_analysis.csv
codebase-report src/module2/ --output module2_analysis.csv
```

### Performance Optimization

#### For Large Codebases
```bash
# Analyze specific subdirectories instead of entire project
codebase-report src/core/ --output core_analysis.csv
codebase-report src/api/ --output api_analysis.csv

# Use summary-only for quick checks
codebase-report large_project/ --summary-only

# Export to files to avoid terminal limitations
codebase-report src/ --format csv --output analysis.csv
```

#### Memory Management
```bash
# For very large projects, analyze in chunks
find src/ -name "*.py" | head -100 | xargs -I {} dirname {} | sort -u | while read dir; do
    codebase-report "$dir" --output "analysis_$(basename $dir).csv"
done
```

### Data Quality Issues

#### Empty Reports
```bash
# If report shows no entities
```

**Possible causes:**
- Files contain only imports/constants
- Syntax errors preventing parsing
- Files are empty or contain only comments

**Verification:**
```bash
# Check file contents
head -20 src/empty_file.py

# Verify file has functions/classes
grep -n "^def\|^class" src/file.py
```

#### Incorrect Metrics
```bash
# If metrics seem wrong
```

**Debugging:**
```bash
# Analyze single file to verify
codebase-report src/specific_file.py --format table

# Check specific entities manually
grep -n "def\|class" src/specific_file.py

# Verify line counts
wc -l src/specific_file.py
```

## 📚 Advanced Usage Patterns

### Automated Reporting Pipeline

```bash
#!/bin/bash
# automated_analysis.sh - Complete analysis pipeline

DATE=$(date +%Y%m%d_%H%M%S)
REPORT_DIR="reports/$DATE"

mkdir -p "$REPORT_DIR"

echo "🔍 Starting comprehensive code analysis..."

# Generate all format reports
codebase-report src/ --format csv --output "$REPORT_DIR/detailed_analysis.csv"
codebase-report src/ --format json --output "$REPORT_DIR/analysis_data.json"
codebase-report src/ --summary-only > "$REPORT_DIR/summary.txt"

# Analyze by module
for module in src/*/; do
    if [ -d "$module" ]; then
        module_name=$(basename "$module")
        codebase-report "$module" --format csv --output "$REPORT_DIR/${module_name}_analysis.csv"
    fi
done

echo "✅ Analysis complete. Reports saved to $REPORT_DIR"
```

### Quality Metrics Dashboard

```python
#!/usr/bin/env python3
# quality_dashboard.py - Generate HTML quality dashboard

import pandas as pd
import json
from pathlib import Path

def generate_dashboard(analysis_file):
    """Generate HTML dashboard from analysis data."""
    
    with open(analysis_file, 'r') as f:
        data = json.load(f)
    
    df = pd.DataFrame(data)
    
    # Calculate metrics
    total_entities = len(df)
    doc_coverage = df['has_docstring'].mean() * 100
    avg_complexity = df['total_lines'].mean()
    
    # Generate HTML
    html = f"""
    <html>
    <head><title>Code Quality Dashboard</title></head>
    <body>
        <h1>Code Quality Dashboard</h1>
        <div>
            <h2>Summary Metrics</h2>
            <p>Total Entities: {total_entities}</p>
            <p>Documentation Coverage: {doc_coverage:.1f}%</p>
            <p>Average Complexity: {avg_complexity:.1f} lines</p>
        </div>
        <div>
            <h2>Detailed Analysis</h2>
            {df.to_html(index=False)}
        </div>
    </body>
    </html>
    """
    
    with open('quality_dashboard.html', 'w') as f:
        f.write(html)
    
    print("📊 Dashboard generated: quality_dashboard.html")

if __name__ == "__main__":
    generate_dashboard('analysis_data.json')
```

---

## 🎉 Conclusion

The `codebase-report` CLI is an essential tool for understanding and maintaining code quality. Use it to:

- **📊 Monitor** project health and complexity trends
- **📋 Assess** documentation coverage and quality
- **🔍 Identify** refactoring opportunities
- **📈 Track** code metrics over time
- **🛠️ Support** code review and quality assurance processes
- **📚 Generate** data for technical debt analysis

The tool integrates seamlessly into development workflows, CI/CD pipelines, and quality assurance processes, providing actionable insights for maintaining high-quality codebases.

For more advanced usage and Python library integration, see the main [USAGE.md](USAGE.md) documentation.

**Happy code analysis!** 🚀