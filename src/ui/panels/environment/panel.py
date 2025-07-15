"""Environment variables management panel."""
import os
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import EnvironmentTree
from .dialogs import AddVariableDialog

class EnvironmentPanel(BasePanel):
    """Panel for managing environment variables."""
    
    def __init__(self, main_window):
        """Initialize environment panel.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        self.refresh_variables()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Create tree widget
        self.tree = EnvironmentTree()
        layout.addWidget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        add_button = QPushButton("Add")
        add_button.clicked.connect(self.add_variable)
        button_layout.addWidget(add_button)
        
        edit_button = QPushButton("Edit")
        edit_button.clicked.connect(self.edit_variable)
        button_layout.addWidget(edit_button)
        
        delete_button = QPushButton("Delete")
        delete_button.clicked.connect(self.delete_variable)
        button_layout.addWidget(delete_button)
        
        refresh_button = QPushButton("Refresh")
        refresh_button.clicked.connect(self.refresh_variables)
        button_layout.addWidget(refresh_button)
        
        layout.addLayout(button_layout)
        
    def add_variable(self):
        """Add a new environment variable."""
        dialog = AddVariableDialog(self)
        if dialog.exec():
            name, value, var_type = dialog.get_variable()
            try:
                # Set environment variable
                if var_type == "System":
                    # TODO: Use Windows API to set system variable
                    pass
                else:
                    os.environ[name] = value
                    
                self.tree.add_variable(name, value, var_type)
                self.logger.info(f"Added {var_type} variable: {name}={value}")
            except Exception as e:
                self.logger.error(f"Failed to add variable: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add variable: {str(e)}"
                )
                
    def edit_variable(self):
        """Edit selected environment variable."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a variable to edit."
            )
            return
            
        name, value, var_type = self.tree.get_variable(item)
        dialog = AddVariableDialog(self, name, value, var_type)
        
        if dialog.exec():
            new_name, new_value, new_type = dialog.get_variable()
            try:
                # Update environment variable
                if new_type == "System":
                    # TODO: Use Windows API to set system variable
                    pass
                else:
                    if name != new_name:
                        del os.environ[name]
                    os.environ[new_name] = new_value
                    
                self.tree.update_variable(item, new_name, new_value, new_type)
                self.logger.info(
                    f"Updated variable: {name}={value} -> {new_name}={new_value}"
                )
            except Exception as e:
                self.logger.error(f"Failed to update variable: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update variable: {str(e)}"
                )
                
    def delete_variable(self):
        """Delete selected environment variable."""
        item = self.tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a variable to delete."
            )
            return
            
        name, _, var_type = self.tree.get_variable(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete {var_type} variable '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete environment variable
                if var_type == "System":
                    # TODO: Use Windows API to delete system variable
                    pass
                else:
                    del os.environ[name]
                    
                self.tree.takeTopLevelItem(
                    self.tree.indexOfTopLevelItem(item)
                )
                self.logger.info(f"Deleted {var_type} variable: {name}")
            except Exception as e:
                self.logger.error(f"Failed to delete variable: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete variable: {str(e)}"
                )
                
    def refresh_variables(self):
        """Refresh environment variables list."""
        self.tree.clear_variables()
        
        # Add user variables
        for name, value in os.environ.items():
            self.tree.add_variable(name, value, "User")
            
        # TODO: Add system variables using Windows API
        
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local env vars when remote
