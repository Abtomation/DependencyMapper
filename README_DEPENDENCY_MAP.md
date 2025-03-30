# Dependency Map Generator

This set of scripts helps you analyze and visualize the dependencies between Python files in the TimeTracking project.

## Overview

The dependency mapper starts from `main.py` and recursively analyzes all imported modules, creating a map of which file depends on which other files. This can be useful for:

- Understanding the project structure
- Identifying highly coupled components
- Planning refactoring efforts
- Documenting the codebase

## Files

- `dependency_mapper.py` - The core module that analyzes Python files and builds the dependency map
- `generate_dependency_map.py` - Script to generate the dependency map and save it to a JSON file
- `visualize_dependencies.py` - Script to create visualizations of the dependency map
- `dependency_map.json` - The generated dependency map (after running the generator)

## Usage

### Generating the Dependency Map

To generate the dependency map, run:

```bash
python generate_dependency_map.py
```

This will:
1. Start from `main.py`
2. Recursively analyze all imported modules
3. Create a map of dependencies
4. Save the map to `dependency_map.json`

### Visualizing the Dependencies

To visualize the dependency map, run:

```bash
python visualize_dependencies.py
```

This will:
1. Load the dependency map from `dependency_map.json`
2. Create an HTML visualization (`dependency_graph.html`)
3. If networkx and matplotlib are available, also create a graph visualization (`dependency_graph.png`)

## HTML Visualization Features

The HTML visualization provides:

- A tree view of all files and their dependencies
- Ability to expand/collapse individual files
- Search functionality to find specific files
- Expand All / Collapse All buttons

## Requirements

- Python 3.6+
- For graph visualization: networkx and matplotlib (optional)

## Notes

- External modules (standard library and third-party packages) are excluded from the dependency map
- The mapper attempts to resolve imports in various ways, but some imports might not be resolved correctly
- The visualization focuses on direct dependencies; indirect dependencies can be inferred by following the chain

## Example Output

The dependency map is a JSON file with the following structure:

```json
{
  "main.py": [
    "ui/ui.py"
  ],
  "ui/ui.py": [
    "database.py",
    "ui/company_ui.py",
    "ui/invoices_ui_improved.py",
    "ui/customer_ui_improved.py",
    "ui/helpers/ui_table_manager.py",
    "ui/db_switch_ui.py",
    "ui/field_manager_ui_improved.py",
    "ui/reports_ui.py",
    "data/CRUD_helpers.py",
    "services/log_service.py",
    "services/customer_service_extended.py",
    "logging_manager.py"
  ],
  ...
}
```

Each key is a file path, and its value is an array of file paths that it depends on.