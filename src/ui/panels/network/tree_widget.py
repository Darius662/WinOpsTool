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
        
    def add_virtual_interface(self, name, type="Unknown", manufacturer="", mac="", ipv4="", ipv6="",
                            speed=0, mtu=0, up=False):
        """Add a virtual network interface entry from imported configuration.
        
        A virtual interface represents an interface from the imported configuration
        that doesn't exist in the system yet or needs to be modified. It will be 
        highlighted to indicate it's from the imported configuration.
        
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
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            type,
            manufacturer,
            mac,
            ipv4,
            ipv6,
            str(speed) if speed > 0 else "Unknown",
            str(mtu) if mtu > 0 else "Unknown",
            "Up (Virtual)" if up else "Down (Virtual)",
            "N/A",  # Sent MB
            "N/A"   # Received MB
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(6, Qt.AlignmentFlag.AlignRight)  # Speed
        item.setTextAlignment(7, Qt.AlignmentFlag.AlignRight)  # MTU
        item.setTextAlignment(9, Qt.AlignmentFlag.AlignRight)  # Sent
        item.setTextAlignment(10, Qt.AlignmentFlag.AlignRight) # Received
        
        # Apply highlighting for virtual item
        self.highlight_item(item, is_virtual=True)
        
        self.addTopLevelItem(item)
        return item
    
    def highlight_item(self, item, is_virtual=False):
        """Highlight an item to indicate it's from imported configuration.
        
        Args:
            item: QTreeWidgetItem to highlight
            is_virtual: Whether this is a virtual entry (not in system yet)
        """
        for col in range(self.columnCount()):
            item.setBackground(col, Qt.GlobalColor.cyan)
            item.setForeground(col, Qt.GlobalColor.darkBlue)
            
            if is_virtual:
                item.setToolTip(col, "Virtual interface from configuration file (not applied yet)")
            else:
                item.setToolTip(col, "Imported from configuration file")
    
    def get_all_items(self):
        """Get all items in the tree.
        
        Returns:
            list: List of all QTreeWidgetItems
        """
        items = []
        for i in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(i))
        return items


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
        
    def add_virtual_connection(self, protocol, local_address, remote_address,
                             status="Unknown", pid="N/A", process="Virtual"):
        """Add a virtual network connection entry from imported configuration.
        
        A virtual connection represents a connection from the imported configuration
        that doesn't exist in the system yet. It will be highlighted to indicate
        it's from the imported configuration.
        
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
            pid,
            process
        ])
        
        # Right-align PID column
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight)
        
        # Apply highlighting for virtual item
        self.highlight_item(item, is_virtual=True)
        
        self.addTopLevelItem(item)
        return item
    
    def highlight_item(self, item, is_virtual=False):
        """Highlight an item to indicate it's from imported configuration.
        
        Args:
            item: QTreeWidgetItem to highlight
            is_virtual: Whether this is a virtual entry (not in system yet)
        """
        for col in range(self.columnCount()):
            item.setBackground(col, Qt.GlobalColor.cyan)
            item.setForeground(col, Qt.GlobalColor.darkBlue)
            
            if is_virtual:
                item.setToolTip(col, "Virtual connection from configuration file (not applied yet)")
            else:
                item.setToolTip(col, "Imported from configuration file")
    
    def get_all_items(self):
        """Get all items in the tree.
        
        Returns:
            list: List of all QTreeWidgetItems
        """
        items = []
        for i in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(i))
        return items
        
    def find_connection(self, protocol, local_address, remote_address):
        """Find a connection by protocol and addresses.
        
        Args:
            protocol: Protocol (TCP/UDP)
            local_address: Local address:port
            remote_address: Remote address:port
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if (item.text(0) == protocol and 
                item.text(1) == local_address and 
                item.text(2) == remote_address):
                return item
        return None
        
    def clear_connections(self):
        """Clear all connections from the tree."""
        self.clear()
