"""
Generate Dependency Map

This script runs the dependency mapper to generate a JSON file with the dependency map.
It starts from main.py and recursively maps all dependencies, avoiding duplicates.
"""

import os
import json
import time
from dependency_mapper import DependencyMapper

def main():
    """Main function to generate the dependency map."""
    # Get the current directory
    current_dir = os.path.dirname(os.path.abspath(__file__))

    print(f"Generating dependency map from directory: {current_dir}")
    print("This may take a few moments...")

    # Record start time
    start_time = time.time()

    # Create a dependency mapper
    mapper = DependencyMapper(current_dir)

    # Map dependencies starting from main.py
    print("Mapping dependencies starting from main.py...")
    dependency_map = mapper.map_dependencies('main.py')

    # Calculate statistics
    total_files = len(dependency_map)
    total_dependencies = sum(len(deps) for deps in dependency_map.values())
    files_with_no_deps = sum(1 for deps in dependency_map.values() if not deps)
    max_deps_file = max(dependency_map.items(), key=lambda x: len(x[1]), default=("None", []))

    # Save the dependency map to a JSON file
    output_file = 'dependency_map.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dependency_map, f, indent=2, sort_keys=True)

    # Record end time and calculate duration
    end_time = time.time()
    duration = end_time - start_time

    # Print summary
    print("\nDependency Map Generation Complete")
    print("=" * 40)
    print(f"Dependency map saved to: {output_file}")
    print(f"Total files analyzed: {total_files}")
    print(f"Total dependencies found: {total_dependencies}")
    print(f"Files with no dependencies: {files_with_no_deps}")
    print(f"File with most dependencies: {max_deps_file[0]} ({len(max_deps_file[1])} dependencies)")
    print(f"Time taken: {duration:.2f} seconds")
    print("=" * 40)

if __name__ == "__main__":
    main()