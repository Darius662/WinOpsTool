"""Tree widget for Windows software."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class SoftwareTree(QTreeWidget):
    """Tree widget for displaying installed software."""
    
    def __init__(self, parent=None):
        """Initialize software tree.
        
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
            "Version",
            "Publisher",
            "Install Date",
            "Size",
            "Location"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 100)  # Version
        self.setColumnWidth(2, 150)  # Publisher
        self.setColumnWidth(3, 100)  # Install Date
        self.setColumnWidth(4, 100)  # Size
        self.setColumnWidth(5, 300)  # Location
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_software(self, name, version, publisher, install_date,
                   size, location):
        """Add software to the tree.
        
        Args:
            name: Software name
            version: Version string
            publisher: Publisher name
            install_date: Installation date
            size: Estimated size
            location: Install location
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            version,
            publisher,
            install_date,
            size,
            location
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def get_software(self, item):
        """Get software details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Software properties
        """
        return {
            'name': item.text(0),
            'version': item.text(1),
            'publisher': item.text(2),
            'install_date': item.text(3),
            'size': item.text(4),
            'location': item.text(5)
        }
        
    def clear_software(self):
        """Clear all software from the tree."""
        self.clear()
        
    def find_software(self, name):
        """Find software by name.
        
        Args:
            name: Software name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
