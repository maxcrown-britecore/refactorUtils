#!/usr/bin/env python3
"""
Test the target file feature with uv run.
This works with the src layout without needing venv setup.
"""

from pathlib import Path
import sys

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from services.extractor_service import CodeExtractorService
from core.parser import PythonASTParser
from core.file_writer import FileWriter
from core.import_analyzer import ImportAnalyzer
from core.dependency_resolver import DependencyResolver
from core.import_optimizer import ImportOptimizer


def create_extractor() -> CodeExtractorService:
    """Factory function to create configured extractor service."""
    parser = PythonASTParser()
    file_writer = FileWriter()
    import_analyzer = ImportAnalyzer()
    dependency_resolver = DependencyResolver()
    import_optimizer = ImportOptimizer()
    return CodeExtractorService(
        parser, file_writer, import_analyzer, dependency_resolver, import_optimizer
    )


def test_target_file_feature():
    """Test the target file feature with your BriteCore extraction."""
    
    # Your specific paths
    source_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py")
    target_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/policy_utilities.py")
    
    # Your 22 entities to extract
    entities = [
        "get_policy_status", "validate_policy_type", "is_valid_policy_type",
        "validate_multi_policy", "can_set_policy_status_to_binder_active", 
        "can_set_policy_status_to_active", "get_polid", "get_polid_from_polnum", 
        "get_policy_number_from_account_number", "get_policy_numbers_from_account_numbers",
        "get_policy_id_with_regex", "is_risk_address_field", "is_zip_code_format_valid",
        "find_decimal_value_match", "get_unique_emails", "daterange", "from_table",
        "is_first_revision", "is_new_business", "is_build_mem", "has_auto_policy",
        "policy_has_poor_payment_history"
    ]
    
    print("🚀 Testing Target File Feature with uv")
    print("=" * 50)
    print(f"📁 Source: {source_file.name}")
    print(f"🎯 Target: {target_file.name}")
    print(f"📦 Entities: {len(entities)} functions")
    print()
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        print("💡 Update the path to your actual BriteCore utils.py file")
        return
    
    # Create extractor and run extraction
    extractor = create_extractor()
    
    try:
        print("⚡ Running TARGET FILE extraction...")
        result = extractor.extract_code_entities(
            source_file=source_file,
            entity_names=entities,
            target_file=target_file,  # 🎯 NEW FEATURE!
            py2_top_most_import=True,
            top_custom_block="# Policy utilities extracted from utils.py"
        )
        
        print("🎉 SUCCESS!")
        print(f"   📁 Source: {result['source_file']}")
        print(f"   🎯 Target modified: {result['target_file_modified']}")
        print(f"   📦 Entities extracted: {len(result['extracted_entities'])}")
        print(f"   📄 Files created: {len(result['files_created'])} (should be 0)")
        print(f"   🔧 Init updated: {result['init_file_updated']} (should be False)")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    test_target_file_feature() 