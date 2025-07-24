"""Build script to create executable files using PyInstaller."""
import os
import shutil
import subprocess
import sys
from pathlib import Path

def build_executable(script_name, icon=None):
    """Build an executable from a Python script."""
    print(f"\nBuilding {script_name}...")
    
    # Get the name for the executable without extension
    exe_name = os.path.splitext(os.path.basename(script_name))[0]
    
    # Base command
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--onefile',
        '--windowed',  # Hide console window for GUI applications
        '--uac-admin',  # Request admin privileges
        '--name', exe_name,
        # Include all necessary directories
        '--add-data', 'src;src',
        '--add-data', 'config;config',
        '--add-data', 'assets;assets',
        # Add hidden imports for PyQt6
        '--hidden-import', 'PyQt6.QtCore',
        '--hidden-import', 'PyQt6.QtWidgets',
        '--hidden-import', 'PyQt6.QtGui',
        # Add any other directories that might be needed
        '--log-level', 'INFO'
    ]
    
    # Add icon if provided
    if icon and os.path.exists(icon):
        cmd.extend(['--icon', icon])
    
    # Add the script
    cmd.append(script_name)
    
    print("Command:", ' '.join(cmd))
    
    # Run PyInstaller
    try:
        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        print(f"Successfully built {script_name}")
    except subprocess.CalledProcessError as e:
        print(f"Error building {script_name}:")
        print("Output:")
        print(e.stdout)
        print("\nErrors:")
        print(e.stderr)
        sys.exit(1)

def ensure_directories():
    """Ensure all necessary directories exist."""
    # Create directories if they don't exist
    for dir_name in ['assets', 'logs', 'backups']:
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
            print(f"Created directory: {dir_name}")

def clean_previous_builds():
    """Clean previous build artifacts."""
    print("Cleaning previous builds...")
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
            print(f"Removed directory: {dir_name}")
    
    # Also remove .spec files
    for spec_file in Path('.').glob('*.spec'):
        spec_file.unlink()
        print(f"Removed spec file: {spec_file}")

def main():
    """Main build function."""
    # Ensure directories exist
    ensure_directories()
    
    # Clean previous builds
    clean_previous_builds()
    
    # Define icons (if they exist)
    main_icon = os.path.join('assets', 'WinOpsTool.ico') if os.path.exists(os.path.join('assets', 'WinOpsTool.ico')) else None
    config_icon = os.path.join('assets', 'WinOpsInit.ico') if os.path.exists(os.path.join('assets', 'WinOpsInit.ico')) else None
    
    # Build executables
    build_executable('WinOpsTool.py', icon=main_icon)
    build_executable('WinOpsInit.py', icon=config_icon)
    
    print("\nBuild completed successfully!")
    print("Executables can be found in the 'dist' directory.")

if __name__ == '__main__':
    main()
