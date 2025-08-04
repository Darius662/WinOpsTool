"""
WinOpsTool REST API Integration Test

This script tests the end-to-end functionality of the REST API implementation,
including the server, client, remote managers, and manager factory.
"""

import os
import sys
import time
import uuid
import logging
import subprocess
import threading
from pathlib import Path

# Add the parent directory to the path so we can import our modules
script_dir = Path(__file__).parent
sys.path.append(str(script_dir.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(script_dir / "integration_test.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("integration_test")

# Import the necessary modules
from src.core.remote.integration import RemoteIntegration
from src.core.manager_factory import ManagerFactory, OperationMode
from src.api_server import server as api_server

class IntegrationTest:
    """Integration test for WinOpsTool REST API"""
    
    def __init__(self):
        """Initialize the test"""
        self.api_key = str(uuid.uuid4())
        self.server_process = None
        self.server_port = 8000
        self.remote_integration = None
        self.manager_factory = None
    
    def start_server(self):
        """Start the API server"""
        logger.info("Starting API server...")
        
        # Set the API key in the environment
        os.environ["WINOPSTOOL_API_KEY"] = self.api_key
        
        # Start the server in a separate thread
        def run_server():
            import uvicorn
            uvicorn.run(api_server.app, host="127.0.0.1", port=self.server_port)
        
        self.server_thread = threading.Thread(target=run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        
        # Wait for the server to start
        logger.info("Waiting for server to start...")
        time.sleep(2)
        
        logger.info(f"API server started with key: {self.api_key}")
    
    def setup_remote_integration(self):
        """Setup the remote integration"""
        logger.info("Setting up remote integration...")
        
        self.remote_integration = RemoteIntegration()
        
        # Connect to the "remote" machine (localhost in this case)
        result = self.remote_integration.connect_to_remote(
            name="Test Remote",
            hostname="127.0.0.1",
            api_key=self.api_key,
            port=self.server_port
        )
        
        if not result:
            logger.error("Failed to connect to remote machine")
            return False
        
        logger.info("Connected to remote machine")
        
        # Get the manager factory
        self.manager_factory = self.remote_integration.get_manager_factory()
        
        if not self.manager_factory:
            logger.error("Failed to get manager factory")
            return False
        
        logger.info("Remote integration setup complete")
        return True
    
    def test_system_info(self):
        """Test getting system information"""
        logger.info("Testing system info...")
        
        system_manager = self.manager_factory.get_system_manager()
        
        # Get system info
        system_info = system_manager.get_system_info()
        
        if not system_info:
            logger.error("Failed to get system info")
            return False
        
        logger.info(f"System info: {system_info}")
        return True
    
    def test_services(self):
        """Test service management"""
        logger.info("Testing services...")
        
        service_manager = self.manager_factory.get_service_manager()
        
        # Get all services
        services = service_manager.get_services()
        
        if not services:
            logger.error("Failed to get services")
            return False
        
        logger.info(f"Found {len(services)} services")
        
        # Get a specific service (Windows Update)
        service = service_manager.get_service("wuauserv")
        
        if not service:
            logger.error("Failed to get Windows Update service")
            return False
        
        logger.info(f"Windows Update service: {service}")
        
        # We won't test starting/stopping services as it requires admin rights
        # and could disrupt the system
        
        return True
    
    def test_processes(self):
        """Test process management"""
        logger.info("Testing processes...")
        
        process_manager = self.manager_factory.get_process_manager()
        
        # Get all processes
        processes = process_manager.get_processes()
        
        if not processes:
            logger.error("Failed to get processes")
            return False
        
        logger.info(f"Found {len(processes)} processes")
        
        # Get a specific process (explorer.exe)
        explorer_processes = [p for p in processes if p.get('name', '').lower() == 'explorer.exe']
        
        if not explorer_processes:
            logger.error("Failed to find explorer.exe process")
            return False
        
        explorer = explorer_processes[0]
        logger.info(f"Explorer process: {explorer}")
        
        # We won't test terminating processes as it could disrupt the system
        
        return True
    
    def test_environment_variables(self):
        """Test environment variable management"""
        logger.info("Testing environment variables...")
        
        env_manager = self.manager_factory.get_environment_manager()
        
        # Get all environment variables
        variables = env_manager.get_environment_variables()
        
        if not variables:
            logger.error("Failed to get environment variables")
            return False
        
        logger.info(f"Found {len(variables)} environment variables")
        
        # Create a test variable
        test_var_name = f"WINOPSTOOL_TEST_{uuid.uuid4().hex[:8]}"
        test_var_value = "test_value"
        
        # Set the variable
        result = env_manager.set_environment_variable(test_var_name, test_var_value, False)
        
        if not result:
            logger.error(f"Failed to set environment variable {test_var_name}")
            return False
        
        logger.info(f"Set environment variable {test_var_name}={test_var_value}")
        
        # Get the variable
        variables = env_manager.get_environment_variables()
        test_var = next((v for v in variables if v.get('name') == test_var_name), None)
        
        if not test_var or test_var.get('value') != test_var_value:
            logger.error(f"Failed to verify environment variable {test_var_name}")
            return False
        
        logger.info(f"Verified environment variable {test_var_name}={test_var_value}")
        
        # Delete the variable
        result = env_manager.delete_environment_variable(test_var_name, False)
        
        if not result:
            logger.error(f"Failed to delete environment variable {test_var_name}")
            return False
        
        logger.info(f"Deleted environment variable {test_var_name}")
        
        return True
    
    def test_registry(self):
        """Test registry management"""
        logger.info("Testing registry...")
        
        registry_manager = self.manager_factory.get_registry_manager()
        
        # Create a test key
        test_key_path = f"SOFTWARE\\WinOpsToolTest_{uuid.uuid4().hex[:8]}"
        
        # Create the key
        result = registry_manager.create_key("HKEY_CURRENT_USER", test_key_path)
        
        if not result:
            logger.error(f"Failed to create registry key {test_key_path}")
            return False
        
        logger.info(f"Created registry key HKEY_CURRENT_USER\\{test_key_path}")
        
        # Set a value
        result = registry_manager.set_value(
            "HKEY_CURRENT_USER",
            test_key_path,
            "TestValue",
            "Hello World",
            "REG_SZ"
        )
        
        if not result:
            logger.error(f"Failed to set registry value")
            return False
        
        logger.info(f"Set registry value TestValue='Hello World'")
        
        # Get the value
        value = registry_manager.get_value("HKEY_CURRENT_USER", test_key_path, "TestValue")
        
        if not value or value.get('data') != "Hello World":
            logger.error(f"Failed to verify registry value")
            return False
        
        logger.info(f"Verified registry value TestValue={value}")
        
        # Delete the value
        result = registry_manager.delete_value("HKEY_CURRENT_USER", test_key_path, "TestValue")
        
        if not result:
            logger.error(f"Failed to delete registry value")
            return False
        
        logger.info(f"Deleted registry value TestValue")
        
        # Delete the key
        result = registry_manager.delete_key("HKEY_CURRENT_USER", test_key_path)
        
        if not result:
            logger.error(f"Failed to delete registry key")
            return False
        
        logger.info(f"Deleted registry key HKEY_CURRENT_USER\\{test_key_path}")
        
        return True
    
    def test_mode_switching(self):
        """Test switching between local and remote modes"""
        logger.info("Testing mode switching...")
        
        # Get the current mode
        current_mode = self.manager_factory.get_operation_mode()
        
        if current_mode != OperationMode.REMOTE:
            logger.error(f"Expected operation mode to be REMOTE, got {current_mode}")
            return False
        
        logger.info(f"Current operation mode: {current_mode}")
        
        # Switch to local mode
        self.manager_factory.set_operation_mode(OperationMode.LOCAL)
        
        new_mode = self.manager_factory.get_operation_mode()
        
        if new_mode != OperationMode.LOCAL:
            logger.error(f"Failed to switch to LOCAL mode, got {new_mode}")
            return False
        
        logger.info(f"Switched to operation mode: {new_mode}")
        
        # Get a local manager
        system_manager = self.manager_factory.get_system_manager()
        
        # Get system info using local manager
        system_info = system_manager.get_system_info()
        
        if not system_info:
            logger.error("Failed to get system info using local manager")
            return False
        
        logger.info(f"Local system info: {system_info}")
        
        # Switch back to remote mode
        self.manager_factory.set_operation_mode(OperationMode.REMOTE)
        
        new_mode = self.manager_factory.get_operation_mode()
        
        if new_mode != OperationMode.REMOTE:
            logger.error(f"Failed to switch back to REMOTE mode, got {new_mode}")
            return False
        
        logger.info(f"Switched back to operation mode: {new_mode}")
        
        return True
    
    def cleanup(self):
        """Clean up after tests"""
        logger.info("Cleaning up...")
        
        # Disconnect from remote
        if self.remote_integration:
            self.remote_integration.disconnect_from_remote("Test Remote")
        
        # The server thread is a daemon, so it will be terminated when the script exits
        
        logger.info("Cleanup complete")
    
    def run_tests(self):
        """Run all tests"""
        try:
            logger.info("Starting integration tests...")
            
            # Start the API server
            self.start_server()
            
            # Setup remote integration
            if not self.setup_remote_integration():
                logger.error("Failed to setup remote integration")
                return False
            
            # Run tests
            tests = [
                self.test_system_info,
                self.test_services,
                self.test_processes,
                self.test_environment_variables,
                self.test_registry,
                self.test_mode_switching
            ]
            
            results = []
            
            for test in tests:
                try:
                    result = test()
                    results.append((test.__name__, result))
                except Exception as e:
                    logger.error(f"Test {test.__name__} failed with exception: {str(e)}")
                    results.append((test.__name__, False))
            
            # Print results
            logger.info("\n--- Test Results ---")
            
            all_passed = True
            
            for name, result in results:
                status = "PASSED" if result else "FAILED"
                logger.info(f"{name}: {status}")
                
                if not result:
                    all_passed = False
            
            logger.info(f"\nOverall result: {'PASSED' if all_passed else 'FAILED'}")
            
            return all_passed
        
        finally:
            self.cleanup()

if __name__ == "__main__":
    test = IntegrationTest()
    success = test.run_tests()
    
    sys.exit(0 if success else 1)
