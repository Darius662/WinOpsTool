"""Tree widgets for disks and volumes."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class DisksTree(QTreeWidget):
    """Tree widget for displaying physical disks."""
    
    def __init__(self, parent=None):
        """Initialize disks tree.
        
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
            "Model",
            "Interface",
            "Size (GB)",
            "Partitions",
            "Status",
            "Serial",
            "Firmware"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 150)  # Name
        self.setColumnWidth(1, 200)  # Model
        self.setColumnWidth(2, 100)  # Interface
        self.setColumnWidth(3, 100)  # Size
        self.setColumnWidth(4, 80)   # Partitions
        self.setColumnWidth(5, 100)  # Status
        self.setColumnWidth(6, 150)  # Serial
        self.setColumnWidth(7, 100)  # Firmware
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_disk(self, name, model, interface, size, partitions,
                status, serial, firmware):
        """Add a disk to the tree.
        
        Args:
            name: Disk name
            model: Model name
            interface: Interface type
            size: Size in bytes
            partitions: Number of partitions
            status: Status string
            serial: Serial number
            firmware: Firmware version
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Convert size to GB
        size_gb = int(int(size) / (1024 * 1024 * 1024))
        
        item = QTreeWidgetItem([
            name,
            model,
            interface,
            str(size_gb),
            str(partitions),
            status,
            serial,
            firmware
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(3, Qt.AlignmentFlag.AlignRight)  # Size
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight)  # Partitions
        
        self.addTopLevelItem(item)
        return item
        
    def clear_disks(self):
        """Clear all disks from the tree."""
        self.clear()
        
    def find_disk(self, device_id):
        """Find a disk by device ID.
        
        Args:
            device_id: Disk device ID to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if device_id in item.text(0):  # Name contains device ID
                return item
        return None


class VolumesTree(QTreeWidget):
    """Tree widget for displaying volumes (drives)."""
    
    def __init__(self, parent=None):
        """Initialize volumes tree.
        
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
            "Drive",
            "Label",
            "Type",
            "Filesystem",
            "Total (GB)",
            "Used (GB)",
            "Free (GB)",
            "Used %"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 80)   # Drive
        self.setColumnWidth(1, 150)  # Label
        self.setColumnWidth(2, 100)  # Type
        self.setColumnWidth(3, 100)  # Filesystem
        self.setColumnWidth(4, 100)  # Total
        self.setColumnWidth(5, 100)  # Used
        self.setColumnWidth(6, 100)  # Free
        self.setColumnWidth(7, 80)   # Used %
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_volume(self, device, label, type, fstype, total, used, free):
        """Add a volume to the tree.
        
        Args:
            device: Device path
            label: Volume label
            type: Drive type
            fstype: Filesystem type
            total: Total size in bytes
            used: Used space in bytes
            free: Free space in bytes
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Convert sizes to GB
        total_gb = round(total / (1024 * 1024 * 1024), 1)
        used_gb = round(used / (1024 * 1024 * 1024), 1)
        free_gb = round(free / (1024 * 1024 * 1024), 1)
        used_percent = round((used / total * 100), 1) if total > 0 else 0
        
        item = QTreeWidgetItem([
            device,
            label,
            type,
            fstype,
            f"{total_gb:.1f}",
            f"{used_gb:.1f}",
            f"{free_gb:.1f}",
            f"{used_percent:.1f}"
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight)  # Total
        item.setTextAlignment(5, Qt.AlignmentFlag.AlignRight)  # Used
        item.setTextAlignment(6, Qt.AlignmentFlag.AlignRight)  # Free
        item.setTextAlignment(7, Qt.AlignmentFlag.AlignRight)  # Used %
        
        self.addTopLevelItem(item)
        return item
        
    def update_volume(self, item, used=None, free=None):
        """Update a volume in the tree.
        
        Args:
            item: QTreeWidgetItem to update
            used: New used space in bytes (optional)
            free: New free space in bytes (optional)
        """
        if used is not None and free is not None:
            total = float(item.text(4)) * 1024 * 1024 * 1024  # Convert GB to bytes
            used_gb = round(used / (1024 * 1024 * 1024), 1)
            free_gb = round(free / (1024 * 1024 * 1024), 1)
            used_percent = round((used / total * 100), 1) if total > 0 else 0
            
            item.setText(5, f"{used_gb:.1f}")
            item.setText(6, f"{free_gb:.1f}")
            item.setText(7, f"{used_percent:.1f}")
            
    def add_virtual_volume(self, device, label="", type="Network Drive", fstype="Unknown", 
                         total=0, used=0, free=0):
        """Add a virtual volume entry from imported configuration.
        
        A virtual volume represents a volume from the imported configuration
        that doesn't exist in the system yet or needs to be modified. It will be 
        highlighted to indicate it's from the imported configuration.
        
        Args:
            device: Device path (drive letter)
            label: Volume label
            type: Drive type
            fstype: Filesystem type
            total: Total size in bytes
            used: Used space in bytes
            free: Free space in bytes
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Convert sizes to GB
        total_gb = round(total / (1024 * 1024 * 1024), 1) if total > 0 else 0
        used_gb = round(used / (1024 * 1024 * 1024), 1) if used > 0 else 0
        free_gb = round(free / (1024 * 1024 * 1024), 1) if free > 0 else 0
        used_percent = round((used / total * 100), 1) if total > 0 else 0
        
        item = QTreeWidgetItem([
            device,
            label,
            f"{type} (Virtual)",
            fstype,
            f"{total_gb:.1f}" if total > 0 else "N/A",
            f"{used_gb:.1f}" if used > 0 else "N/A",
            f"{free_gb:.1f}" if free > 0 else "N/A",
            f"{used_percent:.1f}" if total > 0 else "N/A"
        ])
        
        # Right-align numeric columns
        item.setTextAlignment(4, Qt.AlignmentFlag.AlignRight)  # Total
        item.setTextAlignment(5, Qt.AlignmentFlag.AlignRight)  # Used
        item.setTextAlignment(6, Qt.AlignmentFlag.AlignRight)  # Free
        item.setTextAlignment(7, Qt.AlignmentFlag.AlignRight)  # Used %
        
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
                item.setToolTip(col, "Virtual volume from configuration file (not applied yet)")
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
        
    def clear_volumes(self):
        """Clear all volumes from the tree."""
        self.clear()
        
    def find_volume(self, mountpoint):
        """Find a volume by mountpoint.
        
        Args:
            mountpoint: Volume mountpoint to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(mountpoint, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
