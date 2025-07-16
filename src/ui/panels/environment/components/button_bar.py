"""Button bar component for environment panel."""
from PyQt6.QtWidgets import QWidget, QHBoxLayout
from src.core.logger import setup_logger
from .add_button import AddButton
from .edit_button import EditButton
from .delete_button import DeleteButton
from .refresh_button import RefreshButton

class ButtonBar(QWidget):
    """Button bar containing all action buttons for environment panel."""
    
    def __init__(self, parent=None):
        """Initialize button bar.
        
        Args:
            parent: Parent widget (EnvironmentPanel)
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.panel = parent
        self.setup_ui()
        self.connect_signals()
        
    def setup_ui(self):
        """Set up the button bar UI."""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create buttons
        self.add_button = AddButton(self.panel)
        layout.addWidget(self.add_button)
        
        self.edit_button = EditButton(self.panel)
        layout.addWidget(self.edit_button)
        
        self.delete_button = DeleteButton(self.panel)
        layout.addWidget(self.delete_button)
        
        self.refresh_button = RefreshButton(self.panel)
        layout.addWidget(self.refresh_button)
        
    def connect_signals(self):
        """Connect all button signals."""
        self.add_button.connect_signals()
        self.edit_button.connect_signals()
        self.delete_button.connect_signals()
        self.refresh_button.connect_signals()
        
    def update_button_states(self, has_selection=False):
        """Update button enabled states.
        
        Args:
            has_selection: Whether an item is selected in the tree
        """
        self.edit_button.setEnabled(has_selection)
        self.delete_button.setEnabled(has_selection)
