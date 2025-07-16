"""Users and groups management panel."""
import win32netcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTabWidget, QMessageBox)
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import UsersTree, GroupsTree
from .dialogs import AddUserDialog, AddGroupDialog
from .manager import UserManager, GroupManager

class UsersPanel(BasePanel):
    """Panel for managing users and groups."""
    
    def __init__(self, main_window):
        """Initialize users panel.
        
        Args:
            main_window: MainWindow instance
        """
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Initialize managers
        self.user_manager = UserManager()
        self.group_manager = GroupManager()
        
        # Initialize UI and load data
        self.setup_ui()
        self.setup_connections()
        self.load_data()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create tab widget for users and groups
        self.tab_widget = QTabWidget()
        self.add_widget(self.tab_widget)
        
        # Users tab
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        
        self.users_tree = UsersTree()
        users_layout.addWidget(self.users_tree)
        
        users_buttons = QHBoxLayout()
        
        self.add_user_button = QPushButton("Add User")
        users_buttons.addWidget(self.add_user_button)
        
        self.edit_user_button = QPushButton("Edit User")
        users_buttons.addWidget(self.edit_user_button)
        
        self.delete_user_button = QPushButton("Delete User")
        users_buttons.addWidget(self.delete_user_button)
        
        self.refresh_users_button = QPushButton("Refresh")
        users_buttons.addWidget(self.refresh_users_button)
        
        users_layout.addLayout(users_buttons)
        
        self.tab_widget.addTab(users_widget, "Users")
        
        # Groups tab
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        
        self.groups_tree = GroupsTree()
        groups_layout.addWidget(self.groups_tree)
        
        groups_buttons = QHBoxLayout()
        
        self.add_group_button = QPushButton("Add Group")
        groups_buttons.addWidget(self.add_group_button)
        
        self.edit_group_button = QPushButton("Edit Group")
        groups_buttons.addWidget(self.edit_group_button)
        
        self.delete_group_button = QPushButton("Delete Group")
        groups_buttons.addWidget(self.delete_group_button)
        
        self.refresh_groups_button = QPushButton("Refresh")
        groups_buttons.addWidget(self.refresh_groups_button)
        
        groups_layout.addLayout(groups_buttons)
        
        self.tab_widget.addTab(groups_widget, "Groups")
        
    def add_user(self):
        """Add a new user account."""
        dialog = AddUserDialog(self)
        if dialog.exec():
            username, password, full_name, description, disabled = dialog.get_user()
            if self.user_manager.add_user(username, password, full_name, description, disabled):
                # Add to tree
                self.users_tree.add_user(
                    username,
                    full_name,
                    description,
                    disabled
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add user: {username}"
                )
                
    def edit_user(self):
        """Edit selected user account."""
        item = self.users_tree.currentItem()
        if not item:
            return
            
        username, full_name, description, disabled = self.users_tree.get_user(item)
        
        dialog = AddUserDialog(
            self,
            username=username,
            full_name=full_name,
            description=description,
            disabled=disabled
        )
        
        if dialog.exec():
            _, password, new_full_name, new_description, new_disabled = dialog.get_user()
            if self.user_manager.update_user(
                username,
                password=password if password else None,
                full_name=new_full_name,
                description=new_description,
                disabled=new_disabled
            ):
                # Update tree
                self.users_tree.update_user(
                    item,
                    full_name=new_full_name,
                    description=new_description,
                    disabled=new_disabled
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update user: {username}"
                )
                
    def delete_user(self):
        """Delete selected user account."""
        item = self.users_tree.currentItem()
        if not item:
            return
            
        username, _, _, _ = self.users_tree.get_user(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete user '{username}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.user_manager.delete_user(username):
                self.users_tree.takeTopLevelItem(
                    self.users_tree.indexOfTopLevelItem(item)
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete user: {username}"
                )
                
    def add_group(self):
        """Add a new user group."""
        # Get list of users for member selection
        users = [user['name'] for user in self.user_manager.get_users()]
            
        dialog = AddGroupDialog(self, available_users=users)
        if dialog.exec():
            name, description, members = dialog.get_group()
            if self.group_manager.add_group(name, description, members):
                # Add to tree
                self.groups_tree.add_group(
                    name,
                    description,
                    members
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to add group: {name}"
                )
                
    def edit_group(self):
        """Edit selected user group."""
        item = self.groups_tree.currentItem()
        if not item:
            return
            
        name, description, current_members = self.groups_tree.get_group(item)
        
        # Get list of users for member selection
        users = [user['name'] for user in self.user_manager.get_users()]
            
        dialog = AddGroupDialog(
            self,
            name=name,
            description=description,
            members=current_members,
            available_users=users
        )
        
        if dialog.exec():
            _, new_description, new_members = dialog.get_group()
            if self.group_manager.update_group(name, new_description, new_members):
                # Update tree
                self.groups_tree.update_group(
                    item,
                    description=new_description,
                    members=new_members
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to update group: {name}"
                )
                
    def delete_group(self):
        """Delete selected user group."""
        item = self.groups_tree.currentItem()
        if not item:
            return
            
        name, _, _ = self.groups_tree.get_group(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete group '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.group_manager.delete_group(name):
                self.groups_tree.takeTopLevelItem(
                    self.groups_tree.indexOfTopLevelItem(item)
                )
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to delete group: {name}"
                )
                
    def setup_connections(self):
        """Set up signal/slot connections."""
        # User tab connections
        self.add_user_button.clicked.connect(self.add_user)
        self.edit_user_button.clicked.connect(self.edit_user)
        self.delete_user_button.clicked.connect(self.delete_user)
        self.refresh_users_button.clicked.connect(self.refresh_lists)
        
        # Group tab connections
        self.add_group_button.clicked.connect(self.add_group)
        self.edit_group_button.clicked.connect(self.edit_group)
        self.delete_group_button.clicked.connect(self.delete_group)
        self.refresh_groups_button.clicked.connect(self.refresh_lists)
        
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
            
            # Refresh users
            for user in self.user_manager.get_users():
                self.users_tree.add_user(
                    user['name'],
                    user.get('full_name', ''),
                    user.get('comment', ''),
                    bool(user.get('flags', 0) & win32netcon.UF_ACCOUNTDISABLE)
                )
                    
            # Refresh groups
            for group in self.group_manager.get_groups():
                self.groups_tree.add_group(
                    group['name'],
                    group.get('comment', ''),
                    group.get('members', [])
                )
                    
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
