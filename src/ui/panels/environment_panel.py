"""Environment Variables Management Panel."""
import os
import winreg
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTableWidget,
                          QTableWidgetItem, QComboBox, QMessageBox, QInputDialog,
                          QLineEdit)
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class EnvironmentPanel(BasePanel):
    """Panel for managing system and user environment variables."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Scope selector
        self.scope_combo = QComboBox()
        self.scope_combo.addItems(["User Variables", "System Variables"])
        self.scope_combo.currentTextChanged.connect(self.load_variables)
        self.add_widget(self.scope_combo)
        
        # Variables table
        self.variables_table = QTableWidget()
        self.variables_table.setColumnCount(2)
        self.variables_table.setHorizontalHeaderLabels(["Variable", "Value"])
        self.variables_table.horizontalHeader().setStretchLastSection(True)
        self.add_widget(self.variables_table)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Variable")
        self.edit_btn = QPushButton("Edit Selected")
        self.delete_btn = QPushButton("Delete Selected")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.edit_btn, self.delete_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_variable)
        self.edit_btn.clicked.connect(self.edit_variable)
        self.delete_btn.clicked.connect(self.delete_variable)
        self.refresh_btn.clicked.connect(self.load_variables)
        
        # Initial load
        self.load_variables()
        
    def load_variables(self):
        """Load environment variables based on selected scope."""
        try:
            self.variables_table.setRowCount(0)
            
            if self.scope_combo.currentText() == "User Variables":
                key = winreg.HKEY_CURRENT_USER
                subkey = "Environment"
            else:
                key = winreg.HKEY_LOCAL_MACHINE
                subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_READ) as reg_key:
                index = 0
                while True:
                    try:
                        name, value, _ = winreg.EnumValue(reg_key, index)
                        self.variables_table.insertRow(index)
                        self.variables_table.setItem(index, 0, QTableWidgetItem(name))
                        self.variables_table.setItem(index, 1, QTableWidgetItem(str(value)))
                        index += 1
                    except WindowsError:
                        break
                        
        except Exception as e:
            self.logger.error(f"Failed to load environment variables: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to load environment variables: {str(e)}")
            
    def add_variable(self, name=None, value=None, scope=None):
        """Add a new environment variable."""
        try:
            if name is None or value is None:
                name, ok = QInputDialog.getText(self, "Add Variable", "Variable name:")
                if ok and name:
                    value, ok = QInputDialog.getText(self, "Add Variable", "Variable value:")
                    if not ok:
                        return
                else:
                    return
                    
            if scope is None:
                scope = self.scope_combo.currentText()
                
            if scope == "User Variables":
                key = winreg.HKEY_CURRENT_USER
                subkey = "Environment"
            else:
                key = winreg.HKEY_LOCAL_MACHINE
                subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
            with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                winreg.SetValueEx(reg_key, name, 0, winreg.REG_EXPAND_SZ, value)
                
            self.load_variables()
            self.logger.info(f"Added environment variable: {name}")
            
        except Exception as e:
            self.logger.error(f"Failed to add environment variable: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add environment variable: {str(e)}")
            
    def edit_variable(self):
        """Edit the selected environment variable."""
        try:
            current_row = self.variables_table.currentRow()
            if current_row >= 0:
                name = self.variables_table.item(current_row, 0).text()
                old_value = self.variables_table.item(current_row, 1).text()
                
                value, ok = QInputDialog.getText(
                    self, "Edit Variable",
                    f"New value for {name}:",
                    QLineEdit.EchoMode.Normal,
                    old_value
                )
                
                if ok:
                    if self.scope_combo.currentText() == "User Variables":
                        key = winreg.HKEY_CURRENT_USER
                        subkey = "Environment"
                    else:
                        key = winreg.HKEY_LOCAL_MACHINE
                        subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                        
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                        winreg.SetValueEx(reg_key, name, 0, winreg.REG_EXPAND_SZ, value)
                        
                    self.load_variables()
                    self.logger.info(f"Updated environment variable: {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to edit environment variable: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit environment variable: {str(e)}")
            
    def delete_variable(self):
        """Delete the selected environment variable."""
        try:
            current_row = self.variables_table.currentRow()
            if current_row >= 0:
                name = self.variables_table.item(current_row, 0).text()
                
                reply = QMessageBox.question(
                    self,
                    "Confirm Delete",
                    f"Are you sure you want to delete the environment variable '{name}'?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                
                if reply == QMessageBox.StandardButton.Yes:
                    if self.scope_combo.currentText() == "User Variables":
                        key = winreg.HKEY_CURRENT_USER
                        subkey = "Environment"
                    else:
                        key = winreg.HKEY_LOCAL_MACHINE
                        subkey = r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
                        
                    with winreg.OpenKey(key, subkey, 0, winreg.KEY_SET_VALUE) as reg_key:
                        winreg.DeleteValue(reg_key, name)
                        
                    self.load_variables()
                    self.logger.info(f"Deleted environment variable: {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to delete environment variable: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete environment variable: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def get_remote_vars(self, remote_pc):
        """Get environment variables from remote PC."""
        try:
            remote_reg = winreg.ConnectRegistry(remote_pc.hostname, winreg.HKEY_LOCAL_MACHINE)
            system_vars = {}
            user_vars = {}
            
            # Get system variables
            system_key = winreg.OpenKey(
                remote_reg,
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment",
                0,
                winreg.KEY_READ
            )
            try:
                i = 0
                while True:
                    name, value, _ = winreg.EnumValue(system_key, i)
                    system_vars[name] = value
                    i += 1
            except WindowsError:
                pass
            finally:
                winreg.CloseKey(system_key)
                
            # Get user variables
            user_key = winreg.OpenKey(
                remote_reg,
                r"Environment",
                0,
                winreg.KEY_READ
            )
            try:
                i = 0
                while True:
                    name, value, _ = winreg.EnumValue(user_key, i)
                    user_vars[name] = value
                    i += 1
            except WindowsError:
                pass
            finally:
                winreg.CloseKey(user_key)
                
            return system_vars, user_vars
            
        except Exception as e:
            self.logger.error(f"Failed to get environment variables from {remote_pc.name}: {str(e)}")
            return {}, {}
            
    def apply_remote(self, remote_pc):
        """Apply environment variables to remote PC."""
        try:
            # Get remote variables
            remote_system_vars, remote_user_vars = self.get_remote_vars(remote_pc)
            
            # Check for conflicts
            from ..dialogs.env_var_conflict_dialog import EnvVarConflictDialog
            
            # System variables conflicts
            if remote_system_vars:
                dialog = EnvVarConflictDialog(
                    self.system_vars,
                    remote_system_vars,
                    remote_pc.name,
                    self
                )
                if dialog.exec() == EnvVarConflictDialog.DialogCode.Accepted:
                    system_resolutions = dialog.get_resolutions()
                else:
                    return False
            else:
                system_resolutions = self.system_vars
                
            # User variables conflicts
            if remote_user_vars:
                dialog = EnvVarConflictDialog(
                    self.user_vars,
                    remote_user_vars,
                    remote_pc.name,
                    self
                )
                if dialog.exec() == EnvVarConflictDialog.DialogCode.Accepted:
                    user_resolutions = dialog.get_resolutions()
                else:
                    return False
            else:
                user_resolutions = self.user_vars
                
            # Apply resolutions
            remote_reg = winreg.ConnectRegistry(remote_pc.hostname, winreg.HKEY_LOCAL_MACHINE)
            
            # Apply system variables
            for name, value in system_resolutions.items():
                self.set_remote_env_var(remote_reg, name, value, is_system=True)
                
            # Apply user variables
            for name, value in user_resolutions.items():
                self.set_remote_env_var(remote_reg, name, value, is_system=False)
                
            return True
                
        except Exception as e:
            self.logger.error(f"Failed to apply environment variables to {remote_pc.name}: {str(e)}")
            return False
                
            # Apply local variables to remote PC
            # System variables
            with winreg.OpenKey(system_key, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 0, winreg.KEY_SET_VALUE) as key:
                for var in self.system_vars:
                    winreg.SetValueEx(key, var.name, 0, winreg.REG_EXPAND_SZ, var.value)
                    
            # User variables
            with winreg.OpenKey(user_key, "Environment", 0, winreg.KEY_SET_VALUE) as key:
                for var in self.user_vars:
                    winreg.SetValueEx(key, var.name, 0, winreg.REG_EXPAND_SZ, var.value)
                    
            # Notify the system about the change
            win32api.SendMessage(
                win32con.HWND_BROADCAST,
                win32con.WM_SETTINGCHANGE,
                0,
                "Environment",
                0
            )
            
            self.logger.info(f"Applied environment variables to remote PC: {remote_pc.name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply environment variables to {remote_pc.name}: {str(e)}")
            return False
