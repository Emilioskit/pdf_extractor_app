#!/usr/bin/env python3
"""
Build script to create executables for Windows and Mac
Run this script after installing requirements.txt
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{description}...")
    print(f"Running: {' '.join(command)}")
    
    try:
        result = subprocess.run(command, check=True, capture_output=True, text=True)
        print("✓ Success!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error: {e}")
        if e.stdout:
            print(f"Stdout: {e.stdout}")
        if e.stderr:
            print(f"Stderr: {e.stderr}")
        return False

def build_executable():
    """Build the executable using PyInstaller"""
    
    print("=== PDF Task Extractor - Executable Builder ===")
    print(f"Platform: {platform.system()}")
    print(f"Python version: {sys.version}")
    
    # Check if main script exists
    main_script = "pdf_extractor.py"
    if not os.path.exists(main_script):
        print(f"\n✗ Error: {main_script} not found!")
        print("Please make sure the main application file is named 'pdf_extractor.py'")
        return False
    
    # PyInstaller command
        # Use correct separator for --add-data
    sep = ";" if platform.system() == "Windows" else ":"

    pyinstaller_cmd = [
        "pyinstaller",
        "--onefile",
        "--windowed",
        "--name", "PDFTaskExtractor",
        "--add-data", f"requirements.txt{sep}.",
        main_script
    ]

    
    # Platform-specific adjustments
    if platform.system() == "Windows":
        # Add Windows-specific options
        pyinstaller_cmd.extend([
            "--icon", "icon.ico"  # Add if you have an icon file
        ])
        executable_name = "PDFTaskExtractor.exe"
    elif platform.system() == "Darwin":  # macOS
        # Add macOS-specific options
        pyinstaller_cmd.extend([
            "--icon", "icon.icns"  # Add if you have a macOS icon file
        ])
        executable_name = "PDFTaskExtractor.app"
    else:  # Linux
        executable_name = "PDFTaskExtractor"
    
    # Remove icon options if files don't exist
    if "--icon" in pyinstaller_cmd:
        icon_index = pyinstaller_cmd.index("--icon")
        icon_file = pyinstaller_cmd[icon_index + 1]
        if not os.path.exists(icon_file):
            print(f"Warning: Icon file {icon_file} not found, building without icon")
            pyinstaller_cmd.pop(icon_index + 1)  # Remove icon file path
            pyinstaller_cmd.pop(icon_index)      # Remove --icon flag
    
    # Build the executable
    if run_command(pyinstaller_cmd, "Building executable with PyInstaller"):
        print(f"\n🎉 Build completed successfully!")
        print(f"Executable location: dist/{executable_name}")
        
        # Additional instructions
        print(f"\n📋 Instructions:")
        print(f"1. Your executable is ready: dist/{executable_name}")
        print(f"2. You can distribute this single file to users")
        print(f"3. No Python installation required on target machines")
        
        if platform.system() == "Darwin":
            print(f"4. On macOS, users may need to right-click and 'Open' the first time")
            print(f"   due to Gatekeeper security (unsigned app)")
        
        return True
    else:
        print(f"\n✗ Build failed!")
        return False

def install_requirements():
    """Install required packages"""
    requirements_file = "requirements.txt"
    if not os.path.exists(requirements_file):
        print(f"✗ Error: {requirements_file} not found!")
        return False
    
    pip_cmd = [sys.executable, "-m", "pip", "install", "-r", requirements_file]
    return run_command(pip_cmd, "Installing requirements")

def main():
    print("Starting build process...\n")
    
    # Step 1: Install requirements
    if not install_requirements():
        print("Failed to install requirements. Please install manually:")
        print("pip install -r requirements.txt")
        return
    
    # Step 2: Build executable
    if not build_executable():
        print("Build failed. Please check the error messages above.")
        return
    
    print("\n All done! Your executable is ready to distribute.")

if __name__ == "__main__":
    main()