#!/usr/bin/env python3
"""
Test script for PowerShell Remoting functionality.
This script tests the basic functionality of the PSRemoteManager class.
"""

import sys
import os
import getpass
from src.core.remote.ps_remote_manager import PSRemoteManager
from src.core.logger import setup_logger

def main():
    """Main test function."""
    logger = setup_logger("PSRemoteTest")
    logger.info("Starting PowerShell Remoting test")
    
    # Create PSRemoteManager instance
    manager = PSRemoteManager()
    
    # Get connection details from user
    print("=== PowerShell Remoting Test ===")
    print("This script will test the PowerShell Remoting functionality.")
    print("Please ensure that WinRM is enabled on the remote PC with:")
    print("  Enable-PSRemoting -Force")
    print()
    
    hostname = input("Enter remote hostname or IP: ")
    username = input("Enter username: ")
    password = getpass.getpass("Enter password: ")
    
    # Test connection
    print("\nTesting connection...")
    connection_name = f"test_{hostname}"
    
    if not manager.test_winrm_availability(hostname):
        print(f"ERROR: WinRM is not available on {hostname}")
        print("Please ensure that:")
        print("1. The hostname is correct")
        print("2. WinRM is enabled on the remote PC")
        print("3. The remote PC is reachable")
        return 1
        
    print(f"WinRM is available on {hostname}")
    
    # Add connection
    print("\nAdding connection...")
    if not manager.add_connection(connection_name, hostname, username, password):
        print(f"ERROR: Failed to add connection to {hostname}")
        return 1
        
    print(f"Successfully connected to {hostname}")
    
    # Test command execution
    print("\nTesting command execution...")
    return_code, stdout, stderr = manager.execute_command("Get-ComputerInfo | Select-Object CsName, CsDomain, OsName, OsVersion | Format-List")
    
    if return_code != 0:
        print(f"ERROR: Command execution failed: {stderr}")
        return 1
        
    print("Command execution successful:")
    print(stdout)
    
    # Test script execution
    print("\nTesting script execution...")
    script = """
    $processes = Get-Process | Sort-Object -Property CPU -Descending | Select-Object -First 5
    $processes | Format-Table Name, Id, CPU -AutoSize
    """
    
    return_code, stdout, stderr = manager.execute_script(script)
    
    if return_code != 0:
        print(f"ERROR: Script execution failed: {stderr}")
        return 1
        
    print("Script execution successful:")
    print(stdout)
    
    # Test file transfer
    print("\nTesting file transfer...")
    
    # Create a test file
    test_file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_file.txt")
    with open(test_file_path, "w") as f:
        f.write("This is a test file for PowerShell Remoting file transfer.")
        
    # Copy file to remote
    remote_path = "C:\\Temp\\test_file.txt"
    print(f"Copying {test_file_path} to {remote_path}...")
    
    if not manager.copy_file_to_remote(test_file_path, remote_path):
        print("ERROR: Failed to copy file to remote PC")
        os.unlink(test_file_path)
        return 1
        
    print("File copied successfully")
    
    # Copy file back from remote
    local_copy_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "test_file_copy.txt")
    print(f"Copying {remote_path} to {local_copy_path}...")
    
    if not manager.copy_file_from_remote(remote_path, local_copy_path):
        print("ERROR: Failed to copy file from remote PC")
        os.unlink(test_file_path)
        return 1
        
    print("File copied back successfully")
    
    # Clean up
    os.unlink(test_file_path)
    os.unlink(local_copy_path)
    
    # Disconnect
    print("\nDisconnecting...")
    manager.disconnect()
    
    print("\nAll tests completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
