"""
WinOpsTool REST API Remote Deployment Script

This script helps deploy the WinOpsTool REST API server to remote machines.
It copies the necessary files, installs dependencies, and sets up the service.
"""

import os
import sys
import argparse
import subprocess
import shutil
import tempfile
import uuid
import logging
from pathlib import Path

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("remote_deploy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("remote_deploy")

def create_deployment_package(output_dir=None):
    """
    Create a deployment package for the REST API server.
    
    Args:
        output_dir: Directory to create the package in. If None, a temporary directory is used.
        
    Returns:
        Path to the deployment package
    """
    try:
        # Get the source directory
        src_dir = Path(__file__).parent
        project_dir = src_dir.parent.parent
        
        # Create a temporary directory if output_dir is not specified
        if output_dir is None:
            output_dir = tempfile.mkdtemp(prefix="winopstool_api_")
            logger.info(f"Created temporary directory: {output_dir}")
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"Using output directory: {output_dir}")
        
        # Create the package structure
        package_dir = Path(output_dir) / "winopstool_api"
        package_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy the API server files
        api_dir = package_dir / "api_server"
        api_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy server.py
        shutil.copy2(src_dir / "server.py", api_dir / "server.py")
        
        # Copy deploy_service.py
        shutil.copy2(src_dir / "deploy_service.py", api_dir / "deploy_service.py")
        
        # Copy README.md
        shutil.copy2(src_dir / "README.md", api_dir / "README.md")
        
        # Create an empty __init__.py file
        with open(api_dir / "__init__.py", "w") as f:
            f.write("# WinOpsTool REST API Server\n")
        
        # Create a requirements.txt file
        with open(package_dir / "requirements.txt", "w") as f:
            f.write("fastapi>=0.95.0\n")
            f.write("uvicorn>=0.21.1\n")
            f.write("psutil>=5.9.0\n")
            f.write("pywin32>=306\n")
        
        # Create a setup.py file
        with open(package_dir / "setup.py", "w") as f:
            f.write("""
from setuptools import setup, find_packages

setup(
    name="winopstool_api",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.95.0",
        "uvicorn>=0.21.1",
        "psutil>=5.9.0",
        "pywin32>=306"
    ],
    author="WinOpsTool Team",
    description="REST API server for WinOpsTool remote management",
    python_requires=">=3.8",
)
""")
        
        # Create an install.bat file
        with open(package_dir / "install.bat", "w") as f:
            f.write("""@echo off
echo Installing WinOpsTool REST API Server...

REM Check for Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH
    exit /b 1
)

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

REM Install the service
echo Installing the service...
python api_server\\deploy_service.py --install

echo Installation complete!
echo API key is saved in api_server\\api_key.txt
""")
        
        # Create an uninstall.bat file
        with open(package_dir / "uninstall.bat", "w") as f:
            f.write("""@echo off
echo Uninstalling WinOpsTool REST API Server...

REM Uninstall the service
echo Uninstalling the service...
python api_server\\deploy_service.py --uninstall

echo Uninstallation complete!
""")
        
        # Create a README.md file
        with open(package_dir / "README.md", "w") as f:
            f.write("""# WinOpsTool REST API Server Deployment Package

This package contains the WinOpsTool REST API server for remote management.

## Installation

1. Run `install.bat` with administrator privileges
2. The service will be installed and started automatically
3. The API key will be displayed and saved to `api_server\\api_key.txt`

## Uninstallation

1. Run `uninstall.bat` with administrator privileges
2. The service will be stopped and uninstalled

## Manual Installation

1. Install the required Python packages:

```
pip install -r requirements.txt
```

2. Install the service:

```
python api_server\\deploy_service.py --install
```

## Manual Uninstallation

```
python api_server\\deploy_service.py --uninstall
```
""")
        
        # Create a zip file
        zip_path = Path(output_dir) / "winopstool_api.zip"
        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", output_dir, "winopstool_api")
        
        logger.info(f"Created deployment package: {zip_path}")
        return zip_path
    
    except Exception as e:
        logger.error(f"Failed to create deployment package: {str(e)}")
        return None

def deploy_to_remote(remote_host, username=None, password=None, package_path=None):
    """
    Deploy the REST API server to a remote machine.
    
    Args:
        remote_host: Hostname or IP address of the remote machine
        username: Username for authentication
        password: Password for authentication
        package_path: Path to the deployment package
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Create a deployment package if not specified
        if package_path is None:
            package_path = create_deployment_package()
            if package_path is None:
                return False
        
        # Check if psexec is available
        try:
            subprocess.run(["psexec", "/?"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        except FileNotFoundError:
            logger.error("psexec is not available. Please install PsTools from Microsoft.")
            return False
        
        # Create a temporary directory on the remote machine
        remote_dir = f"C:\\WinOpsToolAPI_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Creating directory on remote machine: {remote_dir}")
        
        psexec_cmd = ["psexec", f"\\\\{remote_host}"]
        if username:
            psexec_cmd.extend(["-u", username])
        if password:
            psexec_cmd.extend(["-p", password])
        
        psexec_cmd.extend(["-h", "cmd", "/c", f"mkdir {remote_dir}"])
        
        subprocess.run(psexec_cmd, check=True)
        
        # Copy the deployment package to the remote machine
        logger.info(f"Copying deployment package to remote machine: {remote_host}")
        
        copy_cmd = ["xcopy", str(package_path), f"\\\\{remote_host}\\admin$\\{remote_dir.replace('C:', '')}", "/Y"]
        subprocess.run(copy_cmd, check=True)
        
        # Extract the zip file on the remote machine
        logger.info("Extracting deployment package on remote machine")
        
        extract_cmd = ["psexec", f"\\\\{remote_host}"]
        if username:
            extract_cmd.extend(["-u", username])
        if password:
            extract_cmd.extend(["-p", password])
        
        extract_cmd.extend(["-h", "powershell", "-command", 
                          f"Expand-Archive -Path '{remote_dir}\\winopstool_api.zip' -DestinationPath '{remote_dir}' -Force"])
        
        subprocess.run(extract_cmd, check=True)
        
        # Install the service on the remote machine
        logger.info("Installing the service on remote machine")
        
        install_cmd = ["psexec", f"\\\\{remote_host}"]
        if username:
            install_cmd.extend(["-u", username])
        if password:
            install_cmd.extend(["-p", password])
        
        install_cmd.extend(["-h", "cmd", "/c", f"cd /d {remote_dir}\\winopstool_api && install.bat"])
        
        process = subprocess.run(install_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        
        # Extract the API key from the output
        api_key = None
        for line in process.stdout.splitlines():
            if "API key:" in line:
                api_key = line.split("API key:")[1].strip()
                break
        
        if api_key:
            logger.info(f"API key for remote machine {remote_host}: {api_key}")
        else:
            logger.warning(f"Could not extract API key from output")
        
        logger.info(f"Deployment to {remote_host} completed successfully")
        
        # Return the API key
        return {
            "success": True,
            "host": remote_host,
            "api_key": api_key,
            "port": 8000
        }
    
    except Exception as e:
        logger.error(f"Failed to deploy to remote machine {remote_host}: {str(e)}")
        return {
            "success": False,
            "host": remote_host,
            "error": str(e)
        }

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Remote Deployment")
    
    # Add arguments
    parser.add_argument("--create-package", action="store_true", help="Create a deployment package")
    parser.add_argument("--output-dir", help="Output directory for the deployment package")
    parser.add_argument("--deploy", action="store_true", help="Deploy to a remote machine")
    parser.add_argument("--host", help="Hostname or IP address of the remote machine")
    parser.add_argument("--username", help="Username for authentication")
    parser.add_argument("--password", help="Password for authentication")
    parser.add_argument("--package", help="Path to the deployment package")
    
    args = parser.parse_args()
    
    # Process arguments
    if args.create_package:
        create_deployment_package(args.output_dir)
    elif args.deploy:
        if not args.host:
            logger.error("Host is required for deployment")
            parser.print_help()
            return
        
        result = deploy_to_remote(args.host, args.username, args.password, args.package)
        
        if result["success"]:
            print("\nDeployment successful!")
            print(f"Host: {result['host']}")
            print(f"API Key: {result['api_key']}")
            print(f"Port: {result['port']}")
            print("\nUse these details to connect to the remote API server.")
        else:
            print("\nDeployment failed!")
            print(f"Host: {result['host']}")
            print(f"Error: {result['error']}")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
