import os
import sys
import subprocess
import logging
import argparse
import shutil
from pathlib import Path
import secrets

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("winopstool_install.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("winopstool_installer")

# Define paths
script_dir = Path(__file__).parent.absolute()
deps_dir = script_dir / "dependencies"
src_dir = script_dir / "src"
api_server_dir = src_dir / "api_server"

def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Installer")
    parser.add_argument("--install-dir", default="C:\\Program Files\\WinOpsToolAPI",
                        help="Installation directory")
    parser.add_argument("--no-service", action="store_true",
                        help="Don't install as a Windows service")
    args = parser.parse_args()
    return args

def install_dependencies():
    """Install all dependencies from the local directory"""
    logger.info("Installing dependencies...")
    
    # Check if pip is available
    try:
        subprocess.run([sys.executable, "-m", "pip", "--version"], check=True)
    except subprocess.CalledProcessError:
        logger.error("pip is not installed or not working properly")
        return False
    
    # Install all wheel files first (they're easier)
    wheel_files = list(deps_dir.glob("*.whl"))
    if wheel_files:
        logger.info(f"Installing {len(wheel_files)} wheel packages...")
        try:
            subprocess.run([
                sys.executable, "-m", "pip", "install", "--no-index",
                "--find-links", str(deps_dir),
                *[str(wheel) for wheel in wheel_files]
            ], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to install wheel packages: {e}")
            # Continue anyway, we'll try with the source distributions
    
    # Install all source distributions
    try:
        logger.info("Installing packages from source distributions...")
        subprocess.run([
            sys.executable, "-m", "pip", "install", "--no-index",
            "--find-links", str(deps_dir),
            "fastapi", "uvicorn", "psutil", "pywin32", "requests", "pyinstaller"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install packages: {e}")
        return False
    
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    logger.info("Building executable...")
    
    # Create a service launcher script
    service_launcher_path = api_server_dir / "service_launcher.py"
    api_key = secrets.token_hex(16)
    
    # Create PyInstaller spec file
    spec_path = api_server_dir / "api_installer.spec"
    
    with open(spec_path, "w") as f:
        f.write(f'''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    [r'{api_server_dir / "server.py"}'],
    pathex=[r'{src_dir}'],
    binaries=[],
    datas=[
        (r'{src_dir.parent / "docs/REST_API_GUIDE.md"}', 'docs'),
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
''')
    
    # Build the executable
    try:
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            str(spec_path)
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {e}")
        return False
    
    return True

def install_service(install_dir):
    """Install the service"""
    logger.info(f"Installing service to {install_dir}...")
    
    # Create installation directory
    install_path = Path(install_dir)
    install_path.mkdir(parents=True, exist_ok=True)
    
    # Copy the executable and related files
    dist_dir = src_dir.parent / "dist"
    exe_path = dist_dir / "WinOpsToolAPI.exe"
    
    if not exe_path.exists():
        logger.error(f"Executable not found at {exe_path}")
        return False
    
    shutil.copy(exe_path, install_path / "WinOpsToolAPI.exe")
    
    # Copy documentation
    docs_dir = install_path / "docs"
    docs_dir.mkdir(exist_ok=True)
    
    api_guide = dist_dir / "docs" / "REST_API_GUIDE.md"
    if api_guide.exists():
        shutil.copy(api_guide, docs_dir / "REST_API_GUIDE.md")
    
    # Install the service
    try:
        subprocess.run([
            str(install_path / "WinOpsToolAPI.exe"),
            "--install"
        ], check=True)
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install service: {e}")
        return False
    
    return True

def main():
    """Main function"""
    logger.info("Starting WinOpsTool REST API Service installation...")
    
    args = parse_args()
    
    # Install dependencies
    if not install_dependencies():
        logger.error("Failed to install dependencies")
        return 1
    
    # Build executable
    if not build_executable():
        logger.error("Failed to build executable")
        return 1
    
    # Install service if requested
    if not args.no_service:
        if not install_service(args.install_dir):
            logger.error("Failed to install service")
            return 1
    else:
        logger.info("Skipping service installation as requested")
        # Just copy the executable to the installation directory
        install_path = Path(args.install_dir)
        install_path.mkdir(parents=True, exist_ok=True)
        
        dist_dir = src_dir.parent / "dist"
        exe_path = dist_dir / "WinOpsToolAPI.exe"
        
        if not exe_path.exists():
            logger.error(f"Executable not found at {exe_path}")
            return 1
        
        shutil.copy(exe_path, install_path / "WinOpsToolAPI.exe")
    
    logger.info("Installation completed successfully")
    print("\n" + "="*50)
    print("WinOpsTool REST API Service installed successfully!")
    print("="*50)
    
    if not args.no_service:
        print("\nThe service has been installed and started.")
        print("You can manage it using:")
        print(f"  {args.install_dir}\\WinOpsToolAPI.exe --status")
        print(f"  {args.install_dir}\\WinOpsToolAPI.exe --stop")
        print(f"  {args.install_dir}\\WinOpsToolAPI.exe --start")
    else:
        print("\nThe executable has been installed to:")
        print(f"  {args.install_dir}\\WinOpsToolAPI.exe")
        print("\nYou can run it manually or install it as a service with:")
        print(f"  {args.install_dir}\\WinOpsToolAPI.exe --install")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
