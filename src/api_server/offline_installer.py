"""
WinOpsTool REST API Service Offline Installer Creator

This script creates an offline installer package for the WinOpsTool REST API service.
It downloads all required dependencies, bundles them with the source code, and creates
an executable installer that can be used on machines with limited or no internet access.

Usage:
    python offline_installer.py [--output-dir OUTPUT_DIR]
"""

import os
import sys
import subprocess
import logging
import argparse
import shutil
import tempfile
import zipfile
import secrets
from pathlib import Path
import urllib.request

# Define paths
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent.parent.absolute()
build_dir = project_dir / "build" / "offline_installer"
dist_dir = project_dir / "dist"
temp_dir = build_dir / "temp"
deps_dir = build_dir / "dependencies"
output_dir = dist_dir
templates_dir = script_dir / "templates"
logs_dir = project_dir / "logs"

# Ensure logs directory exists
logs_dir.mkdir(parents=True, exist_ok=True)

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / "offline_installer.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("offline_installer")

# Define dependencies
dependencies = [
    "pyinstaller>=5.8.0",
    "fastapi>=0.95.0",
    "uvicorn>=0.21.1",
    "psutil>=5.9.0",
    "pywin32>=306",
    "requests>=2.28.0"
]

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Offline Installer Creator")
    parser.add_argument("--output-dir", help="Custom output directory for the offline installer")
    args = parser.parse_args()
    
    global output_dir
    if args.output_dir:
        output_dir = Path(args.output_dir).absolute()
    
    return args

def setup_directories():
    """Create necessary directories"""
    logger.info("Setting up directories...")
    
    # Create build directory
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create temp directory
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir(parents=True)
    
    # Create dependencies directory
    if deps_dir.exists():
        shutil.rmtree(deps_dir)
    deps_dir.mkdir(parents=True)
    
    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create templates directory if it doesn't exist
    templates_dir.mkdir(parents=True, exist_ok=True)
    
    return True

def download_dependencies():
    """Download all dependencies to the dependencies directory"""
    logger.info("Downloading dependencies...")
    
    for dep in dependencies:
        logger.info(f"Downloading {dep}")
        try:
            # Try to download binary distributions first (wheels)
            subprocess.run([
                sys.executable, "-m", "pip", "download",
                "--dest", str(deps_dir),
                dep
            ], check=True)
            
            # Try to download source distributions as well if possible
            # But don't fail if this doesn't work
            try:
                subprocess.run([
                    sys.executable, "-m", "pip", "download",
                    "--dest", str(deps_dir),
                    "--no-binary", dep,  # Source distribution for this package
                    dep
                ], check=False)
            except subprocess.CalledProcessError:
                logger.warning(f"Could not download source distribution for {dep}, continuing with wheel only")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to download {dep}: {e}")
            logger.warning(f"Attempting to continue despite failure to download {dep}")
    
    # Check if we have at least some packages downloaded
    if not os.listdir(deps_dir):
        logger.error("No dependencies were downloaded successfully")
        return False
        
    return True

def create_installer_script():
    """Create the installer script that will be run on the target machine"""
    logger.info("Creating installer script...")
    
    installer_script_path = temp_dir / "install.py"
    template_path = templates_dir / "installer_template.py"
    
    if not template_path.exists():
        logger.error(f"Installer template not found at {template_path}")
        return False
    
    # Read the template file
    with open(template_path, "r") as f:
        script_content = f.read()
    
    # Write the installer script
    with open(installer_script_path, "w") as f:
        f.write(script_content)
    
    return True

def create_service_launcher():
    """Create the service launcher script"""
    logger.info("Creating service launcher script...")
    
    # Create api_server directory in temp/src
    api_server_dir = temp_dir / "src" / "api_server"
    api_server_dir.mkdir(parents=True, exist_ok=True)
    
    service_launcher_path = api_server_dir / "service_launcher.py"
    template_path = templates_dir / "service_launcher_template.py"
    
    if not template_path.exists():
        logger.error(f"Service launcher template not found at {template_path}")
        return False
    
    # Generate API key
    api_key = secrets.token_hex(16)
    
    # Read the service launcher template
    with open(template_path, "r") as f:
        service_launcher_content = f.read()
    
    # Replace the API key placeholder
    service_launcher_content = service_launcher_content.replace("{api_key}", api_key)
    
    # Write the service launcher script
    with open(service_launcher_path, "w") as f:
        f.write(service_launcher_content)
    
    return True

def create_pyinstaller_spec():
    """Create the PyInstaller spec file"""
    logger.info("Creating PyInstaller spec file...")
    
    api_server_dir = temp_dir / "src" / "api_server"
    spec_path = api_server_dir / "api_installer.spec"
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{api_server_dir / "server.py"}'],
    pathex=[r'{temp_dir / "src"}'],
    binaries=[],
    datas=[
        (r'{temp_dir / "docs/REST_API_GUIDE.md"}', 'docs'),
        (r'{api_server_dir / "service_launcher.py"}', '.')
    ],
    hiddenimports=[
        'uvicorn.logging',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        'uvicorn.lifespan.off',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.protocols.websockets.websockets_impl',
        'uvicorn.protocols.websockets.wsproto_impl',
        'win32timezone',
        'win32serviceutil',
        'win32service',
        'win32event',
        'servicemanager',
        'socket',
        'psutil',
        'fastapi',
        'pydantic',
        'starlette',
        'starlette.routing',
        'starlette.applications'
    ],
    hookspath=[],
    hooksconfig={{}},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='WinOpsToolAPI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
"""
    
    with open(spec_path, "w") as f:
        f.write(spec_content)
    
    return True

def copy_source_files():
    """Copy source files to the temp directory"""
    logger.info("Copying source files...")
    
    # Create src directory in temp
    src_dir = temp_dir / "src"
    src_dir.mkdir(parents=True, exist_ok=True)
    
    # Copy api_server directory
    api_server_src = project_dir / "src" / "api_server"
    api_server_dest = src_dir / "api_server"
    
    # Create api_server directory if it doesn't exist
    api_server_dest.mkdir(parents=True, exist_ok=True)
    
    # Copy server.py and other necessary files
    for file in ["server.py", "registry_manager.py", "config.py"]:
        src_file = api_server_src / file
        if src_file.exists():
            shutil.copy(src_file, api_server_dest / file)
    
    # Copy docs directory
    docs_src = project_dir / "docs"
    docs_dest = temp_dir / "docs"
    docs_dest.mkdir(parents=True, exist_ok=True)
    
    # Copy REST_API_GUIDE.md
    api_guide = docs_src / "REST_API_GUIDE.md"
    if api_guide.exists():
        shutil.copy(api_guide, docs_dest / "REST_API_GUIDE.md")
    
    return True

def create_batch_installer():
    """Create a batch file to run the installer"""
    logger.info("Creating batch installer...")
    
    batch_path = temp_dir / "install.bat"
    
    batch_content = """@echo off
echo WinOpsTool REST API Service Installer
echo ====================================

:: Check for admin rights
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo This installer requires administrator privileges.
    echo Please right-click on install.bat and select "Run as administrator".
    pause
    exit /b 1
)

:: Check if Python is installed
python --version >nul 2>&1
if %errorLevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo.
    
    if exist "python_installer\\python-3.8.10-amd64.exe" (
        echo Installing Python 3.8.10...
        start /wait python_installer\python-3.8.10-amd64.exe /quiet PrependPath=1
        
        :: Check if Python was installed successfully
        python --version >nul 2>&1
        if %errorLevel% neq 0 (
            echo Failed to install Python. Please install Python 3.8 or later manually.
            pause
            exit /b 1
        )
        
        echo Python installed successfully.
    ) else (
        echo Python installer not found. Please install Python 3.8 or later manually.
        pause
        exit /b 1
    )
)

:: Run the installer
echo.
echo Running installer...
python install.py %*

pause
"""
    
    with open(batch_path, "w") as f:
        f.write(batch_content)
    
    return True

def create_readme():
    """Create a README file for the offline installer"""
    logger.info("Creating README...")
    
    readme_path = temp_dir / "README.md"
    
    readme_content = """# WinOpsTool REST API Service Offline Installer

This package contains everything needed to install the WinOpsTool REST API service on a machine with limited or no internet access.

## Requirements

- Windows 10 or later
- Administrator privileges

## Installation

1. Extract all files from the zip package to a directory on the target machine.
2. Right-click on `install.bat` and select "Run as administrator".
3. Follow the on-screen instructions.

If Python is not installed on the target machine, the installer will attempt to install Python 3.8.10 automatically.

## Installation Options

The installer supports the following command-line options:

- `--install-dir DIRECTORY`: Specify a custom installation directory (default: C:\\Program Files\\WinOpsToolAPI)
- `--no-service`: Install the executable only, without installing it as a Windows service

Example:
```
install.bat --install-dir "D:\\WinOpsToolAPI" --no-service
```

## API Key

During installation, an API key will be generated and displayed. This key is required to authenticate with the API.
The key is also stored in the installation directory in a file named `api_key.txt`.

## Troubleshooting

If the installation fails, check the following log files:

1. `winopstool_install.log`: Installation log
2. `api_service_launcher.log`: Service launcher log (after installation)

### Common Issues

1. **Installation fails with permission errors**:
   - Make sure you're running the installer as administrator
   - Check if the installation directory is writable

2. Common issues:
   - **Service won't start**: Check Windows Event Viewer for more details
   - **Port conflict**: The service uses port 8000 by default, make sure it's not in use
   - **Permission issues**: Make sure you're running the installer as administrator

## Uninstalling

To uninstall the service:

1. Open a command prompt with administrator privileges.
2. Run: `"C:\\Program Files\\WinOpsToolAPI\\WinOpsToolAPI.exe" --uninstall`
3. Delete the installation directory.
"""
    
    with open(readme_path, "w") as f:
        f.write(readme_content)
    
    return True

def download_python_installer():
    """Download the Python installer for offline installation"""
    logger.info("Downloading Python installer...")
    
    python_installer_dir = temp_dir / "python_installer"
    python_installer_dir.mkdir(parents=True, exist_ok=True)
    
    python_installer_path = python_installer_dir / "python-3.8.10-amd64.exe"
    
    try:
        logger.info("Downloading Python 3.8.10 installer...")
        urllib.request.urlretrieve(
            "https://www.python.org/ftp/python/3.8.10/python-3.8.10-amd64.exe",
            python_installer_path
        )
    except Exception as e:
        logger.error(f"Failed to download Python installer: {e}")
        return False
    
    return True

def create_offline_package():
    """Create the final offline installer package"""
    logger.info("Creating offline installer package...")
    
    # Create output directory if it doesn't exist
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a zip file containing all the files
    zip_path = output_dir / "WinOpsToolAPI_Offline_Installer.zip"
    
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from the temp directory
        for root, _, files in os.walk(temp_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, temp_dir)
                zipf.write(file_path, arcname)
    
    logger.info(f"Offline installer package created at: {zip_path}")
    
    return True

def main():
    """Main function"""
    logger.info("Starting offline installer creation...")
    
    args = parse_args()
    
    # Setup directories
    if not setup_directories():
        logger.error("Failed to set up directories")
        return 1
    
    # Download dependencies
    if not download_dependencies():
        logger.error("Failed to download dependencies")
        return 1
    
    # Copy dependencies to temp directory
    shutil.copytree(deps_dir, temp_dir / "dependencies")
    
    # Copy source files
    if not copy_source_files():
        logger.error("Failed to copy source files")
        return 1
    
    # Create service launcher script
    if not create_service_launcher():
        logger.error("Failed to create service launcher script")
        return 1
    
    # Create PyInstaller spec file
    if not create_pyinstaller_spec():
        logger.error("Failed to create PyInstaller spec file")
        return 1
    
    # Create installer script
    if not create_installer_script():
        logger.error("Failed to create installer script")
        return 1
    
    # Create batch installer
    if not create_batch_installer():
        logger.error("Failed to create batch installer")
        return 1
    
    # Create README
    if not create_readme():
        logger.error("Failed to create README")
        return 1
    
    # Download Python installer
    if not download_python_installer():
        logger.warning("Failed to download Python installer. The offline installer will require Python to be installed manually.")
    
    # Create offline package
    if not create_offline_package():
        logger.error("Failed to create offline package")
        return 1
    
    logger.info("Offline installer creation completed successfully")
    print("\n" + "="*50)
    print(f"Offline installer package created at: {output_dir / 'WinOpsToolAPI_Offline_Installer.zip'}")
    print("="*50)
    print("\nThis package contains everything needed to install the WinOpsTool REST API service on a machine with limited or no internet access.")
    print("\nTo use the offline installer:")
    print("1. Copy the zip file to the target machine")
    print("2. Extract all files")
    print("3. Run install.bat as administrator")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
