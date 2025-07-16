"""Tree widget for device drivers."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class DriversTree(QTreeWidget):
    """Tree widget for displaying device drivers."""
    
    def __init__(self, parent=None):
        """Initialize drivers tree.
        
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
            "Display Name",
            "Manufacturer",
            "Start Type",
            "State"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 250)  # Display Name
        self.setColumnWidth(2, 200)  # Manufacturer
        self.setColumnWidth(3, 100)  # Start Type
        self.setColumnWidth(4, 100)  # State
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_driver(self, name, display_name, manufacturer, start_type, state):
        """Add a driver to the tree.
        
        Args:
            name: Driver name
            display_name: Display name
            manufacturer: Manufacturer name
            start_type: Start type
            state: Current state
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            display_name,
            manufacturer,
            start_type,
            state
        ])
        
        self.addTopLevelItem(item)
        return item
        
    def update_driver(self, item, name=None, display_name=None,
                    manufacturer=None, start_type=None, state=None):
        """Update an existing driver entry.
        
        Args:
            item: QTreeWidgetItem to update
            name: New name (optional)
            display_name: New display name (optional)
            manufacturer: New manufacturer (optional)
            start_type: New start type (optional)
            state: New state (optional)
        """
        if name is not None:
            item.setText(0, name)
        if display_name is not None:
            item.setText(1, display_name)
        if manufacturer is not None:
            item.setText(2, manufacturer)
        if start_type is not None:
            item.setText(3, start_type)
        if state is not None:
            item.setText(4, state)
            
    def get_driver(self, item):
        """Get driver details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            tuple: (name, display_name, manufacturer, start_type, state)
        """
        return (
            item.text(0),  # name
            item.text(1),  # display_name
            item.text(2),  # manufacturer
            item.text(3),  # start_type
            item.text(4)   # state
        )
        
    def clear_drivers(self):
        """Clear all drivers from the tree."""
        self.clear()
        
    def find_driver(self, name):
        """Find a driver by name.
        
        Args:
            name: Driver name
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
