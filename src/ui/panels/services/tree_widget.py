"""Tree widget for Windows Services."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class ServicesTree(QTreeWidget):
    """Tree widget for displaying Windows Services."""
    
    def __init__(self, parent=None):
        """Initialize services tree.
        
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
            "Description",
            "State",
            "Startup Type",
            "Path",
            "Account"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 150)  # Name
        self.setColumnWidth(1, 200)  # Display Name
        self.setColumnWidth(2, 300)  # Description
        self.setColumnWidth(3, 80)   # State
        self.setColumnWidth(4, 100)  # Startup Type
        self.setColumnWidth(5, 300)  # Path
        self.setColumnWidth(6, 150)  # Account
        
        # Enable sorting and alternating row colors
        self.setSortingEnabled(True)
        self.setAlternatingRowColors(True)
        self.sortByColumn(1, Qt.SortOrder.AscendingOrder)
        
    def add_service(self, name, display_name, description, state,
                  start_type, path, account):
        """Add a service to the tree.
        
        Args:
            name: Service name
            display_name: Display name
            description: Description
            state: Current state
            start_type: Startup type
            path: Binary path
            account: Account name
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        item = QTreeWidgetItem([
            name,
            display_name,
            description,
            state,
            start_type,
            path,
            account
        ])
        self.addTopLevelItem(item)
        return item
        
    def update_service(self, item, state=None, start_type=None):
        """Update a service in the tree.
        
        Args:
            item: QTreeWidgetItem to update
            state: New state (optional)
            start_type: New startup type (optional)
        """
        if state is not None:
            item.setText(3, state)
        if start_type is not None:
            item.setText(4, start_type)
            
    def get_service(self, item):
        """Get service details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            dict: Service properties
        """
        return {
            'name': item.text(0),
            'display_name': item.text(1),
            'description': item.text(2),
            'state': item.text(3),
            'start_type': item.text(4),
            'path': item.text(5),
            'account': item.text(6)
        }
        
    def clear_services(self):
        """Clear all services from the tree."""
        self.clear()
        
    def find_service(self, name):
        """Find a service by name.
        
        Args:
            name: Service name to find
            
        Returns:
            QTreeWidgetItem: Found item or None
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
