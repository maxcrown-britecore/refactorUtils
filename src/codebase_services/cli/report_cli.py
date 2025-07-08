#!/usr/bin/env python3
"""
Command-line interface for CodeReportService.
"""

import argparse
import sys
from pathlib import Path
from ..main import create_report_service


def main():
    """Main CLI entry point for code reporting."""
    parser = argparse.ArgumentParser(
        description="Generate analytical reports about Python code structure"
    )
    parser.add_argument(
        "source", 
        type=Path,
        help="Source Python file or directory to analyze"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file for the report (CSV format)"
    )
    parser.add_argument(
        "--summary-only",
        "-s",
        action="store_true", 
        help="Show only summary statistics"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["table", "csv", "json"],
        default="table",
        help="Output format (default: table)"
    )
    parser.add_argument(
        "--cluster",
        "-c",
        action="store_true",
        help="Cluster code entities by similarity"
    )
    parser.add_argument(
        "--entities",
        "-e",
        type=str,
        help=("Comma-separated list of entity names to filter by "
              "(e.g., 'func1,Class2,method3')")
    )
    parser.add_argument(
        "--missing-imports",
        action="store_true",
        help="Analyze missing imports instead of code entities"
    )
    
    args = parser.parse_args()
    
    # Parse entity names if provided
    entity_names = None
    if args.entities:
        entity_names = [name.strip() for name in args.entities.split(',')]
        if entity_names:
            print(f"🔍 Filtering entities: {', '.join(entity_names)}")
    
    try:
        # Create report service
        reporter = create_report_service()
        
        # Determine files to analyze
        if args.source.is_file():
            if not args.source.suffix == '.py':
                print("❌ Error: Source file must be a Python file", 
                      file=sys.stderr)
                return 1
            file_paths = [args.source]
        elif args.source.is_dir():
            file_paths = list(args.source.rglob("*.py"))
            if not file_paths:
                print("❌ Error: No Python files found in directory", 
                      file=sys.stderr)
                return 1
        else:
            print("❌ Error: Source path does not exist", file=sys.stderr)
            return 1
        
        # Generate report based on mode
        if args.missing_imports:
            # Missing imports analysis mode
            if len(file_paths) == 1:
                df = reporter.analyze_missing_imports(file_paths[0])
            else:
                df = reporter.analyze_multi_file_missing_imports(file_paths)
            
            # Get summary statistics for missing imports
            stats = reporter.get_missing_imports_summary(df)
        else:
            # Regular entity analysis mode
            if len(file_paths) == 1:
                df = reporter.generate_code_report(file_paths[0], entity_names)
            else:
                df = reporter.generate_multi_file_report(file_paths, entity_names)

            if args.cluster:
                df = reporter.cluster_code_entities(df)
            
            # Get summary statistics
            stats = reporter.get_summary_statistics(df, entity_names)
        
        # Output results
        if args.summary_only:
            if args.missing_imports:
                print("📊 Missing Imports Analysis Summary")
                print("=" * 35)
                print(f"Total missing symbols: {stats['total_missing_symbols']}")
                print(f"Files with missing imports: "
                      f"{stats['files_with_missing_imports']}")
                if stats['most_common_missing']:
                    print("Most common missing symbols:")
                    for symbol, count in stats['most_common_missing'].items():
                        print(f"  • {symbol}: {count} occurrences")
                if stats['symbols_by_type']:
                    print("Symbols by type:")
                    for symbol_type, count in stats['symbols_by_type'].items():
                        print(f"  • {symbol_type}: {count}")
            else:
                print("📊 Code Analysis Summary")
                print("=" * 30)
                print(f"Total entities: {stats['total_entities']}")
                print(f"Functions: {stats['functions_count']}")
                print(f"Classes: {stats['classes_count']}")
                print(f"Files analyzed: {stats['files_analyzed']}")
                avg_length = f"{stats['avg_code_length']:.1f}"
                print(f"Average code length: {avg_length} characters")
                docstring_info = (f"Entities with docstrings: "
                                f"{stats['entities_with_docstrings']} "
                                f"({stats['docstring_percentage']}%)")
                print(docstring_info)
                print(f"Total lines: {stats['total_lines']}")
        else:
            if args.format == "table":
                if args.missing_imports:
                    print("📋 Missing Imports Report")
                    print("=" * 50)
                    if not df.empty:
                        print(df.to_string(index=False))
                    else:
                        print("No missing imports found.")
                    print("\n📊 Summary Statistics:")
                    print("-" * 30)
                    for key, value in stats.items():
                        if isinstance(value, dict) and value:
                            print(f"{key.replace('_', ' ').title()}:")
                            for k, v in value.items():
                                print(f"  • {k}: {v}")
                        else:
                            print(f"{key.replace('_', ' ').title()}: {value}")
                else:
                    print("📋 Code Structure Report")
                    print("=" * 50)
                    if not df.empty:
                        print(df.to_string(index=False))
                    else:
                        if entity_names:
                            entities_str = ', '.join(entity_names)
                            no_match_msg = f"No entities found matching: {entities_str}"
                            print(no_match_msg)
                        else:
                            print("No entities found.")
                    print("\n📊 Summary Statistics:")
                    print("-" * 30)
                    for key, value in stats.items():
                        print(f"{key.replace('_', ' ').title()}: {value}")
            
            elif args.format == "csv":
                if args.output:
                    df.to_csv(args.output, index=False)
                    print(f"✅ Report saved to: {args.output}")
                else:
                    print(df.to_csv(index=False))
            
            elif args.format == "json":
                if args.output:
                    df.to_json(args.output, orient="records", indent=2)
                    print(f"✅ Report saved to: {args.output}")
                else:
                    print(df.to_json(orient="records", indent=2))
            
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 