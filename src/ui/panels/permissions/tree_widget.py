"""Tree widget for Windows permissions."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class PermissionsTree(QTreeWidget):
    """Tree widget for displaying file/folder permissions."""
    
    def __init__(self, parent=None):
        """Initialize permissions tree.
        
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
            "Permissions"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 100)  # Type
        self.setColumnWidth(2, 300)  # Permissions
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_permission(self, name, type, permissions):
        """Add a permission to the tree.
        
        Args:
            name: User/group name
            type: Account type
            permissions: List of permission names
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            type,
            ", ".join(permissions)
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def get_permission(self, item):
        """Get permission details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Permission properties
        """
        return {
            'name': item.text(0),
            'type': item.text(1),
            'permissions': item.text(2).split(", ")
        }
        
    def clear_permissions(self):
        """Clear all permissions from the tree."""
        self.clear()
        
    def find_permission(self, name):
        """Find a permission by name.
        
        Args:
            name: User/group name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
