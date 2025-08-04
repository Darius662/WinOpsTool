"""
Test script for the WinOpsTool REST API

This script tests the REST API server and client implementation.
It can be used to verify that remote operations are working correctly.
"""

import os
import sys
import time
import uuid
import logging
import subprocess
import threading
import requests
from pathlib import Path

# Add the parent directory to the path so we can import our modules
sys.path.append(str(Path(__file__).parent.parent))

from src.core.remote.rest_client import RestApiClient

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_rest_api")

# API server process
server_process = None
API_KEY = str(uuid.uuid4())
API_PORT = 8000

def start_api_server():
    """Start the API server in a separate process."""
    global server_process
    
    # Set the API key environment variable
    os.environ["WINOPSTOOL_API_KEY"] = API_KEY
    
    # Start the server
    server_script = str(Path(__file__).parent.parent / "src" / "api_server" / "server.py")
    server_process = subprocess.Popen(
        [sys.executable, server_script],
        env=os.environ,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait for the server to start
    time.sleep(2)
    
    logger.info(f"Started API server with PID {server_process.pid}")
    logger.info(f"API Key: {API_KEY}")

def stop_api_server():
    """Stop the API server."""
    global server_process
    
    if server_process:
        server_process.terminate()
        server_process.wait()
        logger.info("Stopped API server")
        server_process = None

def test_api_connectivity():
    """Test basic API connectivity."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    # Test connection
    logger.info("Testing API connectivity...")
    if client.test_connection():
        logger.info("✅ API connection successful")
        return True
    else:
        logger.error("❌ API connection failed")
        return False

def test_system_info():
    """Test system info endpoint."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    logger.info("Testing system info endpoint...")
    response = client.get_system_info()
    
    if response.get("success", False):
        logger.info("✅ System info endpoint working")
        logger.info(f"Hostname: {response['data']['hostname']}")
        logger.info(f"OS Version: {response['data']['os_version']}")
        return True
    else:
        logger.error("❌ System info endpoint failed")
        logger.error(f"Error: {response.get('message', 'Unknown error')}")
        return False

def test_services():
    """Test services endpoints."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    logger.info("Testing services endpoints...")
    
    # Get all services
    response = client.get_services()
    if response.get("success", False):
        logger.info("✅ Get services endpoint working")
        logger.info(f"Found {len(response['data'])} services")
        
        # Try to get a specific service
        if response['data']:
            service_name = response['data'][0]['name']
            logger.info(f"Testing get service endpoint with service: {service_name}")
            
            service_response = client.get_service(service_name)
            if service_response.get("success", False):
                logger.info("✅ Get service endpoint working")
                return True
            else:
                logger.error("❌ Get service endpoint failed")
                logger.error(f"Error: {service_response.get('message', 'Unknown error')}")
                return False
    else:
        logger.error("❌ Get services endpoint failed")
        logger.error(f"Error: {response.get('message', 'Unknown error')}")
        return False

def test_processes():
    """Test processes endpoints."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    logger.info("Testing processes endpoints...")
    
    # Get all processes
    response = client.get_processes()
    if response.get("success", False):
        logger.info("✅ Get processes endpoint working")
        logger.info(f"Found {len(response['data'])} processes")
        
        # Try to get a specific process
        if response['data']:
            pid = response['data'][0]['pid']
            logger.info(f"Testing get process endpoint with PID: {pid}")
            
            process_response = client.get_process(pid)
            if process_response.get("success", False):
                logger.info("✅ Get process endpoint working")
                return True
            else:
                logger.error("❌ Get process endpoint failed")
                logger.error(f"Error: {process_response.get('message', 'Unknown error')}")
                return False
    else:
        logger.error("❌ Get processes endpoint failed")
        logger.error(f"Error: {response.get('message', 'Unknown error')}")
        return False

def test_environment_variables():
    """Test environment variables endpoints."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    logger.info("Testing environment variables endpoints...")
    
    # Get all environment variables
    response = client.get_environment_variables()
    if response.get("success", False):
        logger.info("✅ Get environment variables endpoint working")
        logger.info(f"Found {len(response['data'])} environment variables")
        
        # Try to set and delete a test environment variable
        test_var_name = f"TEST_VAR_{uuid.uuid4().hex[:8]}"
        test_var_value = "test_value"
        
        logger.info(f"Testing set environment variable endpoint with variable: {test_var_name}")
        set_response = client.set_environment_variable(test_var_name, test_var_value, False)  # User env var
        
        if set_response.get("success", False):
            logger.info("✅ Set environment variable endpoint working")
            
            # Delete the test variable
            logger.info(f"Testing delete environment variable endpoint with variable: {test_var_name}")
            delete_response = client.delete_environment_variable(test_var_name, False)  # User env var
            
            if delete_response.get("success", False):
                logger.info("✅ Delete environment variable endpoint working")
                return True
            else:
                logger.error("❌ Delete environment variable endpoint failed")
                logger.error(f"Error: {delete_response.get('message', 'Unknown error')}")
                return False
        else:
            logger.error("❌ Set environment variable endpoint failed")
            logger.error(f"Error: {set_response.get('message', 'Unknown error')}")
            return False
    else:
        logger.error("❌ Get environment variables endpoint failed")
        logger.error(f"Error: {response.get('message', 'Unknown error')}")
        return False

def test_registry():
    """Test registry endpoints."""
    client = RestApiClient(f"http://localhost:{API_PORT}", API_KEY)
    
    logger.info("Testing registry endpoints...")
    
    # Test key path that should exist on all Windows systems
    hkey = "HKEY_LOCAL_MACHINE"
    key_path = "SOFTWARE\\Microsoft\\Windows NT\\CurrentVersion"
    
    # Get registry values
    response = client._make_request("GET", "/registry", params={
        "hkey": hkey,
        "key_path": key_path
    })
    
    if response.get("success", False):
        logger.info("✅ Get registry values endpoint working")
        logger.info(f"Found {len(response['data'])} registry values")
        
        # Try to create, set, and delete a test registry key/value
        test_key_path = f"SOFTWARE\\WinOpsTool\\Test_{uuid.uuid4().hex[:8]}"
        
        # Create key
        logger.info(f"Testing create registry key endpoint with key: {hkey}\\{test_key_path}")
        create_response = client._make_request("PUT", "/registry/key", data={
            "hkey": hkey,
            "key_path": test_key_path
        })
        
        if create_response.get("success", False):
            logger.info("✅ Create registry key endpoint working")
            
            # Set value
            test_value_name = "TestValue"
            test_value_data = "TestData"
            
            logger.info(f"Testing set registry value endpoint with value: {test_value_name}")
            set_response = client._make_request("POST", "/registry", data={
                "hkey": hkey,
                "key_path": test_key_path,
                "value_name": test_value_name,
                "value_data": test_value_data,
                "value_type": "REG_SZ"
            })
            
            if set_response.get("success", False):
                logger.info("✅ Set registry value endpoint working")
                
                # Delete value
                logger.info(f"Testing delete registry value endpoint with value: {test_value_name}")
                delete_value_response = client._make_request("DELETE", "/registry", params={
                    "hkey": hkey,
                    "key_path": test_key_path,
                    "value_name": test_value_name
                })
                
                if delete_value_response.get("success", False):
                    logger.info("✅ Delete registry value endpoint working")
                    
                    # Delete key
                    logger.info(f"Testing delete registry key endpoint with key: {hkey}\\{test_key_path}")
                    delete_key_response = client._make_request("DELETE", "/registry/key", params={
                        "hkey": hkey,
                        "key_path": test_key_path
                    })
                    
                    if delete_key_response.get("success", False):
                        logger.info("✅ Delete registry key endpoint working")
                        return True
                    else:
                        logger.error("❌ Delete registry key endpoint failed")
                        logger.error(f"Error: {delete_key_response.get('message', 'Unknown error')}")
                else:
                    logger.error("❌ Delete registry value endpoint failed")
                    logger.error(f"Error: {delete_value_response.get('message', 'Unknown error')}")
            else:
                logger.error("❌ Set registry value endpoint failed")
                logger.error(f"Error: {set_response.get('message', 'Unknown error')}")
        else:
            logger.error("❌ Create registry key endpoint failed")
            logger.error(f"Error: {create_response.get('message', 'Unknown error')}")
    else:
        logger.error("❌ Get registry values endpoint failed")
        logger.error(f"Error: {response.get('message', 'Unknown error')}")
    
    return False

def run_tests():
    """Run all tests."""
    tests = [
        test_api_connectivity,
        test_system_info,
        test_services,
        test_processes,
        test_environment_variables,
        test_registry
    ]
    
    results = []
    
    for test in tests:
        try:
            result = test()
            results.append((test.__name__, result))
        except Exception as e:
            logger.error(f"Test {test.__name__} failed with exception: {str(e)}")
            results.append((test.__name__, False))
    
    # Print summary
    logger.info("\n--- Test Summary ---")
    all_passed = True
    
    for name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        if not result:
            all_passed = False
        logger.info(f"{name}: {status}")
    
    if all_passed:
        logger.info("\n🎉 All tests passed!")
    else:
        logger.info("\n❌ Some tests failed")

if __name__ == "__main__":
    try:
        # Start the API server
        start_api_server()
        
        # Run the tests
        run_tests()
    finally:
        # Stop the API server
        stop_api_server()
