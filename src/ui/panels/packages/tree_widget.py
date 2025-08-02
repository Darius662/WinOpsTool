"""Tree widget for Windows packages."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush
from src.core.logger import setup_logger

class PackagesTree(QTreeWidget):
    """Tree widget for displaying installed programs and packages."""
    
    def __init__(self, parent=None):
        """Initialize packages tree.
        
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
            "Version",
            "Publisher",
            "Install Date",
            "Location",
            "Registry Key"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 250)  # Name
        self.setColumnWidth(1, 100)  # Version
        self.setColumnWidth(2, 200)  # Publisher
        self.setColumnWidth(3, 100)  # Install Date
        self.setColumnWidth(4, 300)  # Location
        self.setColumnWidth(5, 200)  # Registry Key
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_program(self, name, version, publisher, install_date,
                  install_location, registry_key):
        """Add a program to the tree.
        
        Args:
            name: Program name
            version: Version string
            publisher: Publisher name
            install_date: Installation date
            install_location: Install path
            registry_key: Registry key name
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            version,
            publisher,
            install_date,
            install_location,
            registry_key
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def add_virtual_program(self, name, version, publisher):
        """Add a virtual program to the tree (from imported config).
        
        Args:
            name: Program name
            version: Version string
            publisher: Publisher name
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        # Add with placeholder values for virtual entries
        item = self.add_program(
            name,
            version,
            publisher,
            "N/A (Virtual)",
            "Not installed",
            "Config Import"
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
            tooltip = "Virtual package from imported configuration (not installed)"
        else:
            tooltip = "Package from imported configuration"
            
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
        
    def get_program(self, item):
        """Get program details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Program properties
        """
        return {
            'name': item.text(0),
            'version': item.text(1),
            'publisher': item.text(2),
            'install_date': item.text(3),
            'install_location': item.text(4),
            'registry_key': item.text(5)
        }
        
    def clear_programs(self):
        """Clear all programs from the tree."""
        self.clear()
        
    def find_program(self, name):
        """Find a program by name.
        
        Args:
            name: Program name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
