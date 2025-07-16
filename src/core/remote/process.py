"""Remote process management."""
import win32process
import win32security
import win32api
import win32con
from src.core.logger import setup_logger

class ProcessManager:
    """Handles remote process management."""
    
    def __init__(self):
        """Initialize process manager."""
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
        
    def list_processes(self):
        """List running processes on remote system.
        
        Returns:
            list: List of process dictionaries with name, id, etc.
            
        Raises:
            ConnectionError: If not connected
            OSError: If listing fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        try:
            processes = []
            # Use WMI to get process list
            for process in self.connection.wmi.Win32_Process():
                processes.append({
                    'id': process.ProcessId,
                    'name': process.Name,
                    'path': process.ExecutablePath or '',
                    'command_line': process.CommandLine or '',
                    'username': self._get_process_username(process),
                    'memory': process.WorkingSetSize,
                    'cpu_time': process.UserModeTime + process.KernelModeTime
                })
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to list processes: {str(e)}")
            raise OSError(f"Failed to list processes: {str(e)}")
            
    def start_process(self, command, args=None, working_dir=None,
                   run_as=None, password=None):
        """Start a new process on remote system.
        
        Args:
            command: Process executable path
            args: Optional command line arguments
            working_dir: Optional working directory
            run_as: Optional username to run as
            password: Optional password for run_as user
            
        Returns:
            int: Process ID
            
        Raises:
            ConnectionError: If not connected
            OSError: If process start fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        try:
            # Build command line
            cmd = f'"{command}"'
            if args:
                cmd += f' {args}'
                
            # Get logon flags
            flags = win32con.NORMAL_PRIORITY_CLASS
            
            # Create process with different credentials if specified
            if run_as and password:
                token = win32security.LogonUser(
                    run_as,
                    self.connection.get_host(),
                    password,
                    win32con.LOGON32_LOGON_INTERACTIVE,
                    win32con.LOGON32_PROVIDER_DEFAULT
                )
                process_info = win32process.CreateProcessAsUser(
                    token,
                    command,
                    cmd,
                    None,
                    None,
                    False,
                    flags,
                    None,
                    working_dir,
                    win32process.STARTUPINFO()
                )
            else:
                process_info = win32process.CreateProcess(
                    command,
                    cmd,
                    None,
                    None,
                    False,
                    flags,
                    None,
                    working_dir,
                    win32process.STARTUPINFO()
                )
                
            pid = process_info[2]
            self.logger.info(f"Started process {command} (PID: {pid})")
            return pid
            
        except Exception as e:
            self.logger.error(f"Failed to start process: {str(e)}")
            raise OSError(f"Failed to start process: {str(e)}")
            
    def terminate_process(self, pid):
        """Terminate a process on remote system.
        
        Args:
            pid: Process ID to terminate
            
        Raises:
            ConnectionError: If not connected
            OSError: If termination fails
        """
        if not self.connection or not self.connection.is_connected():
            raise ConnectionError("Not connected to remote system")
            
        try:
            handle = win32api.OpenProcess(
                win32con.PROCESS_TERMINATE,
                False,
                pid
            )
            win32process.TerminateProcess(handle, 0)
            win32api.CloseHandle(handle)
            
            self.logger.info(f"Terminated process {pid}")
            
        except Exception as e:
            self.logger.error(f"Failed to terminate process: {str(e)}")
            raise OSError(f"Failed to terminate process: {str(e)}")
            
    def _get_process_username(self, process):
        """Get username of process owner."""
        try:
            owner = process.GetOwner()
            if owner[0]:  # Domain
                return f"{owner[0]}\\{owner[1]}"
            return owner[1]  # Username only
        except:
            return "N/A"
