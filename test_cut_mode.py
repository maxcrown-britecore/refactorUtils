#!/usr/bin/env python3
"""
Test the new CUT mode feature in CodeExtractorService.
This demonstrates cutting entities from source and moving to target file.
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


def test_cut_vs_copy_modes():
    """Test both COPY and CUT modes to show the difference."""
    
    # Your specific paths
    source_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/utils.py")
    target_file = Path("/Users/maxicorona/Projects/Britecore/BriteCore/lib/policies/utils/policy_utilities.py")
    
    # Test with just a few entities for demo
    test_entities = [
        "get_policy_status", 
        "validate_policy_type", 
        "is_valid_policy_type"
    ]
    
    print("🚀 Testing CUT vs COPY Modes")
    print("=" * 50)
    print(f"📁 Source: {source_file.name}")
    print(f"🎯 Target: {target_file.name}")
    print(f"📦 Test Entities: {len(test_entities)} functions")
    print()
    
    if not source_file.exists():
        print(f"❌ Source file not found: {source_file}")
        print("💡 Update the path to your actual BriteCore utils.py file")
        return
    
    extractor = create_extractor()
    
    # Test 1: COPY Mode (default)
    print("📋 TEST 1: COPY MODE (default)")
    print("-" * 30)
    try:
        result_copy = extractor.extract_code_entities(
            source_file=source_file,
            entity_names=test_entities,
            target_file=target_file,
            cut_entities=False,  # 📄 COPY mode
            top_custom_block="# COPY MODE: Functions copied from utils.py"
        )
        
        print("✅ COPY Mode completed!")
        print(f"   🎯 Target modified: {result_copy['target_file_modified']}")
        print(f"   📦 Entities extracted: {len(result_copy['extracted_entities'])}")
        print(f"   📁 Source modified: {result_copy.get('source_file_modified', 'N/A')}")
        print(f"   ✂️  Entities cut: {result_copy.get('entities_cut', 'N/A')}")
        print()
        
    except Exception as e:
        print(f"❌ COPY Mode error: {e}")
        return
    
    # Test 2: CUT Mode 
    print("✂️  TEST 2: CUT MODE (new feature!)")
    print("-" * 30)
    try:
        result_cut = extractor.extract_code_entities(
            source_file=source_file,
            entity_names=test_entities,
            target_file=target_file,
            cut_entities=True,  # ✂️ CUT mode - NEW!
            top_custom_block="# CUT MODE: Functions moved from utils.py"
        )
        
        print("✅ CUT Mode completed!")
        print(f"   🎯 Target modified: {result_cut['target_file_modified']}")
        print(f"   📦 Entities extracted: {len(result_cut['extracted_entities'])}")
        print(f"   📁 Source modified: {result_cut.get('source_file_modified', False)}")
        print(f"   ✂️  Entities cut: {result_cut.get('entities_cut', [])}")
        print()
        
    except Exception as e:
        print(f"❌ CUT Mode error: {e}")
        import traceback
        traceback.print_exc()


def demonstrate_cut_feature():
    """Show the CUT mode capabilities."""
    print("=" * 60)
    print("🔧 CUT MODE FEATURE OVERVIEW")
    print("=" * 60)
    
    print("""
📄 COPY MODE (Default):
----------------------------------------
result = extractor.extract_code_entities(
    source_file=Path("utils.py"),
    entity_names=["func1", "func2"],
    target_file=Path("target.py"),
    cut_entities=False  # Default - COPY mode
)

Result:
✅ Entities copied to target.py
✅ Source file unchanged
✅ Original entities remain in utils.py

✂️  CUT MODE (NEW!):
----------------------------------------
result = extractor.extract_code_entities(
    source_file=Path("utils.py"),
    entity_names=["func1", "func2"], 
    target_file=Path("target.py"),
    cut_entities=True  # 🆕 CUT mode!
)

Result:
✅ Entities moved to target.py
✅ Entities removed from utils.py  
✅ Empty lines cleaned up
✅ Imports preserved in source
✅ Returns: source_file_modified=True, entities_cut=["func1", "func2"]

🎯 Perfect for clean refactoring workflows!
""")


if __name__ == "__main__":
    print("🧪 Testing CUT Mode Enhancement")
    print("📋 CodeExtractorService - Cut vs Copy")
    print()
    
    # Run the comparison test
    test_cut_vs_copy_modes()
    
    # Show feature overview
    demonstrate_cut_feature()
    
    print("\n" + "=" * 60)
    print("✨ CUT Mode Test Complete!")
    print("💡 CUT mode enables clean refactoring by removing entities from source.") 