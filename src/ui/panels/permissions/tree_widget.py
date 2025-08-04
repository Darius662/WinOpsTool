"""Tree widget for Windows permissions."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
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
        
        # Track virtual items
        self.virtual_items = set()
        
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
        
    def add_virtual_permission(self, name, type, permissions):
        """Add a virtual permission to the tree (from imported config).
        
        Args:
            name: User/group name
            type: Account type
            permissions: List of permission names
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Add with "Virtual" appended to type
        virtual_type = f"{type} (Virtual)"
        
        item = self.add_permission(
            name,
            virtual_type,
            permissions
        )
        
        # Mark as virtual
        self.virtual_items.add(item)
        
        # Highlight the item
        self.highlight_item(item, is_virtual=True)
        
        return item
        
    def highlight_item(self, item, is_virtual=False):
        """Highlight an item to indicate it's from imported config or virtual.
        
        Args:
            item: QTreeWidgetItem to highlight
            is_virtual: Whether this is a virtual item
        """
        # Use cyan background with dark blue text for highlighting
        background_color = QColor(200, 255, 255)  # Light cyan
        text_color = QColor(0, 0, 128)  # Dark blue
        
        # Set background color for all columns
        for col in range(self.columnCount()):
            item.setBackground(col, QBrush(background_color))
            item.setForeground(col, QBrush(text_color))
            
        # Set tooltip
        if is_virtual:
            tooltip = "Virtual permission from imported configuration (does not exist in system)"
        else:
            tooltip = "Permission from imported configuration"
            
        for col in range(self.columnCount()):
            item.setToolTip(col, tooltip)
            
    def is_virtual_item(self, item):
        """Check if an item is a virtual item.
        
        Args:
            item: QTreeWidgetItem to check
            
        Returns:
            bool: True if item is virtual, False otherwise
        """
        return item in self.virtual_items
        
    def get_all_items(self):
        """Get all items in the tree.
        
        Returns:
            list: List of all QTreeWidgetItems
        """
        items = []
        for i in range(self.topLevelItemCount()):
            items.append(self.topLevelItem(i))
        return items
        
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
