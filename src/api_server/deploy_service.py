"""
WinOpsTool REST API Service Deployment Script

This script installs and configures the WinOpsTool REST API server as a Windows service.
It handles installation, uninstallation, starting, stopping, and status checking of the service.
"""

import os
import sys
import uuid
import argparse
import subprocess
import win32service
import win32serviceutil
import win32event
import win32api
import servicemanager
import socket
import logging
from pathlib import Path

# Add the parent directory to the path so we can import our modules
script_dir = Path(__file__).parent
sys.path.append(str(script_dir.parent.parent))

# Import the server module
import src.api_server.server as server

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(script_dir / "service_deploy.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("deploy_service")

# Service name and display name
SERVICE_NAME = "WinOpsToolAPI"
SERVICE_DISPLAY_NAME = "WinOpsTool REST API Service"
SERVICE_DESCRIPTION = "REST API server for WinOpsTool remote management"

class WinOpsToolAPIService(win32serviceutil.ServiceFramework):
    """Windows Service for WinOpsTool REST API Server"""
    
    _svc_name_ = SERVICE_NAME
    _svc_display_name_ = SERVICE_DISPLAY_NAME
    _svc_description_ = SERVICE_DESCRIPTION
    
    def __init__(self, args):
        """Initialize the service"""
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.is_running = False
        
        # Setup logging for the service
        self.log_file = script_dir / "api_service.log"
        self.logger = logging.getLogger("api_service")
        self.logger.setLevel(logging.INFO)
        handler = logging.FileHandler(self.log_file)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)
    
    def SvcStop(self):
        """Stop the service"""
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False
        self.logger.info("Service stopping...")
    
    def SvcDoRun(self):
        """Run the service"""
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.is_running = True
        self.main()
    
    def main(self):
        """Main service function"""
        self.logger.info("Service starting...")
        
        # Read API key from environment or config file
        api_key_file = script_dir / "api_key.txt"
        if os.environ.get("WINOPSTOOL_API_KEY"):
            api_key = os.environ.get("WINOPSTOOL_API_KEY")
        elif api_key_file.exists():
            with open(api_key_file, "r") as f:
                api_key = f.read().strip()
        else:
            # Generate a new API key
            api_key = str(uuid.uuid4())
            with open(api_key_file, "w") as f:
                f.write(api_key)
        
        # Set the API key in the environment
        os.environ["WINOPSTOOL_API_KEY"] = api_key
        self.logger.info(f"Using API key: {api_key}")
        
        # Start the server
        import uvicorn
        
        # Configure the server
        config = uvicorn.Config(
            app=server.app,
            host="0.0.0.0",
            port=8000,
            log_level="info"
        )
        
        # Create and start the server
        self.server = uvicorn.Server(config)
        
        # Run the server in a way that can be interrupted
        self.logger.info("Starting API server...")
        
        # We need to modify the server's main loop to check for stop events
        original_run = self.server.run
        
        def patched_run():
            self.server.config.setup_event_loop()
            loop = self.server.loop
            
            # Add the stop check to the event loop
            def check_stop():
                if win32event.WaitForSingleObject(self.hWaitStop, 0) == win32event.WAIT_OBJECT_0:
                    self.logger.info("Stop event received, shutting down server...")
                    asyncio.ensure_future(self.server.shutdown(), loop=loop)
                else:
                    loop.call_later(1.0, check_stop)
            
            loop.call_soon(check_stop)
            
            # Run the server
            self.server.run_app()
        
        self.server.run = patched_run
        
        try:
            self.server.run()
        except Exception as e:
            self.logger.error(f"Server error: {str(e)}")
        
        self.logger.info("Service stopped")

def install_service():
    """Install the service"""
    try:
        # Get the path to the Python executable and this script
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        # Install the service
        subprocess.run([
            python_exe, script_path, "install"
        ], check=True)
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' installed successfully")
        
        # Generate API key if it doesn't exist
        api_key_file = script_dir / "api_key.txt"
        if not api_key_file.exists():
            api_key = str(uuid.uuid4())
            with open(api_key_file, "w") as f:
                f.write(api_key)
            logger.info(f"Generated API key: {api_key}")
            logger.info(f"API key saved to: {api_key_file}")
        
        # Start the service
        subprocess.run([
            "net", "start", SERVICE_NAME
        ], check=True)
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' started")
        
        # Display the API key
        if api_key_file.exists():
            with open(api_key_file, "r") as f:
                api_key = f.read().strip()
            logger.info(f"API key: {api_key}")
            logger.info("Use this API key to connect to the REST API server")
        
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to install service: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error installing service: {str(e)}")
        return False

def uninstall_service():
    """Uninstall the service"""
    try:
        # Stop the service if it's running
        try:
            subprocess.run([
                "net", "stop", SERVICE_NAME
            ], check=True)
            logger.info(f"Service '{SERVICE_DISPLAY_NAME}' stopped")
        except subprocess.CalledProcessError:
            # Service might not be running
            pass
        
        # Get the path to the Python executable and this script
        python_exe = sys.executable
        script_path = os.path.abspath(__file__)
        
        # Uninstall the service
        subprocess.run([
            python_exe, script_path, "remove"
        ], check=True)
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' uninstalled successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to uninstall service: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error uninstalling service: {str(e)}")
        return False

def start_service():
    """Start the service"""
    try:
        subprocess.run([
            "net", "start", SERVICE_NAME
        ], check=True)
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' started")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to start service: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error starting service: {str(e)}")
        return False

def stop_service():
    """Stop the service"""
    try:
        subprocess.run([
            "net", "stop", SERVICE_NAME
        ], check=True)
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' stopped")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to stop service: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Error stopping service: {str(e)}")
        return False

def check_service_status():
    """Check the status of the service"""
    try:
        # Check if the service is installed
        status = win32serviceutil.QueryServiceStatus(SERVICE_NAME)
        
        # Map status code to string
        status_map = {
            win32service.SERVICE_STOPPED: "Stopped",
            win32service.SERVICE_START_PENDING: "Starting",
            win32service.SERVICE_STOP_PENDING: "Stopping",
            win32service.SERVICE_RUNNING: "Running",
            win32service.SERVICE_CONTINUE_PENDING: "Continuing",
            win32service.SERVICE_PAUSE_PENDING: "Pausing",
            win32service.SERVICE_PAUSED: "Paused"
        }
        
        status_str = status_map.get(status[1], f"Unknown ({status[1]})")
        
        logger.info(f"Service '{SERVICE_DISPLAY_NAME}' status: {status_str}")
        
        # Display the API key if the service is installed
        api_key_file = script_dir / "api_key.txt"
        if api_key_file.exists():
            with open(api_key_file, "r") as f:
                api_key = f.read().strip()
            logger.info(f"API key: {api_key}")
        
        return True
    except Exception as e:
        logger.error(f"Service '{SERVICE_DISPLAY_NAME}' is not installed")
        return False

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WinOpsTool REST API Service Deployment")
    
    # If run with no arguments, show help
    if len(sys.argv) == 1:
        parser.print_help()
        return
    
    # Check if running as a service
    if len(sys.argv) > 1 and sys.argv[1] in ["install", "remove", "update", "start", "stop", "restart", "debug"]:
        win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        return
    
    # Add arguments
    parser.add_argument("--install", action="store_true", help="Install the service")
    parser.add_argument("--uninstall", action="store_true", help="Uninstall the service")
    parser.add_argument("--start", action="store_true", help="Start the service")
    parser.add_argument("--stop", action="store_true", help="Stop the service")
    parser.add_argument("--status", action="store_true", help="Check the status of the service")
    parser.add_argument("--generate-key", action="store_true", help="Generate a new API key")
    
    args = parser.parse_args()
    
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
        # Generate a new API key
        api_key = str(uuid.uuid4())
        api_key_file = script_dir / "api_key.txt"
        
        with open(api_key_file, "w") as f:
            f.write(api_key)
        
        logger.info(f"Generated new API key: {api_key}")
        logger.info(f"API key saved to: {api_key_file}")
        
        # Restart the service if it's running
        try:
            status = win32serviceutil.QueryServiceStatus(SERVICE_NAME)
            if status[1] == win32service.SERVICE_RUNNING:
                logger.info("Restarting service to apply new API key...")
                stop_service()
                start_service()
        except:
            pass

if __name__ == "__main__":
    main()
