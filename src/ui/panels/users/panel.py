"""Users and groups management panel."""
import win32net
import win32netcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTabWidget, QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import UsersTree, GroupsTree
from .dialogs import AddUserDialog, AddGroupDialog

class UsersPanel(BasePanel):
    """Panel for managing users and groups."""
    
    def __init__(self, main_window):
        """Initialize users panel.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        # Initialize UI and load data
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Call parent setup_ui first
        super().setup_ui()
        layout = QVBoxLayout(self)
        
        # Create tab widget for users and groups
        self.tab_widget = QTabWidget()
        layout.addWidget(self.tab_widget)
        
        # Users tab
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        
        self.users_tree = UsersTree()
        users_layout.addWidget(self.users_tree)
        
        users_buttons = QHBoxLayout()
        
        add_user_button = QPushButton("Add User")
        add_user_button.clicked.connect(self.add_user)
        users_buttons.addWidget(add_user_button)
        
        edit_user_button = QPushButton("Edit User")
        edit_user_button.clicked.connect(self.edit_user)
        users_buttons.addWidget(edit_user_button)
        
        delete_user_button = QPushButton("Delete User")
        delete_user_button.clicked.connect(self.delete_user)
        users_buttons.addWidget(delete_user_button)
        
        refresh_users_button = QPushButton("Refresh")
        refresh_users_button.clicked.connect(self.refresh_lists)
        users_buttons.addWidget(refresh_users_button)
        
        users_layout.addLayout(users_buttons)
        
        self.tab_widget.addTab(users_widget, "Users")
        
        # Groups tab
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        
        self.groups_tree = GroupsTree()
        groups_layout.addWidget(self.groups_tree)
        
        groups_buttons = QHBoxLayout()
        
        add_group_button = QPushButton("Add Group")
        add_group_button.clicked.connect(self.add_group)
        groups_buttons.addWidget(add_group_button)
        
        edit_group_button = QPushButton("Edit Group")
        edit_group_button.clicked.connect(self.edit_group)
        groups_buttons.addWidget(edit_group_button)
        
        delete_group_button = QPushButton("Delete Group")
        delete_group_button.clicked.connect(self.delete_group)
        groups_buttons.addWidget(delete_group_button)
        
        refresh_groups_button = QPushButton("Refresh")
        refresh_groups_button.clicked.connect(self.refresh_lists)
        groups_buttons.addWidget(refresh_groups_button)
        
        groups_layout.addLayout(groups_buttons)
        
        self.tab_widget.addTab(groups_widget, "Groups")
        
    def add_user(self):
        """Add a new user account."""
        dialog = AddUserDialog(self)
        if dialog.exec():
            username, password, full_name, description, disabled = dialog.get_user()
            try:
                # Prepare user info
                user_info = {
                    'name': username,
                    'password': password,
                    'comment': description,
                    'full_name': full_name,
                    'flags': (win32netcon.UF_NORMAL_ACCOUNT |
                            win32netcon.UF_SCRIPT |
                            (win32netcon.UF_ACCOUNTDISABLE if disabled else 0))
                }
                
                # Create user
                win32net.NetUserAdd(None, 1, user_info)
                
                # Add to tree
                self.users_tree.add_user(
                    username,
                    full_name,
                    description,
                    disabled
                )
                self.logger.info(f"Added user account: {username}")
                
            except Exception as e:
                self.logger.error(f"Failed to add user account: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add user account: {str(e)}"
                )
                
    def edit_user(self):
        """Edit selected user account."""
        item = self.users_tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a user to edit."
            )
            return
            
        username, full_name, description, disabled = self.users_tree.get_user(item)
        dialog = AddUserDialog(self, username, full_name, description, disabled)
        
        if dialog.exec():
            new_username, password, new_full_name, new_description, new_disabled = dialog.get_user()
            try:
                # Get current user info
                user_info = win32net.NetUserGetInfo(None, username, 1)
                
                # Update fields
                user_info['name'] = new_username
                if password:
                    user_info['password'] = password
                user_info['full_name'] = new_full_name
                user_info['comment'] = new_description
                user_info['flags'] = (win32netcon.UF_NORMAL_ACCOUNT |
                                  win32netcon.UF_SCRIPT |
                                  (win32netcon.UF_ACCOUNTDISABLE if new_disabled else 0))
                
                # Update user
                win32net.NetUserSetInfo(None, username, 1, user_info)
                
                # Update tree
                self.users_tree.update_user(
                    item,
                    new_username,
                    new_full_name,
                    new_description,
                    new_disabled
                )
                self.logger.info(f"Updated user account: {username}")
                
            except Exception as e:
                self.logger.error(f"Failed to update user account: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update user account: {str(e)}"
                )
                
    def delete_user(self):
        """Delete selected user account."""
        item = self.users_tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a user to delete."
            )
            return
            
        username, _, _, _ = self.users_tree.get_user(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                win32net.NetUserDel(None, username)
                self.users_tree.takeTopLevelItem(
                    self.users_tree.indexOfTopLevelItem(item)
                )
                self.logger.info(f"Deleted user account: {username}")
                
            except Exception as e:
                self.logger.error(f"Failed to delete user account: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete user account: {str(e)}"
                )
                
    def add_group(self):
        """Add a new user group."""
        # Get list of users for member selection
        users = []
        try:
            resume = 0
            while True:
                user_list, _, resume = win32net.NetUserEnum(
                    None, 0, win32netcon.FILTER_NORMAL_ACCOUNT, resume
                )
                users.extend([user['name'] for user in user_list])
                if not resume:
                    break
        except Exception as e:
            self.logger.error(f"Failed to enumerate users: {str(e)}")
            users = []
            
        dialog = AddGroupDialog(self, available_users=users)
        if dialog.exec():
            name, description, members = dialog.get_group()
            try:
                # Create group
                group_info = {
                    'name': name,
                    'comment': description
                }
                win32net.NetLocalGroupAdd(None, 1, group_info)
                
                # Add members
                for member in members:
                    member_info = {'domainandname': member}
                    win32net.NetLocalGroupAddMembers(
                        None, name, 3, [member_info]
                    )
                    
                # Add to tree
                self.groups_tree.add_group(name, description, members)
                self.logger.info(f"Added group: {name}")
                
            except Exception as e:
                self.logger.error(f"Failed to add group: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add group: {str(e)}"
                )
                
    def edit_group(self):
        """Edit selected user group."""
        item = self.groups_tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a group to edit."
            )
            return
            
        name, description, members = self.groups_tree.get_group(item)
        
        # Get list of users for member selection
        users = []
        try:
            resume = 0
            while True:
                user_list, _, resume = win32net.NetUserEnum(
                    None, 0, win32netcon.FILTER_NORMAL_ACCOUNT, resume
                )
                users.extend([user['name'] for user in user_list])
                if not resume:
                    break
        except Exception as e:
            self.logger.error(f"Failed to enumerate users: {str(e)}")
            users = []
            
        dialog = AddGroupDialog(self, name, description, members, users)
        
        if dialog.exec():
            new_name, new_description, new_members = dialog.get_group()
            try:
                # Update group
                group_info = {
                    'name': new_name,
                    'comment': new_description
                }
                win32net.NetLocalGroupSetInfo(None, name, 1, group_info)
                
                # Update members
                try:
                    # Remove all current members
                    resume = 0
                    while True:
                        member_list, _, resume = win32net.NetLocalGroupGetMembers(
                            None, name, 3, resume
                        )
                        if member_list:
                            win32net.NetLocalGroupDelMembers(
                                None, name, [m['domainandname'] for m in member_list]
                            )
                        if not resume:
                            break
                except Exception:
                    pass  # Group might be empty
                    
                # Add new members
                for member in new_members:
                    member_info = {'domainandname': member}
                    win32net.NetLocalGroupAddMembers(
                        None, new_name, 3, [member_info]
                    )
                    
                # Update tree
                self.groups_tree.update_group(
                    item,
                    new_name,
                    new_description,
                    new_members
                )
                self.logger.info(f"Updated group: {name}")
                
            except Exception as e:
                self.logger.error(f"Failed to update group: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update group: {str(e)}"
                )
                
    def delete_group(self):
        """Delete selected user group."""
        item = self.groups_tree.currentItem()
        if not item:
            QMessageBox.warning(
                self,
                "No Selection",
                "Please select a group to delete."
            )
            return
            
        name, _, _ = self.groups_tree.get_group(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete group '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                win32net.NetLocalGroupDel(None, name)
                self.groups_tree.takeTopLevelItem(
                    self.groups_tree.indexOfTopLevelItem(item)
                )
                self.logger.info(f"Deleted group: {name}")
                
            except Exception as e:
                self.logger.error(f"Failed to delete group: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete group: {str(e)}"
                )
                
    def setup_connections(self):
        """Set up signal/slot connections."""
        # No additional connections needed
        pass
        
    def load_data(self):
        """Load or refresh panel data."""
        self.refresh_lists()
        
    def save_data(self):
        """Save panel data."""
        # No data to save
        pass
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        # No cleanup needed
        pass
        
    def refresh_lists(self):
        """Refresh users and groups lists."""
        try:
            # Clear trees
            self.users_tree.clear_users()
            self.groups_tree.clear_groups()
            
            # Enumerate users
            resume = 0
            while True:
                user_list, _, resume = win32net.NetUserEnum(
                    None, 1, win32netcon.FILTER_NORMAL_ACCOUNT, resume
                )
                for user in user_list:
                    self.users_tree.add_user(
                        user['name'],
                        user.get('full_name', ''),
                        user.get('comment', ''),
                        bool(user.get('flags', 0) & win32netcon.UF_ACCOUNTDISABLE)
                    )
                if not resume:
                    break
                    
            # Enumerate groups
            resume = 0
            while True:
                group_list, _, resume = win32net.NetLocalGroupEnum(None, 1, resume)
                for group in group_list:
                    # Get group members
                    members = []
                    try:
                        member_resume = 0
                        while True:
                            member_list, _, member_resume = win32net.NetLocalGroupGetMembers(
                                None, group['name'], 3, member_resume
                            )
                            members.extend([m['domainandname'] for m in member_list])
                            if not member_resume:
                                break
                    except Exception:
                        pass  # Group might be empty
                        
                    self.groups_tree.add_group(
                        group['name'],
                        group.get('comment', ''),
                        members
                    )
                if not resume:
                    break
                    
            self.logger.info("Refreshed users and groups lists")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh lists: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh lists: {str(e)}"
            )
            
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local user management when remote
