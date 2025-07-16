"""Tree widget for Windows Processes."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class ProcessesTree(QTreeWidget):
    """Tree widget for displaying Windows Processes."""
    
    def __init__(self, parent=None):
        """Initialize processes tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        # Set up columns
        self.setHeaderLabels([
            "PID",
            "Name",
            "CPU %",
            "Memory %",
            "Status",
            "Threads",
            "Username",
            "Priority"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 80)   # PID
        self.setColumnWidth(1, 200)  # Name
        self.setColumnWidth(2, 80)   # CPU %
        self.setColumnWidth(3, 80)   # Memory %
        self.setColumnWidth(4, 80)   # Status
        self.setColumnWidth(5, 80)   # Threads
        self.setColumnWidth(6, 200)  # Username
        self.setColumnWidth(7, 100)  # Priority
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(2, Qt.SortOrder.DescendingOrder)  # Sort by CPU % by default
        
    def add_process(self, pid, name, cpu_percent, memory_percent,
                  status, threads, username, priority):
        """Add a process to the tree.
        
        Args:
            pid: Process ID
            name: Process name
            cpu_percent: CPU usage percentage
            memory_percent: Memory usage percentage
            status: Process status
            threads: Thread count
            username: User name
            priority: Priority class
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            str(pid),
            name,
            f"{cpu_percent:.1f}",
            f"{memory_percent:.1f}",
            status,
            str(threads),
            username,
            priority
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(0, Qt.AlignmentFlag.AlignRight)  # PID
        item.setTextAlignment(2, Qt.AlignmentFlag.AlignRight)  # CPU %
        item.setTextAlignment(3, Qt.AlignmentFlag.AlignRight)  # Memory %
        item.setTextAlignment(5, Qt.AlignmentFlag.AlignRight)  # Threads
        
        self.addTopLevelItem(item)
        return item
        
    def update_process(self, item, cpu_percent=None, memory_percent=None,
                     status=None, threads=None, priority=None):
        """Update a process in the tree.
        
        Args:
            item: QTreeWidgetItem to update
            cpu_percent: New CPU usage percentage (optional)
            memory_percent: New memory usage percentage (optional)
            status: New status (optional)
            threads: New thread count (optional)
            priority: New priority class (optional)
        """
        if cpu_percent is not None:
            item.setText(2, f"{cpu_percent:.1f}")
        if memory_percent is not None:
            item.setText(3, f"{memory_percent:.1f}")
        if status is not None:
            item.setText(4, status)
        if threads is not None:
            item.setText(5, str(threads))
        if priority is not None:
            item.setText(7, priority)
            
    def get_process(self, item):
        """Get process details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Process properties
        """
        return {
            'pid': int(item.text(0)),
            'name': item.text(1),
            'cpu_percent': float(item.text(2)),
            'memory_percent': float(item.text(3)),
            'status': item.text(4),
            'threads': int(item.text(5)),
            'username': item.text(6),
            'priority': item.text(7)
        }
        
    def clear_processes(self):
        """Clear all processes from the tree."""
        self.clear()
        
    def find_process(self, pid):
        """Find a process by PID.
        
        Args:
            pid: Process ID to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(str(pid), Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
