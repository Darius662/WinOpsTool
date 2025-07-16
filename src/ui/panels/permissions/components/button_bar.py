"""Button bar component for permissions panel."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from PyQt6.QtCore import pyqtSignal

from .add_button import AddButton
from .edit_button import EditButton
from .delete_button import DeleteButton
from .refresh_button import RefreshButton


class ButtonBar(QWidget):
    """Button bar for permissions panel."""
    
    # Signals emitted when buttons are clicked
    add_permission = pyqtSignal(str)
    edit_permission = pyqtSignal(str)
    remove_permission = pyqtSignal(str)
    refresh_permissions = pyqtSignal(str)
    
    def __init__(self, path=None, parent=None):
        """Initialize button bar.
        
        Args:
            path: Current path
            parent: Parent widget
        """
        super().__init__(parent)
        self.path = path
        self.setup_ui()
        self.setup_connections()
        
    def setup_ui(self):
        """Set up the UI components."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.add_btn = AddButton(self.path, self)
        self.edit_btn = EditButton(self.path, self)
        self.delete_btn = DeleteButton(self.path, self)
        self.refresh_btn = RefreshButton(self.path, self)
        
        # Add buttons to layout
        layout.addWidget(self.add_btn)
        layout.addWidget(self.edit_btn)
        layout.addWidget(self.delete_btn)
        layout.addWidget(self.refresh_btn)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
    def setup_connections(self):
        """Set up signal connections."""
        self.add_btn.clicked_with_path.connect(self.add_permission)
        self.edit_btn.clicked_with_path.connect(self.edit_permission)
        self.delete_btn.clicked_with_path.connect(self.remove_permission)
        self.refresh_btn.clicked_with_path.connect(self.refresh_permissions)
        
    def update_path(self, path):
        """Update the path for all buttons.
        
        Args:
            path: New path
        """
        self.path = path
        self.add_btn.update_path(path)
        self.edit_btn.update_path(path)
        self.delete_btn.update_path(path)
        self.refresh_btn.update_path(path)
        
    def update_button_states(self, has_selection):
        """Update button enabled states based on selection.
        
        Args:
            has_selection: Whether an item is selected
        """
        has_path = bool(self.path)
        self.edit_btn.update_state(has_path, has_selection)
        self.delete_btn.update_state(has_path, has_selection)
