"""
WinOpsTool REST API Service Installer Creator

This script creates a standalone installer for the WinOpsTool REST API service.
It bundles Python, all dependencies, and the API server code into a single executable.
"""

import os
import sys
import shutil
import subprocess
import logging
import argparse
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("installer_build.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("create_installer")

# Define paths
script_dir = Path(__file__).parent
project_dir = script_dir.parent.parent
build_dir = project_dir / "build" / "api_installer"
dist_dir = project_dir / "dist"
spec_file = build_dir / "api_installer.spec"

import platform

# Define dependencies
dependencies = [
    "fastapi>=0.95.0",
    "uvicorn>=0.21.1",
    "psutil>=5.9.0",
    "pywin32>=306",
    "requests>=2.28.0",
    "pyinstaller>=5.8.0"
]

# Optional dependencies
optional_dependencies = [
    "innosetup>=0.10.0"
]

def check_prerequisites():
    """Check if all prerequisites are installed"""
    logger.info("Checking prerequisites...")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 8):
        logger.error("Python 3.8 or higher is required")
        return False
    
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check if pip is installed
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True, stdout=subprocess.PIPE)
        logger.info("pip is installed")
    except subprocess.CalledProcessError:
        logger.error("pip is not installed")
        return False
    
    # Check if Inno Setup is installed
    try:
        # Try to find iscc.exe in common locations
        inno_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe"
        ]
        
        inno_found = False
        for path in inno_paths:
            if os.path.exists(path):
                os.environ["INNO_SETUP_PATH"] = path
                inno_found = True
                logger.info(f"Inno Setup found at: {path}")
                break
        
        if not inno_found:
            logger.warning("Inno Setup not found in common locations")
            logger.warning("Will attempt to use innosetup Python package instead")
    except Exception as e:
        logger.warning(f"Error checking for Inno Setup: {str(e)}")
    
    return True

def install_dependencies():
    """Install all required dependencies"""
    logger.info("Installing dependencies...")
    
    try:
        # Install required dependencies
        for dep in dependencies:
            logger.info(f"Installing {dep}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to install {dep}: {str(e)}")
                return False
        
        # Try to install optional dependencies
        for dep in optional_dependencies:
            logger.info(f"Installing optional dependency {dep}")
            try:
                subprocess.run([sys.executable, "-m", "pip", "install", dep], check=False)
                logger.info(f"Successfully installed {dep}")
            except subprocess.CalledProcessError as e:
                logger.warning(f"Failed to install optional dependency {dep}: {str(e)}")
                logger.warning(f"This may limit some functionality but is not critical")
        
        logger.info("All required dependencies installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False

def create_pyinstaller_spec():
    """Create a PyInstaller spec file"""
    logger.info("Creating PyInstaller spec file...")
    
    # Create build directory if it doesn't exist
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the spec file
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['{script_dir.joinpath("service_launcher.py")}'],
    pathex=['{project_dir}'],
    binaries=[],
    datas=[
        ('{script_dir.joinpath("server.py")}', 'src/api_server'),
        ('{script_dir.joinpath("deploy_service.py")}', 'src/api_server'),
    ],
    hiddenimports=[
        'fastapi', 'uvicorn', 'psutil', 'win32service', 'win32serviceutil', 
        'win32event', 'win32api', 'servicemanager', 'socket', 'uuid'
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
    icon='{project_dir.joinpath("assets/icon.ico") if os.path.exists(project_dir.joinpath("assets/icon.ico")) else None}',
)
"""
    
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    logger.info(f"PyInstaller spec file created at {spec_file}")
    return True

def create_service_launcher():
    """Create a service launcher script"""
    logger.info("Creating service launcher script...")
    
    launcher_path = script_dir / "service_launcher.py"
    
    launcher_content = """#!/usr/bin/env python
'''
WinOpsTool REST API Service Launcher

This script is the entry point for the standalone executable.
It installs and manages the WinOpsTool REST API service.
'''

import os
import sys
import argparse
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_service_launcher.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("service_launcher")

def main():
    '''Main function'''
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service")
    
    # Add arguments
    parser.add_argument("--install", action="store_true", help="Install the service")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--status", action="store_true", help="Check the status of the service")
    parser.add_argument("--generate-key", action="store_true", help="Generate a new API key")
    parser.add_argument("--run", action="store_true", help="Run the server directly (not as a service)")
    
    args = parser.parse_args()
    
    # Get the directory of the executable
    if getattr(sys, 'frozen', False):
        # Running as compiled executable
        app_dir = Path(sys._MEIPASS)
    else:
        # Running as script
        app_dir = Path(__file__).parent
    
    # Add the app directory to the path
    sys.path.insert(0, str(app_dir))
    
    # Import the deploy_service module
    try:
        sys.path.append(str(app_dir))
        from src.api_server.deploy_service import install_service, uninstall_service, start_service, stop_service, check_service_status
        logger.info("Imported deploy_service module")
    except ImportError as e:
        logger.error(f"Failed to import deploy_service module: {str(e)}")
        return 1
    
    # Process arguments
    if args.install:
        install_service()
    elif args.uninstall:
        uninstall_service()
    elif args.start:
        start_service()
    elif args.stop:
        stop_service()
    elif args.status:
        check_service_status()
    elif args.generate_key:
        # Import the deploy_service module for generate_key
        from src.api_server.deploy_service import main as deploy_main
        sys.argv = [sys.argv[0], "--generate-key"]
        deploy_main()
    elif args.run:
        # Run the server directly
        try:
            import uvicorn
            from src.api_server.server import app
            
            # Start the server
            uvicorn.run(app, host="0.0.0.0", port=8000)
        except ImportError as e:
            logger.error(f"Failed to import server module: {str(e)}")
            return 1
    else:
        parser.print_help()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
"""
    
    with open(launcher_path, "w") as f:
        f.write(launcher_content)
    
    logger.info(f"Service launcher script created at {launcher_path}")
    return True

def create_inno_setup_script():
    """Create an Inno Setup script"""
    logger.info("Creating Inno Setup script...")
    
    # Create the output directory if it doesn't exist
    dist_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the Inno Setup script
    inno_script_path = build_dir / "installer.iss"
    
    inno_script = f"""#define MyAppName "WinOpsTool REST API Service"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "WinOpsTool Team"
#define MyAppURL "https://github.com/yourusername/WinOpsTool"
#define MyAppExeName "WinOpsToolAPI.exe"

[Setup]
AppId={{{{8A7D8AE3-9F0D-4C8B-B6A1-17E457CA8F9A}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
AppPublisherURL={{#MyAppURL}}
AppSupportURL={{#MyAppURL}}
AppUpdatesURL={{#MyAppURL}}
DefaultDirName={{autopf}}\\WinOpsToolAPI
DefaultGroupName={{#MyAppName}}
AllowNoIcons=yes
LicenseFile={project_dir / "LICENSE" if os.path.exists(project_dir / "LICENSE") else build_dir / "LICENSE.txt"}
OutputDir={dist_dir}
OutputBaseFilename=WinOpsToolAPI_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin
SetupIconFile={project_dir / "assets/icon.ico" if os.path.exists(project_dir / "assets/icon.ico") else ""}

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked
Name: "installservice"; Description: "Install as Windows Service"; GroupDescription: "Service Options"; Flags: checkedonce

[Files]
Source: "{project_dir / "dist/WinOpsToolAPI.exe"}"; DestDir: "{{app}}"; Flags: ignoreversion
Source: "{project_dir / "docs/REST_API_GUIDE.md"}"; DestDir: "{{app}}\\docs"; Flags: ignoreversion
Source: "{script_dir / "README.md"}"; DestDir: "{{app}}"; Flags: ignoreversion isreadme

[Icons]
Name: "{{group}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"
Name: "{{group}}\\Documentation"; Filename: "{{app}}\\docs\\REST_API_GUIDE.md"
Name: "{{group}}\\{{cm:UninstallProgram,{{#MyAppName}}}}"; Filename: "{{uninstallexe}}"
Name: "{{commondesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Parameters: "--install"; Description: "Install Windows Service"; Flags: runhidden; Tasks: installservice
Filename: "{{app}}\\{{#MyAppExeName}}"; Parameters: "--status"; Description: "Show API Key"; Flags: postinstall runhidden

[UninstallRun]
Filename: "{{app}}\\{{#MyAppExeName}}"; Parameters: "--uninstall"; Flags: runhidden

[Code]
procedure CurStepChanged(CurStep: TSetupStep);
begin
  if CurStep = ssPostInstall then
  begin
    if WizardIsTaskSelected('installservice') then
    begin
      // Start the service after installation
      Exec(ExpandConstant('{{app}}\\{{#MyAppExeName}}'), '--start', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
    end;
  end;
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usUninstall then
  begin
    // Stop the service before uninstallation
    Exec(ExpandConstant('{{app}}\\{{#MyAppExeName}}'), '--stop', '', SW_HIDE, ewWaitUntilTerminated, ResultCode);
  end;
end;
"""
    
    # Create a default LICENSE.txt if it doesn't exist
    if not os.path.exists(project_dir / "LICENSE"):
        with open(build_dir / "LICENSE.txt", "w") as f:
            f.write("""MIT License

Copyright (c) 2023 WinOpsTool Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
""")
    
    with open(inno_script_path, "w") as f:
        f.write(inno_script)
    
    logger.info(f"Inno Setup script created at {inno_script_path}")
    return inno_script_path

def build_executable():
    """Build the executable using PyInstaller"""
    logger.info("Building executable with PyInstaller...")
    
    try:
        # Run PyInstaller
        subprocess.run([
            sys.executable, "-m", "PyInstaller", 
            "--clean", "--noconfirm", str(spec_file)
        ], check=True)
        
        logger.info("Executable built successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error building executable: {str(e)}")
        return False

def build_installer(inno_script_path):
    """Build the installer using Inno Setup"""
    logger.info("Building installer with Inno Setup...")
    
    try:
        # Check if we have a direct path to Inno Setup
        if "INNO_SETUP_PATH" in os.environ and os.path.exists(os.environ["INNO_SETUP_PATH"]):
            # Use the direct path
            try:
                subprocess.run([
                    os.environ["INNO_SETUP_PATH"], str(inno_script_path)
                ], check=True)
                logger.info(f"Installer built successfully at {dist_dir / 'WinOpsToolAPI_Setup.exe'}")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"Failed to build installer with direct Inno Setup path: {str(e)}")
        
        # Try the innosetup Python package
        try:
            from innosetup import innosetup
            innosetup(str(inno_script_path))
            logger.info(f"Installer built successfully at {dist_dir / 'WinOpsToolAPI_Setup.exe'}")
            return True
        except ImportError:
            logger.warning("Inno Setup not found and innosetup package not installed")
            
        # Try to find iscc.exe in common locations
        common_paths = [
            r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
            r"C:\Program Files\Inno Setup 6\ISCC.exe",
            r"C:\Program Files (x86)\Inno Setup 5\ISCC.exe",
            r"C:\Program Files\Inno Setup 5\ISCC.exe"
        ]
        
        for path in common_paths:
            if os.path.exists(path):
                try:
                    subprocess.run([path, str(inno_script_path)], check=True)
                    logger.info(f"Installer built successfully at {dist_dir / 'WinOpsToolAPI_Setup.exe'}")
                    return True
                except subprocess.CalledProcessError:
                    continue
        
        # If we got here, we couldn't build the installer
        logger.warning("Could not build installer with Inno Setup")
        logger.warning("Please install Inno Setup from https://jrsoftware.org/isdl.php")
        logger.warning(f"You can manually run the Inno Setup script at {inno_script_path}")
        return False
    except Exception as e:
        logger.error(f"Error building installer: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Installer Creator")
    
    # Add arguments
    parser.add_argument("--skip-deps", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--exe-only", action="store_true", help="Build executable only, skip installer creation")
    parser.add_argument("--output-dir", help="Custom output directory for the installer")
    
    args = parser.parse_args()
    
    logger.info("Starting installer creation process...")
    logger.info(f"Python version: {platform.python_version()}")
    logger.info(f"Platform: {platform.platform()}")
    
    # Check prerequisites
    if not check_prerequisites():
        logger.error("Prerequisites check failed")
        return 1
    
    # Install dependencies
    if not args.skip_deps:
        if not install_dependencies():
            logger.error("Failed to install dependencies")
            return 1
    
    # Create service launcher
    if not create_service_launcher():
        logger.error("Failed to create service launcher")
        return 1
    
    # Create PyInstaller spec file
    if not create_pyinstaller_spec():
        logger.error("Failed to create PyInstaller spec file")
        return 1
    
    # Build executable
    if not build_executable():
        logger.error("Failed to build executable")
        return 1
    
    # If exe-only flag is set, stop here
    if args.exe_only:
        logger.info("Executable creation completed successfully!")
        logger.info(f"Executable is available at: {project_dir / 'dist/WinOpsToolAPI.exe'}")
        return 0
    
    # Create Inno Setup script
    inno_script_path = create_inno_setup_script()
    if not inno_script_path:
        logger.error("Failed to create Inno Setup script")
        return 1
    
    # Build installer
    if not build_installer(inno_script_path):
        logger.warning("Could not build full installer, but executable was created successfully")
        logger.info(f"Executable is available at: {project_dir / 'dist/WinOpsToolAPI.exe'}")
        return 0
    
    logger.info("Installer creation completed successfully!")
    logger.info(f"Installer is available at: {dist_dir / 'WinOpsToolAPI_Setup.exe'}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
