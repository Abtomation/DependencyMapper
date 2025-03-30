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

def create_graph(dependency_map: Dict[str, List[str]]) -> nx.DiGraph:
    """
    Create a directed graph from the dependency map.
    
    Args:
        dependency_map: The dependency map
        
    Returns:
        The directed graph
    """
    G = nx.DiGraph()
    
    # Add nodes
    for file_path in dependency_map.keys():
        # Use just the filename for display
        node_name = os.path.basename(file_path)
        G.add_node(node_name, full_path=file_path)
    
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
    
    # Draw nodes
    nx.draw_networkx_nodes(G, pos, node_size=500, node_color='lightblue', alpha=0.8)
    
    # Draw edges
    nx.draw_networkx_edges(G, pos, width=1.0, alpha=0.5, arrows=True, arrowsize=20)
    
    # Draw labels
    nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
    
    # Save the figure
    plt.axis('off')
    plt.tight_layout()
    plt.savefig(output_file, dpi=300, bbox_inches='tight')
    print(f"Graph visualization saved to {output_file}")
    
    # Close the figure to free memory
    plt.close()

def create_html_visualization(dependency_map: Dict[str, List[str]], output_file: str = 'dependency_graph.html') -> None:
    """
    Create an HTML visualization of the dependency map.
    
    Args:
        dependency_map: The dependency map
        output_file: The output file path
    """
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
                margin: 5px 0;
                cursor: pointer;
            }
            .dependencies {
                margin-left: 20px;
                display: none;
            }
            .toggle {
                cursor: pointer;
                color: blue;
                text-decoration: underline;
            }
            .search {
                margin-bottom: 20px;
            }
            #searchInput {
                padding: 5px;
                width: 300px;
            }
            .highlight {
                background-color: yellow;
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
        
        <div class="tree" id="tree">
    """
    
    # Sort files by name for better readability
    sorted_files = sorted(dependency_map.keys())
    
    # Add each file and its dependencies
    for file_path in sorted_files:
        dependencies = dependency_map[file_path]
        html += f"""
        <div class="file" id="{file_path.replace('/', '_')}">
            <span class="toggle" onclick="toggle(this)">[+]</span> 
            <span>{file_path}</span> ({len(dependencies)} dependencies)
            <div class="dependencies">
        """
        
        if dependencies:
            for dependency in sorted(dependencies):
                html += f'<div>{dependency}</div>\n'
        else:
            html += '<div>No dependencies</div>\n'
        
        html += """
            </div>
        </div>
        """
    
    # Add JavaScript for interactivity
    html += """
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