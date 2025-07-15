"""Windows Permissions Management Panel."""
import os
import win32security
import win32api
import win32con
import ntsecuritycon
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout,
                          QMessageBox, QInputDialog, QLineEdit, QComboBox,
                          QFileDialog, QDialog, QVBoxLayout, QFormLayout,
                          QDialogButtonBox, QCheckBox)
from PyQt6.QtCore import Qt
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class AddPermissionDialog(QDialog):
    """Dialog for adding a new permission."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Permission")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        # User/Group name
        self.name_edit = QLineEdit()
        form_layout.addRow("User/Group Name:", self.name_edit)
        
        # Permissions
        self.permissions = {
            "Full Control": ntsecuritycon.FILE_ALL_ACCESS,
            "Modify": ntsecuritycon.FILE_GENERIC_WRITE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
            "Read & Execute": ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
            "List Folder Contents": ntsecuritycon.FILE_LIST_DIRECTORY,
            "Read": ntsecuritycon.FILE_GENERIC_READ,
            "Write": ntsecuritycon.FILE_GENERIC_WRITE
        }
        
        self.permission_checks = {}
        for perm_name in self.permissions:
            self.permission_checks[perm_name] = QCheckBox(perm_name)
            form_layout.addRow("", self.permission_checks[perm_name])
            
        layout.addLayout(form_layout)
        
        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_permission_data(self):
        """Get the permission data from the dialog."""
        mask = 0
        for perm_name, check in self.permission_checks.items():
            if check.isChecked():
                mask |= self.permissions[perm_name]
                
        return {
            "name": self.name_edit.text(),
            "mask": mask
        }

class PermissionsPanel(BasePanel):
    """Panel for managing file and folder permissions."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.current_path = None
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Path selection
        self.path_combo = QComboBox()
        self.path_combo.setEditable(True)
        self.path_combo.setMaxCount(10)
        self.path_combo.currentTextChanged.connect(self.path_changed)
        self.add_widget(self.path_combo)
        
        # Browse button
        browse_layout = QHBoxLayout()
        self.browse_btn = QPushButton("Browse...")
        self.browse_btn.clicked.connect(self.browse_path)
        browse_layout.addWidget(self.browse_btn)
        self.add_layout(browse_layout)
        
        # Permissions tree
        self.permissions_tree = QTreeWidget()
        self.permissions_tree.setHeaderLabels([
            "Name",
            "Type",
            "Permissions"
        ])
        self.permissions_tree.setAlternatingRowColors(True)
        for i, width in enumerate([200, 100, 300]):
            self.permissions_tree.setColumnWidth(i, width)
            
        self.add_widget(self.permissions_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Permission")
        self.edit_btn = QPushButton("Edit Permission")
        self.remove_btn = QPushButton("Remove Permission")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.edit_btn, self.remove_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_permission)
        self.edit_btn.clicked.connect(self.edit_permission)
        self.remove_btn.clicked.connect(self.remove_permission)
        self.refresh_btn.clicked.connect(self.refresh_permissions)
        
    def browse_path(self):
        """Browse for a file or folder."""
        path = QFileDialog.getExistingDirectory(
            self,
            "Select Folder",
            os.path.expanduser("~")
        )
        
        if path:
            self.path_combo.insertItem(0, path)
            self.path_combo.setCurrentIndex(0)
            
    def path_changed(self, path):
        """Handle path change."""
        if path and os.path.exists(path):
            self.current_path = path
            self.refresh_permissions()
            
    def refresh_permissions(self):
        """Refresh the permissions list."""
        try:
            self.permissions_tree.clear()
            
            if not self.current_path or not os.path.exists(self.current_path):
                return
                
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                self.current_path,
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Get DACL
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                return
                
            # Process each ACE
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                try:
                    # Get trustee (user/group)
                    sid = ace[2]
                    name, domain, type = win32security.LookupAccountSid(None, sid)
                    
                    # Get permissions
                    mask = ace[1]
                    perms = []
                    
                    if mask & ntsecuritycon.FILE_ALL_ACCESS:
                        perms.append("Full Control")
                    else:
                        if mask & ntsecuritycon.FILE_GENERIC_READ:
                            perms.append("Read")
                        if mask & ntsecuritycon.FILE_GENERIC_WRITE:
                            perms.append("Write")
                        if mask & ntsecuritycon.FILE_GENERIC_EXECUTE:
                            perms.append("Execute")
                        if mask & ntsecuritycon.FILE_LIST_DIRECTORY:
                            perms.append("List")
                            
                    item = QTreeWidgetItem([
                        f"{domain}\\{name}",
                        "Group" if type == win32security.SidTypeGroup else "User",
                        ", ".join(perms)
                    ])
                    self.permissions_tree.addTopLevelItem(item)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to process ACE: {str(e)}")
                    
            self.permissions_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh permissions: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh permissions: {str(e)}")
            
    def add_permission(self):
        """Add a new permission."""
        try:
            if not self.current_path:
                QMessageBox.warning(self, "Warning", "Please select a file or folder first")
                return
                
            dialog = AddPermissionDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                # Get security descriptor
                sd = win32security.GetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION
                )
                
                # Get DACL
                dacl = sd.GetSecurityDescriptorDacl()
                if dacl is None:
                    dacl = win32security.ACL()
                    
                # Get SID for user/group
                try:
                    domain, _, type = win32security.LookupAccountName(None, data["name"])
                except:
                    QMessageBox.warning(self, "Warning", f"User or group '{data['name']}' not found")
                    return
                    
                # Add ACE
                dacl.AddAccessAllowedAce(
                    win32security.ACL_REVISION,
                    data["mask"],
                    domain
                )
                
                # Set DACL
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION,
                    sd
                )
                
                self.logger.info(f"Added permission for {data['name']} on {self.current_path}")
                self.refresh_permissions()
                
        except Exception as e:
            self.logger.error(f"Failed to add permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add permission: {str(e)}")
            
    def edit_permission(self):
        """Edit the selected permission."""
        try:
            current_item = self.permissions_tree.currentItem()
            if not current_item or not self.current_path:
                return
                
            # Get current permissions
            name = current_item.text(0)
            dialog = AddPermissionDialog(self)
            dialog.name_edit.setText(name)
            dialog.name_edit.setEnabled(False)  # Can't change user/group
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                data = dialog.get_permission_data()
                
                # Get security descriptor
                sd = win32security.GetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION
                )
                
                # Get DACL
                dacl = sd.GetSecurityDescriptorDacl()
                if dacl is None:
                    return
                    
                # Get SID for user/group
                try:
                    domain = win32security.LookupAccountName(None, name)[0]
                except:
                    QMessageBox.warning(self, "Warning", f"User or group '{name}' not found")
                    return
                    
                # Find and replace ACE
                for i in range(dacl.GetAceCount()):
                    ace = dacl.GetAce(i)
                    sid = ace[2]
                    if sid == domain:
                        dacl.DeleteAce(i)
                        dacl.AddAccessAllowedAce(
                            win32security.ACL_REVISION,
                            data["mask"],
                            domain
                        )
                        break
                        
                # Set DACL
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION,
                    sd
                )
                
                self.logger.info(f"Updated permission for {name} on {self.current_path}")
                self.refresh_permissions()
                
        except Exception as e:
            self.logger.error(f"Failed to edit permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit permission: {str(e)}")
            
    def remove_permission(self):
        """Remove the selected permission."""
        try:
            current_item = self.permissions_tree.currentItem()
            if not current_item or not self.current_path:
                return
                
            name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove permissions for '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Get security descriptor
                sd = win32security.GetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION
                )
                
                # Get DACL
                dacl = sd.GetSecurityDescriptorDacl()
                if dacl is None:
                    return
                    
                # Get SID for user/group
                try:
                    domain = win32security.LookupAccountName(None, name)[0]
                except:
                    QMessageBox.warning(self, "Warning", f"User or group '{name}' not found")
                    return
                    
                # Find and remove ACE
                for i in range(dacl.GetAceCount()):
                    ace = dacl.GetAce(i)
                    sid = ace[2]
                    if sid == domain:
                        dacl.DeleteAce(i)
                        break
                        
                # Set DACL
                sd.SetSecurityDescriptorDacl(1, dacl, 0)
                win32security.SetFileSecurity(
                    self.current_path,
                    win32security.DACL_SECURITY_INFORMATION,
                    sd
                )
                
                self.logger.info(f"Removed permission for {name} on {self.current_path}")
                self.refresh_permissions()
                
        except Exception as e:
            self.logger.error(f"Failed to remove permission: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove permission: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
