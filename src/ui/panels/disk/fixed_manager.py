"""Disk manager module for managing disk operations."""

import os
import re
import subprocess
import psutil
import logging
import platform
import json
from PyQt6.QtCore import QObject, pyqtSignal

class DiskManager(QObject):
    """Manager for disk operations."""
    
    # Signals
    volumes_refreshed = pyqtSignal(list)
    volume_mounted = pyqtSignal(dict)
    volume_unmounted = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        """Initialize the disk manager."""
        super().__init__()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.volumes = []
    
    def refresh_volumes(self):
        """Refresh the list of volumes.
        
        Returns:
            list: List of volume information dictionaries
        """
        try:
            self.logger.debug("Refreshing volumes")
            volumes = []
            
            # Get all disk partitions
            partitions = psutil.disk_partitions(all=True)
            
            for partition in partitions:
                volume = {
                    'device': partition.device,
                    'mountpoint': partition.mountpoint,
                    'fstype': partition.fstype,
                    'opts': partition.opts,
                    'is_network_drive': False,
                    'network_path': None
                }
                
                # Add usage information if available
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    volume['total'] = usage.total
                    volume['used'] = usage.used
                    volume['free'] = usage.free
                    volume['percent'] = usage.percent
                except (PermissionError, FileNotFoundError):
                    volume['total'] = 0
                    volume['used'] = 0
                    volume['free'] = 0
                    volume['percent'] = 0
                
                # Check if this is a network drive
                if partition.fstype == 'NTFS' and (partition.opts and 'remote' in partition.opts.lower()):
                    volume['is_network_drive'] = True
                    
                    # Try to get the network path
                    try:
                        # Use net use to get network path
                        drive_letter = partition.device.rstrip('\\')
                        result = subprocess.run(
                            ['net', 'use', drive_letter],
                            capture_output=True,
                            text=True
                        )
                        
                        # Extract network path from output
                        if result.returncode == 0:
                            match = re.search(r'Remote name\s+\\\\([^\s]+)', result.stdout)
                            if match:
                                volume['network_path'] = f"\\\\{match.group(1)}"
                    except Exception as e:
                        self.logger.error(f"Error getting network path: {str(e)}")
                
                volumes.append(volume)
            
            # Get additional information for each volume
            for volume in volumes:
                try:
                    # Get volume label
                    if platform.system() == 'Windows' and volume['mountpoint']:
                        drive_letter = volume['mountpoint'].rstrip('\\')
                        result = subprocess.run(
                            ['cmd', '/c', f'vol {drive_letter}'],
                            capture_output=True,
                            text=True
                        )
                        
                        # Extract volume label from output
                        if result.returncode == 0:
                            match = re.search(r'Volume in drive [A-Z] is (.*)', result.stdout)
                            if match:
                                volume['label'] = match.group(1).strip()
                            else:
                                volume['label'] = 'No Label'
                        else:
                            volume['label'] = 'Unknown'
                    else:
                        volume['label'] = 'Unknown'
                except Exception as e:
                    self.logger.error(f"Error getting volume label: {str(e)}")
                    volume['label'] = 'Error'
            
            self.volumes = volumes
            self.volumes_refreshed.emit(volumes)
            self.logger.debug("Refreshed volumes")
            return volumes
        except Exception as e:
            error_msg = f"Failed to refresh volumes: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return []

    def map_network_drive(self, network_path, drive_letter, use_windows_creds=True, 
                         username='', password='', reconnect=True):
        """Map a network drive.
        
        Args:
            network_path: UNC path to the network share (e.g., \\\\server\\\\share)
            drive_letter: Drive letter to map to (e.g., Z:)
            use_windows_creds: Whether to use current Windows credentials
            username: Username for custom credentials
            password: Password for custom credentials
            reconnect: Whether to reconnect at sign-in
            
        Returns:
            dict: Result with success flag and error message if applicable
        """
        try:
            # Ensure drive letter format is correct
            if len(drive_letter) == 1:
                drive_letter = f"{drive_letter}:"
            
            # First, delete any existing mapping to ensure clean state
            try:
                # Quietly try to delete any existing mapping
                subprocess.run(
                    ["net", "use", drive_letter, "/delete", "/y"],
                    capture_output=True,
                    text=True
                )
            except Exception:
                # Ignore errors here - the drive might not be mapped
                pass
                
            # Use a simple approach that works reliably
            if use_windows_creds:
                # For Windows credentials, use the simple net use command
                self.logger.debug("Using current Windows credentials")
                cmd = [
                    "net", "use", drive_letter, network_path,
                    "/persistent:" + ("yes" if reconnect else "no")
                ]
                
                process = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True
                )
                
                stdout = process.stdout
                stderr = process.stderr
                
            else:
                # For custom credentials, use a direct approach with win32 API
                self.logger.debug(f"Using win32 API to map drive with custom credentials for user: {username}")
                
                # Import win32 modules
                try:
                    import win32wnet
                    import win32netcon
                    import win32api
                    import pywintypes
                    
                    # Set up the NETRESOURCE structure
                    netresource = win32wnet.NETRESOURCE()
                    netresource.lpLocalName = drive_letter
                    netresource.lpRemoteName = network_path
                    netresource.dwType = win32netcon.RESOURCETYPE_DISK
                    
                    # Try to connect with the provided credentials
                    try:
                        # WNetAddConnection2 handles credentials properly
                        win32wnet.WNetAddConnection2(netresource, password, username, 0 if not reconnect else win32netcon.CONNECT_UPDATE_PROFILE)
                        stdout = f"Successfully mapped {network_path} to {drive_letter} using win32 API"
                        stderr = ""
                        self.logger.info(stdout)
                    except pywintypes.error as e:
                        # Handle specific error codes
                        error_code = e.winerror
                        error_msg = e.strerror
                        
                        # Log detailed error information
                        self.logger.error(f"Win32 API error: {error_code} - {error_msg}")
                        
                        # Special handling for error 1219 (multiple connections)
                        if error_code == 1219:
                            # Get server name from network path (\\server\share)
                            parts = network_path.split('\\')
                            server_name = parts[2] if len(parts) > 2 else "server"
                            
                            self.logger.warning(f"Multiple connection error detected for server: {server_name}")
                            
                            # List existing connections using a separate command
                            try:
                                list_process = subprocess.run(
                                    ["net", "use"],
                                    capture_output=True,
                                    text=True
                                )
                                
                                if list_process.stdout:
                                    self.logger.debug(f"Existing connections:\n{list_process.stdout}")
                                
                                # Create a helpful error message
                                error_msg = (
                                    f"Cannot connect to {network_path} with user '{username}' because you already "
                                    f"have a connection to the same server with different credentials.\n\n"
                                    f"Please disconnect existing connections to {server_name} first using 'net use /delete', "
                                    f"or use the same credentials for all connections to this server."
                                )
                                
                                stdout = ""
                                stderr = error_msg
                                
                            except Exception as list_err:
                                self.logger.error(f"Error listing connections: {str(list_err)}")
                                stderr = f"Multiple connections error: {error_msg}"
                        else:
                            # For other errors, try a fallback approach with the net use command
                            self.logger.debug("Trying fallback with net use command")
                            cmd = [
                                "net", "use", drive_letter, network_path,
                                "/user:" + username, password,
                                "/persistent:" + ("yes" if reconnect else "no")
                            ]
                            
                            process = subprocess.run(
                                cmd,
                                capture_output=True,
                                text=True
                            )
                            
                            stdout = process.stdout
                            stderr = process.stderr
                        
                except ImportError as e:
                    self.logger.error(f"Failed to import win32 modules: {str(e)}")
                    stderr = f"Failed to import win32 modules: {str(e)}"
                    stdout = ""
            
            # Log the command output for debugging
            if stdout:
                self.logger.debug(f"Command output: {stdout}")
            if stderr:
                self.logger.debug(f"Command error: {stderr}")
                
            # Check if the operation was successful
            if stderr and "error" in stderr.lower():
                self.logger.error(f"Failed to map network drive: {stderr}")
                self.logger.error(f"Network path: {network_path}, Drive: {drive_letter}")
                self.logger.error(f"Using Windows creds: {use_windows_creds}, Username: {username}")
                
                # Try to get more information about the error
                if not use_windows_creds:
                    self.logger.error(f"Return code: {process.returncode if 'process' in locals() else 2}")
                    self.logger.debug("Attempting diagnostic command...")
                    self.logger.debug(f"Diagnostic command (password redacted): net use {drive_letter} {network_path} /user:{username} PASSWORD /persistent:{'yes' if reconnect else 'no'}")
                    
                    # Try to ping the server to check connectivity
                    try:
                        server = network_path.split('\\')[2]
                        self.logger.debug(f"Attempting to ping server: {server}")
                        ping_result = subprocess.run(
                            ["ping", "-n", "1", server],
                            capture_output=True,
                            text=True
                        )
                        self.logger.debug(f"Network connectivity test: \n{ping_result.stdout}")
                    except Exception as ping_err:
                        self.logger.error(f"Error pinging server: {str(ping_err)}")
                
                self.error_occurred.emit(f"Failed to map network drive: {stderr}")
                return {
                    'success': False,
                    'error': stderr
                }
            else:
                self.logger.info(f"Mapping network drive {network_path} to {drive_letter}")
                
                # Refresh volumes to include the new mapping
                self.refresh_volumes()
                
                # Emit signal
                self.volume_mounted.emit({
                    'device': drive_letter,
                    'mountpoint': drive_letter + '\\',
                    'network_path': network_path,
                    'is_network_drive': True
                })
                
                return {
                    'success': True
                }
        except Exception as e:
            error_msg = f"Failed to map network drive: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {
                'success': False,
                'error': str(e)
            }

    def disconnect_network_drive(self, drive_letter):
        """Disconnect a network drive.
        
        Args:
            drive_letter: Drive letter to disconnect (e.g., Z:)
            
        Returns:
            dict: Result with success flag and error message if applicable
        """
        try:
            # Ensure drive letter format is correct
            if len(drive_letter) == 1:
                drive_letter = f"{drive_letter}:"
            
            # Use net use to disconnect
            process = subprocess.run(
                ["net", "use", drive_letter, "/delete"],
                capture_output=True,
                text=True
            )
            
            stdout = process.stdout
            stderr = process.stderr
            
            # Log the command output for debugging
            self.logger.debug(f"Command output: {stdout}")
            if stderr:
                self.logger.debug(f"Command error: {stderr}")
                
            # Check if the operation was successful
            if process.returncode != 0:
                self.logger.error(f"Failed to disconnect network drive: {stderr}")
                self.error_occurred.emit(f"Failed to disconnect network drive: {stderr}")
                return {
                    'success': False,
                    'error': stderr
                }
            else:
                self.logger.info(f"Disconnected network drive {drive_letter}")
                
                # Refresh volumes to remove the disconnected mapping
                self.refresh_volumes()
                
                # Emit signal
                self.volume_unmounted.emit(drive_letter)
                
                return {
                    'success': True
                }
        except Exception as e:
            error_msg = f"Failed to disconnect network drive: {str(e)}"
            self.logger.error(error_msg)
            self.error_occurred.emit(error_msg)
            return {
                'success': False,
                'error': str(e)
            }
