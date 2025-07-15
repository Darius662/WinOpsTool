"""Tree widget for registry entries."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class RegistryTree(QTreeWidget):
    """Tree widget for displaying registry entries."""
    
    def __init__(self, parent=None):
        """Initialize registry tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setHeaderLabels([
            "Path",
            "Name",
            "Type",
            "Value"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 300)  # Path
        self.setColumnWidth(1, 150)  # Name
        self.setColumnWidth(2, 100)  # Type
        self.setColumnWidth(3, 200)  # Value
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_entry(self, path, name, reg_type, value):
        """Add a registry entry to the tree.
        
        Args:
            path: Registry key path
            name: Value name
            reg_type: Registry value type
            value: Registry value
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            path,
            name,
            reg_type,
            str(value)
        ])
        self.addTopLevelItem(item)
        return item
        
    def update_entry(self, item, path=None, name=None, reg_type=None, value=None):
        """Update an existing registry entry.
        
        Args:
            item: QTreeWidgetItem to update
            path: New registry key path (optional)
            name: New value name (optional)
            reg_type: New registry value type (optional)
            value: New registry value (optional)
        """
        if path is not None:
            item.setText(0, path)
        if name is not None:
            item.setText(1, name)
        if reg_type is not None:
            item.setText(2, reg_type)
        if value is not None:
            item.setText(3, str(value))
            
    def get_entry(self, item):
        """Get registry entry details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            tuple: (path, name, type, value)
        """
        return (
            item.text(0),  # path
            item.text(1),  # name
            item.text(2),  # type
            item.text(3)   # value
        )
        
    def clear_entries(self):
        """Clear all registry entries from the tree."""
        self.clear()
        
    def find_entry(self, path, name):
        """Find a registry entry by path and name.
        
        Args:
            path: Registry key path
            name: Value name
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(
            path,
            Qt.MatchFlag.MatchExactly,
            0  # Path column
        )
        
        for item in items:
            if item.text(1) == name:  # Check name column
                return item
                
        return None
