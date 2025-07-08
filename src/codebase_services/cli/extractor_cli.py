#!/usr/bin/env python3
"""
Command-line interface for CodeExtractorService.
"""

import argparse
import sys
from pathlib import Path
from typing import List
from ..main import create_extractor


def resolve_target_path(target_folder: Path, entity_names: List[str]) -> Path:
    """
    Smart resolution of target path based on input.
    
    Args:
        target_folder: User-provided target folder or file path
        entity_names: List of entity names being extracted
    
    Returns:
        Resolved target file path
    """
    # Case 1: User provided full file path (ends with .py)
    if str(target_folder).endswith('.py'):
        return target_folder
    
    # Case 2: User provided directory - generate filename
    if len(entity_names) == 1:
        filename = f"{entity_names[0]}.py"
    else:
        # Multiple entities - use first entity name
        filename = f"{entity_names[0]}.py"
    
    return target_folder / filename


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
        type=str,
        help=(
            "Comma-separated names of entities to extract "
            "(default: extract all)"
        )
    )
    parser.add_argument(
        "--target-folder",
        "-t", 
        type=Path,
        help=(
            "Target folder or file path. If folder: auto-generates filename. "
            "If file: uses as-is"
        )
    )
    parser.add_argument(
        "--mode",
        "-m",
        choices=["copy", "cut", "safe"],
        default="copy",
        help=(
            "Extraction mode: 'copy' (default) leaves original intact, "
            "'cut' removes original, 'safe' replaces with import wrapper"
        )
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
        
        # Parse entities argument (comma-separated)
        entity_names = None
        if args.entities:
            entity_names = [
                e.strip() for e in args.entities.split(",") if e.strip()
            ]
        
        # Resolve target file path (smart folder/file handling)
        target_file = None
        if args.target_folder:
            if entity_names:
                target_file = resolve_target_path(
                    args.target_folder, entity_names
                )
            else:
                # If no specific entities, use source filename for target
                source_name = args.source_file.stem
                target_file = resolve_target_path(
                    args.target_folder, [source_name]
                )
        
        # Perform extraction
        result = extractor.extract_code_entities(
            source_file=args.source_file,
            entity_names=entity_names,
            target_file=target_file,
            mode=args.mode,
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