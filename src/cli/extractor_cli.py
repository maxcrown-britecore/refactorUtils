#!/usr/bin/env python3
"""
Command-line interface for CodeExtractorService.
"""

import argparse
import sys
from pathlib import Path
from ..main import create_extractor


def main():
    """Main CLI entry point for code extraction."""
    parser = argparse.ArgumentParser(
        description="Extract functions and classes from Python files"
    )
    parser.add_argument(
        "source_file", 
        type=Path,
        help="Source Python file to extract from"
    )
    parser.add_argument(
        "--entities", 
        "-e",
        nargs="+",
        help="Names of entities to extract (default: extract all)"
    )
    parser.add_argument(
        "--target-file",
        "-t", 
        type=Path,
        help="Target file to move entities to (instead of separate files)"
    )
    parser.add_argument(
        "--cut",
        "-c",
        action="store_true",
        help="Remove entities from source file after extraction"
    )
    parser.add_argument(
        "--py2-import",
        action="store_true",
        help="Add Python 2 compatibility imports"
    )
    parser.add_argument(
        "--custom-block",
        help="Custom comment block to add to extracted files"
    )
    parser.add_argument(
        "--root-prefix",
        help="Root path prefix for import statements"
    )
    
    args = parser.parse_args()
    
    try:
        # Create extractor service
        extractor = create_extractor()
        
        # Perform extraction
        result = extractor.extract_code_entities(
            source_file=args.source_file,
            entity_names=args.entities,
            target_file=args.target_file,
            cut_entities=args.cut,
            py2_top_most_import=args.py2_import,
            top_custom_block=args.custom_block,
            root_path_prefix=args.root_prefix
        )
        
        # Print results
        print(f"✅ Extraction completed!")
        print(f"📄 Source file: {result['source_file']}")
        print(f"🔍 Extracted entities: {len(result['extracted_entities'])}")
        
        for entity in result['extracted_entities']:
            print(f"   • {entity['name']} ({entity['type']})")
        
        if result.get('target_file_modified'):
            print(f"📁 Target file modified: {result['target_file_modified']}")
        else:
            print(f"📁 Files created: {len(result['files_created'])}")
            for file_path in result['files_created']:
                print(f"   • {file_path}")
        
        if result.get('init_file_updated'):
            print("📦 __init__.py file updated")
        
        if result.get('entities_cut'):
            print(f"✂️  Entities cut from source: {result['entities_cut']}")
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 