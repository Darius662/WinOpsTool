"""Tree widget for startup entries."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class StartupTree(QTreeWidget):
    """Tree widget for displaying startup entries."""
    
    def __init__(self, parent=None):
        """Initialize startup tree.
        
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
            "Command",
            "Location",
            "Type",
            "Status"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 300)  # Command
        self.setColumnWidth(2, 150)  # Location
        self.setColumnWidth(3, 100)  # Type
        self.setColumnWidth(4, 100)  # Status
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_entry(self, name, command, location, entry_type, enabled):
        """Add a startup entry to the tree.
        
        Args:
            name: Entry name
            command: Command or path
            location: Registry key or folder
            entry_type: Type (Registry, Shortcut, Service)
            enabled: Whether entry is enabled
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            command,
            location,
            entry_type,
            "Enabled" if enabled else "Disabled"
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def update_entry(self, item, name=None, command=None, location=None,
                   entry_type=None, enabled=None):
        """Update an existing startup entry.
        
        Args:
            item: QTreeWidgetItem to update
            name: New name (optional)
            command: New command (optional)
            location: New location (optional)
            entry_type: New type (optional)
            enabled: New enabled state (optional)
        """
        if name is not None:
            item.setText(0, name)
        if command is not None:
            item.setText(1, command)
        if location is not None:
            item.setText(2, location)
        if entry_type is not None:
            item.setText(3, entry_type)
        if enabled is not None:
            item.setText(4, "Enabled" if enabled else "Disabled")
            
    def get_entry(self, item):
        """Get startup entry details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            tuple: (name, command, location, type, enabled)
        """
        return (
            item.text(0),  # name
            item.text(1),  # command
            item.text(2),  # location
            item.text(3),  # type
            item.text(4) == "Enabled"  # enabled
        )
        
    def clear_entries(self):
        """Clear all startup entries from the tree."""
        self.clear()
        
    def find_entry(self, name, location):
        """Find a startup entry by name and location.
        
        Args:
            name: Entry name
            location: Entry location
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        for item in items:
            if item.text(2) == location:
                return item
        return None

    def add_virtual_entry(self, name, command, location, entry_type):
        """Add a virtual startup entry to the tree.
        
        A virtual entry represents an entry from the imported configuration
        that doesn't exist in the system yet. It will be highlighted to
        indicate it's from the imported configuration.
        
        Args:
            name: Entry name
            command: Command or path
            location: Registry key or folder
            entry_type: Type (Registry, Shortcut, Service)
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            command,
            location,
            entry_type,
            "Virtual (Not Applied)"
        ])
        
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
                item.setToolTip(col, "Virtual entry from configuration file (not in system yet)")
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
