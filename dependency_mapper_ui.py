"""
Dependency Mapper UI

This script provides a graphical user interface for the dependency mapper.
It allows users to:
1. Select the folder to analyze
2. Select the output folder for the dependency map and visualizations
3. Select the starting file for the analysis
4. View dependencies from and to each file
5. Click on dependencies to navigate between files
"""

import os
import json
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import threading
import time
import webbrowser
import configparser
from typing import Dict, List, Optional, Tuple, Any

# Import the dependency mapper
from dependency_mapper import DependencyMapper
import visualize_dependencies

class DependencyMapperUI:
    """UI for the dependency mapper."""

    # Settings file path
    SETTINGS_FILE = "dependency_mapper_settings.ini"

    def __init__(self, root):
        """
        Initialize the UI.

        Args:
            root: The tkinter root window
        """
        self.root = root
        self.root.title("Dependency Mapper")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Variables
        self.source_folder = tk.StringVar()
        self.output_folder = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.progress = tk.DoubleVar(value=0)
        self.search_term = tk.StringVar()
        self.last_selected_file = tk.StringVar()
        self.selected_system = tk.StringVar()

        # Set default values
        self.source_folder.set(os.getcwd())
        self.output_folder.set(os.getcwd())

        # Store the dependency map
        self.dependency_map = {}
        self.reverse_dependency_map = {}
        self.systems = []  # List of systems (connected components)

        # Load settings from file
        self._load_settings()

        # Create the UI
        self._create_ui()

        # Bind window close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)

        # Bind tab change event to update views
        self.notebook.bind("<<NotebookTabChanged>>", self._on_tab_changed)
    
    def _create_ui(self):
        """Create the UI elements."""
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create notebook (tabs)
        self.notebook = ttk.Notebook(main_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Configuration tab
        config_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(config_frame, text="Configuration")

        # Dependencies tab
        self.dependencies_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.dependencies_frame, text="Dependencies")

        # Standalone Files tab (files without dependencies)
        self.standalone_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.standalone_frame, text="Standalone Files")

        # Unused Files tab (potentially dead code)
        self.unused_frame = ttk.Frame(self.notebook, padding="10")
        self.notebook.add(self.unused_frame, text="Unused Files")

        # Create the configuration tab content
        self._create_config_tab(config_frame)

        # Create the dependencies tab content
        self._create_dependencies_tab(self.dependencies_frame)

        # Create the standalone files tab content
        self._create_standalone_files_tab(self.standalone_frame)

        # Create the unused files tab content
        self._create_unused_files_tab(self.unused_frame)

        # Status and progress
        status_frame = ttk.Frame(main_frame)
        status_frame.pack(fill=tk.X, pady=5, side=tk.BOTTOM)

        ttk.Label(status_frame, text="Status:").pack(side=tk.LEFT, padx=5)
        ttk.Label(status_frame, textvariable=self.status).pack(side=tk.LEFT, padx=5)

        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress, maximum=100)
        self.progress_bar.pack(side=tk.RIGHT, padx=5, fill=tk.X, expand=True)

    def _create_config_tab(self, parent):
        """Create the configuration tab content."""
        # Source folder selection
        source_frame = ttk.LabelFrame(parent, text="Source Folder", padding="5")
        source_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(source_frame, textvariable=self.source_folder, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(source_frame, text="Browse...", command=self._browse_source_folder).pack(side=tk.RIGHT, padx=5)

        # Output folder selection
        output_frame = ttk.LabelFrame(parent, text="Output Folder", padding="5")
        output_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(output_frame, textvariable=self.output_folder, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(output_frame, text="Browse...", command=self._browse_output_folder).pack(side=tk.RIGHT, padx=5)

        # Information about automatic scanning
        info_frame = ttk.LabelFrame(parent, text="Automatic Scanning", padding="5")
        info_frame.pack(fill=tk.X, pady=5)

        info_text = (
            "The dependency mapper will automatically scan all Python files in the source folder "
            "and identify systems. A system is a group of files that have dependencies with each other "
            "but not with files from other systems."
        )
        ttk.Label(info_frame, text=info_text, wraplength=800, justify=tk.LEFT).pack(
            fill=tk.X, padx=5, pady=5)

        # Options frame
        options_frame = ttk.LabelFrame(parent, text="Options", padding="5")
        options_frame.pack(fill=tk.X, pady=5)

        # Create HTML visualization checkbox
        self.create_html = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create HTML visualization", variable=self.create_html).pack(anchor=tk.W, padx=5)

        # Create graph visualization checkbox
        self.create_graph = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Create graph visualization (requires networkx and matplotlib)",
                        variable=self.create_graph).pack(anchor=tk.W, padx=5)

        # Action buttons
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Generate Dependency Map", command=self._generate_map).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Exit", command=self.root.destroy).pack(side=tk.RIGHT, padx=5)

    def _create_standalone_files_tab(self, parent):
        """Create the standalone files tab content."""
        # Explanation frame
        explanation_frame = ttk.LabelFrame(parent, text="About Standalone Files", padding="10")
        explanation_frame.pack(fill=tk.X, pady=5)

        explanation_text = (
            "Standalone files are Python files that don't import any other project files. "
            "These files typically fall into these categories:\n\n"
            "• Entry Points: Main scripts meant to be run directly\n"
            "• Utility Libraries: Self-contained utility modules\n"
            "• Configuration Files: Files defining constants or settings\n"
            "• Standalone Modules: Independent, reusable modules\n"
            "• Dead Code: Files no longer used but not removed\n"
            "• Test Files: Test modules that don't import implementation\n"
            "• Documentation Generators: Scripts for generating documentation"
        )

        ttk.Label(explanation_frame, text=explanation_text, wraplength=800, justify=tk.LEFT).pack(
            fill=tk.X, padx=5, pady=5)

    def _create_unused_files_tab(self, parent):
        """Create the unused files tab content."""
        # Explanation frame
        explanation_frame = ttk.LabelFrame(parent, text="About Unused Files", padding="10")
        explanation_frame.pack(fill=tk.X, pady=5)

        explanation_text = (
            "Unused files are Python files that are potentially dead code. "
            "These files meet the following criteria:\n\n"
            "• Not imported by any other files in the project\n"
            "• Don't appear to be entry points (no __main__ block, not named main.py, etc.)\n\n"
            "These files might be candidates for cleanup or might need to be integrated "
            "into the project properly. Review each file carefully before removing."
        )

        ttk.Label(explanation_frame, text=explanation_text, wraplength=800, justify=tk.LEFT).pack(
            fill=tk.X, padx=5, pady=5)

        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=5)

        self.unused_search_term = tk.StringVar()
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.unused_search_term, width=30).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search",
                  command=self._search_unused_files).pack(side=tk.LEFT, padx=5)

        # Files frame
        files_frame = ttk.LabelFrame(parent, text="Potentially Unused Files")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create treeview for unused files
        self.unused_tree = ttk.Treeview(files_frame, columns=("file", "last_modified"), show="headings")
        self.unused_tree.heading("file", text="File Path")
        self.unused_tree.heading("last_modified", text="Last Modified")
        self.unused_tree.column("file", width=400)
        self.unused_tree.column("last_modified", width=200)
        self.unused_tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click to jump to the selected file in Dependencies tab
        self.unused_tree.bind("<Double-1>", self._on_unused_double_click)

        # Add tooltip-like hint
        ttk.Label(files_frame, text="Double-click to view file in Dependencies tab",
                 font=("", 8, "italic")).pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Add scrollbar
        unused_scroll = ttk.Scrollbar(files_frame, orient=tk.VERTICAL,
                                     command=self.unused_tree.yview)
        unused_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.unused_tree.configure(yscrollcommand=unused_scroll.set)

        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Refresh",
                  command=self._refresh_unused_files).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Export to CSV",
                  command=self._export_unused_files).pack(side=tk.RIGHT, padx=5)

        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=5)

        self.standalone_search_term = tk.StringVar()
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.standalone_search_term, width=30).pack(
            side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search",
                  command=self._search_standalone_files).pack(side=tk.LEFT, padx=5)

        # Files frame
        files_frame = ttk.LabelFrame(parent, text="Files Without Dependencies")
        files_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Create treeview for standalone files
        self.standalone_tree = ttk.Treeview(files_frame, columns=("file", "type"), show="headings")
        self.standalone_tree.heading("file", text="File Path")
        self.standalone_tree.heading("type", text="Possible Type")
        self.standalone_tree.column("file", width=400)
        self.standalone_tree.column("type", width=200)
        self.standalone_tree.pack(fill=tk.BOTH, expand=True)

        # Bind double-click to jump to the selected file in Dependencies tab
        self.standalone_tree.bind("<Double-1>", self._on_standalone_double_click)

        # Add tooltip-like hint
        ttk.Label(files_frame, text="Double-click to view file in Dependencies tab",
                 font=("", 8, "italic")).pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Add scrollbar
        standalone_scroll = ttk.Scrollbar(files_frame, orient=tk.VERTICAL,
                                         command=self.standalone_tree.yview)
        standalone_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.standalone_tree.configure(yscrollcommand=standalone_scroll.set)

        # Button frame
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Refresh",
                  command=self._refresh_standalone_files).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Export to CSV",
                  command=self._export_standalone_files).pack(side=tk.RIGHT, padx=5)

    def _create_dependencies_tab(self, parent):
        """Create the dependencies tab content."""
        # Top frame for system and file selection
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=5)

        # System selection dropdown
        ttk.Label(top_frame, text="Select System:").pack(side=tk.LEFT, padx=5)
        self.system_combo = ttk.Combobox(top_frame, width=30, state="readonly", textvariable=self.selected_system)
        self.system_combo.pack(side=tk.LEFT, padx=5)
        self.system_combo.bind("<<ComboboxSelected>>", self._on_system_selected)

        # File selection dropdown
        ttk.Label(top_frame, text="Select File:").pack(side=tk.LEFT, padx=5)
        self.file_combo = ttk.Combobox(top_frame, width=50, state="readonly")
        self.file_combo.pack(side=tk.LEFT, padx=5)
        self.file_combo.bind("<<ComboboxSelected>>", self._on_file_selected)

        # Search frame
        search_frame = ttk.Frame(parent)
        search_frame.pack(fill=tk.X, pady=5)

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(search_frame, textvariable=self.search_term, width=30).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(search_frame, text="Search", command=self._search_dependencies).pack(side=tk.LEFT, padx=5)

        # Create a frame with two panes
        paned_window = ttk.PanedWindow(parent, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=5)

        # Left pane: Files this file imports
        imports_frame = ttk.LabelFrame(paned_window, text="Files this file imports")
        paned_window.add(imports_frame, weight=1)

        # Right pane: Files that import this file
        imported_by_frame = ttk.LabelFrame(paned_window, text="Files that import this file")
        paned_window.add(imported_by_frame, weight=1)

        # Create treeviews for dependencies
        self.imports_tree = ttk.Treeview(imports_frame, columns=("file",), show="headings")
        self.imports_tree.heading("file", text="File Path")
        self.imports_tree.pack(fill=tk.BOTH, expand=True)
        # Bind double-click to jump to the selected file
        self.imports_tree.bind("<Double-1>", self._on_dependency_double_click)
        # Add tooltip-like hint
        ttk.Label(imports_frame, text="Double-click to jump to file", font=("", 8, "italic")).pack(anchor=tk.W, padx=5, pady=(0, 5))

        self.imported_by_tree = ttk.Treeview(imported_by_frame, columns=("file",), show="headings")
        self.imported_by_tree.heading("file", text="File Path")
        self.imported_by_tree.pack(fill=tk.BOTH, expand=True)
        # Bind double-click to jump to the selected file
        self.imported_by_tree.bind("<Double-1>", self._on_dependency_double_click)
        # Add tooltip-like hint
        ttk.Label(imported_by_frame, text="Double-click to jump to file", font=("", 8, "italic")).pack(anchor=tk.W, padx=5, pady=(0, 5))

        # Add scrollbars
        imports_scroll = ttk.Scrollbar(imports_frame, orient=tk.VERTICAL, command=self.imports_tree.yview)
        imports_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.imports_tree.configure(yscrollcommand=imports_scroll.set)

        imported_by_scroll = ttk.Scrollbar(imported_by_frame, orient=tk.VERTICAL, command=self.imported_by_tree.yview)
        imported_by_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.imported_by_tree.configure(yscrollcommand=imported_by_scroll.set)

        # Button to open HTML visualization
        button_frame = ttk.Frame(parent)
        button_frame.pack(fill=tk.X, pady=10)

        ttk.Button(button_frame, text="Open HTML Visualization", command=self._open_html_visualization).pack(side=tk.RIGHT, padx=5)
        ttk.Button(button_frame, text="Refresh Dependencies", command=self._refresh_dependencies).pack(side=tk.RIGHT, padx=5)
    
    def _browse_source_folder(self):
        """Browse for the source folder."""
        folder = filedialog.askdirectory(initialdir=self.source_folder.get())
        if folder:
            self.source_folder.set(folder)
            # Update the output folder to match if it's the default
            if self.output_folder.get() == os.getcwd():
                self.output_folder.set(folder)
    
    def _browse_output_folder(self):
        """Browse for the output folder."""
        folder = filedialog.askdirectory(initialdir=self.output_folder.get())
        if folder:
            self.output_folder.set(folder)
    
    def _browse_start_file(self):
        """Browse for the start file."""
        file = filedialog.askopenfilename(
            initialdir=self.source_folder.get(),
            filetypes=[("Python files", "*.py"), ("All files", "*.*")]
        )
        if file:
            # Make the path relative to the source folder if possible
            try:
                rel_path = os.path.relpath(file, self.source_folder.get())
                self.start_file.set(rel_path)
            except ValueError:
                # If the file is on a different drive, use the absolute path
                self.start_file.set(file)
    
    def _update_status(self, message, progress=None):
        """
        Update the status message and progress bar.
        
        Args:
            message: The status message
            progress: The progress value (0-100), or None to leave unchanged
        """
        self.status.set(message)
        if progress is not None:
            self.progress.set(progress)
        self.root.update_idletasks()
    
    def _generate_map(self):
        """Generate the dependency map."""
        # Validate inputs
        source_folder = self.source_folder.get()
        output_folder = self.output_folder.get()

        if not os.path.isdir(source_folder):
            messagebox.showerror("Error", "Source folder does not exist.")
            return

        if not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Output folder does not exist.")
            return

        # Start the generation in a separate thread to keep the UI responsive
        threading.Thread(target=self._generate_map_thread, args=(source_folder, output_folder)).start()
    
    def _generate_map_thread(self, source_folder, output_folder):
        """
        Generate the dependency map in a separate thread.

        Args:
            source_folder: The source folder
            output_folder: The output folder
        """
        try:
            self._update_status("Initializing...", 0)

            # Record start time
            start_time = time.time()

            # Create a dependency mapper
            self._update_status("Creating dependency mapper...", 10)
            mapper = DependencyMapper(source_folder)

            # Map dependencies for all Python files
            self._update_status("Mapping dependencies for all Python files...", 20)
            self.dependency_map = mapper.map_dependencies()

            # Build reverse dependency map
            self._update_status("Building reverse dependency map...", 40)
            self._build_reverse_dependency_map()

            # Identify systems
            self._update_status("Identifying systems...", 50)
            self.systems = mapper.identify_systems()

            # Identify unused files
            self._update_status("Identifying unused files...", 60)
            self.unused_files = mapper.identify_unused_files()

            # Calculate statistics
            total_files = len(self.dependency_map)
            total_dependencies = sum(len(deps) for deps in self.dependency_map.values())
            files_with_no_deps = sum(1 for deps in self.dependency_map.values() if not deps)
            max_deps_file = max(self.dependency_map.items(), key=lambda x: len(x[1]), default=("None", []))
            total_systems = len(self.systems)
            total_unused = len(self.unused_files)

            # Save the dependency map to a JSON file
            self._update_status("Saving dependency map...", 60)
            output_file = os.path.join(output_folder, 'dependency_map.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.dependency_map, f, indent=2, sort_keys=True)

            # Create visualizations
            if self.create_html.get():
                self._update_status("Creating HTML visualization...", 70)
                self.html_output = os.path.join(output_folder, 'dependency_graph.html')
                visualize_dependencies.create_html_visualization(
                    self.dependency_map,
                    self.html_output,
                    unused_files=self.unused_files
                )

            if self.create_graph.get():
                try:
                    self._update_status("Creating graph visualization...", 80)
                    graph_output = os.path.join(output_folder, 'dependency_graph.png')
                    G = visualize_dependencies.create_graph(
                        self.dependency_map,
                        unused_files=self.unused_files
                    )
                    visualize_dependencies.visualize_graph(G, graph_output)
                except ImportError:
                    messagebox.showwarning("Warning", "Could not create graph visualization. Please install networkx and matplotlib.")
                except Exception as e:
                    messagebox.showwarning("Warning", f"Error creating graph visualization: {str(e)}")

            # Record end time and calculate duration
            end_time = time.time()
            duration = end_time - start_time

            # Update status with summary
            self._update_status(f"Complete. Time taken: {duration:.2f} seconds", 100)

            # Show summary
            summary = (
                f"Dependency Map Generation Complete\n\n"
                f"Dependency map saved to: {output_file}\n"
                f"Total files analyzed: {total_files}\n"
                f"Total dependencies found: {total_dependencies}\n"
                f"Files with no dependencies: {files_with_no_deps}\n"
                f"File with most dependencies: {max_deps_file[0]} ({len(max_deps_file[1])} dependencies)\n"
                f"Systems identified: {total_systems}\n"
                f"Potentially unused files: {total_unused}\n"
                f"Time taken: {duration:.2f} seconds"
            )
            messagebox.showinfo("Summary", summary)

            # Update the dependencies view (which also updates standalone files view)
            self._update_dependencies_view()

            # If there are standalone files, switch to that tab, otherwise go to dependencies tab
            standalone_files = self._get_standalone_files()
            if standalone_files:
                self.notebook.select(2)  # Select the standalone files tab
            else:
                self.notebook.select(1)  # Select the dependencies tab

        except Exception as e:
            self._update_status(f"Error: {str(e)}", 0)
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def _build_reverse_dependency_map(self):
        """Build a reverse dependency map (which files import this file)."""
        self.reverse_dependency_map = {}

        # Initialize with empty lists
        for file_path in self.dependency_map.keys():
            self.reverse_dependency_map[file_path] = []

        # Fill in the reverse dependencies
        for file_path, dependencies in self.dependency_map.items():
            for dependency in dependencies:
                if dependency in self.reverse_dependency_map:
                    self.reverse_dependency_map[dependency].append(file_path)

    def _get_standalone_files(self):
        """
        Get files that don't have any dependencies (don't import any other project files).

        Returns:
            A list of file paths that don't have dependencies
        """
        if not self.dependency_map:
            return []

        standalone_files = []
        for file_path, dependencies in self.dependency_map.items():
            if not dependencies:
                standalone_files.append(file_path)

        return sorted(standalone_files)

    def _guess_file_type(self, file_path):
        """
        Guess the type of a standalone file based on its name and location.

        Args:
            file_path: The file path to analyze

        Returns:
            A string describing the likely type of the file
        """
        file_name = os.path.basename(file_path)
        dir_name = os.path.dirname(file_path)

        # Check if it's imported by other files
        imported_by = self.reverse_dependency_map.get(file_path, [])

        if not imported_by:
            if file_name.startswith('__main__') or file_name == 'main.py':
                return "Entry Point"
            elif 'test' in file_name.lower() or 'test' in dir_name.lower():
                return "Test File"
            elif file_name.startswith('setup') or file_name.endswith('setup.py'):
                return "Setup/Configuration"
            elif 'config' in file_name.lower() or 'settings' in file_name.lower():
                return "Configuration"
            elif file_name.startswith('__init__'):
                return "Package Initializer"
            elif 'doc' in file_name.lower() or 'doc' in dir_name.lower():
                return "Documentation"
            else:
                return "Standalone Module"
        else:
            return "Utility Library"

    def _update_standalone_files_view(self):
        """Update the standalone files view with current data."""
        # Clear the treeview
        for item in self.standalone_tree.get_children():
            self.standalone_tree.delete(item)

        # Get standalone files
        standalone_files = self._get_standalone_files()

        # Add files to the treeview
        for file_path in standalone_files:
            file_type = self._guess_file_type(file_path)
            self.standalone_tree.insert("", "end", values=(file_path, file_type))

    def _search_standalone_files(self):
        """Search for standalone files matching the search term."""
        search_term = self.standalone_search_term.get().lower()

        # Clear the treeview
        for item in self.standalone_tree.get_children():
            self.standalone_tree.delete(item)

        # Get standalone files
        standalone_files = self._get_standalone_files()

        # Add matching files to the treeview
        for file_path in standalone_files:
            if search_term in file_path.lower():
                file_type = self._guess_file_type(file_path)
                self.standalone_tree.insert("", "end", values=(file_path, file_type))

    def _refresh_standalone_files(self):
        """Refresh the standalone files view."""
        self._update_standalone_files_view()

    def _on_standalone_double_click(self, event):
        """Handle double-click on a standalone file."""
        # Get the selected item
        selection = self.standalone_tree.selection()
        if not selection:
            return

        # Get the file path
        file_path = self.standalone_tree.item(selection[0], "values")[0]

        # Switch to the Dependencies tab
        self.notebook.select(1)  # Select the Dependencies tab

        # Select the file in the combobox
        if file_path in self.file_combo["values"]:
            self.file_combo.set(file_path)
            self._on_file_selected(None)

    def _update_unused_files_view(self):
        """Update the unused files view with current data."""
        # Clear the treeview
        for item in self.unused_tree.get_children():
            self.unused_tree.delete(item)

        if not hasattr(self, 'unused_files') or not self.unused_files:
            return

        # Add files to the treeview
        for file_path in self.unused_files:
            # Get last modified time
            try:
                abs_path = os.path.join(self.source_folder.get(), file_path)
                last_modified = time.strftime('%Y-%m-%d %H:%M:%S',
                                             time.localtime(os.path.getmtime(abs_path)))
            except:
                last_modified = "Unknown"

            self.unused_tree.insert("", "end", values=(file_path, last_modified))

    def _search_unused_files(self):
        """Search for unused files matching the search term."""
        search_term = self.unused_search_term.get().lower()

        # Clear the treeview
        for item in self.unused_tree.get_children():
            self.unused_tree.delete(item)

        if not hasattr(self, 'unused_files') or not self.unused_files:
            return

        # Add matching files to the treeview
        for file_path in self.unused_files:
            if search_term in file_path.lower():
                # Get last modified time
                try:
                    abs_path = os.path.join(self.source_folder.get(), file_path)
                    last_modified = time.strftime('%Y-%m-%d %H:%M:%S',
                                                 time.localtime(os.path.getmtime(abs_path)))
                except:
                    last_modified = "Unknown"

                self.unused_tree.insert("", "end", values=(file_path, last_modified))

    def _refresh_unused_files(self):
        """Refresh the unused files view."""
        self._update_unused_files_view()

    def _on_unused_double_click(self, event):
        """Handle double-click on an unused file."""
        # Get the selected item
        selection = self.unused_tree.selection()
        if not selection:
            return

        # Get the file path
        file_path = self.unused_tree.item(selection[0], "values")[0]

        # Switch to the Dependencies tab
        self.notebook.select(1)  # Select the Dependencies tab

        # Select the file in the combobox
        if file_path in self.file_combo["values"]:
            self.file_combo.set(file_path)
            self._on_file_selected(None)

    def _export_unused_files(self):
        """Export the unused files to a CSV file."""
        if not hasattr(self, 'unused_files') or not self.unused_files:
            messagebox.showinfo("Info", "No unused files available. Generate a map first.")
            return

        # Ask for the output file
        output_file = filedialog.asksaveasfilename(
            initialdir=self.output_folder.get(),
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Unused Files"
        )

        if not output_file:
            return

        try:
            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["File Path", "Last Modified"])

                for file_path in self.unused_files:
                    # Get last modified time
                    try:
                        abs_path = os.path.join(self.source_folder.get(), file_path)
                        last_modified = time.strftime('%Y-%m-%d %H:%M:%S',
                                                     time.localtime(os.path.getmtime(abs_path)))
                    except:
                        last_modified = "Unknown"

                    writer.writerow([file_path, last_modified])

            messagebox.showinfo("Export Complete", f"Unused files exported to {output_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Error exporting unused files: {str(e)}")

    def _export_standalone_files(self):
        """Export the standalone files to a CSV file."""
        if not self.dependency_map:
            messagebox.showinfo("Info", "No dependency map available. Generate a map first.")
            return

        # Ask for the output file
        output_file = filedialog.asksaveasfilename(
            initialdir=self.output_folder.get(),
            defaultextension=".csv",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")],
            title="Export Standalone Files"
        )

        if not output_file:
            return

        try:
            # Get standalone files
            standalone_files = self._get_standalone_files()

            # Write to CSV
            with open(output_file, 'w', newline='', encoding='utf-8') as f:
                import csv
                writer = csv.writer(f)
                writer.writerow(["File Path", "Possible Type"])

                for file_path in standalone_files:
                    file_type = self._guess_file_type(file_path)
                    writer.writerow([file_path, file_type])

            messagebox.showinfo("Export Complete", f"Standalone files exported to {output_file}")

        except Exception as e:
            messagebox.showerror("Error", f"Error exporting standalone files: {str(e)}")

    def _update_dependencies_view(self):
        """Update the dependencies view with the current dependency map."""
        # Clear the system and file comboboxes
        self.system_combo['values'] = ()
        self.file_combo['values'] = ()

        if not self.dependency_map or not self.systems:
            return

        # Update the system combobox
        system_names = [f"System {s['id']}: {s['name']} ({s['file_count']} files)" for s in self.systems]
        self.system_combo['values'] = system_names

        # Select the first system
        if system_names:
            self.system_combo.current(0)
            self._on_system_selected(None)

        # Update the standalone files view
        self._update_standalone_files_view()

        # Update the unused files view
        if hasattr(self, 'unused_files'):
            self._update_unused_files_view()

    def _on_system_selected(self, event):
        """Handle system selection in the combobox."""
        selected_system = self.system_combo.get()
        if not selected_system or not self.systems:
            return

        # Extract system ID from the selection
        try:
            system_id = int(selected_system.split(':')[0].replace('System ', ''))
            system = next((s for s in self.systems if s['id'] == system_id), None)

            if system:
                # Update the file combobox with files from this system
                sorted_files = sorted(system['files'])
                self.file_combo['values'] = sorted_files

                # Try to select the last selected file if it's in this system, or the first file
                last_file = self.last_selected_file.get()
                if last_file and last_file in sorted_files:
                    index = sorted_files.index(last_file)
                    self.file_combo.current(index)
                elif sorted_files:
                    self.file_combo.current(0)

                # Update the view
                self._on_file_selected(None)
        except (ValueError, IndexError):
            pass

    def _on_file_selected(self, event):
        """Handle file selection in the combobox."""
        selected_file = self.file_combo.get()
        if not selected_file:
            return

        # Save the selected file
        self.last_selected_file.set(selected_file)

        # Clear the treeviews
        self.imports_tree.delete(*self.imports_tree.get_children())
        self.imported_by_tree.delete(*self.imported_by_tree.get_children())

        # Get dependencies
        imports = self.dependency_map.get(selected_file, [])
        imported_by = self.reverse_dependency_map.get(selected_file, [])

        # Update the imports treeview
        for i, file_path in enumerate(sorted(imports)):
            self.imports_tree.insert("", "end", values=(file_path,))

        # Update the imported_by treeview
        for i, file_path in enumerate(sorted(imported_by)):
            self.imported_by_tree.insert("", "end", values=(file_path,))

        # Save settings to persist the selection
        self._save_settings()

    def _search_dependencies(self):
        """Search for files matching the search term within the selected system."""
        search_term = self.search_term.get().lower()
        if not search_term:
            return

        # Get the selected system
        selected_system = self.system_combo.get()
        if not selected_system or not self.systems:
            return

        try:
            # Extract system ID from the selection
            system_id = int(selected_system.split(':')[0].replace('System ', ''))
            system = next((s for s in self.systems if s['id'] == system_id), None)

            if not system:
                return

            # Find matching files within this system
            matching_files = [
                file_path for file_path in system['files']
                if search_term in file_path.lower()
            ]

            if not matching_files:
                messagebox.showinfo("Search Results", "No matching files found in the selected system.")
                return

            # Update the file combobox
            self.file_combo['values'] = matching_files

            # Select the first matching file
            self.file_combo.current(0)
            self._on_file_selected(None)
        except (ValueError, IndexError):
            pass

    def _refresh_dependencies(self):
        """Refresh the dependencies view."""
        self._update_dependencies_view()

    def _open_html_visualization(self):
        """Open the HTML visualization in a web browser."""
        if hasattr(self, 'html_output') and os.path.exists(self.html_output):
            webbrowser.open(f"file://{os.path.abspath(self.html_output)}")
        else:
            messagebox.showinfo("Information", "Please generate the dependency map first.")

    def _on_tab_changed(self, event):
        """Handle tab change event."""
        # Get the selected tab index
        selected_tab = self.notebook.index("current")

        # If the standalone files tab is selected, refresh it
        if selected_tab == 2 and self.dependency_map:  # 2 is the index of the standalone files tab
            self._update_standalone_files_view()

        # If the unused files tab is selected, refresh it
        elif selected_tab == 3 and hasattr(self, 'unused_files'):  # 3 is the index of the unused files tab
            self._update_unused_files_view()

    def _on_dependency_double_click(self, event):
        """Handle double-clicking on a dependency in either treeview."""
        # Get the treeview that was clicked
        tree = event.widget

        # Get the selected item
        selection = tree.selection()
        if not selection:
            return

        # Get the file path from the selected item
        item = selection[0]
        file_path = tree.item(item, "values")[0]

        # Set this file as the selected file in the combobox
        if file_path in self.dependency_map:
            # Find the index of the file in the combobox values
            values = self.file_combo['values']
            if file_path in values:
                index = values.index(file_path)
                self.file_combo.current(index)
                self._on_file_selected(None)

                # Save the last selected file
                self.last_selected_file.set(file_path)
                self._save_settings()

    def _load_settings(self):
        """Load settings from the settings file."""
        config = configparser.ConfigParser()

        # Check if settings file exists
        if os.path.exists(self.SETTINGS_FILE):
            try:
                config.read(self.SETTINGS_FILE)

                # Load general settings
                if 'General' in config:
                    if 'source_folder' in config['General']:
                        folder = config['General']['source_folder']
                        if os.path.isdir(folder):
                            self.source_folder.set(folder)

                    if 'output_folder' in config['General']:
                        folder = config['General']['output_folder']
                        if os.path.isdir(folder):
                            self.output_folder.set(folder)

                    # No longer need to load start_file

                    if 'last_selected_file' in config['General']:
                        self.last_selected_file.set(config['General']['last_selected_file'])

                # Load visualization settings
                if 'Visualization' in config:
                    if 'create_html' in config['Visualization']:
                        self.create_html = tk.BooleanVar(value=config['Visualization'].getboolean('create_html'))
                    else:
                        self.create_html = tk.BooleanVar(value=True)

                    if 'create_graph' in config['Visualization']:
                        self.create_graph = tk.BooleanVar(value=config['Visualization'].getboolean('create_graph'))
                    else:
                        self.create_graph = tk.BooleanVar(value=True)
                else:
                    self.create_html = tk.BooleanVar(value=True)
                    self.create_graph = tk.BooleanVar(value=True)

                # Load dependency map if it exists
                if 'Files' in config and 'dependency_map' in config['Files']:
                    map_file = config['Files']['dependency_map']
                    if os.path.exists(map_file):
                        try:
                            with open(map_file, 'r', encoding='utf-8') as f:
                                self.dependency_map = json.load(f)
                            self._build_reverse_dependency_map()

                            # Store the HTML output path if it exists
                            html_file = os.path.join(os.path.dirname(map_file), 'dependency_graph.html')
                            if os.path.exists(html_file):
                                self.html_output = html_file
                        except Exception as e:
                            print(f"Error loading dependency map: {str(e)}")
            except Exception as e:
                print(f"Error loading settings: {str(e)}")

    def _save_settings(self):
        """Save settings to the settings file."""
        config = configparser.ConfigParser()

        # General settings
        config['General'] = {
            'source_folder': self.source_folder.get(),
            'output_folder': self.output_folder.get(),
            'last_selected_file': self.last_selected_file.get()
        }

        # Visualization settings
        config['Visualization'] = {
            'create_html': str(self.create_html.get()),
            'create_graph': str(self.create_graph.get())
        }

        # Files
        config['Files'] = {}
        if hasattr(self, 'html_output') and os.path.exists(self.html_output):
            map_file = os.path.join(os.path.dirname(self.html_output), 'dependency_map.json')
            if os.path.exists(map_file):
                config['Files']['dependency_map'] = map_file

        # Write to file
        try:
            with open(self.SETTINGS_FILE, 'w') as f:
                config.write(f)
        except Exception as e:
            print(f"Error saving settings: {str(e)}")

    def _on_close(self):
        """Handle window close event."""
        self._save_settings()
        self.root.destroy()

def main():
    """Main function to run the UI."""
    root = tk.Tk()
    app = DependencyMapperUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()