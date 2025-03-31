"""
Simple script to build a Windows executable for Dependency Mapper.
"""

import os
import sys
import subprocess

def main():
    """Build the Windows executable using a simpler approach."""
    print("Installing PyInstaller if needed...")
    subprocess.call([sys.executable, "-m", "pip", "install", "pyinstaller"])
    
    print("\nBuilding executable...")
    # Use a direct command that should work in most environments
    build_command = f"{sys.executable} -m PyInstaller --onefile --windowed --name DependencyMapper dependency_mapper_ui.py"
    
    # Check for icon
    if os.path.exists("dependency_mapper.ico"):
        build_command = f"{sys.executable} -m PyInstaller --onefile --windowed --icon=dependency_mapper.ico --name DependencyMapper dependency_mapper_ui.py"
        print("Using icon: dependency_mapper.ico")
    
    # Print the command so user can run it manually if needed
    print(f"Running: {build_command}")
    
    # Execute the command
    result = os.system(build_command)
    
    if result == 0:
        print("\nBuild successful!")
        print("The executable is located at: dist/DependencyMapper.exe")
        print("\nTo create a desktop shortcut:")
        print("1. Right-click on dist/DependencyMapper.exe")
        print("2. Select 'Create shortcut'")
        print("3. Move the shortcut to your desktop")
    else:
        print("\nBuild failed with error code:", result)
        print("Try running the command manually in your command prompt:")
        print(build_command)

if __name__ == "__main__":
    main()