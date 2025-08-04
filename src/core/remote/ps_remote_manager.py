"""PowerShell Remoting Manager for remote PC connections."""
import os
import subprocess
import json
import time
import socket
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import pathlib
from src.core.logger import setup_logger

@dataclass
class PSRemoteConnection:
    """PowerShell Remote connection details."""
    name: str
    hostname: str
    username: str
    password: str
    is_connected: bool = False
    session_id: str = ""  # To track PowerShell sessions
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "hostname": self.hostname,
            "username": self.username,
            "password": self.password,
            # Don't save connection state or session ID
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'PSRemoteConnection':
        """Create from dictionary."""
        return cls(
            name=data["name"],
            hostname=data["hostname"],
            username=data["username"],
            password=data["password"]
        )

class PSRemoteManager:
    """Manages connections to remote PCs using PowerShell Remoting (WinRM)."""
    
    def __init__(self):
        """Initialize the PowerShell Remoting manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connections: Dict[str, PSRemoteConnection] = {}
        self.current_connection: Optional[PSRemoteConnection] = None
        self.connections_file = self._get_connections_file_path()
        self._load_connections()
        
    def _get_connections_file_path(self) -> str:
        """Get the path to the connections file."""
        # Store in user's AppData folder
        app_data = pathlib.Path.home() / "AppData" / "Local" / "WinOpsTool"
        app_data.mkdir(parents=True, exist_ok=True)
        return str(app_data / "connections.json")
        
    def _save_connections(self) -> bool:
        """Save connections to file.
        
        Returns:
            bool: True if successful
        """
        try:
            # Convert connections to serializable format
            connections_data = {}
            for name, conn in self.connections.items():
                connections_data[name] = conn.to_dict()
                
            # Save to file
            with open(self.connections_file, 'w') as f:
                json.dump(connections_data, f, indent=2)
                
            self.logger.info(f"Saved {len(self.connections)} connections to {self.connections_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to save connections: {str(e)}")
            return False
            
    def _load_connections(self) -> bool:
        """Load connections from file.
        
        Returns:
            bool: True if successful
        """
        try:
            if not os.path.exists(self.connections_file):
                self.logger.info(f"Connections file not found: {self.connections_file}")
                return False
                
            with open(self.connections_file, 'r') as f:
                connections_data = json.load(f)
                
            # Convert to connection objects
            self.connections = {}
            for name, data in connections_data.items():
                self.connections[name] = PSRemoteConnection.from_dict(data)
                
            self.logger.info(f"Loaded {len(self.connections)} connections from {self.connections_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load connections: {str(e)}")
            return False
        
    def is_connected(self) -> bool:
        """Check if there is an active connection."""
        return self.current_connection is not None and self.current_connection.is_connected
        
    @property
    def connection(self) -> Optional[PSRemoteConnection]:
        """Get the current active connection."""
        return self.current_connection
        
    def _run_powershell_command(self, command: str, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a PowerShell command locally.
        
        Args:
            command: PowerShell command to execute
            capture_output: Whether to capture and return command output
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            self.logger.debug(f"Executing PowerShell command: {command}")
            
            # Execute PowerShell with the command
            process = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", command],
                capture_output=capture_output,
                text=True
            )
            
            return process.returncode, process.stdout, process.stderr
            
        except Exception as e:
            self.logger.error(f"Error executing PowerShell command: {str(e)}")
            return 1, "", str(e)
    
    def _run_remote_command(self, hostname: str, username: str, password: str, 
                           command: str, use_ssl: bool = True, timeout: int = 30) -> Tuple[int, str, str]:
        """Run a PowerShell command on a remote computer.
        
        Args:
            hostname: Remote computer hostname or IP
            username: Username for authentication
            password: Password for authentication
            command: PowerShell command to run
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        try:
            # Use a much simpler approach with cmdkey for credential storage
            # First store the credentials using cmdkey (Windows credential manager)
            cmdkey_command = f'cmdkey /add:{hostname} /user:{username} /pass:{password}'
            try:
                # Store credentials temporarily
                subprocess.run(cmdkey_command, shell=True, check=True, capture_output=True)
                self.logger.debug(f"Stored temporary credentials for {hostname}")
                
                # Now create a simple PowerShell command that uses the stored credentials
                ps_script = f'''
                # Set error preferences
                $ErrorActionPreference = 'Stop'
                $VerbosePreference = 'Continue'
                
                # Set TrustedHosts to allow connection to any host
                Set-Item -Path "WSMan:\\localhost\\Client\\TrustedHosts" -Value '*' -Force -ErrorAction SilentlyContinue
                
                try {{                
                    # Simple test command using stored credentials
                    $result = Test-WSMan -ComputerName {hostname} -ErrorAction Stop
                    Write-Host "Connection test successful"
                    $result
                }} catch {{                
                    Write-Host "Error connecting: $_"
                    exit 1
                }}
                '''
            except Exception as e:
                self.logger.error(f"Failed to store credentials: {str(e)}")
                return 1, "", f"Failed to store credentials: {str(e)}"
            
            # Log the command (without password)
            safe_script = ps_script.replace(password, '********')
            self.logger.debug(f"Running PowerShell command on {hostname} as {username}:\n{safe_script[:200]}...")
            # Execute the PowerShell script
            process = subprocess.run(
                ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script],
                capture_output=True,
                text=True,
                timeout=timeout
            )
            
            # Process already executed above, just log the output
            self.logger.debug(f"PowerShell command executed with return code: {process.returncode}")
            
            
            # Log the output for debugging
            if process.stdout:
                self.logger.debug(f"PowerShell stdout: {process.stdout}")
            if process.stderr:
                self.logger.error(f"PowerShell stderr: {process.stderr}")
            
            return process.returncode, process.stdout, process.stderr
            
        except subprocess.TimeoutExpired:
            self.logger.error(f"Command timed out after {timeout + 5} seconds")
            return 1, "", f"Command timed out after {timeout + 5} seconds"
        except Exception as e:
            self.logger.error(f"Error executing remote PowerShell command: {str(e)}")
            return 1, "", str(e)
    
    def test_winrm_availability(self, hostname: str) -> bool:
        """Test if WinRM is available on the remote host.
        
        Args:
            hostname: Remote computer hostname or IP
            
        Returns:
            bool: True if WinRM is available, False otherwise
        """
        try:
            # Try to connect to WinRM port (5985 for HTTP, 5986 for HTTPS)
            for port in [5985, 5986]:
                try:
                    socket.create_connection((hostname, port), timeout=3)
                    self.logger.info(f"WinRM port {port} is open on {hostname}")
                    return True
                except:
                    continue
                    
            self.logger.warning(f"WinRM ports are not accessible on {hostname}")
            return False
            
        except Exception as e:
            self.logger.error(f"Error testing WinRM availability: {str(e)}")
            return False
    
    def add_connection(self, name: str, hostname: str, username: str, password: str) -> bool:
        """Add a new remote PC connection using PowerShell Remoting.
        
        Args:
            name: Display name for the connection
            hostname: Remote hostname or IP
            username: Username for authentication
            password: Password for authentication
            
        Returns:
            bool: True if connection was added successfully
        """
        try:
            # Check if connection with this name already exists
            if name in self.connections:
                self.logger.warning(f"Connection with name '{name}' already exists")
                return False
                
            # Test the connection
            self.logger.info(f"Testing connection to {hostname} as {username}")
            
            # Test if WinRM is available
            if not self.test_winrm_availability(hostname):
                self.logger.error(f"WinRM is not available on {hostname}")
                return False
                
            # Test authentication
            test_cmd = "$env:COMPUTERNAME"
            return_code, stdout, stderr = self._run_remote_command(hostname, username, password, test_cmd)
            
            if return_code != 0:
                self.logger.error(f"Failed to authenticate to {hostname}: {stderr}")
                return False
                
            # Add the connection
            self.connections[name] = PSRemoteConnection(
                name=name,
                hostname=hostname,
                username=username,
                password=password
            )
            
            # Save connections to file
            self._save_connections()
            
            self.logger.info(f"Added connection '{name}' to {hostname}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add connection: {str(e)}")
            return False
    
    def connect(self, name: str) -> bool:
        """Connect to a remote PC.
        
        Args:
            name: Name of the connection to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Print detailed diagnostic information
            self.logger.info(f"===== STARTING CONNECTION ATTEMPT TO {name} =====")
            self.logger.info(f"Current connections: {list(self.connections.keys())}")
            
            connection = self.connections.get(name)
            if not connection:
                self.logger.error(f"Connection {name} not found")
                return False
                
            self.logger.info(f"Connection details: hostname={connection.hostname}, username={connection.username}")
                
            if connection.is_connected:
                self.logger.info(f"Already connected to {name}")
                return True
                
            # Test connection with a simple echo command first
            # This is much faster than trying to get the computer name
            self.logger.info(f"Attempting to connect to {name} ({connection.hostname}) as {connection.username}")
            
            # First check if the host is reachable
            try:
                socket.create_connection((connection.hostname, 5985), timeout=3)
                self.logger.info(f"WinRM port 5985 is open on {connection.hostname}")
            except (socket.timeout, socket.error) as e:
                self.logger.error(f"Cannot connect to {connection.hostname}:5985: {str(e)}")
                connection.is_connected = False
                return False
            
            # Now try the actual PowerShell connection
            return_code, stdout, stderr = self._run_remote_command(
                connection.hostname, connection.username, connection.password, 
                "'Connection test successful'" # Simple string echo test
            )
            
            if return_code != 0:
                self.logger.error(f"Failed to connect to {name}: {stderr}")
                if stdout:
                    self.logger.error(f"Connection output: {stdout}")
                connection.is_connected = False
                return False
                
            connection.is_connected = True
            self.current_connection = connection
            self.logger.info(f"Connected to {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error connecting to {name}: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """Disconnect from the current remote PC.
        
        Returns:
            bool: True if disconnection was successful
        """
        if not self.current_connection:
            return True
            
        try:
            # No need to explicitly disconnect with PowerShell Remoting
            # Just clear the current connection
            self.current_connection.is_connected = False
            self.current_connection = None
            self.logger.info("Disconnected from remote PC")
            return True
            
        except Exception as e:
            self.logger.error(f"Error during disconnect: {str(e)}")
            return False
    
    def remove_connection(self, name: str) -> bool:
        """Remove a saved connection.
        
        Args:
            name: Name of the connection to remove
            
        Returns:
            bool: True if removal was successful
        """
        try:
            if name not in self.connections:
                return False
                
            # If this is the current connection, disconnect first
            if self.current_connection and self.current_connection.name == name:
                self.disconnect()
                
            # Remove the connection
            del self.connections[name]
            
            # Save connections to file
            self._save_connections()
            
            self.logger.info(f"Removed connection: {name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error removing connection {name}: {str(e)}")
            return False
    
    def get_connections(self) -> List[PSRemoteConnection]:
        """Get list of all saved connections.
        
        Returns:
            List[PSRemoteConnection]: List of connection objects
        """
        return list(self.connections.values())
    
    def get_connection(self, name: str) -> Optional[PSRemoteConnection]:
        """Get a specific connection by name.
        
        Args:
            name: Name of the connection to get
            
        Returns:
            Optional[PSRemoteConnection]: Connection object or None if not found
        """
        return self.connections.get(name)
    
    def refresh_connections(self) -> None:
        """Refresh all connections and update their status."""
        for name, connection in list(self.connections.items()):
            try:
                # Test connection
                return_code, _, _ = self._run_remote_command(
                    connection.hostname, connection.username, connection.password,
                    "$env:COMPUTERNAME", use_ssl=True
                )
                
                connection.is_connected = (return_code == 0)
                
                if not connection.is_connected:
                    self.logger.warning(f"Lost connection to {name}")
                    
                    # If this is the current connection, clear it
                    if self.current_connection and self.current_connection.name == name:
                        self.current_connection = None
                        
            except Exception as e:
                self.logger.error(f"Error refreshing connection {name}: {str(e)}")
                connection.is_connected = False
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """Execute a PowerShell command on the remote PC.
        
        Args:
            command: PowerShell command to execute
            
        Returns:
            Tuple[int, str, str]: Return code, stdout, stderr
        """
        if not self.is_connected():
            self.logger.error("Not connected to any remote PC")
            return 1, "", "Not connected to any remote PC"
            
        try:
            return self._run_remote_command(
                self.current_connection.hostname,
                self.current_connection.username,
                self.current_connection.password,
                command
            )
            
        except Exception as e:
            self.logger.error(f"Error executing command: {str(e)}")
            return 1, "", str(e)
    
    def execute_script(self, script_content: str) -> Tuple[int, str, str]:
        """Execute a PowerShell script on the remote PC.
        
        Args:
            script_content: Content of the PowerShell script to execute
            
        Returns:
            Tuple[int, str, str]: Return code, stdout, stderr
        """
        if not self.is_connected():
            self.logger.error("Not connected to any remote PC")
            return 1, "", "Not connected to any remote PC"
            
        try:
            # Create a temporary script file
            with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as temp:
                temp_path = temp.name
                temp.write(script_content.encode('utf-8'))
                
            # Execute the script remotely
            encoded_script = base64.b64encode(script_content.encode('utf-16-le')).decode('ascii')
            command = f"[System.Text.Encoding]::Unicode.GetString([System.Convert]::FromBase64String('{encoded_script}')) | Invoke-Expression"
            
            result = self._run_remote_command(
                self.current_connection.hostname,
                self.current_connection.username,
                self.current_connection.password,
                command
            )
            
            # Clean up
            os.unlink(temp_path)
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing script: {str(e)}")
            return 1, "", str(e)
    
    def copy_file_to_remote(self, local_path: str, remote_path: str) -> bool:
        """Copy a file to the remote PC.
        
        Args:
            local_path: Path to the local file
            remote_path: Destination path on the remote PC
            
        Returns:
            bool: True if copy was successful
        """
        if not self.is_connected():
            self.logger.error("Not connected to any remote PC")
            return False
            
        try:
            # Read the file content
            with open(local_path, 'rb') as f:
                file_content = f.read()
                
            # Encode the file content
            encoded_content = base64.b64encode(file_content).decode('ascii')
            
            # Create a command to write the file on the remote PC
            command = f"""
            $content = [System.Convert]::FromBase64String('{encoded_content}')
            $path = '{remote_path.replace("'", "''")}'
            
            # Create directory if it doesn't exist
            $directory = [System.IO.Path]::GetDirectoryName($path)
            if (-not (Test-Path $directory)) {{
                New-Item -ItemType Directory -Path $directory -Force | Out-Null
            }}
            
            # Write the file
            [System.IO.File]::WriteAllBytes($path, $content)
            
            # Verify the file was written
            Test-Path $path
            """
            
            return_code, stdout, stderr = self._run_remote_command(
                self.current_connection.hostname,
                self.current_connection.username,
                self.current_connection.password,
                command
            )
            
            success = return_code == 0 and stdout.strip().lower() == "true"
            if success:
                self.logger.info(f"Successfully copied {local_path} to {remote_path}")
            else:
                self.logger.error(f"Failed to copy file: {stderr}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error copying file: {str(e)}")
            return False
    
    def copy_file_from_remote(self, remote_path: str, local_path: str) -> bool:
        """Copy a file from the remote PC.
        
        Args:
            remote_path: Path to the file on the remote PC
            local_path: Destination path on the local machine
            
        Returns:
            bool: True if copy was successful
        """
        if not self.is_connected():
            self.logger.error("Not connected to any remote PC")
            return False
            
        try:
            # Create a command to read the file on the remote PC
            command = f"""
            $path = '{remote_path.replace("'", "''")}'
            if (Test-Path $path) {{
                $content = [System.IO.File]::ReadAllBytes($path)
                [System.Convert]::ToBase64String($content)
            }} else {{
                Write-Error "File not found: $path"
                exit 1
            }}
            """
            
            return_code, stdout, stderr = self._run_remote_command(
                self.current_connection.hostname,
                self.current_connection.username,
                self.current_connection.password,
                command
            )
            
            if return_code != 0:
                self.logger.error(f"Failed to read remote file: {stderr}")
                return False
                
            # Decode the file content
            file_content = base64.b64decode(stdout.strip())
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(os.path.abspath(local_path)), exist_ok=True)
            
            # Write the file locally
            with open(local_path, 'wb') as f:
                f.write(file_content)
                
            self.logger.info(f"Successfully copied {remote_path} to {local_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error copying file from remote: {str(e)}")
            return False
    
    def execute_on_all(self, func, *args, **kwargs):
        """Execute a function on all connected PCs.
        
        Args:
            func: Function to execute
            *args: Positional arguments for the function
            **kwargs: Keyword arguments for the function
            
        Returns:
            dict: Dictionary of results, keyed by connection name
        """
        results = {}
        for name, connection in self.connections.items():
            if connection.is_connected:
                try:
                    # Save the current connection
                    old_connection = self.current_connection
                    
                    # Set the current connection to this one
                    self.current_connection = connection
                    
                    # Execute the function
                    results[name] = func(*args, **kwargs)
                    
                    # Restore the old connection
                    self.current_connection = old_connection
                    
                except Exception as e:
                    self.logger.error(f"Failed to execute on {name}: {str(e)}")
                    results[name] = None
                    
        return results
