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
    
    args = parser.parse_args()
    
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
        
        # Generate report
        if len(file_paths) == 1:
            df = reporter.generate_code_report(file_paths[0])
        else:
            df = reporter.generate_multi_file_report(file_paths)
        
        # Get summary statistics
        stats = reporter.get_summary_statistics(df)
        
        # Output results
        if args.summary_only:
            print("📊 Code Analysis Summary")
            print("=" * 30)
            print(f"Total entities: {stats['total_entities']}")
            print(f"Functions: {stats['functions_count']}")
            print(f"Classes: {stats['classes_count']}")
            print(f"Files analyzed: {stats['files_analyzed']}")
            print(f"Average code length: {stats['avg_code_length']:.1f} characters")
            print(f"Entities with docstrings: {stats['entities_with_docstrings']} ({stats['docstring_percentage']}%)")
        else:
            if args.format == "table":
                print("📋 Code Structure Report")
                print("=" * 50)
                if not df.empty:
                    print(df.to_string(index=False))
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