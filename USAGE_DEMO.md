# 🎯 TARGET FILE FEATURE - Usage Demo

## Your Specific Extraction Request

**Source File:** `/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py`
**Target File:** `/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/policy_utilities.py`

**Entities to Extract (21 functions):**
```
1.  get_policy_status
2.  validate_policy_type
3.  is_valid_policy_type
4.  validate_multi_policy
5.  can_set_policy_status_to_binder_active
6.  can_set_policy_status_to_active
7.  get_polid
8.  get_polid_from_polnum
9.  get_policy_number_from_account_number
10. get_policy_numbers_from_account_numbers
11. get_policy_id_with_regex
12. is_risk_address_field
13. is_zip_code_format_valid
14. find_decimal_value_match
15. get_unique_emails
16. daterange
17. from_table
18. is_first_revision
19. is_new_business
20. is_build_mem
21. has_auto_policy
22. policy_has_poor_payment_history
```

## 🆕 NEW TARGET FILE FEATURE - Complete Code

```python
from pathlib import Path
from main import create_extractor

# Create the extractor service
extractor = create_extractor()

# Define your specific paths
source_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py")
target_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/policy_utilities.py")

# All entities you want to extract
entities_to_extract = [
    # Policy status and validation functions
    "get_policy_status",
    "validate_policy_type", 
    "is_valid_policy_type",
    "validate_multi_policy",
    "can_set_policy_status_to_binder_active",
    "can_set_policy_status_to_active",
    
    # Policy ID and number utilities
    "get_polid",
    "get_polid_from_polnum", 
    "get_policy_number_from_account_number",
    "get_policy_numbers_from_account_numbers",
    "get_policy_id_with_regex",
    
    # Address and validation utilities
    "is_risk_address_field",
    "is_zip_code_format_valid",
    "find_decimal_value_match",
    
    # General utilities
    "get_unique_emails",
    "daterange",
    "from_table",
    
    # Policy state checking functions
    "is_first_revision",
    "is_new_business", 
    "is_build_mem",
    "has_auto_policy",
    "policy_has_poor_payment_history"
]

# 🎯 NEW FEATURE: Extract to target file
result = extractor.extract_code_entities(
    source_file=source_file,
    entity_names=entities_to_extract,
    target_file=target_file,  # 🆕 This is the new parameter!
    py2_top_most_import=True,
    top_custom_block="# Policy utilities extracted from utils.py\n# Consolidated for better organization"
)

print("✅ Extraction completed!")
print(f"📁 Source: {result['source_file']}")
print(f"🎯 Target modified: {result['target_file_modified']}")
print(f"📦 Entities extracted: {len(result['extracted_entities'])}")
print(f"📄 Files created: {len(result['files_created'])} (should be 0)")
print(f"🔧 Init updated: {result['init_file_updated']} (should be False)")
```

## 📊 Expected Result Structure

```python
{
    'source_file': '/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py',
    'target_file_modified': '/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/policy_utilities.py',
    'extracted_entities': [
        {'name': 'get_policy_status', 'type': 'function'},
        {'name': 'validate_policy_type', 'type': 'function'},
        # ... 21 more entities ...
    ],
    'files_created': [],  # ✅ Empty - no separate files!
    'init_file_updated': False  # ✅ No __init__.py changes!
}
```

## 🔧 What Happens Behind the Scenes

### 1. **File Validation**
- ✅ Validates `policy_utilities.py` has `.py` extension
- ✅ Creates the file if it doesn't exist
- ✅ Creates parent directories if needed

### 2. **Smart Import Resolution**
- ✅ Analyzes all 22 entities collectively
- ✅ Resolves all required imports for all entities
- ✅ Merges imports with existing file content
- ✅ Adds Python 2 compatibility imports
- ✅ Handles internal dependencies between entities

### 3. **Content Organization**
- ✅ Preserves existing content in `policy_utilities.py`
- ✅ Adds new imports in organized sections
- ✅ Appends all entities to the end of the file
- ✅ Includes custom header block

### 4. **Final File Structure**
```python
# Existing imports (preserved)
from existing_module import something

# Additional imports from extraction
from __future__ import print_function, division, absolute_import
from newly_required import modules

# Policy utilities extracted from utils.py
# Consolidated for better organization

def get_policy_status(...):
    # function implementation

def validate_policy_type(...):
    # function implementation

# ... all 22 entities ...

def policy_has_poor_payment_history(...):
    # function implementation
```

## ✨ Key Benefits

| Feature | Original Mode | 🆕 Target File Mode |
|---------|---------------|-------------------|
| **Files Created** | 22 separate files | 1 consolidated file |
| **Import Management** | Individual per file | Smart collective merging |
| **Organization** | Many small modules | Feature-focused grouping |
| **Maintenance** | Update 22 files | Update 1 file |
| **Dependencies** | Complex __init__.py | Simple target file |

## 🚀 Ready to Execute!

Once the import configuration is resolved, you can run this exact code to move all 22 policy utility functions from `utils.py` into your consolidated `policy_utilities.py` file.

The new target file feature handles everything automatically:
- ✅ **Smart import merging**
- ✅ **Dependency resolution** 
- ✅ **File organization**
- ✅ **Content preservation**

**Your policy utilities will be perfectly organized in one place! 🎉** 