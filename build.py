"""Build script to create executable files using PyInstaller."""
import os
import shutil
import subprocess
import sys

def build_executable(script_name):
    """Build an executable from a Python script."""
    print(f"\nBuilding {script_name}...")
    
    # Base command
    cmd = [
        sys.executable,
        '-m',
        'PyInstaller',
        '--noconfirm',
        '--clean',
        '--onefile',
        '--console',  # Show console for debugging
        '--uac-admin',  # Request admin privileges
        '--name', os.path.splitext(script_name)[0],
        '--add-data', 'src;src',  # Include src directory
        '--add-data', 'config;config',  # Include config directory
        '--log-level', 'DEBUG'
    ]
    
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

def main():
    """Main build function."""
    # Create assets directory if it doesn't exist
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Clean previous builds
    for dir_name in ['build', 'dist']:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Build executables
    build_executable('main.py')
    build_executable('config_manager.py')
    
    print("\nBuild completed successfully!")
    print("Executables can be found in the 'dist' directory.")

if __name__ == '__main__':
    main()
