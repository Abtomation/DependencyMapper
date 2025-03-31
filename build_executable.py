"""
Build a standalone executable for Dependency Mapper.

This script uses PyInstaller to create a standalone executable.
"""

import os
import platform
import subprocess
import sys

def main():
    """Build the executable."""
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    # Determine the icon file based on the platform
    icon_file = None
    if platform.system() == "Windows":
        icon_file = os.path.join("icons", "dependency_mapper.ico")
    elif platform.system() == "Darwin":  # macOS
        icon_file = os.path.join("icons", "dependency_mapper.icns")
    else:  # Linux
        icon_file = os.path.join("icons", "dependency_mapper.png")
    
    # Check if the icon file exists
    icon_param = []
    if os.path.exists(icon_file):
        icon_param = ["--icon", icon_file]
    else:
        print(f"Warning: Icon file {icon_file} not found. The executable will use the default icon.")
    
    # Build the command
    cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "DependencyMapper",
        *icon_param,
        "dependency_mapper_ui.py"
    ]
    
    # Run PyInstaller
    print("Building executable...")
    subprocess.check_call(cmd)
    
    print("\nBuild complete!")
    print(f"The executable is located in the 'dist' folder.")
    
    # Additional instructions
    if platform.system() == "Windows":
        print("\nTo create a desktop shortcut:")
        print("1. Right-click on dist/DependencyMapper.exe")
        print("2. Select 'Create shortcut'")
        print("3. Move the shortcut to your desktop")
    elif platform.system() == "Darwin":  # macOS
        print("\nTo move to Applications:")
        print("1. Open the dist folder")
        print("2. Drag DependencyMapper to Applications")
    else:  # Linux
        print("\nTo create a desktop shortcut:")
        print("1. Copy dependency-mapper.desktop to ~/.local/share/applications/")
        print("2. Edit the file to update the Exec and Icon paths")

if __name__ == "__main__":
    main()