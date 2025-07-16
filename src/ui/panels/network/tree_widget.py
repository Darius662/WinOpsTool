"""Tree widgets for network interfaces and connections."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class InterfacesTree(QTreeWidget):
    """Tree widget for displaying network interfaces."""
    
    def __init__(self, parent=None):
        """Initialize interfaces tree.
        
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
            "Name",
            "Type",
            "Manufacturer",
            "MAC Address",
            "IPv4",
            "IPv6",
            "Speed (Mbps)",
            "MTU",
            "Status",
            "Sent (MB)",
            "Received (MB)"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 150)  # Name
        self.setColumnWidth(1, 100)  # Type
        self.setColumnWidth(2, 150)  # Manufacturer
        self.setColumnWidth(3, 120)  # MAC
        self.setColumnWidth(4, 120)  # IPv4
        self.setColumnWidth(5, 150)  # IPv6
        self.setColumnWidth(6, 100)  # Speed
        self.setColumnWidth(7, 80)   # MTU
        self.setColumnWidth(8, 80)   # Status
        self.setColumnWidth(9, 100)  # Sent
        self.setColumnWidth(10, 100) # Received
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_interface(self, name, type, manufacturer, mac, ipv4, ipv6,
                    speed, mtu, up, bytes_sent, bytes_recv):
        """Add a network interface to the tree.
        
        Args:
            name: Interface name
            type: Adapter type
            manufacturer: Manufacturer
            mac: MAC address
            ipv4: IPv4 address
            ipv6: IPv6 address
            speed: Speed in Mbps
            mtu: MTU size
            up: Whether interface is up
            bytes_sent: Bytes sent
            bytes_recv: Bytes received
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Convert bytes to MB
        sent_mb = bytes_sent / (1024 * 1024)
        recv_mb = bytes_recv / (1024 * 1024)
        
        item = QTreeWidgetItem([
            name,
            type,
            manufacturer,
            mac,
            ipv4,
            ipv6,
            str(speed) if speed > 0 else "Unknown",
            str(mtu),
            "Up" if up else "Down",
            f"{sent_mb:.1f}",
            f"{recv_mb:.1f}"
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(6, Qt.AlignmentFlag.AlignRight)  # Speed
        item.setTextAlignment(7, Qt.AlignmentFlag.AlignRight)  # MTU
        item.setTextAlignment(9, Qt.AlignmentFlag.AlignRight)  # Sent
        item.setTextAlignment(10, Qt.AlignmentFlag.AlignRight) # Received
        
        self.addTopLevelItem(item)
        return item
        
    def update_interface(self, item, up=None, bytes_sent=None, bytes_recv=None):
        """Update a network interface in the tree.
        
        Args:
            item: QTreeWidgetItem to update
            up: New up status (optional)
            bytes_sent: New bytes sent (optional)
            bytes_recv: New bytes received (optional)
        """
        if up is not None:
            item.setText(8, "Up" if up else "Down")
        if bytes_sent is not None:
            sent_mb = bytes_sent / (1024 * 1024)
            item.setText(9, f"{sent_mb:.1f}")
        if bytes_recv is not None:
            recv_mb = bytes_recv / (1024 * 1024)
            item.setText(10, f"{recv_mb:.1f}")
            
    def clear_interfaces(self):
        """Clear all interfaces from the tree."""
        self.clear()
        
    def find_interface(self, name):
        """Find an interface by name.
        
        Args:
            name: Interface name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None


class ConnectionsTree(QTreeWidget):
    """Tree widget for displaying network connections."""
    
    def __init__(self, parent=None):
        """Initialize connections tree.
        
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
            "Protocol",
            "Local Address",
            "Remote Address",
            "Status",
            "PID",
            "Process"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 80)   # Protocol
        self.setColumnWidth(1, 200)  # Local Address
        self.setColumnWidth(2, 200)  # Remote Address
        self.setColumnWidth(3, 120)  # Status
        self.setColumnWidth(4, 80)   # PID
        self.setColumnWidth(5, 150)  # Process
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        
    def add_connection(self, protocol, local_address, remote_address,
                     status, pid, process):
        """Add a network connection to the tree.
        
        Args:
            protocol: Protocol (TCP/UDP)
            local_address: Local address:port
            remote_address: Remote address:port
            status: Connection status
            pid: Process ID
            process: Process name
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            protocol,
            local_address,
            remote_address,
            status,
            str(pid),
            process
        ])
        
        # Right-align PID column
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight)
        
        self.addTopLevelItem(item)
        return item
        
    def clear_connections(self):
        """Clear all connections from the tree."""
        self.clear()
