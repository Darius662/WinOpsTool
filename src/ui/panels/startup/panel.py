"""Windows Startup management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import StartupTree
from .dialogs import AddStartupDialog
from .manager import StartupManager

class StartupPanel(BasePanel):
    """Panel for managing Windows startup entries."""
    
    def __init__(self, parent=None):
        """Initialize startup panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = StartupManager()
        self.setup_ui()
        
        # Initial refresh
        self.refresh_entries()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Create tree widget
        self.tree = StartupTree()
        layout.addWidget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_entry)
        button_layout.addWidget(add_button)
        
        remove_button = QPushButton("Remove")
        remove_button.clicked.connect(self.remove_entry)
        button_layout.addWidget(remove_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_entries)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
    def add_entry(self):
        """Add a new startup entry."""
        dialog = AddStartupDialog(self)
        if dialog.exec():
            name, command, user_specific = dialog.get_entry()
            
            try:
                if self.manager.add_registry_startup(name, command, user_specific):
                    location = 'HKCU_RUN' if user_specific else 'HKLM_RUN'
                    self.tree.add_entry(
                        name,
                        command,
                        location,
                        'Registry',
                        True
                    )
                    self.logger.info(f"Added startup entry: {name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to add startup entry."
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to add startup entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add startup entry: {str(e)}"
                )
                
    def remove_entry(self):
        """Remove selected startup entry."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select an entry to remove."
            )
            return
            
        name, _, location, entry_type, _ = self.tree.get_entry(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Are you sure you want to remove '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                success = False
                
                if entry_type == 'Registry':
                    success = self.manager.remove_registry_startup(name, location)
                elif entry_type == 'Shortcut':
                    success = self.manager.remove_folder_startup(name, location)
                else:
                    QMessageBox.warning(
                        self,
                        "Cannot Remove",
                        f"Cannot remove entries of type: {entry_type}"
                    )
                    return
                    
                if success:
                    self.tree.takeTopLevelItem(
                        self.tree.indexOfTopLevelItem(item)
                    )
                    self.logger.info(f"Removed startup entry: {name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        "Failed to remove startup entry."
                    )
                    
            except Exception as e:
                self.logger.error(f"Failed to remove startup entry: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to remove startup entry: {str(e)}"
                )
                
    def refresh_entries(self):
        """Refresh startup entries list."""
        try:
            # Clear existing entries
            self.tree.clear_entries()
            
            # Add registry entries
            for entry in self.manager.get_registry_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            # Add folder entries
            for entry in self.manager.get_folder_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            # Add service entries
            for entry in self.manager.get_service_startups():
                self.tree.add_entry(
                    entry['name'],
                    entry['command'],
                    entry['location'],
                    entry['type'],
                    entry['enabled']
                )
                
            self.logger.debug("Refreshed startup entries")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh startup entries: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh startup entries: {str(e)}"
            )
