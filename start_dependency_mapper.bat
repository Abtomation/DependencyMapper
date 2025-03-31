@echo off
echo Starting Dependency Mapper...

REM Try to find Python in common locations
set PYTHON_CMD=python

REM Check if python command works
%PYTHON_CMD% --version >nul 2>&1
if errorlevel 1 (
    REM Try python3 instead
    set PYTHON_CMD=python3
    %PYTHON_CMD% --version >nul 2>&1
    if errorlevel 1 (
        REM Try with full path to Python
        if exist "C:\Program Files\Python311\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python311\python.exe"
        ) else if exist "C:\Program Files\Python310\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python310\python.exe"
        ) else if exist "C:\Program Files\Python39\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python39\python.exe"
        ) else if exist "C:\Program Files\Python38\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python38\python.exe"
        ) else if exist "C:\Program Files\Python37\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python37\python.exe"
        ) else if exist "C:\Program Files\Python36\python.exe" (
            set PYTHON_CMD="C:\Program Files\Python36\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python311\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python311\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python310\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python310\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python39\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python39\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python38\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python38\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python37\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python37\python.exe"
        ) else if exist "%LOCALAPPDATA%\Programs\Python\Python36\python.exe" (
            set PYTHON_CMD="%LOCALAPPDATA%\Programs\Python\Python36\python.exe"
        ) else (
            echo Python not found. Please install Python or make sure it's in your PATH.
            pause
            exit /b 1
        )
    )
)

REM Run the application
echo Using Python: %PYTHON_CMD%
%PYTHON_CMD% "%~dp0dependency_mapper_ui.py"

if errorlevel 1 (
    echo Error starting Dependency Mapper.
    echo Please check that all dependencies are installed.
    echo You might need to run: pip install -r requirements.txt
    pause
)@echo off
echo Starting Dependency Mapper...
python "%~dp0dependency_mapper_ui.py"
if errorlevel 1 (
    echo Error starting Dependency Mapper.
    echo Please make sure Python is installed and in your PATH.
    pause
)