"""Windows Process management."""
import psutil
import win32process
import win32con
import win32api
import pywintypes
from src.core.logger import setup_logger

class ProcessManager:
    """Manager for Windows Processes."""
    
    def __init__(self):
        """Initialize process manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_processes(self):
        """Get list of all processes.
        
        Returns:
            list: List of process dictionaries with properties
        """
        try:
            processes = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
                try:
                    # Get basic info
                    info = proc.info
                    pid = info['pid']
                    
                    # Get additional details
                    process = psutil.Process(pid)
                    username = process.username()
                    status = process.status()
                    threads = process.num_threads()
                    priority = self._get_priority_class(pid)
                    
                    processes.append({
                        'pid': pid,
                        'name': info['name'],
                        'cpu_percent': info['cpu_percent'] or 0.0,
                        'memory_percent': info['memory_percent'] or 0.0,
                        'status': status,
                        'threads': threads,
                        'username': username,
                        'priority': priority
                    })
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
            return processes
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate processes: {str(e)}")
            return []
            
    def _get_priority_class(self, pid):
        """Get process priority class.
        
        Args:
            pid: Process ID
            
        Returns:
            str: Priority class name
        """
        try:
            handle = win32api.OpenProcess(win32con.PROCESS_QUERY_INFORMATION, False, pid)
            try:
                priority = win32process.GetPriorityClass(handle)
                return {
                    win32process.IDLE_PRIORITY_CLASS: "Low",
                    win32process.BELOW_NORMAL_PRIORITY_CLASS: "Below Normal",
                    win32process.NORMAL_PRIORITY_CLASS: "Normal",
                    win32process.ABOVE_NORMAL_PRIORITY_CLASS: "Above Normal",
                    win32process.HIGH_PRIORITY_CLASS: "High",
                    win32process.REALTIME_PRIORITY_CLASS: "Realtime"
                }.get(priority, "Unknown")
            finally:
                win32api.CloseHandle(handle)
        except pywintypes.error:
            return "Unknown"
            
    def terminate_process(self, pid):
        """Terminate a process.
        
        Args:
            pid: Process ID
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            process = psutil.Process(pid)
            process.terminate()
            self.logger.info(f"Terminated process {pid}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to terminate process {pid}: {str(e)}")
            return False
            
    def set_priority(self, pid, priority):
        """Set process priority.
        
        Args:
            pid: Process ID
            priority: Priority class name
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Map priority name to win32process constant
            priority_map = {
                "Low": win32process.IDLE_PRIORITY_CLASS,
                "Below Normal": win32process.BELOW_NORMAL_PRIORITY_CLASS,
                "Normal": win32process.NORMAL_PRIORITY_CLASS,
                "Above Normal": win32process.ABOVE_NORMAL_PRIORITY_CLASS,
                "High": win32process.HIGH_PRIORITY_CLASS,
                "Realtime": win32process.REALTIME_PRIORITY_CLASS
            }
            
            if priority not in priority_map:
                raise ValueError(f"Invalid priority: {priority}")
                
            handle = win32api.OpenProcess(win32con.PROCESS_SET_INFORMATION, False, pid)
            try:
                win32process.SetPriorityClass(handle, priority_map[priority])
                self.logger.info(f"Set priority for process {pid} to {priority}")
                return True
            finally:
                win32api.CloseHandle(handle)
                
        except Exception as e:
            self.logger.error(f"Failed to set priority for process {pid}: {str(e)}")
            return False
