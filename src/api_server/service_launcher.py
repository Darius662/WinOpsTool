#!/usr/bin/env python
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
