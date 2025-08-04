"""
WinOpsTool REST API Service Simple Executable Builder

This script creates a standalone executable for the WinOpsTool REST API service.
It bundles Python, all dependencies, and the API server code into a single executable.
"""

import os
import sys
import subprocess
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("simple_build.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("simple_build")

# Define paths
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent.parent.absolute()
build_dir = project_dir / "build" / "api_exe"
dist_dir = project_dir / "dist"

def install_dependencies():
    """Install required dependencies"""
    logger.info("Installing required dependencies...")
    
    dependencies = [
        "pyinstaller>=5.8.0",
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "psutil>=5.9.0",
        "pywin32>=306",
        "requests>=2.28.0"
    ]
    
    for dep in dependencies:
        logger.info(f"Installing {dep}")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", dep], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install {dep}: {e}")
            return False
    
    return True

def create_spec_file():
    """Create PyInstaller spec file"""
    logger.info("Creating spec file...")
    
    # Create build directory if it doesn't exist
    build_dir.mkdir(parents=True, exist_ok=True)
    
    spec_path = build_dir / "simple_api.spec"
    
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{script_dir / "server.py"}'],
    pathex=[r'{project_dir}'],
    binaries=[],
    datas=[
        (r'{project_dir / "docs/REST_API_GUIDE.md"}', 'docs'),
        (r'{script_dir / "README.md"}', '.')
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
)
"""
    
    with open(spec_path, 'w') as f:
        f.write(spec_content)
    
    logger.info(f"Spec file created at {spec_path}")
    return spec_path

def build_executable(spec_path):
    """Build executable using PyInstaller"""
    logger.info("Building executable...")
    
    try:
        subprocess.run([
            sys.executable, 
            "-m", 
            "PyInstaller", 
            "--clean",
            str(spec_path)
        ], check=True)
        
        logger.info(f"Executable built successfully at {dist_dir / 'WinOpsToolAPI.exe'}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {e}")
        return False

def main():
    """Main function"""
    logger.info("Starting simple build process...")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        return 1
    
    # Create spec file
    spec_path = create_spec_file()
    if not spec_path:
        logger.error("Failed to create spec file")
        return 1
    
    # Build executable
    if not build_executable(spec_path):
        logger.error("Failed to build executable")
        return 1
    
    logger.info("Build process completed successfully!")
    logger.info(f"Executable is available at: {dist_dir / 'WinOpsToolAPI.exe'}")
    
    print("\n=== Manual Installer Creation Instructions ===")
    print("To create a Windows installer, download and install Inno Setup from:")
    print("https://jrsoftware.org/isdl.php")
    print("\nThen create a simple Inno Setup script (installer.iss) with the following content:")
    print("""
#define MyAppName "WinOpsTool REST API Service"
#define MyAppVersion "1.0.0"
#define MyAppPublisher "WinOpsTool Team"
#define MyAppExeName "WinOpsToolAPI.exe"

[Setup]
AppId={{8A7D8AE3-9F0D-4C8B-B6A1-17E457CA8F9A}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\\WinOpsToolAPI
DefaultGroupName={#MyAppName}
AllowNoIcons=yes
OutputDir=dist
OutputBaseFilename=WinOpsToolAPI_Setup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "dist\\WinOpsToolAPI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "docs\\REST_API_GUIDE.md"; DestDir: "{app}\\docs"; Flags: ignoreversion
Source: "src\\api_server\\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

[Icons]
Name: "{group}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"
Name: "{group}\\Documentation"; Filename: "{app}\\docs\\REST_API_GUIDE.md"
Name: "{commondesktop}\\{#MyAppName}"; Filename: "{app}\\{#MyAppExeName}"; Tasks: desktopicon
    """)
    print("\nAnd run: iscc.exe installer.iss")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
