# ✂️ Codebase Extract CLI Guide (`codebase-extract`)

A powerful command-line tool for extracting and refactoring Python code entities (functions and classes) from large files into well-organized, modular structures. The `codebase-extract` CLI helps you break down monolithic Python files, reorganize code architecture, and maintain clean import dependencies.

## 📋 Table of Contents

- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Command Syntax](#-command-syntax)
- [Arguments](#-arguments)
- [Extraction Modes](#-extraction-modes)
- [Usage Examples](#-usage-examples)
- [Advanced Features](#-advanced-features)
- [Refactoring Workflows](#-refactoring-workflows)
- [Best Practices](#-best-practices)
- [Integration Examples](#-integration-examples)
- [Troubleshooting](#-troubleshooting)

## 🚀 Quick Start

```bash
# Extract all functions and classes to separate files
codebase-extract src/large_module.py

# Extract specific entities only
codebase-extract src/models.py --entities UserModel,validate_email

# Move entities to a single target file
codebase-extract src/utils.py --entities helper_func,calculate_tax --target-file src/math_utils.py

# Extract and remove from source (cut mode)
codebase-extract src/legacy.py --entities OldClass --mode cut

# Extract with safe wrapper (preserves function signature)
codebase-extract src/legacy.py --entities helper_function --mode safe

# Extract with custom header and Python 2 compatibility
codebase-extract src/core.py --entities CoreEngine --py2-import --custom-block "# Extracted from core module"
```

## 📦 Installation

### Prerequisites
- Python 3.8+
- `codebase_services` package installed
- Write permissions in target directories

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
codebase-extract --help
```

## 📝 Command Syntax

```bash
codebase-extract <source_file> [OPTIONS]
```

### Required Arguments

| Argument | Description | Example |
|----------|-------------|---------|
| `source_file` | Python file to extract entities from | `src/models.py` |

### Optional Arguments

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--entities` | `-e` | Comma-separated names of specific entities to extract | Extract all |
| `--target-folder` | `-t` | Target folder or file path for extracted entities | Create separate files |
| `--mode` | `-m` | Extraction mode: `copy`, `cut`, or `safe` | `copy` |
| `--py2-import` | | Add Python 2 compatibility imports | No compatibility imports |
| `--custom-block` | | Custom comment block to add to extracted files | No custom block |
| `--root-prefix` | | Root path prefix for import statements | Auto-detect |

## 🔄 Extraction Modes

### 1. **Copy Mode** (Default: `--mode copy`)
Creates new files while leaving the original entities intact in the source file.

```bash
codebase-extract src/models.py --entities UserModel ProductModel --mode copy
# or simply:
codebase-extract src/models.py --entities UserModel ProductModel
```

**Result:**
```
src/
├── models.py          # Original file (unchanged)
├── UserModel.py       # New file with UserModel class
├── ProductModel.py    # New file with ProductModel class
└── __init__.py        # Updated with imports
```

### 2. **Cut Mode** (`--mode cut`)
Removes entities from source file after extraction (destructive).

```bash
codebase-extract src/legacy.py --entities OldClass deprecated_func --mode cut
```

**Result:**
```
src/
├── legacy.py          # Modified: OldClass and deprecated_func removed
├── OldClass.py        # New file with OldClass
└── deprecated_func.py # New file with deprecated_func
```

### 3. **Safe Mode** (`--mode safe`) ⭐ New!
Replaces entities in source with import wrappers, maintaining backward compatibility.

```bash
codebase-extract src/utils.py --entities helper_function --mode safe
```

**Original `src/utils.py`:**
```python
def helper_function(arg1, arg2="default"):
    """Original implementation."""
    return f"processing {arg1} with {arg2}"
```

**After safe extraction:**

**`src/helper_function.py`:** (extracted)
```python
def helper_function(arg1, arg2="default"):
    """Original implementation."""
    return f"processing {arg1} with {arg2}"
```

**`src/utils.py`:** (wrapper)
```python
def helper_function(arg1, arg2="default"):
    from .helper_function import helper_function
    return helper_function(arg1, arg2)
```

This allows existing code to continue working unchanged while the implementation is moved to a separate file.

### 4. **Target Folder/File Combinations**
All modes work with target folder specification:

```bash
# Copy to specific directory
codebase-extract src/models.py --entities User --target-folder models/ --mode copy

# Cut and move to specific file
codebase-extract src/monolith.py --entities ServiceA ServiceB --target-folder services/core.py --mode cut

# Safe extraction to organized structure
codebase-extract src/legacy.py --entities helper_func --target-folder utils/helpers.py --mode safe
```

## 💡 Usage Examples

### Basic Extraction

```bash
# Extract all entities to separate files
codebase-extract src/large_file.py

# Extract specific functions
codebase-extract src/utils.py --entities calculate_tax format_currency

# Extract specific classes
codebase-extract src/models.py --entities User Product Order
```

### Selective Extraction

```bash
# Extract only utility functions
codebase-extract src/mixed_module.py --entities helper_func validate_input sanitize_data

# Extract core classes for refactoring
codebase-extract src/legacy.py --entities DatabaseManager ConfigHandler LogManager

# Extract specific function and its helper
codebase-extract src/complex.py --entities main_algorithm helper_function
```

### Target Folder Consolidation

```bash
# Consolidate utilities into shared module
codebase-extract src/module1.py --entities util_func1,util_func2 --target-folder src/shared_utils.py

# Move models to dedicated models directory
codebase-extract src/app.py --entities User,Product,Category --target-folder src/models/

# Consolidate validators in specific file
codebase-extract src/forms.py --entities email_validator,phone_validator --target-folder src/validators.py
```

### Cut Mode (Destructive)

```bash
# Remove deprecated code
codebase-extract src/old_system.py --entities DeprecatedClass,old_function --mode cut

# Extract and remove test helpers
codebase-extract src/main.py --entities TestHelper,debug_function --target-folder tests/helpers.py --mode cut

# Refactor by moving classes out
codebase-extract src/monolith.py --entities UserService,ProductService --mode cut
```

### Safe Mode (Backward Compatible)

```bash
# Safely extract utility functions (preserves API)
codebase-extract src/utils.py --entities calculate_tax,format_currency --mode safe

# Extract legacy functions with compatibility wrappers
codebase-extract src/legacy.py --entities old_helper,deprecated_util --target-folder utils/ --mode safe

# Gradually refactor large functions
codebase-extract src/monolith.py --entities process_payment --target-folder services/payment.py --mode safe
```

### Advanced Configuration

```bash
# Extract with Python 2 compatibility
codebase-extract src/legacy.py --entities OldClass --py2-import

# Add custom header to extracted files
codebase-extract src/core.py --entities Engine --custom-block "# Core Engine Module\n# Extracted: $(date)"

# Extract with custom import prefix
codebase-extract src/package/module.py --entities Helper --root-prefix myproject.package

# Safe mode with all features
codebase-extract src/complex.py \
  --entities MainClass,HelperClass \
  --target-folder src/refactored.py \
  --mode safe \
  --py2-import \
  --custom-block "# Refactored from complex.py\n# Date: 2024-01-15" \
  --root-prefix myproject.core

# Cut mode with target folder
codebase-extract src/legacy.py \
  --entities OldService,DeprecatedHelper \
  --target-folder services/legacy/ \
  --mode cut \
  --custom-block "# Legacy services - marked for replacement"
```

## 🔧 Advanced Features

### Automatic Import Resolution

The tool automatically handles import dependencies:

```python
# Original file: src/models.py
import json
from datetime import datetime
from .utils import validate_email

class User:
    def __init__(self, email):
        self.email = validate_email(email)  # Uses validate_email
        self.created = datetime.now()       # Uses datetime
        
def save_user(user):
    return json.dumps(user.__dict__)        # Uses json
```

**After extraction:**
```bash
codebase-extract src/models.py --entities User
```

**Generated User.py:**
```python
import json
from datetime import datetime
from .utils import validate_email

class User:
    def __init__(self, email):
        self.email = validate_email(email)
        self.created = datetime.now()
```

### Internal Dependency Handling

```python
# Original file with internal dependencies
class DatabaseManager:
    def connect(self):
        return "connected"

class UserService:
    def __init__(self):
        self.db = DatabaseManager()  # Internal dependency
```

**After extraction:**
```bash
codebase-extract src/services.py --entities UserService
```

**Generated UserService.py:**
```python
from .DatabaseManager import DatabaseManager

class UserService:
    def __init__(self):
        self.db = DatabaseManager()
```

### Custom Block Integration

```bash
codebase-extract src/core.py --entities Engine --custom-block "# -*- coding: utf-8 -*-
# Engine Module
# Extracted from core.py
# Maintainer: Development Team"
```

**Generated Engine.py:**
```python
# -*- coding: utf-8 -*-
# Engine Module  
# Extracted from core.py
# Maintainer: Development Team

import os
from pathlib import Path

class Engine:
    def __init__(self):
        self.config = {}
```

### Python 2 Compatibility

```bash
codebase-extract src/legacy.py --entities OldClass --py2-import
```

**Generated OldClass.py:**
```python
from __future__ import print_function, division, absolute_import

import sys

class OldClass:
    def __init__(self):
        print("Compatible with Python 2 and 3")
```

## 🔄 Refactoring Workflows

### Workflow 1: Breaking Down Monolithic Files

```bash
# Step 1: Analyze the monolithic file
codebase-report src/monolith.py --summary-only

# Step 2: Extract models first (safe mode for backward compatibility)
codebase-extract src/monolith.py --entities User,Product,Order --target-folder src/models.py --mode safe

# Step 3: Extract services (safe mode to preserve existing imports)
codebase-extract src/monolith.py --entities UserService,ProductService --target-folder src/services.py --mode safe

# Step 4: Extract utilities (copy mode to keep in monolith temporarily)
codebase-extract src/monolith.py --entities validate_email,format_currency --target-folder src/utils.py --mode copy

# Step 5: After testing, cut remaining entities if needed
codebase-extract src/monolith.py --entities ConfigManager --mode cut
```

### Workflow 2: Legacy Code Modernization

```bash
# Step 1: Extract reusable components (safe mode for compatibility)
codebase-extract src/legacy_system.py --entities DatabaseHelper FileManager --target-folder src/shared/legacy_utils.py --mode safe

# Step 2: Extract and modernize core classes (copy mode for testing)
codebase-extract src/legacy_system.py --entities LegacyProcessor --py2-import --custom-block "# Legacy processor - needs modernization" --mode copy

# Step 3: After validation, use safe mode to replace deprecated code gradually
codebase-extract src/legacy_system.py --entities DeprecatedClass old_function --mode safe

# Step 4: Finally cut truly obsolete code
codebase-extract src/legacy_system.py --entities TrulyObsoleteClass --mode cut

# Step 5: Verify remaining code
codebase-report src/legacy_system.py --summary-only
```

### Workflow 3: Microservice Extraction

```bash
# Extract user-related functionality (safe mode first for testing)
codebase-extract src/monolith.py \
  --entities User,UserService,UserValidator \
  --target-folder microservices/user_service/models.py \
  --mode safe

# After testing microservice, cut the entities
codebase-extract src/monolith.py \
  --entities User,UserService,UserValidator \
  --mode cut

# Extract product functionality (safe mode for gradual migration)
codebase-extract src/monolith.py \
  --entities Product,ProductService,ProductValidator \
  --target-folder microservices/product_service/models.py \
  --mode safe

# Extract shared utilities (copy mode to share between services)
codebase-extract src/monolith.py \
  --entities EmailSender,Logger \
  --target-folder shared/common_utils.py \
  --mode copy
```

### Workflow 4: Test Code Organization

```bash
# Extract test utilities (copy mode to share across tests)
codebase-extract tests/test_main.py \
  --entities TestHelper,MockDatabase \
  --target-folder tests/utils/test_helpers.py \
  --mode copy

# Extract specific test classes (cut mode for reorganization)
codebase-extract tests/test_models.py \
  --entities UserTestCase,ProductTestCase \
  --mode cut

# Reorganize by feature (cut mode for clean separation)
codebase-extract tests/test_services.py \
  --entities UserServiceTests \
  --target-folder tests/user/test_user_service.py \
  --mode cut
```

### Workflow 5: Library Development

```bash
# Extract public API classes (safe mode to maintain compatibility)
codebase-extract src/internal.py \
  --entities PublicAPI,ClientManager \
  --target-folder src/api.py \
  --mode safe \
  --custom-block "# Public API - Stable Interface"

# Extract internal utilities (copy mode to keep in both places)
codebase-extract src/internal.py \
  --entities InternalHelper,PrivateManager \
  --target-folder src/_internal_utils.py \
  --mode copy

# Extract examples (cut mode as they don't belong in main code)
codebase-extract src/internal.py \
  --entities ExampleUsage,DemoClass \
  --target-folder examples/usage_examples.py \
  --mode cut
```

## 🎯 Mode Selection Guide

### When to Use Each Mode

#### **Copy Mode** (`--mode copy`) - Default & Safest ✅
- **Use for**: Experimentation, testing extraction feasibility
- **Benefits**: Non-destructive, allows validation before committing
- **Best for**: New projects, proof of concepts, temporary duplicates

```bash
# Safe experimentation
codebase-extract src/experimental.py --entities NewFeature --mode copy
```

#### **Safe Mode** (`--mode safe`) - Gradual Refactoring ⭐
- **Use for**: Production refactoring, maintaining backward compatibility
- **Benefits**: Preserves API contracts, allows gradual migration
- **Best for**: Legacy systems, live applications, team environments

```bash
# Gradually modernize without breaking existing code
codebase-extract src/legacy.py --entities CriticalFunction --mode safe --target-folder services/
```

**Safe Mode Benefits:**
- ✅ Existing imports continue to work
- ✅ No immediate breaking changes
- ✅ Gradual migration path
- ✅ Easy rollback (just remove wrapper)
- ✅ Team can migrate at their own pace

#### **Cut Mode** (`--mode cut`) - Clean Refactoring ⚠️
- **Use for**: Final cleanup, removing obsolete code
- **Benefits**: Clean separation, no duplication
- **Best for**: Deprecation, architectural restructuring

```bash
# Remove after confirming safe mode works
codebase-extract src/cleaned.py --entities ObsoleteClass --mode cut
```

### Migration Strategy

```bash
# Step 1: Copy mode for testing
codebase-extract src/monolith.py --entities UserService --mode copy
# Test the extracted service...

# Step 2: Safe mode for production
codebase-extract src/monolith.py --entities UserService --mode safe
# Update applications to use new import...

# Step 3: Cut mode for cleanup (optional)
codebase-extract src/monolith.py --entities UserService --mode cut
```

## 📚 Best Practices

### 1. **Pre-Extraction Analysis**

```bash
# Always analyze before extracting
codebase-report src/large_file.py --format table

# Check dependencies
codebase-deps src/large_file.py TargetClass class --format tree
```

### 2. **Incremental Extraction**

```bash
# Extract in logical groups
codebase-extract src/models.py --entities User,Profile  # Related models
codebase-extract src/models.py --entities Product,Category  # Related models

# Don't extract everything at once
# ❌ Bad: codebase-extract src/huge_file.py  
# ✅ Good: Extract specific, related entities
```

### 3. **Choose the Right Mode**

```bash
# Use copy mode for experimentation (safe, non-destructive)
codebase-extract src/experimental.py --entities NewFeature --mode copy

# Use safe mode for gradual refactoring (maintains backward compatibility)
codebase-extract src/legacy.py --entities OldFunction --mode safe

# Use cut mode only after thorough testing (destructive)
cp src/important_file.py src/important_file.py.backup  # Always backup first!
codebase-extract src/important_file.py --entities ObsoleteClass --mode cut

# Verify result after any mode
codebase-report src/important_file.py --summary-only
```

### 4. **Naming Conventions**

```bash
# Use descriptive target file names
codebase-extract src/utils.py --entities math_helpers --target-folder src/math_utils.py

# Group related functionality
codebase-extract src/models.py --entities User,UserProfile --target-folder src/user_models.py

# Use directories for organization (auto-generates filename)
codebase-extract src/services.py --entities EmailService --target-folder src/services/

# Explicit file in directory
codebase-extract src/services.py --entities EmailService --target-folder src/services/email_service.py
```

### 5. **Import Management**

```bash
# Use root-prefix for package imports
codebase-extract src/mypackage/module.py --entities Helper --root-prefix mypackage

# Consider Python 2 compatibility if needed
codebase-extract src/legacy.py --entities OldClass --py2-import

# Add meaningful headers
codebase-extract src/core.py --entities Engine --custom-block "# Core Engine - Handle with care"
```

## 🔗 Integration Examples

### Git Workflow Integration

#### Pre-commit Hook
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Check for large files that might need extraction
find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 200 {print "⚠️  Large file: " $2 " (" $1 " lines)"}' 

# Suggest extraction for files over 300 lines
find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 300 {print "💡 Consider extraction: codebase-extract " $2}'
```

#### Feature Branch Refactoring
```bash
# Create refactoring branch
git checkout -b refactor/extract-user-models

# Extract user-related models
codebase-extract src/models.py --entities User,UserProfile,UserSettings --target-file src/user_models.py --cut

# Commit changes
git add .
git commit -m "refactor: extract user models to separate file"

# Test extraction
python -m pytest tests/test_user_models.py
```

### CI/CD Pipeline Integration

#### GitHub Actions Workflow
```yaml
name: Code Extraction Validation
on:
  pull_request:
    paths:
      - '**.py'

jobs:
  validate-extraction:
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
    
    - name: Check for large files
      run: |
        echo "🔍 Checking for files that might benefit from extraction..."
        find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 200 {print "File " $2 " has " $1 " lines - consider extraction"}'
    
    - name: Validate extraction syntax
      run: |
        # Test extraction on large files (dry run simulation)
        for file in $(find src/ -name "*.py" -exec wc -l {} + | awk '$1 > 300 {print $2}'); do
          echo "Testing extraction capability for $file"
          codebase-report "$file" --summary-only
        done
```

### Development Environment Integration

#### VS Code Tasks
```json
{
    "version": "2.0.0",
    "tasks": [
        {
            "label": "Extract Current File Entities",
            "type": "shell",
            "command": "codebase-extract",
            "args": ["${file}"],
            "group": "build",
            "presentation": {
                "echo": true,
                "reveal": "always",
                "focus": false,
                "panel": "shared"
            },
            "problemMatcher": []
        },
        {
            "label": "Extract Specific Entity",
            "type": "shell",
            "command": "codebase-extract",
            "args": [
                "${file}",
                "--entities",
                "${input:entityName}"
            ],
            "group": "build"
        }
    ],
    "inputs": [
        {
            "id": "entityName",
            "description": "Entity name to extract",
            "default": "",
            "type": "promptString"
        }
    ]
}
```

#### Makefile Integration
```makefile
.PHONY: extract-models extract-services extract-utils refactor-check

# Extract models to separate files
extract-models:
	@echo "🔄 Extracting model classes..."
	codebase-extract src/models.py --entities User,Product,Order --mode cut
	@echo "✅ Models extracted"

# Extract services to services directory
extract-services:
	@echo "🔄 Extracting service classes..."
	mkdir -p src/services/
	codebase-extract src/main.py --entities UserService,ProductService --target-folder src/services/business_services.py --mode cut
	@echo "✅ Services extracted"

# Extract utilities (safe mode for backward compatibility)
extract-utils:
	@echo "🔄 Extracting utility functions..."
	codebase-extract src/helpers.py --entities validate_email,format_currency --target-folder src/utils.py --mode safe
	@echo "✅ Utilities extracted"

# Check for files that need extraction
refactor-check:
	@echo "🔍 Checking for large files..."
	@find src/ -name "*.py" -exec wc -l {} + | awk '$$1 > 200 {print "⚠️  " $$2 " has " $$1 " lines"}'
	@echo "💡 Consider using: make extract-models, make extract-services, or make extract-utils"

# Complete refactoring workflow
refactor-all: refactor-check extract-models extract-services extract-utils
	@echo "🎉 Refactoring complete!"
	@echo "📊 Generating post-refactor report..."
	codebase-report src/ --summary-only
```

### Automated Refactoring Scripts

#### Batch Extraction Script
```bash
#!/bin/bash
# batch_extract.sh - Automated extraction for multiple files

BACKUP_DIR="backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

echo "🔄 Starting batch extraction..."

# Backup original files
echo "💾 Creating backups in $BACKUP_DIR..."
find src/ -name "*.py" -exec cp {} "$BACKUP_DIR/" \;

# Extract models from multiple files (safe mode for gradual migration)
echo "📦 Extracting models..."
for file in src/app.py src/main.py src/core.py; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        codebase-extract "$file" --entities User,Product,Order,Category --target-folder src/models.py --mode safe 2>/dev/null || true
    fi
done

# Extract services (copy mode to keep functionality in place)
echo "🔧 Extracting services..."
for file in src/app.py src/main.py; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        codebase-extract "$file" --entities UserService,ProductService --target-folder src/services.py --mode copy 2>/dev/null || true
    fi
done

# Extract utilities (safe mode to maintain imports)
echo "🛠️  Extracting utilities..."
for file in src/*.py; do
    if [ -f "$file" ]; then
        echo "Processing $file..."
        codebase-extract "$file" --entities validate_email,format_currency,sanitize_input --target-folder src/utils.py --mode safe 2>/dev/null || true
    fi
done

echo "✅ Batch extraction complete!"
echo "📊 Generating summary report..."
codebase-report src/ --summary-only

echo "💾 Backups available in: $BACKUP_DIR"
```

#### Smart Extraction Script
```python
#!/usr/bin/env python3
# smart_extract.py - Intelligent extraction based on analysis

import subprocess
import json
from pathlib import Path

def analyze_file(file_path):
    """Analyze file and suggest extractions."""
    result = subprocess.run([
        'codebase-report', str(file_path), '--format', 'json'
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        return json.loads(result.stdout)
    return []

def suggest_extractions(analysis):
    """Suggest extraction strategies based on analysis."""
    suggestions = []
    
    # Find large entities
    large_entities = [
        entity for entity in analysis 
        if entity['total_lines'] > 50
    ]
    
    if large_entities:
        suggestions.append({
            'type': 'large_entities',
            'entities': [e['name'] for e in large_entities],
            'reason': 'Large entities (>50 lines) should be extracted'
        })
    
    # Find entities with many dependencies
    coupled_entities = [
        entity for entity in analysis 
        if entity['internal_dependencies_count'] > 3
    ]
    
    if coupled_entities:
        suggestions.append({
            'type': 'coupled_entities', 
            'entities': [e['name'] for e in coupled_entities],
            'reason': 'Highly coupled entities should be reviewed'
        })
    
    return suggestions

def main():
    src_files = list(Path('src').glob('*.py'))
    
    for file_path in src_files:
        print(f"🔍 Analyzing {file_path}...")
        analysis = analyze_file(file_path)
        
        if analysis:
            suggestions = suggest_extractions(analysis)
            
            for suggestion in suggestions:
                print(f"💡 {suggestion['reason']}")
                print(f"   Entities: {', '.join(suggestion['entities'])}")
                
                # Auto-extract large entities
                if suggestion['type'] == 'large_entities':
                    response = input(f"   Extract these entities? (y/N): ")
                    if response.lower() == 'y':
                        cmd = [
                            'codebase-extract', str(file_path),
                            '--entities'] + suggestion['entities']
                        
                        result = subprocess.run(cmd)
                        if result.returncode == 0:
                            print("   ✅ Extraction completed")
                        else:
                            print("   ❌ Extraction failed")

if __name__ == "__main__":
    main()
```

## 🔧 Troubleshooting

### Common Issues

#### 1. Source File Not Found
```bash
❌ Error: Source file not found: src/missing.py
```

**Solutions:**
```bash
# Check file path
ls -la src/missing.py

# Use absolute path
codebase-extract /full/path/to/src/models.py

# Check current directory
pwd
ls -la src/
```

#### 2. Entity Not Found
```bash
❌ No entities found matching: NonExistentClass
```

**Solutions:**
```bash
# List available entities first
codebase-report src/models.py --format table

# Check entity names (case sensitive)
grep -n "^class\|^def" src/models.py

# Extract all entities to see what's available
codebase-extract src/models.py
```

#### 3. Permission Denied
```bash
❌ Error: Permission denied: /readonly/path/
```

**Solutions:**
```bash
# Check directory permissions
ls -la /path/to/target/directory/

# Use writable directory
codebase-extract src/models.py --target-file ~/extracted/models.py

# Create directory with proper permissions
mkdir -p extracted/
chmod 755 extracted/
codebase-extract src/models.py --target-file extracted/models.py
```

#### 4. Import Resolution Issues
```bash
❌ Warning: Failed to resolve imports for EntityName
```

**Solutions:**
```bash
# Check source file syntax
python -m py_compile src/models.py

# Verify imports in source file
head -20 src/models.py

# Use root-prefix for complex imports
codebase-extract src/models.py --entities MyClass --root-prefix myproject.src
```

#### 5. Target File Creation Failed
```bash
❌ Error: Failed to create target file
```

**Solutions:**
```bash
# Ensure target directory exists
mkdir -p $(dirname target/file.py)

# Check target file permissions
touch target/file.py
ls -la target/file.py

# Use different target location
codebase-extract src/models.py --entities MyClass --target-folder ~/temp/extracted.py

# Try directory instead of file
codebase-extract src/models.py --entities MyClass --target-folder ~/temp/
```

#### 6. Safe Mode Import Issues
```bash
❌ Warning: Safe mode wrapper may have import conflicts
```

**Solutions:**
```bash
# Check for circular imports
python -c "from src.module import function_name; print('✅ Import works')"

# Verify relative import path
codebase-extract src/models.py --entities MyClass --mode safe --target-folder services/

# Use absolute imports if needed
codebase-extract src/models.py --entities MyClass --mode safe --root-prefix myproject.src
```

### Performance Issues

#### Large File Extraction
```bash
# For very large files, extract incrementally
codebase-extract large_file.py --entities Class1 Class2  # First batch
codebase-extract large_file.py --entities Class3 Class4  # Second batch

# Use cut mode to reduce source file size
codebase-extract large_file.py --entities OldClass --cut
```

#### Memory Usage
```bash
# Monitor memory usage for large extractions
/usr/bin/time -v codebase-extract huge_file.py --entities MassiveClass

# Extract in smaller batches if needed
codebase-extract huge_file.py --entities Class1
codebase-extract huge_file.py --entities Class2
```

### Validation and Recovery

#### Validate Extraction Results
```bash
# Check syntax of extracted files
find . -name "*.py" -exec python -m py_compile {} \;

# Verify imports work
python -c "from extracted_module import ExtractedClass; print('✅ Import successful')"

# Compare before/after metrics
codebase-report original_file.py --summary-only > before.txt
codebase-report . --summary-only > after.txt
diff before.txt after.txt
```

#### Recovery from Failed Extraction
```bash
# If extraction fails, restore from backup
cp original_file.py.backup original_file.py

# Clean up partial extraction
rm -f ExtractedClass.py ExtractedFunction.py

# Try extraction with different options
codebase-extract original_file.py --entities SafeClass  # Extract one entity first
```

### Debugging Extraction Issues

#### Verbose Analysis
```bash
# Analyze dependencies before extraction
codebase-deps src/models.py UserModel class --format tree

# Check what imports are detected
codebase-report src/models.py --format json | jq '.[] | select(.name=="UserModel")'

# Test extraction on simple entities first
codebase-extract src/models.py --entities SimpleFunction --mode copy  # Start simple and safe
```

#### Step-by-Step Debugging
```bash
# 1. Verify source file is valid
python -c "import ast; ast.parse(open('src/models.py').read()); print('✅ Valid syntax')"

# 2. Check entity exists
grep -n "class UserModel\|def UserModel" src/models.py

# 3. Test basic extraction
codebase-extract src/models.py --entities UserModel

# 4. Check generated files
ls -la UserModel.py
python -m py_compile UserModel.py

# 5. Test imports
python -c "from UserModel import UserModel; print('✅ Import works')"
```

## 📈 Advanced Usage Patterns

### Conditional Extraction

```bash
#!/bin/bash
# conditional_extract.sh - Extract based on conditions

FILE="src/models.py"
LINES=$(wc -l < "$FILE")

if [ "$LINES" -gt 500 ]; then
    echo "📊 File has $LINES lines - extracting large classes..."
    
    # Extract classes over 100 lines
    codebase-report "$FILE" --format json | \
    jq -r '.[] | select(.total_lines > 100 and .entity_type == "class") | .name' | \
    while read class_name; do
        echo "Extracting large class: $class_name"
        codebase-extract "$FILE" --entities "$class_name" --cut
    done
else
    echo "📊 File has $LINES lines - no extraction needed"
fi
```

### Batch Processing

```bash
#!/bin/bash
# batch_process.sh - Process multiple files

for file in src/*.py; do
    if [ -f "$file" ]; then
        echo "🔄 Processing $file..."
        
        # Extract models to models directory
        mkdir -p models/
        codebase-extract "$file" --entities "*Model" --target-file "models/$(basename $file)" 2>/dev/null || true
        
        # Extract services to services directory  
        mkdir -p services/
        codebase-extract "$file" --entities "*Service" --target-file "services/$(basename $file)" 2>/dev/null || true
    fi
done

echo "✅ Batch processing complete"
```

---

## 🎉 Conclusion

The `codebase-extract` CLI is a powerful tool for code refactoring and architectural improvements. Use it to:

- **✂️ Break down** monolithic files into manageable modules
- **🔄 Refactor** legacy codebases with confidence using safe mode
- **📦 Organize** code into logical, maintainable structures
- **🚀 Modernize** Python projects with proper separation of concerns
- **🛡️ Maintain backward compatibility** during gradual migrations
- **🛠️ Automate** repetitive refactoring tasks
- **📚 Prepare** code for microservice architectures
- **⚡ Choose your approach**: copy for testing, safe for production, cut for cleanup

The tool handles complex import dependencies, maintains code integrity, and provides flexible extraction modes to suit any refactoring workflow.

For more advanced usage and Python library integration, see the main [USAGE.md](USAGE.md) documentation.

**Happy refactoring!** 🚀