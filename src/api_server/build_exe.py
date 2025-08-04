"""
WinOpsTool REST API Service Executable Builder

This script creates a standalone executable for the WinOpsTool REST API service.
It bundles Python, all dependencies, and the API server code into a single executable.
"""

import os
import sys
import shutil
import subprocess
import logging
import argparse
import platform
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("exe_build.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("build_exe")

# Define paths
script_dir = Path(__file__).parent.absolute()
project_dir = script_dir.parent.parent.absolute()
build_dir = project_dir / "build" / "api_exe"
dist_dir = project_dir / "dist"
spec_file = build_dir / "api_exe.spec"

# Define dependencies
dependencies = [
    "fastapi>=0.95.0",
    "uvicorn>=0.21.1",
    "psutil>=5.9.0",
    "pywin32>=306",
    "requests>=2.28.0",
    "pyinstaller>=5.8.0"
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
        
        logger.info("All required dependencies installed successfully")
        return True
    except Exception as e:
        logger.error(f"Error installing dependencies: {str(e)}")
        return False

def create_service_launcher():
    """Create a service launcher script"""
    logger.info("Creating service launcher script...")
    
    # Create the build directory if it doesn't exist
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the service launcher script
    service_launcher_path = build_dir / "api_service_launcher.py"
    
    service_launcher = """#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sys
import time
import logging
import argparse
import subprocess
import secrets
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import psutil

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='api_service_launcher.log',
    filemode='a'
)
logger = logging.getLogger('api_service_launcher')

# Service name and display name
SERVICE_NAME = "WinOpsToolAPI"
SERVICE_DISPLAY_NAME = "WinOpsTool REST API Service"
SERVICE_DESCRIPTION = "REST API service for remote management of Windows systems"

# API key file path
API_KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "api_key.txt")

def generate_api_key():
    \"\"\"Generate a new API key\"\"\"
    api_key = secrets.token_urlsafe(32)
    with open(API_KEY_FILE, 'w') as f:
        f.write(api_key)
    return api_key

def get_api_key():
    \"\"\"Get the API key from the file or generate a new one\"\"\"
    if os.path.exists(API_KEY_FILE):
        with open(API_KEY_FILE, 'r') as f:
            return f.read().strip()
    else:
        return generate_api_key()

class APIServerService(win32serviceutil.ServiceFramework):
    \"\"\"Windows service class for the API server\"\"\"
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_alive = True
        socket.setdefaulttimeout(60)
        self.process = None
        self.api_key = get_api_key()
    
    def SvcStop(self):
        \"\"\"Stop the service\"\"\"
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_alive = False
        
        # Kill the server process if it's running
        if self.process:
            try:
                for child in psutil.Process(self.process.pid).children(recursive=True):
                    child.kill()
                self.process.kill()
            except:
                pass
    
    def SvcDoRun(self):
        \"\"\"Run the service\"\"\"
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PID_INFO,
            (self._svc_name_, '')
        )
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)
        self.main()
    
    def main(self):
        \"\"\"Main service function\"\"\"
        logger.info("Starting API server service...")
        
        # Get the directory of the executable
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            script_dir = os.path.dirname(sys.executable)
        else:
            # Running as script
            script_dir = os.path.dirname(os.path.abspath(__file__))
        
        # Set environment variables
        env = os.environ.copy()
        env["WINOPSTOOL_API_KEY"] = self.api_key
        
        # Start the server
        server_script = os.path.join(script_dir, "server.py")
        if os.path.exists(server_script):
            cmd = [sys.executable, server_script]
        else:
            # If running as frozen executable, use the module name
            cmd = [sys.executable, "-m", "api_server.server"]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        
        try:
            # Start the server process
            self.process = subprocess.Popen(
                cmd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                cwd=script_dir
            )
            
            logger.info(f"API server started with PID: {self.process.pid}")
            logger.info(f"API Key: {self.api_key}")
            
            # Wait for the service to be stopped
            while self.is_alive:
                rc = win32event.WaitForSingleObject(self.hWaitStop, 1000)
                if rc == win32event.WAIT_OBJECT_0:
                    # Stop signal received
                    break
                
                # Check if the process is still running
                if self.process.poll() is not None:
                    logger.error(f"API server process exited with code: {self.process.returncode}")
                    
                    # Get the output
                    stdout, stderr = self.process.communicate()
                    logger.error(f"STDOUT: {stdout.decode('utf-8', errors='ignore')}")
                    logger.error(f"STDERR: {stderr.decode('utf-8', errors='ignore')}")
                    
                    # Try to restart the process
                    logger.info("Attempting to restart the API server...")
                    self.process = subprocess.Popen(
                        cmd,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        cwd=script_dir
                    )
                    logger.info(f"API server restarted with PID: {self.process.pid}")
        
        except Exception as e:
            logger.error(f"Error running API server: {str(e)}")
        
        logger.info("API server service stopped")

def install_service():
    \"\"\"Install the service\"\"\"
    try:
        logger.info("Installing service...")
        
        # If running as frozen executable, use the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
            
            # Install the service
            subprocess.run(
                [executable, "--startup", "auto", "install"],
                check=True
            )
        else:
            # Running as script
            win32serviceutil.HandleCommandLine(APIServerService)
        
        # Generate API key
        api_key = get_api_key()
        logger.info(f"Service installed successfully with API Key: {api_key}")
        print(f"Service installed successfully with API Key: {api_key}")
        
        return True
    except Exception as e:
        logger.error(f"Error installing service: {str(e)}")
        return False

def uninstall_service():
    \"\"\"Uninstall the service\"\"\"
    try:
        logger.info("Uninstalling service...")
        
        # If running as frozen executable, use the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
            
            # Stop the service if it's running
            try:
                subprocess.run(
                    [executable, "stop"],
                    check=False
                )
            except:
                pass
            
            # Uninstall the service
            subprocess.run(
                [executable, "remove"],
                check=True
            )
        else:
            # Running as script
            win32serviceutil.HandleCommandLine(APIServerService)
        
        logger.info("Service uninstalled successfully")
        print("Service uninstalled successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error uninstalling service: {str(e)}")
        return False

def start_service():
    \"\"\"Start the service\"\"\"
    try:
        logger.info("Starting service...")
        
        # If running as frozen executable, use the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
            
            # Start the service
            subprocess.run(
                [executable, "start"],
                check=True
            )
        else:
            # Running as script
            win32serviceutil.HandleCommandLine(APIServerService)
        
        logger.info("Service started successfully")
        print("Service started successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error starting service: {str(e)}")
        return False

def stop_service():
    \"\"\"Stop the service\"\"\"
    try:
        logger.info("Stopping service...")
        
        # If running as frozen executable, use the executable path
        if getattr(sys, 'frozen', False):
            # Running as compiled executable
            executable = sys.executable
            
            # Stop the service
            subprocess.run(
                [executable, "stop"],
                check=True
            )
        else:
            # Running as script
            win32serviceutil.HandleCommandLine(APIServerService)
        
        logger.info("Service stopped successfully")
        print("Service stopped successfully")
        
        return True
    except Exception as e:
        logger.error(f"Error stopping service: {str(e)}")
        return False

def get_service_status():
    \"\"\"Get the service status\"\"\"
    try:
        # Check if the service is installed
        service_installed = False
        service_running = False
        
        try:
            import win32serviceutil
            service_installed = win32serviceutil.QueryServiceStatus(SERVICE_NAME)[1] is not None
            service_running = win32serviceutil.QueryServiceStatus(SERVICE_NAME)[1] == win32service.SERVICE_RUNNING
        except:
            pass
        
        # Get the API key
        api_key = get_api_key()
        
        print(f"Service Name: {SERVICE_NAME}")
        print(f"Service Installed: {'Yes' if service_installed else 'No'}")
        print(f"Service Running: {'Yes' if service_running else 'No'}")
        print(f"API Key: {api_key}")
        
        return True
    except Exception as e:
        logger.error(f"Error getting service status: {str(e)}")
        return False

def main():
    \"\"\"Main function\"\"\"
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Launcher")
    
    # Add arguments
    parser.add_argument("--install", action="store_true", help="Install the service")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--status", action="store_true", help="Get the service status")
    parser.add_argument("--generate-key", action="store_true", help="Generate a new API key")
    
    args = parser.parse_args()
    
    # If no arguments are provided, show the help message
    if not any(vars(args).values()):
        parser.print_help()
        return 0
    
    # Install the service
    if args.install:
        if not install_service():
            return 1
    
    # Uninstall the service
    if args.uninstall:
        if not uninstall_service():
            return 1
    
    # Start the service
    if args.start:
        if not start_service():
            return 1
    
    # Stop the service
    if args.stop:
        if not stop_service():
            return 1
    
    # Get the service status
    if args.status:
        if not get_service_status():
            return 1
    
    # Generate a new API key
    if args.generate_key:
        api_key = generate_api_key()
        print(f"New API Key generated: {api_key}")
    
    return 0

if __name__ == "__main__":
    # If run as a service, handle the service commands
    if len(sys.argv) > 1 and sys.argv[1] in ["install", "update", "remove", "start", "stop", "restart"]:
        win32serviceutil.HandleCommandLine(APIServerService)
    else:
        # Otherwise, run the main function
        sys.exit(main())
"""
    
    with open(service_launcher_path, "w") as f:
        f.write(service_launcher)
    
    logger.info(f"Service launcher script created at: {service_launcher_path}")
    return True

def create_pyinstaller_spec():
    """Create a PyInstaller spec file"""
    logger.info("Creating PyInstaller spec file...")
    
    # Create the build directory if it doesn't exist
    build_dir.mkdir(parents=True, exist_ok=True)
    
    # Create the PyInstaller spec file
    spec_content = f"""# -*- mode: python ; coding: utf-8 -*-

import sys
from pathlib import Path

block_cipher = None

# Define paths
script_dir = Path(r"{script_dir}")
project_dir = Path(r"{project_dir}")

# Define data files
data_files = [
    (str(project_dir / "docs/REST_API_GUIDE.md"), "docs"),
    (str(script_dir / "README.md"), "."),
]

# Define hidden imports
hidden_imports = [
    "uvicorn.logging",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
    "uvicorn.lifespan.off",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.websockets.websockets_impl",
    "uvicorn.protocols.websockets.wsproto_impl",
    "win32timezone",
    "win32serviceutil",
    "win32service",
    "win32event",
    "servicemanager",
    "socket",
    "psutil",
    "fastapi",
    "pydantic",
    "starlette",
    "starlette.routing",
    "starlette.applications",
]

a = Analysis(
    [str(build_dir / "api_service_launcher.py")],
    pathex=[str(project_dir)],
    binaries=[],
    datas=data_files,
    hiddenimports=hidden_imports,
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
    [],
    exclude_binaries=True,
    name="WinOpsToolAPI",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(project_dir / "assets/icon.ico") if (project_dir / "assets/icon.ico").exists() else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name="WinOpsToolAPI",
)
"""
    
    with open(spec_file, "w") as f:
        f.write(spec_content)
    
    logger.info(f"PyInstaller spec file created at: {spec_file}")
    return True

def build_executable():
    """Build the executable using PyInstaller"""
    logger.info("Building executable with PyInstaller...")
    
    try:
        # Run PyInstaller
        subprocess.run([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--workpath", str(build_dir),
            "--distpath", str(dist_dir),
            str(spec_file)
        ], check=True)
        
        logger.info(f"Executable built successfully at: {dist_dir / 'WinOpsToolAPI'}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to build executable: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error building executable: {str(e)}")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Executable Builder")
    
    # Add arguments
    parser.add_argument("--skip-deps", action="store_true", help="Skip installing dependencies")
    parser.add_argument("--output-dir", help="Custom output directory for the executable")
    
    args = parser.parse_args()
    
    logger.info("Starting executable creation process...")
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
    
    logger.info("Executable creation completed successfully!")
    logger.info(f"Executable is available at: {dist_dir / 'WinOpsToolAPI'}")
    
    # Provide instructions for manual installer creation
    print("\n=== Manual Installer Creation Instructions ===")
    print("To create a Windows installer, download and install Inno Setup from:")
    print("https://jrsoftware.org/isdl.php")
    print("\nThen run the following command:")
    print(f"iscc.exe {build_dir / 'installer.iss'}")
    print("\nThis will create a WinOpsToolAPI_Setup.exe installer in the dist directory.")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
