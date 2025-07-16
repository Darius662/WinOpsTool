"""Remote file transfer operations."""
import os
import shutil
from src.core.logger import setup_logger

class FileTransfer:
    """Handles file transfer operations."""
    
    def __init__(self):
        """Initialize file transfer handler."""
        self.logger = setup_logger(self.__class__.__name__)
        self.connection = None
        
    def set_connection(self, connection):
        """Set remote connection.
        
        Args:
            connection: RemoteConnection instance
        """
        self.connection = connection
        
    def clear_connection(self):
        """Clear remote connection."""
        self.connection = None
        
    def copy_to_remote(self, local_path, remote_path, callback=None):
        """Copy file or directory to remote system.
        
        Args:
            local_path: Path to local file/directory
            remote_path: Destination path on remote system
            callback: Optional progress callback function
            
        Raises:
            FileNotFoundError: If local path doesn't exist
            PermissionError: If access denied
            OSError: If copy fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        if not os.path.exists(local_path):
            raise FileNotFoundError(f"Local path not found: {local_path}")
            
        try:
            if os.path.isfile(local_path):
                self._copy_file_to_remote(local_path, remote_path, callback)
            else:
                self._copy_dir_to_remote(local_path, remote_path, callback)
                
        except Exception as e:
            self.logger.error(f"Copy to remote failed: {str(e)}")
            raise
            
    def copy_from_remote(self, remote_path, local_path, callback=None):
        """Copy file or directory from remote system.
        
        Args:
            remote_path: Path on remote system
            local_path: Destination path on local system
            callback: Optional progress callback function
            
        Raises:
            FileNotFoundError: If remote path doesn't exist
            PermissionError: If access denied
            OSError: If copy fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        try:
            if os.path.isfile(remote_path):
                self._copy_file_from_remote(remote_path, local_path, callback)
            else:
                self._copy_dir_from_remote(remote_path, local_path, callback)
                
        except Exception as e:
            self.logger.error(f"Copy from remote failed: {str(e)}")
            raise
            
    def _copy_file_to_remote(self, local_file, remote_file, callback=None):
        """Copy single file to remote system."""
        try:
            # Create remote directory if needed
            remote_dir = os.path.dirname(remote_file)
            if not os.path.exists(remote_dir):
                os.makedirs(remote_dir)
                
            shutil.copy2(local_file, remote_file)
            
            if callback:
                callback(1, 1)  # 100% complete
                
            self.logger.info(
                f"Copied {local_file} to {remote_file}"
            )
            
        except Exception as e:
            self.logger.error(f"File copy to remote failed: {str(e)}")
            raise
            
    def _copy_dir_to_remote(self, local_dir, remote_dir, callback=None):
        """Copy directory to remote system."""
        try:
            # Create remote directory
            if not os.path.exists(remote_dir):
                os.makedirs(remote_dir)
                
            # Count total files for progress
            total_files = sum(len(files) for _, _, files in os.walk(local_dir))
            copied_files = 0
            
            # Copy directory contents
            for root, dirs, files in os.walk(local_dir):
                # Create remote subdirectories
                for dir_name in dirs:
                    local_path = os.path.join(root, dir_name)
                    remote_path = os.path.join(
                        remote_dir,
                        os.path.relpath(local_path, local_dir)
                    )
                    if not os.path.exists(remote_path):
                        os.makedirs(remote_path)
                        
                # Copy files
                for file_name in files:
                    local_path = os.path.join(root, file_name)
                    remote_path = os.path.join(
                        remote_dir,
                        os.path.relpath(local_path, local_dir)
                    )
                    shutil.copy2(local_path, remote_path)
                    
                    copied_files += 1
                    if callback:
                        callback(copied_files, total_files)
                        
            self.logger.info(
                f"Copied directory {local_dir} to {remote_dir}"
            )
            
        except Exception as e:
            self.logger.error(f"Directory copy to remote failed: {str(e)}")
            raise
            
    def _copy_file_from_remote(self, remote_file, local_file, callback=None):
        """Copy single file from remote system."""
        try:
            # Create local directory if needed
            local_dir = os.path.dirname(local_file)
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
                
            shutil.copy2(remote_file, local_file)
            
            if callback:
                callback(1, 1)  # 100% complete
                
            self.logger.info(
                f"Copied {remote_file} to {local_file}"
            )
            
        except Exception as e:
            self.logger.error(f"File copy from remote failed: {str(e)}")
            raise
            
    def _copy_dir_from_remote(self, remote_dir, local_dir, callback=None):
        """Copy directory from remote system."""
        try:
            # Create local directory
            if not os.path.exists(local_dir):
                os.makedirs(local_dir)
                
            # Count total files for progress
            total_files = sum(len(files) for _, _, files in os.walk(remote_dir))
            copied_files = 0
            
            # Copy directory contents
            for root, dirs, files in os.walk(remote_dir):
                # Create local subdirectories
                for dir_name in dirs:
                    remote_path = os.path.join(root, dir_name)
                    local_path = os.path.join(
                        local_dir,
                        os.path.relpath(remote_path, remote_dir)
                    )
                    if not os.path.exists(local_path):
                        os.makedirs(local_path)
                        
                # Copy files
                for file_name in files:
                    remote_path = os.path.join(root, file_name)
                    local_path = os.path.join(
                        local_dir,
                        os.path.relpath(remote_path, remote_dir)
                    )
                    shutil.copy2(remote_path, local_path)
                    
                    copied_files += 1
                    if callback:
                        callback(copied_files, total_files)
                        
            self.logger.info(
                f"Copied directory {remote_dir} to {local_dir}"
            )
            
        except Exception as e:
            self.logger.error(f"Directory copy from remote failed: {str(e)}")
            raise
