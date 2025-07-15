"""Tree widget for environment variables."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
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
        self.setHeaderLabels(["Name", "Value", "Type"])
        self.setColumnWidth(0, 200)
        self.setColumnWidth(1, 300)
        
    def add_variable(self, name, value, var_type="User"):
        """Add an environment variable to the tree.
        
        Args:
            name: Variable name
            value: Variable value
            var_type: Variable type (User/System)
        """
        item = QTreeWidgetItem([name, value, var_type])
        self.addTopLevelItem(item)
        return item
        
    def update_variable(self, item, name, value, var_type=None):
        """Update an existing environment variable.
        
        Args:
            item: QTreeWidgetItem to update
            name: New variable name
            value: New variable value
            var_type: New variable type (optional)
        """
        item.setText(0, name)
        item.setText(1, value)
        if var_type:
            item.setText(2, var_type)
            
    def get_variable(self, item):
        """Get variable details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            Tuple of (name, value, type)
        """
        return (
            item.text(0),
            item.text(1),
            item.text(2)
        )
        
    def clear_variables(self):
        """Clear all variables from the tree."""
        self.clear()
