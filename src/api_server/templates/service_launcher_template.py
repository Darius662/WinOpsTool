import os
import sys
import time
import logging
from pathlib import Path

# Set up logging
log_file = Path(__file__).parent / "api_service_launcher.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_service_launcher")

# Store the API key
api_key = "{api_key}"
api_key_file = Path(__file__).parent / "api_key.txt"
with open(api_key_file, "w") as f:
    f.write(api_key)
logger.info(f"API key stored in {api_key_file}")

# Import Windows service modules
import win32serviceutil
import win32service
import win32event
import servicemanager
import socket

# Import the server module
from server import run_server

class WinOpsToolAPIService(win32serviceutil.ServiceFramework):
    _svc_name_ = "WinOpsToolAPI"
    _svc_display_name_ = "WinOpsTool REST API Service"
    _svc_description_ = "Provides REST API endpoints for remote Windows management operations"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.is_running = False
        socket.setdefaulttimeout(60)

    def SvcStop(self):
        logger.info("Service stop requested")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.is_running = False

    def SvcDoRun(self):
        logger.info("Service starting")
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, '')
        )
        self.is_running = True
        
        # Set the API key as an environment variable
        os.environ["WINOPSTOOL_API_KEY"] = api_key
        
        # Start the server in a separate thread
        import threading
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        logger.info("Server started in background thread")
        
        # Wait for service stop signal
        while self.is_running:
            rc = win32event.WaitForSingleObject(self.hWaitStop, 5000)
            if rc == win32event.WAIT_OBJECT_0:
                break
        
        logger.info("Service stopped")

def print_api_key():
    """Print the API key to the console"""
    print("\n" + "="*50)
    print(f"API KEY: {api_key}")
    print("="*50)
    print("\nStore this API key securely. It is required to authenticate with the API.\n")
    print(f"The API key is also stored in {api_key_file}\n")

if __name__ == '__main__':
    if len(sys.argv) == 1:
        servicemanager.Initialize()
        servicemanager.PrepareToHostSingle(WinOpsToolAPIService)
        servicemanager.StartServiceCtrlDispatcher()
    else:
        if sys.argv[1] == '--install':
            print_api_key()
            win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        elif sys.argv[1] == '--start':
            win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        elif sys.argv[1] == '--stop':
            win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        elif sys.argv[1] == '--status':
            win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        elif sys.argv[1] == '--uninstall':
            win32serviceutil.HandleCommandLine(WinOpsToolAPIService)
        elif sys.argv[1] == '--generate-key':
            print_api_key()
        else:
            print("Usage: service_launcher.py [--install|--start|--stop|--status|--uninstall|--generate-key]")
