"""Users and Groups Management Panel."""
import win32net
import win32netcon
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QTabWidget,
                          QTreeWidget, QTreeWidgetItem, QMessageBox, QInputDialog,
                          QLineEdit, QDialog, QLabel, QCheckBox, QFormLayout)
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class UserDialog(QDialog):
    """Dialog for creating/editing users."""
    
    def __init__(self, parent=None, user_info=None):
        super().__init__(parent)
        self.user_info = user_info or {}
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        self.setWindowTitle("User Properties")
        layout = QFormLayout(self)
        
        # Username
        self.username = QLineEdit()
        if self.user_info.get('name'):
            self.username.setText(self.user_info['name'])
            self.username.setEnabled(False)
        layout.addRow("Username:", self.username)
        
        # Full name
        self.fullname = QLineEdit()
        self.fullname.setText(self.user_info.get('full_name', ''))
        layout.addRow("Full Name:", self.fullname)
        
        # Password
        self.password = QLineEdit()
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Password:", self.password)
        
        # Description
        self.description = QLineEdit()
        self.description.setText(self.user_info.get('comment', ''))
        layout.addRow("Description:", self.description)
        
        # Account options
        self.cant_change_pass = QCheckBox("User cannot change password")
        self.pass_never_expires = QCheckBox("Password never expires")
        self.account_disabled = QCheckBox("Account is disabled")
        
        if self.user_info:
            flags = self.user_info.get('flags', 0)
            self.cant_change_pass.setChecked(bool(flags & win32netcon.UF_PASSWD_CANT_CHANGE))
            self.pass_never_expires.setChecked(bool(flags & win32netcon.UF_DONT_EXPIRE_PASSWD))
            self.account_disabled.setChecked(bool(flags & win32netcon.UF_ACCOUNTDISABLE))
            
        layout.addRow(self.cant_change_pass)
        layout.addRow(self.pass_never_expires)
        layout.addRow(self.account_disabled)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.ok_button = QPushButton("OK")
        self.cancel_button = QPushButton("Cancel")
        
        self.ok_button.clicked.connect(self.accept)
        self.cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(self.ok_button)
        button_layout.addWidget(self.cancel_button)
        layout.addRow(button_layout)
        
    def get_user_info(self):
        """Get the user information from the dialog."""
        flags = 0
        if self.cant_change_pass.isChecked():
            flags |= win32netcon.UF_PASSWD_CANT_CHANGE
        if self.pass_never_expires.isChecked():
            flags |= win32netcon.UF_DONT_EXPIRE_PASSWD
        if self.account_disabled.isChecked():
            flags |= win32netcon.UF_ACCOUNTDISABLE
            
        return {
            'name': self.username.text(),
            'password': self.password.text(),
            'full_name': self.fullname.text(),
            'comment': self.description.text(),
            'flags': flags,
            'priv': win32netcon.USER_PRIV_USER
        }

class UsersPanel(BasePanel):
    """Panel for managing Windows users and groups."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create tabs
        self.tabs = QTabWidget()
        self.add_widget(self.tabs)
        
        # Users tab
        users_widget = QTreeWidget()
        users_widget.setHeaderLabels(["Username", "Full Name", "Description"])
        self.tabs.addTab(users_widget, "Users")
        self.users_tree = users_widget
        
        # Groups tab
        groups_widget = QTreeWidget()
        groups_widget.setHeaderLabels(["Group Name", "Description", "Members"])
        self.tabs.addTab(groups_widget, "Groups")
        self.groups_tree = groups_widget
        
        # Buttons for Users
        users_buttons = QHBoxLayout()
        self.add_user_btn = QPushButton("Add User")
        self.edit_user_btn = QPushButton("Edit User")
        self.delete_user_btn = QPushButton("Delete User")
        self.refresh_users_btn = QPushButton("Refresh")
        
        for btn in [self.add_user_btn, self.edit_user_btn, 
                   self.delete_user_btn, self.refresh_users_btn]:
            users_buttons.addWidget(btn)
            
        # Buttons for Groups
        groups_buttons = QHBoxLayout()
        self.add_group_btn = QPushButton("Add Group")
        self.edit_group_btn = QPushButton("Edit Group")
        self.delete_group_btn = QPushButton("Delete Group")
        self.refresh_groups_btn = QPushButton("Refresh")
        
        for btn in [self.add_group_btn, self.edit_group_btn,
                   self.delete_group_btn, self.refresh_groups_btn]:
            groups_buttons.addWidget(btn)
            
        # Add button layouts based on current tab
        self.button_layout = QHBoxLayout()
        self.add_layout(self.button_layout)
        
        # Connect signals
        self.tabs.currentChanged.connect(self.on_tab_changed)
        
        self.add_user_btn.clicked.connect(self.add_user)
        self.edit_user_btn.clicked.connect(self.edit_user)
        self.delete_user_btn.clicked.connect(self.delete_user)
        self.refresh_users_btn.clicked.connect(self.refresh_users)
        
        self.add_group_btn.clicked.connect(self.add_group)
        self.edit_group_btn.clicked.connect(self.edit_group)
        self.delete_group_btn.clicked.connect(self.delete_group)
        self.refresh_groups_btn.clicked.connect(self.refresh_groups)
        
        # Initial load
        self.on_tab_changed(0)
        self.refresh_users()
        self.refresh_groups()
        
    def on_tab_changed(self, index):
        """Handle tab change events."""
        # Clear existing buttons
        while self.button_layout.count():
            item = self.button_layout.takeAt(0)
            if item.widget():
                item.widget().hide()
                
        # Add appropriate buttons
        if index == 0:  # Users tab
            for btn in [self.add_user_btn, self.edit_user_btn,
                       self.delete_user_btn, self.refresh_users_btn]:
                self.button_layout.addWidget(btn)
                btn.show()
        else:  # Groups tab
            for btn in [self.add_group_btn, self.edit_group_btn,
                       self.delete_group_btn, self.refresh_groups_btn]:
                self.button_layout.addWidget(btn)
                btn.show()
                
    def refresh_users(self):
        """Refresh the users list."""
        try:
            self.users_tree.clear()
            resume = 0
            while True:
                users, _, resume = win32net.NetUserEnum(
                    None, 2, win32netcon.FILTER_NORMAL_ACCOUNT, resume
                )
                
                for user in users:
                    item = QTreeWidgetItem([
                        user['name'],
                        user.get('full_name', ''),
                        user.get('comment', '')
                    ])
                    self.users_tree.addTopLevelItem(item)
                    
                if not resume:
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to refresh users: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh users: {str(e)}")
            
    def refresh_groups(self):
        """Refresh the groups list."""
        try:
            self.groups_tree.clear()
            resume = 0
            while True:
                groups, _, resume = win32net.NetLocalGroupEnum(None, 1, resume)
                
                for group in groups:
                    try:
                        members, _ = win32net.NetLocalGroupGetMembers(None, group['name'], 1)
                        member_names = [member['name'] for member in members]
                    except:
                        member_names = []
                        
                    item = QTreeWidgetItem([
                        group['name'],
                        group.get('comment', ''),
                        ', '.join(member_names)
                    ])
                    self.groups_tree.addTopLevelItem(item)
                    
                if not resume:
                    break
                    
        except Exception as e:
            self.logger.error(f"Failed to refresh groups: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh groups: {str(e)}")
            
    def add_user(self):
        """Add a new user."""
        try:
            dialog = UserDialog(self)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                user_info = dialog.get_user_info()
                win32net.NetUserAdd(None, 1, user_info)
                self.refresh_users()
                self.logger.info(f"Added user: {user_info['name']}")
                
        except Exception as e:
            self.logger.error(f"Failed to add user: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add user: {str(e)}")
            
    def edit_user(self):
        """Edit the selected user."""
        try:
            current_item = self.users_tree.currentItem()
            if not current_item:
                return
                
            username = current_item.text(0)
            user_info = win32net.NetUserGetInfo(None, username, 2)
            
            dialog = UserDialog(self, user_info)
            if dialog.exec() == QDialog.DialogCode.Accepted:
                new_info = dialog.get_user_info()
                win32net.NetUserSetInfo(None, username, 2, new_info)
                self.refresh_users()
                self.logger.info(f"Updated user: {username}")
                
        except Exception as e:
            self.logger.error(f"Failed to edit user: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit user: {str(e)}")
            
    def delete_user(self):
        """Delete the selected user."""
        try:
            current_item = self.users_tree.currentItem()
            if not current_item:
                return
                
            username = current_item.text(0)
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the user '{username}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                win32net.NetUserDel(None, username)
                self.refresh_users()
                self.logger.info(f"Deleted user: {username}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete user: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete user: {str(e)}")
            
    def add_group(self):
        """Add a new group."""
        try:
            name, ok = QInputDialog.getText(self, "Add Group", "Group name:")
            if ok and name:
                description, ok = QInputDialog.getText(
                    self, "Add Group", "Group description:"
                )
                if ok:
                    group_info = {
                        'name': name,
                        'comment': description
                    }
                    win32net.NetLocalGroupAdd(None, 1, group_info)
                    self.refresh_groups()
                    self.logger.info(f"Added group: {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to add group: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add group: {str(e)}")
            
    def edit_group(self):
        """Edit the selected group."""
        try:
            current_item = self.groups_tree.currentItem()
            if not current_item:
                return
                
            group_name = current_item.text(0)
            description, ok = QInputDialog.getText(
                self,
                "Edit Group",
                "New description:",
                QLineEdit.EchoMode.Normal,
                current_item.text(1)
            )
            
            if ok:
                group_info = {
                    'name': group_name,
                    'comment': description
                }
                win32net.NetLocalGroupSetInfo(None, group_name, 1, group_info)
                self.refresh_groups()
                self.logger.info(f"Updated group: {group_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to edit group: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to edit group: {str(e)}")
            
    def delete_group(self):
        """Delete the selected group."""
        try:
            current_item = self.groups_tree.currentItem()
            if not current_item:
                return
                
            group_name = current_item.text(0)
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete the group '{group_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                win32net.NetLocalGroupDel(None, group_name)
                self.refresh_groups()
                self.logger.info(f"Deleted group: {group_name}")
                
        except Exception as e:
            self.logger.error(f"Failed to delete group: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to delete group: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
        
    def apply_remote(self, remote_pc):
        """Apply users and groups to remote PC."""
        try:
            # Get current selections
            selected_users = []
            selected_groups = []
            
            for item in self.users_list.selectedItems():
                selected_users.append(item.text())
                
            for item in self.groups_list.selectedItems():
                selected_groups.append(item.text())
                
            # Create groups on remote PC
            for group in selected_groups:
                try:
                    group_info = win32net.NetLocalGroupGetInfo(None, group, 1)
                    # Create group on remote PC
                    win32net.NetLocalGroupAdd(remote_pc.hostname, 1, {
                        'name': group_info['name'],
                        'comment': group_info['comment']
                    })
                    self.logger.info(f"Created group {group} on {remote_pc.name}")
                except Exception as e:
                    self.logger.error(f"Failed to create group {group} on {remote_pc.name}: {str(e)}")
                    
            # Create users on remote PC
            for user in selected_users:
                try:
                    user_info = win32net.NetUserGetInfo(None, user, 3)
                    # Create user on remote PC
                    win32net.NetUserAdd(remote_pc.hostname, 3, {
                        'name': user_info['name'],
                        'password': user_info['password'],
                        'comment': user_info['comment'],
                        'flags': user_info['flags'],
                        'priv': user_info['priv'],
                        'home_dir': user_info['home_dir'],
                        'script_path': user_info['script_path'],
                        'auth_flags': user_info['auth_flags']
                    })
                    self.logger.info(f"Created user {user} on {remote_pc.name}")
                    
                    # Add user to their groups
                    groups = win32net.NetUserGetLocalGroups(None, user)
                    for group in groups:
                        try:
                            win32net.NetLocalGroupAddMembers(remote_pc.hostname, group, 3, [{
                                'domainandname': f"{remote_pc.hostname}\\{user}"
                            }])
                        except Exception as e:
                            self.logger.error(f"Failed to add {user} to group {group} on {remote_pc.name}: {str(e)}")
                            
                except Exception as e:
                    self.logger.error(f"Failed to create user {user} on {remote_pc.name}: {str(e)}")
                    
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to apply users/groups to {remote_pc.name}: {str(e)}")
            return False
