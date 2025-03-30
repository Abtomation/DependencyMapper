# Dependency Map Generator

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

This set of scripts helps you analyze and visualize the dependencies between Python files in a project.

![Dependency Mapper UI](https://github.com/Abtomation/DependencyMapper/blob/master/screenshots/2025-03-30_Dependency_Mapper.png)

## Overview

The dependency mapper starts from a specified Python file and recursively analyzes all imported modules, creating a map of which file depends on which other files. This can be useful for:

- Understanding the project structure
- Identifying highly coupled components
- Planning refactoring efforts
- Documenting the codebase

## Files

- `dependency_mapper.py` - The core module that analyzes Python files and builds the dependency map
- `generate_dependency_map.py` - Script to generate the dependency map and save it to a JSON file
- `visualize_dependencies.py` - Script to create visualizations of the dependency map
- `dependency_mapper_ui.py` - Graphical user interface for the dependency mapper
- `dependency_map.json` - The generated dependency map (after running the generator)

## Usage

### Using the Graphical User Interface

The easiest way to use the dependency mapper is through the graphical user interface:

```bash
python dependency_mapper_ui.py
```

The UI allows you to:
1. Select the folder to analyze
2. Select the output folder for the dependency map and visualizations
3. Select the starting file for the analysis
4. Choose which visualizations to create
5. View dependencies from and to each file in an interactive interface

The UI has two main tabs:
- **Configuration**: Set up the analysis parameters and generate the dependency map
- **Dependencies**: View and explore the dependencies between files
  - See which files a selected file imports
  - See which files import the selected file
  - Search for specific files
  - Open the HTML visualization in a web browser

![Dependency Mapper UI](https://github.com/Abtomation/DependencyMapper/blob/master/screenshots/2025-03-30_Dependency_Mapper.png)

### Generating the Dependency Map from Command Line

To generate the dependency map from the command line, run:

```bash
python generate_dependency_map.py
```

This will:
1. Start from `main.py` in the current directory
2. Recursively analyze all imported modules
3. Create a map of dependencies
4. Save the map to `dependency_map.json`

### Visualizing the Dependencies from Command Line

To visualize the dependency map from the command line, run:

```bash
python visualize_dependencies.py
```

This will:
1. Load the dependency map from `dependency_map.json`
2. Create an HTML visualization (`dependency_graph.html`)
3. If networkx and matplotlib are available, also create a graph visualization (`dependency_graph.png`)

## Visualization Features

### HTML Visualization

The HTML visualization provides:

- A tree view of all files and their dependencies
- Ability to expand/collapse individual files
- Search functionality to find specific files
- Expand All / Collapse All buttons
- Two views:
  - **File View**: Shows each file with its imports and files that import it
  - **Dependency Matrix**: Shows a table with import counts for each file

### UI Dependency Viewer

The UI dependency viewer provides:

- Interactive selection of files to view their dependencies
- Split view showing:
  - Files that the selected file imports (dependencies from)
  - Files that import the selected file (dependencies to)
- Navigation by double-clicking on dependencies to jump to that file
- Search functionality to find specific files
- Direct access to the HTML visualization
- Persistence of settings and last selected file between sessions

## Installation

### Prerequisites

- Python 3.6+
- For graph visualization: networkx and matplotlib (optional)
- For the UI: tkinter (included with most Python installations)

### Clone the Repository

```bash
git clone https://github.com/Abtomation/dependency-mapper.git
cd dependency-mapper
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Run the Application

```bash
python dependency_mapper_ui.py
```

## Notes

- External modules (standard library and third-party packages) are excluded from the dependency map
- The mapper attempts to resolve imports in various ways, but some imports might not be resolved correctly
- The visualization focuses on direct dependencies; indirect dependencies can be inferred by following the chain

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

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