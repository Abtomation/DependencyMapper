# Creating a Windows Desktop Application

This guide explains how to set up Dependency Mapper as a desktop application that you can launch from your Windows desktop.

## Option 1: Using the Batch File (Simple)

The simplest way to run the application from your desktop:

1. **Run the Application**:
   - Double-click on `start_dependency_mapper.bat` to start the application
   - This requires Python to be installed and in your PATH

2. **Create a Desktop Shortcut**:
   - Right-click on `start_dependency_mapper.bat`
   - Select "Create shortcut"
   - Move the shortcut to your desktop
   - (Optional) Rename the shortcut to "Dependency Mapper"

3. **Customize the Shortcut** (optional):
   - Right-click on the shortcut
   - Select "Properties"
   - Click "Change Icon"
   - Browse to an icon file (you can use any .ico file)
   - Click "OK"

## Option 2: Creating a Windows Executable (Advanced)

For a more professional approach, you can create a standalone .exe file that doesn't require Python to be installed:

1. **Install PyInstaller**:
   ```
   pip install pyinstaller
   ```

2. **Create the Executable**:
   - Run one of the build scripts:
   ```
   python build_windows_exe.py
   ```

   - If that doesn't work, try the simpler script:
   ```
   python build_exe_simple.py
   ```

   - Or run PyInstaller directly:
   ```
   python -m PyInstaller --onefile --windowed --name DependencyMapper dependency_mapper_ui.py
   ```

3. **Use the Executable**:
   - Find the executable at `dist/DependencyMapper.exe`
   - Double-click to run
   - Create a shortcut on your desktop by right-clicking the .exe and selecting "Create shortcut"

## Adding a Custom Icon

To give your application a professional look:

1. **For the Batch File Shortcut**:
   - Right-click the shortcut on your desktop
   - Select "Properties"
   - Click "Change Icon"
   - Browse to an .ico file
   - Click "OK"

2. **For the Executable**:
   - Place an icon file named `dependency_mapper.ico` in the same folder as the build script
   - Run the build script to create an executable with this icon
   - Or specify a different icon when running PyInstaller manually:
   ```
   pyinstaller --onefile --windowed --icon=your_icon.ico --name DependencyMapper dependency_mapper_ui.py
   ```

## Troubleshooting

- **"Python is not recognized as an internal or external command"**:
  - Make sure Python is installed
  - Add Python to your PATH environment variable

- **The application doesn't start**:
  - Try running the batch file or executable from a command prompt to see error messages
  - For the batch file, make sure the path to your Python script is correct

- **The executable is flagged by antivirus**:
  - This is common with PyInstaller executables
  - You may need to add an exception in your antivirus software
  - Or use the batch file approach instead