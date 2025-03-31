"""
Visualize Dependencies

This script creates a visualization of the dependency map using networkx and matplotlib.
"""

import os
import json
import networkx as nx
import matplotlib.pyplot as plt
from typing import Dict, List, Set, Any

def load_dependency_map(file_path: str) -> Dict[str, List[str]]:
    """
    Load the dependency map from a JSON file.
    
    Args:
        file_path: The path to the JSON file
        
    Returns:
        The dependency map
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading dependency map: {str(e)}")
        return {}

def create_graph(dependency_map: Dict[str, List[str]], unused_files: List[str] = None) -> nx.DiGraph:
    """
    Create a directed graph from the dependency map.

    Args:
        dependency_map: The dependency map
        unused_files: List of potentially unused files (optional)

    Returns:
        The directed graph
    """
    G = nx.DiGraph()

    # Initialize unused_files if not provided
    if unused_files is None:
        unused_files = []

    # Add nodes
    for file_path in dependency_map.keys():
        # Use just the filename for display
        node_name = os.path.basename(file_path)
        # Mark if this is an unused file
        is_unused = file_path in unused_files
        G.add_node(node_name, full_path=file_path, is_unused=is_unused)

    # Add edges
    for file_path, dependencies in dependency_map.items():
        source = os.path.basename(file_path)
        for dependency in dependencies:
            target = os.path.basename(dependency)
            if target in G.nodes():
                G.add_edge(source, target)

    return G

def visualize_graph(G: nx.DiGraph, output_file: str = 'dependency_graph.png') -> None:
    """
    Visualize the graph and save it to a file.

    Args:
        G: The directed graph
        output_file: The output file path
    """
    plt.figure(figsize=(20, 20))

    # Use a layout that works well for directed graphs
    pos = nx.spring_layout(G, k=0.3, iterations=50)

    # Separate nodes into unused and normal nodes
    unused_nodes = [node for node, attrs in G.nodes(data=True) if attrs.get('is_unused', False)]
    normal_nodes = [node for node in G.nodes() if node not in unused_nodes]

    # Draw normal nodes in light blue
    nx.draw_networkx_nodes(G, pos, nodelist=normal_nodes, node_size=500, node_color='lightblue', alpha=0.8)

    # Draw unused nodes in red
    if unused_nodes:
        nx.draw_networkx_nodes(G, pos, nodelist=unused_nodes, node_size=500, node_color='red', alpha=0.8)

    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrows=True, arrowsize=20)

    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')

    # Add a legend if there are unused files
    if unused_nodes:
        plt.plot([], [], 'o', color='red', label='Unused Files')
        plt.plot([], [], 'o', color='lightblue', label='Active Files')
        plt.legend(loc='upper right')

    # Save the figure
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph visualization saved to {output_file}")

    # Close the figure to free memory
    plt.close()

def create_html_visualization(dependency_map: Dict[str, List[str]], output_file: str = 'dependency_graph.html', unused_files: List[str] = None) -> None:
    """
    Create an HTML visualization of the dependency map.

    Args:
        dependency_map: The dependency map
        output_file: The output file path
        unused_files: List of potentially unused files (optional)
    """
    # Initialize unused_files if not provided
    if unused_files is None:
        unused_files = []
    # Create a simple HTML file with a tree view
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Dependency Map</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
            }
            .tree {
                margin-left: 20px;
            }
            .file {
                margin: 10px 0;
                cursor: pointer;
                border: 1px solid #ddd;
                padding: 8px;
                border-radius: 4px;
                background-color: #f9f9f9;
            }
            .dependencies {
                margin-left: 20px;
                display: none;
                padding: 10px;
                border-left: 2px solid #ddd;
            }
            .toggle {
                cursor: pointer;
                color: blue;
                text-decoration: underline;
                margin-right: 5px;
            }
            .search {
                margin-bottom: 20px;
            }
            #searchInput {
                padding: 5px;
                width: 300px;
            }
            .highlight {
                background-color: #ffffcc;
            }
            .unused-file {
                background-color: #ffdddd;
                border-color: #ff9999;
            }
            .section-title {
                font-weight: bold;
                margin-top: 10px;
                margin-bottom: 5px;
                color: #333;
            }
            .dependency-item {
                margin: 3px 0;
                padding: 3px;
            }
            .imports {
                color: #0066cc;
            }
            .imported-by {
                color: #cc6600;
            }
            .tab-container {
                margin-bottom: 20px;
            }
            .tab {
                display: inline-block;
                padding: 8px 16px;
                cursor: pointer;
                background-color: #f1f1f1;
                border: 1px solid #ccc;
                border-bottom: none;
                border-radius: 4px 4px 0 0;
            }
            .tab.active {
                background-color: #fff;
                border-bottom: 1px solid #fff;
                margin-bottom: -1px;
                position: relative;
            }
            .tab-content {
                display: none;
                padding: 15px;
                border: 1px solid #ccc;
                border-radius: 0 4px 4px 4px;
            }
            .tab-content.active {
                display: block;
            }
        </style>
    </head>
    <body>
        <h1>Dependency Map</h1>

        <div class="search">
            <input type="text" id="searchInput" placeholder="Search for files...">
            <button onclick="search()">Search</button>
            <button onclick="expandAll()">Expand All</button>
            <button onclick="collapseAll()">Collapse All</button>
        </div>

        <div style="margin-bottom: 15px;">
            <div style="display: inline-block; margin-right: 20px;">
                <span style="display: inline-block; width: 15px; height: 15px; background-color: #ffdddd; border: 1px solid #ff9999; margin-right: 5px;"></span>
                <span>Unused Files (potentially dead code)</span>
            </div>
        </div>

        <div class="tab-container">
            <div class="tab active" onclick="switchTab('fileView')">File View</div>
            <div class="tab" onclick="switchTab('dependencyMatrix')">Dependency Matrix</div>
        </div>

        <div id="fileView" class="tab-content active">
            <div class="tree" id="tree">
    """

    # Sort files by name for better readability
    sorted_files = sorted(dependency_map.keys())

    # Build a reverse dependency map (which files import this file)
    reverse_dependency_map = {}
    for file_path in sorted_files:
        reverse_dependency_map[file_path] = []

    for file_path, dependencies in dependency_map.items():
        for dependency in dependencies:
            if dependency in reverse_dependency_map:
                reverse_dependency_map[dependency].append(file_path)

    # Add each file and its dependencies
    for file_path in sorted_files:
        dependencies = dependency_map[file_path]
        imported_by = reverse_dependency_map[file_path]

        total_relations = len(dependencies) + len(imported_by)

        # Check if this is an unused file
        is_unused = file_path in unused_files
        unused_class = 'unused-file' if is_unused else ''
        unused_label = ' [UNUSED]' if is_unused else ''

        html += f"""
        <div class="file {unused_class}" id="{file_path.replace('/', '_')}">
            <span class="toggle" onclick="toggle(this)">[+]</span>
            <span>{file_path}{unused_label}</span> ({total_relations} relationships: {len(dependencies)} imports, {len(imported_by)} imported by)
            <div class="dependencies">
        """

        # Files this file imports (dependencies from)
        html += '<div class="section-title imports">Files this file imports:</div>\n'
        if dependencies:
            for dependency in sorted(dependencies):
                html += f'<div class="dependency-item imports">{dependency}</div>\n'
        else:
            html += '<div class="dependency-item">No imports</div>\n'

        # Files that import this file (dependencies to)
        html += '<div class="section-title imported-by">Files that import this file:</div>\n'
        if imported_by:
            for importer in sorted(imported_by):
                html += f'<div class="dependency-item imported-by">{importer}</div>\n'
        else:
            html += '<div class="dependency-item">Not imported by any file</div>\n'

        html += """
            </div>
        </div>
        """
    
    # Create the dependency matrix view
    html += """
            </div>
        </div>

        <div id="dependencyMatrix" class="tab-content">
            <div class="matrix-container">
                <table id="dependencyTable" border="1" cellspacing="0" cellpadding="5" style="border-collapse: collapse;">
                    <thead>
                        <tr>
                            <th>File</th>
                            <th>Imports</th>
                            <th>Imported By</th>
                            <th>Total Relationships</th>
                        </tr>
                    </thead>
                    <tbody>
    """

    # Add rows to the dependency matrix
    for file_path in sorted_files:
        dependencies = dependency_map[file_path]
        imported_by = reverse_dependency_map[file_path]
        total_relations = len(dependencies) + len(imported_by)

        # Check if this is an unused file
        is_unused = file_path in unused_files
        unused_class = 'class="unused-file"' if is_unused else ''
        unused_label = ' [UNUSED]' if is_unused else ''

        html += f"""
                        <tr {unused_class}>
                            <td>{file_path}{unused_label}</td>
                            <td>{len(dependencies)}</td>
                            <td>{len(imported_by)}</td>
                            <td>{total_relations}</td>
                        </tr>
        """

    html += """
                    </tbody>
                </table>
            </div>
        </div>

        <script>
            function toggle(element) {
                var dependencies = element.parentElement.querySelector('.dependencies');
                if (dependencies.style.display === 'block') {
                    dependencies.style.display = 'none';
                    element.textContent = '[+]';
                } else {
                    dependencies.style.display = 'block';
                    element.textContent = '[-]';
                }
            }

            function search() {
                var searchText = document.getElementById('searchInput').value.toLowerCase();
                var files = document.querySelectorAll('.file');

                // Remove all highlights
                var highlights = document.querySelectorAll('.highlight');
                highlights.forEach(function(element) {
                    element.classList.remove('highlight');
                });

                if (searchText.trim() === '') {
                    return;
                }

                files.forEach(function(file) {
                    var fileText = file.textContent.toLowerCase();
                    if (fileText.includes(searchText)) {
                        file.classList.add('highlight');

                        // Expand the file
                        var toggle = file.querySelector('.toggle');
                        var dependencies = file.querySelector('.dependencies');
                        dependencies.style.display = 'block';
                        toggle.textContent = '[-]';

                        // Scroll to the first match
                        if (file === document.querySelector('.highlight')) {
                            file.scrollIntoView();
                        }
                    }
                });
            }

            function expandAll() {
                var toggles = document.querySelectorAll('.toggle');
                toggles.forEach(function(toggle) {
                    var dependencies = toggle.parentElement.querySelector('.dependencies');
                    dependencies.style.display = 'block';
                    toggle.textContent = '[-]';
                });
            }

            function collapseAll() {
                var toggles = document.querySelectorAll('.toggle');
                toggles.forEach(function(toggle) {
                    var dependencies = toggle.parentElement.querySelector('.dependencies');
                    dependencies.style.display = 'none';
                    toggle.textContent = '[+]';
                });
            }

            function switchTab(tabId) {
                // Hide all tab contents
                document.querySelectorAll('.tab-content').forEach(function(content) {
                    content.classList.remove('active');
                });

                // Deactivate all tabs
                document.querySelectorAll('.tab').forEach(function(tab) {
                    tab.classList.remove('active');
                });

                // Activate the selected tab and content
                document.getElementById(tabId).classList.add('active');
                document.querySelector('.tab[onclick="switchTab(\\''+tabId+'\\')"]').classList.add('active');
            }
        </script>
    </body>
    </html>
    """
    
    # Write the HTML file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"HTML visualization saved to {output_file}")

def main():
    """Main function to visualize the dependency map."""
    # Load the dependency map
    dependency_map = load_dependency_map('dependency_map.json')
    
    if not dependency_map:
        print("No dependency map found. Please run generate_dependency_map.py first.")
        return
    
    # Create an HTML visualization
    create_html_visualization(dependency_map)
    
    # Try to create a graph visualization if networkx and matplotlib are available
    try:
        G = create_graph(dependency_map)
        visualize_graph(G)
    except ImportError:
        print("Could not create graph visualization. Please install networkx and matplotlib.")
    except Exception as e:
        print(f"Error creating graph visualization: {str(e)}")

if __name__ == "__main__":
    main()