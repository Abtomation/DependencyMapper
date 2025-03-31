"""
Build a Windows executable for Dependency Mapper.

This script uses PyInstaller to create a standalone Windows executable.
"""

import os
import subprocess
import sys

def main():
    """Build the Windows executable."""
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller is not installed. Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])

    # Check for an icon file
    icon_file = "dependency_mapper.ico"
    icon_param = []

    if os.path.exists(icon_file):
        icon_param = ["--icon", icon_file]
        print(f"Using icon: {icon_file}")
    else:
        print(f"No icon file found. The executable will use the default icon.")
        print(f"To add a custom icon, place a file named '{icon_file}' in the same folder as this script.")

    # Build the command - use python -m pyinstaller to ensure we use the installed package
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--onefile",
        "--windowed",
        "--name", "DependencyMapper",
        *icon_param,
        "dependency_mapper_ui.py"
    ]

    # Run PyInstaller
    print("Building executable...")
    try:
        subprocess.check_call(cmd)

        print("\nBuild complete!")
        print(f"The executable is located at: dist/DependencyMapper.exe")

        print("\nTo create a desktop shortcut:")
        print("1. Right-click on dist/DependencyMapper.exe")
        print("2. Select 'Create shortcut'")
        print("3. Move the shortcut to your desktop")
    except subprocess.CalledProcessError as e:
        print(f"\nError building executable: {e}")
        print("Try running the PyInstaller command manually:")
        print(f"python -m PyInstaller --onefile --windowed --name DependencyMapper dependency_mapper_ui.py")
    except FileNotFoundError:
        print("\nError: PyInstaller not found in PATH.")
        print("Try running the PyInstaller command manually:")
        print(f"python -m PyInstaller --onefile --windowed --name DependencyMapper dependency_mapper_ui.py")

if __name__ == "__main__":
    main()