"""Tree widget for environment variables."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class EnvironmentTree(QTreeWidget):
    """Tree widget for displaying environment variables."""
    
    def __init__(self, parent=None):
        """Initialize environment tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setAlternatingRowColors(True)
        self.setSortingEnabled(True)
        self.setRootIsDecorated(False)  # No expand/collapse icons
        
    def add_variable(self, name, value):
        """Add an environment variable to the tree.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            The created tree item
        """
        item = QTreeWidgetItem([name, value])
        self.addTopLevelItem(item)
        return item
        
    def update_variable(self, item, name, value):
        """Update an existing environment variable.
        
        Args:
            item: QTreeWidgetItem to update
            name: New variable name
            value: New variable value
        """
        item.setText(0, name)
        item.setText(1, value)
            
    def get_variable(self, item):
        """Get variable details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            Tuple of (name, value)
        """
        return (item.text(0), item.text(1))
        
    def clear_variables(self):
        """Clear all variables from the tree."""
        self.clear()
        
    def find_variable(self, name):
        """Find a variable by name.
        
        Args:
            name: Variable name to find
            
        Returns:
            QTreeWidgetItem if found, None otherwise
        """
        items = self.findItems(name, Qt.MatchFlag.MatchExactly, 0)
        return items[0] if items else None
