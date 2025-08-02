"""Split view for user and system environment variables."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSplitter, QLabel
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from ..tree_widget import EnvironmentTree

class VariablesView(QWidget):
    """Split view component for user and system environment variables."""
    
    def __init__(self, parent=None):
        """Initialize variables view.
        
        Args:
            parent: Parent widget (EnvironmentPanel)
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the variables view UI."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create splitter for user and system variables
        self.splitter = QSplitter(Qt.Orientation.Vertical)
        
        # User variables section
        self.user_section = QWidget()
        user_layout = QVBoxLayout(self.user_section)
        user_layout.setContentsMargins(0, 0, 0, 0)
        
        user_label = QLabel("User Environment Variables")
        user_label.setStyleSheet("font-weight: bold; padding: 5px;")
        user_layout.addWidget(user_label)
        
        self.user_tree = EnvironmentTree()
        self.user_tree.setHeaderLabels(["Name", "Value"])
        self.user_tree.setColumnWidth(0, 200)
        self.user_tree.setColumnWidth(1, 300)
        user_layout.addWidget(self.user_tree)
        
        # System variables section
        self.system_section = QWidget()
        system_layout = QVBoxLayout(self.system_section)
        system_layout.setContentsMargins(0, 0, 0, 0)
        
        system_label = QLabel("System Environment Variables")
        system_label.setStyleSheet("font-weight: bold; padding: 5px;")
        system_layout.addWidget(system_label)
        
        self.system_tree = EnvironmentTree()
        self.system_tree.setHeaderLabels(["Name", "Value"])
        self.system_tree.setColumnWidth(0, 200)
        self.system_tree.setColumnWidth(1, 300)
        system_layout.addWidget(self.system_tree)
        
        # Add sections to splitter
        self.splitter.addWidget(self.user_section)
        self.splitter.addWidget(self.system_section)
        self.splitter.setStretchFactor(0, 1)
        self.splitter.setStretchFactor(1, 1)
        
        layout.addWidget(self.splitter)
        
    def connect_signals(self):
        """Connect tree signals."""
        self.user_tree.itemSelectionChanged.connect(self.on_selection_changed)
        self.system_tree.itemSelectionChanged.connect(self.on_selection_changed)
        
    def on_selection_changed(self):
        """Handle selection change in either tree."""
        # Ensure only one tree has selection at a time
        sender = self.sender()
        if sender == self.user_tree and self.user_tree.selectedItems():
            self.system_tree.clearSelection()
        elif sender == self.system_tree and self.system_tree.selectedItems():
            self.user_tree.clearSelection()
            
        # Notify panel of selection change
        if self.panel:
            self.panel.update_button_states()
            
    def get_selected_tree(self):
        """Get the tree that has the current selection.
        
        Returns:
            The tree widget with selection, or None if no selection
        """
        if self.user_tree.selectedItems():
            return self.user_tree
        elif self.system_tree.selectedItems():
            return self.system_tree
        return None
        
    def get_selected_variable(self):
        """Get the currently selected variable.
        
        Returns:
            Tuple of (name, value, type) or None if no selection
        """
        tree = self.get_selected_tree()
        if not tree:
            return None
            
        item = tree.currentItem()
        if not item:
            return None
            
        var_type = "User" if tree == self.user_tree else "System"
        return (item.text(0), item.text(1), var_type)
        
    def add_variable(self, name, value, var_type):
        """Add a variable to the appropriate tree.
        
        Args:
            name: Variable name
            value: Variable value
            var_type: Variable type ("User" or "System")
            
        Returns:
            The created tree item
        """
        if var_type == "User":
            return self.user_tree.add_variable(name, value)
        else:
            return self.system_tree.add_variable(name, value)
            
    def update_variable(self, name, value, var_type):
        """Update a variable in the appropriate tree.
        
        Args:
            name: Variable name
            value: Variable value
            var_type: Variable type ("User" or "System")
        """
        tree = self.get_selected_tree()
        if not tree:
            return
            
        item = tree.currentItem()
        if not item:
            return
            
        # If type changed, remove from current tree and add to other tree
        current_type = "User" if tree == self.user_tree else "System"
        if current_type != var_type:
            tree.takeTopLevelItem(tree.indexOfTopLevelItem(item))
            self.add_variable(name, value, var_type)
        else:
            tree.update_variable(item, name, value)
            
    def clear_variables(self):
        """Clear all variables from both trees."""
        self.user_tree.clear()
        self.system_tree.clear()
        
    def add_virtual_user_variable(self, name, value):
        """Add a virtual user variable that doesn't exist in the system yet.
        
        This creates a visual entry for a variable from the imported configuration
        that doesn't exist in the system yet. The entry will be highlighted.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            The created tree item
        """
        item = self.user_tree.add_variable(name, value)
        
        # Apply special styling for imported items
        for col in range(2):
            item.setBackground(col, Qt.GlobalColor.cyan)
            item.setForeground(col, Qt.GlobalColor.darkBlue)
            item.setFont(col, self.font())
            item.setToolTip(col, "Imported from configuration file")
            
        return item
        
    def add_virtual_system_variable(self, name, value):
        """Add a virtual system variable that doesn't exist in the system yet.
        
        This creates a visual entry for a variable from the imported configuration
        that doesn't exist in the system yet. The entry will be highlighted.
        
        Args:
            name: Variable name
            value: Variable value
            
        Returns:
            The created tree item
        """
        item = self.system_tree.add_variable(name, value)
        
        # Apply special styling for imported items
        for col in range(2):
            item.setBackground(col, Qt.GlobalColor.cyan)
            item.setForeground(col, Qt.GlobalColor.darkBlue)
            item.setFont(col, self.font())
            item.setToolTip(col, "Imported from configuration file")
            
        return item
        
    def has_selection(self):
        """Check if any tree has a selection.
        
        Returns:
            True if a variable is selected, False otherwise
        """
        return bool(self.user_tree.selectedItems() or self.system_tree.selectedItems())
