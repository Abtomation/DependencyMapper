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
        self.start_file = tk.StringVar()
        self.status = tk.StringVar(value="Ready")
        self.progress = tk.DoubleVar(value=0)
        self.search_term = tk.StringVar()
        self.last_selected_file = tk.StringVar()

        # Set default values
        self.source_folder.set(os.getcwd())
        self.output_folder.set(os.getcwd())

        # Store the dependency map
        self.dependency_map = {}
        self.reverse_dependency_map = {}

        # Load settings from file
        self._load_settings()

        # Create the UI
        self._create_ui()

        # Bind window close event to save settings
        self.root.protocol("WM_DELETE_WINDOW", self._on_close)
    
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

        # Create the configuration tab content
        self._create_config_tab(config_frame)

        # Create the dependencies tab content
        self._create_dependencies_tab(self.dependencies_frame)

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

        # Start file selection
        start_file_frame = ttk.LabelFrame(parent, text="Start File", padding="5")
        start_file_frame.pack(fill=tk.X, pady=5)

        ttk.Entry(start_file_frame, textvariable=self.start_file, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(start_file_frame, text="Browse...", command=self._browse_start_file).pack(side=tk.RIGHT, padx=5)

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

    def _create_dependencies_tab(self, parent):
        """Create the dependencies tab content."""
        # Top frame for search and file selection
        top_frame = ttk.Frame(parent)
        top_frame.pack(fill=tk.X, pady=5)

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
        start_file = self.start_file.get()
        
        if not os.path.isdir(source_folder):
            messagebox.showerror("Error", "Source folder does not exist.")
            return
        
        if not os.path.isdir(output_folder):
            messagebox.showerror("Error", "Output folder does not exist.")
            return
        
        if not start_file:
            messagebox.showerror("Error", "Please select a start file.")
            return
        
        # Get the absolute path of the start file
        if not os.path.isabs(start_file):
            start_file_abs = os.path.join(source_folder, start_file)
        else:
            start_file_abs = start_file
        
        if not os.path.isfile(start_file_abs):
            messagebox.showerror("Error", f"Start file does not exist: {start_file_abs}")
            return
        
        # Start the generation in a separate thread to keep the UI responsive
        threading.Thread(target=self._generate_map_thread, args=(source_folder, output_folder, start_file)).start()
    
    def _generate_map_thread(self, source_folder, output_folder, start_file):
        """
        Generate the dependency map in a separate thread.

        Args:
            source_folder: The source folder
            output_folder: The output folder
            start_file: The start file
        """
        try:
            self._update_status("Initializing...", 0)

            # Record start time
            start_time = time.time()

            # Create a dependency mapper
            self._update_status("Creating dependency mapper...", 10)
            mapper = DependencyMapper(source_folder)

            # Map dependencies
            self._update_status(f"Mapping dependencies starting from {start_file}...", 20)
            self.dependency_map = mapper.map_dependencies(start_file)

            # Build reverse dependency map
            self._update_status("Building reverse dependency map...", 40)
            self._build_reverse_dependency_map()

            # Calculate statistics
            total_files = len(self.dependency_map)
            total_dependencies = sum(len(deps) for deps in self.dependency_map.values())
            files_with_no_deps = sum(1 for deps in self.dependency_map.values() if not deps)
            max_deps_file = max(self.dependency_map.items(), key=lambda x: len(x[1]), default=("None", []))

            # Save the dependency map to a JSON file
            self._update_status("Saving dependency map...", 60)
            output_file = os.path.join(output_folder, 'dependency_map.json')
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.dependency_map, f, indent=2, sort_keys=True)

            # Create visualizations
            if self.create_html.get():
                self._update_status("Creating HTML visualization...", 70)
                self.html_output = os.path.join(output_folder, 'dependency_graph.html')
                visualize_dependencies.create_html_visualization(self.dependency_map, self.html_output)

            if self.create_graph.get():
                try:
                    self._update_status("Creating graph visualization...", 80)
                    graph_output = os.path.join(output_folder, 'dependency_graph.png')
                    G = visualize_dependencies.create_graph(self.dependency_map)
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
                f"Time taken: {duration:.2f} seconds"
            )
            messagebox.showinfo("Summary", summary)

            # Update the dependencies view
            self._update_dependencies_view()

            # Switch to the dependencies tab
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

    def _update_dependencies_view(self):
        """Update the dependencies view with the current dependency map."""
        # Clear the file combobox
        self.file_combo['values'] = ()

        if not self.dependency_map:
            return

        # Sort files by name
        sorted_files = sorted(self.dependency_map.keys())

        # Update the file combobox
        self.file_combo['values'] = sorted_files

        # Try to select the last selected file, or the first file if none
        last_file = self.last_selected_file.get()
        if last_file and last_file in sorted_files:
            index = sorted_files.index(last_file)
            self.file_combo.current(index)
        elif sorted_files:
            self.file_combo.current(0)

        # Update the view
        self._on_file_selected(None)

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
        """Search for files matching the search term."""
        search_term = self.search_term.get().lower()
        if not search_term:
            return

        # Find matching files
        matching_files = [
            file_path for file_path in self.dependency_map.keys()
            if search_term in file_path.lower()
        ]

        if not matching_files:
            messagebox.showinfo("Search Results", "No matching files found.")
            return

        # Update the file combobox
        self.file_combo['values'] = matching_files

        # Select the first matching file
        self.file_combo.current(0)
        self._on_file_selected(None)

    def _refresh_dependencies(self):
        """Refresh the dependencies view."""
        self._update_dependencies_view()

    def _open_html_visualization(self):
        """Open the HTML visualization in a web browser."""
        if hasattr(self, 'html_output') and os.path.exists(self.html_output):
            webbrowser.open(f"file://{os.path.abspath(self.html_output)}")
        else:
            messagebox.showinfo("Information", "Please generate the dependency map first.")

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

                    if 'start_file' in config['General']:
                        self.start_file.set(config['General']['start_file'])

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
            'start_file': self.start_file.get(),
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