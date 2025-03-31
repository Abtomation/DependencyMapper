# Creating a Desktop Application

This guide explains how to set up Dependency Mapper as a desktop application that you can launch from your desktop.

## Option 1: Using Launcher Scripts (Simple)

### Windows

1. **Use the Batch File**:
   - Double-click on `start_dependency_mapper.bat` to run the application
   - To create a desktop shortcut:
     - Right-click on `start_dependency_mapper.bat`
     - Select "Create shortcut"
     - Move the shortcut to your desktop
     - (Optional) Right-click the shortcut, select "Properties", and change the icon

### macOS

1. **Use the Command File**:
   - First, make it executable:
     ```bash
     chmod +x "Start Dependency Mapper.command"
     ```
   - Double-click on `Start Dependency Mapper.command` to run the application
   - To create a desktop shortcut:
     - Right-click on the file
     - Select "Make Alias"
     - Move the alias to your desktop

### Linux

1. **Use the Desktop Entry**:
   - First, make it executable:
     ```bash
     chmod +x dependency-mapper.desktop
     ```
   - Install it to your applications:
     ```bash
     cp dependency-mapper.desktop ~/.local/share/applications/
     ```
   - Edit the file to update the paths:
     ```bash
     nano ~/.local/share/applications/dependency-mapper.desktop
     ```
     Update the `Exec` and `Path` lines to use the absolute path to your application
   - The application should now appear in your applications menu

## Option 2: Creating a Standalone Executable (Advanced)

For a more professional approach, you can create a standalone executable that doesn't require Python to be installed.

### Prerequisites

Install PyInstaller:

```bash
pip install pyinstaller
```

### Building the Executable

Run the build script:

```bash
python build_executable.py
```

This will create a standalone executable in the `dist` folder.

### Using the Executable

- **Windows**: Double-click `dist/DependencyMapper.exe`
- **macOS**: Double-click `dist/DependencyMapper.app`
- **Linux**: Run `dist/DependencyMapper`

### Creating Desktop Shortcuts

- **Windows**:
  - Right-click on `dist/DependencyMapper.exe`
  - Select "Create shortcut"
  - Move the shortcut to your desktop

- **macOS**:
  - Drag `dist/DependencyMapper.app` to your Applications folder
  - (Optional) Drag from Applications to your Dock

- **Linux**:
  - Edit the `dependency-mapper.desktop` file to point to the executable
  - Copy it to `~/.local/share/applications/`

## Adding Custom Icons

1. Create or obtain icon files:
   - Windows: `.ico` file
   - macOS: `.icns` file
   - Linux: `.png` file (256x256 pixels recommended)

2. Place the icon files in the `icons` folder:
   - `icons/dependency_mapper.ico` (Windows)
   - `icons/dependency_mapper.icns` (macOS)
   - `icons/dependency_mapper.png` (Linux)

3. When building the executable, the appropriate icon will be used automatically.

## Troubleshooting

### Windows

- If you get an error about Python not being found, make sure Python is installed and in your PATH
- If the application doesn't start, try running it from the command line to see any error messages

### macOS

- If you get a "not trusted" error, go to System Preferences > Security & Privacy and allow the application
- If the command file doesn't run, make sure it's executable (`chmod +x`)

### Linux

- If the desktop entry doesn't work, check the paths in the `.desktop` file
- Make sure the file is executable (`chmod +x`)
- Try running the application from the terminal to see any error messages