#!/usr/bin/env python3
"""
Test script for the new Target File Feature in CodeExtractorService.

This script demonstrates how to use the enhanced extract_code_entities method
to move multiple entities from a source file to a single target file.

Usage:
    python test_target_file_feature.py
"""

from pathlib import Path
from main import create_extractor


def test_target_file_extraction():
    """
    Test the new target file feature with the BriteCore policy utilities.
    
    This demonstrates moving multiple policy-related functions from utils.py
    to a consolidated policy_utilities.py file.
    """
    
    # Create the extractor using the factory function
    extractor = create_extractor()
    
    # Define your specific paths
    source_file = Path(
        "/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py"
    )
    target_file = Path(
        "/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/"
        "policy_utilities.py"
    )
    
    # Define all the entities you want to extract
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
    
    print("🚀 Testing Target File Feature")
    print("="*60)
    print(f"📁 Source File: {source_file}")
    print(f"🎯 Target File: {target_file}")
    print(f"📦 Entities to Extract: {len(entities_to_extract)} functions/classes")
    print()
    
    # Check if source file exists
    if not source_file.exists():
        print("❌ ERROR: Source file does not exist!")
        print(f"   Expected: {source_file}")
        print("\n💡 This is a demo script. To run with actual files:")
        print("   1. Ensure the source file exists")
        print("   2. Update the paths in this script if needed")
        print("   3. Run the extraction")
        return
    
    try:
        # 🆕 NEW FEATURE: Extract entities to target file
        print("⚡ Executing extraction with TARGET FILE mode...")
        result = extractor.extract_code_entities(
            source_file=source_file,
            entity_names=entities_to_extract,
            target_file=target_file,  # 🎯 This is the new parameter!
            py2_top_most_import=True,
            top_custom_block=(
                "# Policy utilities extracted from utils.py\n"
                "# Consolidated for better organization"
            )
        )
        
        print("✅ Extraction completed successfully!")
        print()
        print("📊 RESULTS:")
        print("="*40)
        
        # Display the results
        print(f"📁 Source File: {result['source_file']}")
        print(f"🎯 Target File Modified: {result['target_file_modified']}")
        print(f"📦 Entities Extracted: {len(result['extracted_entities'])}")
        print(f"📄 Files Created: {len(result['files_created'])} (should be 0)")
        print(f"🔧 Init File Updated: {result['init_file_updated']} (should be False)")
        print()
        
        print("📝 Extracted Entities:")
        for i, entity in enumerate(result['extracted_entities'], 1):
            print(f"   {i:2d}. {entity['name']} ({entity['type']})")
        
        print()
        print("🎉 SUCCESS: All entities have been moved to the target file!")
        print(f"   Check: {result['target_file_modified']}")
        
    except FileNotFoundError as e:
        print(f"❌ FILE ERROR: {e}")
    except ValueError as e:
        print(f"❌ VALIDATION ERROR: {e}")
    except Exception as e:
        print(f"❌ UNEXPECTED ERROR: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_feature_comparison():
    """
    Show the difference between the two extraction modes.
    """
    print("\n" + "="*60)
    print("📚 FEATURE COMPARISON: Two Extraction Modes")
    print("="*60)
    
    print("""
🔧 MODE 1: Separate Files (Original)
----------------------------------------
extractor.extract_code_entities(
    source_file=Path("source.py"),
    entity_names=["ClassA", "function_b"]
    # No target_file parameter
)

Result:
✅ Creates: ClassA.py, function_b.py
✅ Updates: __init__.py
✅ Returns: files_created = ["ClassA.py", "function_b.py"]

🎯 MODE 2: Target File (NEW!)
----------------------------------------
extractor.extract_code_entities(
    source_file=Path("source.py"),
    entity_names=["ClassA", "function_b"],
    target_file=Path("consolidated.py")  # 🆕 NEW!
)

Result:
✅ Appends all entities to: consolidated.py
✅ Merges imports intelligently
✅ Returns: target_file_modified = "consolidated.py"
❌ No separate files created
❌ No __init__.py updates
""")


if __name__ == "__main__":
    print("🧪 Testing New Target File Feature")
    print("📋 CodeExtractorService Enhancement")
    print()
    
    # Run the main test
    test_target_file_extraction()
    
    # Show feature comparison
    demonstrate_feature_comparison()
    
    print("\n" + "="*60)
    print("✨ Test Complete!")
    print("💡 This demonstrates the new target_file parameter functionality.") 