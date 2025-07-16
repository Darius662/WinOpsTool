"""Environment variables management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import EnvironmentTree
from .dialogs import AddVariableDialog
from .manager import EnvironmentManager

class EnvironmentPanel(BasePanel):
    """Panel for managing environment variables."""
    
    def __init__(self, main_window):
        """Initialize environment panel.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = EnvironmentManager()
        self.setup_ui()
        self.refresh_variables()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create tree widget
        self.tree = EnvironmentTree()
        self.add_widget(self.tree)
        
        # Create buttons
        button_layout = QHBoxLayout()
        
        self.add_button = QPushButton("Add")
        button_layout.addWidget(self.add_button)
        
        self.edit_button = QPushButton("Edit")
        button_layout.addWidget(self.edit_button)
        
        self.delete_button = QPushButton("Delete")
        button_layout.addWidget(self.delete_button)
        
        self.refresh_button = QPushButton("Refresh")
        button_layout.addWidget(self.refresh_button)
        
        self.add_layout(button_layout)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        self.add_button.clicked.connect(self.add_variable)
        self.edit_button.clicked.connect(self.edit_variable)
        self.delete_button.clicked.connect(self.delete_variable)
        self.refresh_button.clicked.connect(self.refresh_variables)
        
    def add_variable(self):
        """Add a new environment variable."""
        dialog = AddVariableDialog(self)
        if dialog.exec():
            name, value, var_type = dialog.get_variable()
            try:
                # Set environment variable
                success = False
                if var_type == "System":
                    success = self.manager.set_system_variable(name, value)
                else:
                    success = self.manager.set_user_variable(name, value)
                    
                if success:
                    self.tree.add_variable(name, value, var_type)
                    self.logger.info(f"Added {var_type} variable: {name}={value}")
                else:
                    raise Exception("Failed to set variable")
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
                success = False
                # Delete old variable if name changed
                if name != new_name:
                    if var_type == "System":
                        success = self.manager.delete_system_variable(name)
                    else:
                        success = self.manager.delete_user_variable(name)
                    if not success:
                        raise Exception(f"Failed to delete old variable {name}")
                        
                # Set new variable
                if new_type == "System":
                    success = self.manager.set_system_variable(new_name, new_value)
                else:
                    success = self.manager.set_user_variable(new_name, new_value)
                    
                if success:
                    self.tree.update_variable(item, new_name, new_value, new_type)
                    self.logger.info(
                        f"Updated variable: {name}={value} -> {new_name}={new_value}"
                    )
                else:
                    raise Exception("Failed to set new variable value")
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
                success = False
                if var_type == "System":
                    success = self.manager.delete_system_variable(name)
                else:
                    success = self.manager.delete_user_variable(name)
                    
                if success:
                    self.tree.takeTopLevelItem(
                        self.tree.indexOfTopLevelItem(item)
                    )
                    self.logger.info(f"Deleted {var_type} variable: {name}")
                else:
                    raise Exception("Failed to delete variable")
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
        for name, value in self.manager.get_user_variables().items():
            self.tree.add_variable(name, value, "User")
            
        # Add system variables
        for name, value in self.manager.get_system_variables().items():
            self.tree.add_variable(name, value, "System")
        
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local env vars when remote
