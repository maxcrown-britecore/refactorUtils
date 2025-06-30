#!/usr/bin/env python3
"""
Command-line interface for DependencyTreeService.
"""

import argparse
import sys
from pathlib import Path
from ..main import create_dependency_tree_service


def main():
    """Main CLI entry point for dependency tree analysis."""
    parser = argparse.ArgumentParser(
        description="Build comprehensive dependency trees for Python code entities"
    )
    parser.add_argument(
        "file_path",
        type=Path,
        help="Path to Python file containing the target entity"
    )
    parser.add_argument(
        "entity_name",
        help="Name of the entity to analyze"
    )
    parser.add_argument(
        "entity_type",
        choices=["function", "class", "module"],
        help="Type of the entity"
    )
    parser.add_argument(
        "--max-depth",
        "-d",
        type=int,
        help="Maximum depth to traverse (default: unlimited)"
    )
    parser.add_argument(
        "--codebase-root",
        "-r",
        type=Path,
        help="Root directory to scan for dependencies (default: parent of file_path)"
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["tree", "graph", "list", "df"],
        default="tree",
        help="Output format (default: tree)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        help="Output file to save results"
    )
    parser.add_argument(
        "--upstream-only",
        action="store_true",
        help="Show only upstream dependencies (what target depends on)"
    )
    parser.add_argument(
        "--downstream-only", 
        action="store_true",
        help="Show only downstream dependencies (what depends on target)"
    )
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.upstream_only and args.downstream_only:
        print("❌ Error: Cannot specify both --upstream-only and --downstream-only", file=sys.stderr)
        return 1
    
    try:
        # Create dependency service
        dependency_service = create_dependency_tree_service()
        
        # Build dependency tree
        tree = dependency_service.build_dependency_tree(
            file_path=args.file_path,
            entity_name=args.entity_name,
            entity_type=args.entity_type,
            max_depth=args.max_depth,
            codebase_root=args.codebase_root
        )
        
        # Format output
        if args.format == "tree":
            output = tree.to_pretty_string()
            
            # Filter output if requested
            if args.upstream_only:
                lines = output.split('\n')
                upstream_section = []
                in_upstream = False
                for line in lines:
                    if "UPSTREAM DEPENDENCIES" in line:
                        in_upstream = True
                    elif "DOWNSTREAM DEPENDENCIES" in line:
                        break
                    if in_upstream:
                        upstream_section.append(line)
                output = '\n'.join(upstream_section)
            
            elif args.downstream_only:
                lines = output.split('\n')
                downstream_section = []
                in_downstream = False
                for line in lines:
                    if "DOWNSTREAM DEPENDENCIES" in line:
                        in_downstream = True
                    if in_downstream:
                        downstream_section.append(line)
                output = '\n'.join(downstream_section)
        
        elif args.format == "graph":
            graph = tree.to_graph()
            output = f"📊 Dependency Graph for: {args.entity_name} ({args.entity_type})\n"
            output += f"Nodes: {graph.number_of_nodes()}\n"
            output += f"Edges: {graph.number_of_edges()}\n"
            output += "\nEdges:\n"
            for edge in graph.edges(data=True):
                output += f"  {edge[0]} -> {edge[1]}\n"
        
        elif args.format == "list":
            all_deps = tree.get_all_dependencies()
            output = f"📋 All Dependencies for: {args.entity_name} ({args.entity_type})\n"
            output += "=" * 50 + "\n"
            for i, dep in enumerate(all_deps, 1):
                output += f"{i:2d}. {dep.name} ({dep.entity_type}) - {dep.dependency_type}\n"
                output += f"     📁 {dep.file_path}:{dep.line_start}\n"
        
        elif args.format == "df":
            all_deps = tree.get_all_dependencies_df()
            output = all_deps
        
        # Save or print output
        if args.output:
            args.output.write_text(output)
            print(f"✅ Dependency analysis saved to: {args.output}")
        else:
            print(output)
            
    except ValueError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main()) 