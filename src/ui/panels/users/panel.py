"""Users and groups management panel."""
import win32netcon
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QTabWidget, QMessageBox, QSplitter, QLabel)
from PyQt6.QtCore import Qt, pyqtSlot
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import UsersTree, GroupsTree
from .dialogs import AddUserDialog, AddGroupDialog
from .manager import UserManager, GroupManager
from .components import DetailsView

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
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed.
        
        Override of BasePanel.cleanup to handle specific cleanup tasks.
        """
        # Clear references to UI elements to avoid memory leaks
        if hasattr(self, 'users_tree') and self.users_tree is not None:
            try:
                self.users_tree.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
        
        if hasattr(self, 'groups_tree') and self.groups_tree is not None:
            try:
                self.groups_tree.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        if hasattr(self, 'users_details_view') and self.users_details_view is not None:
            try:
                self.users_details_view.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        if hasattr(self, 'groups_details_view') and self.groups_details_view is not None:
            try:
                self.groups_details_view.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        # Call the parent class cleanup to clear the main layout
        # This should be called after clearing individual widgets
        super().cleanup()
    
    def setup_ui(self):
        """Set up the panel UI."""
        # Clear any existing layout if this is not the initial setup
        if hasattr(self, 'tab_widget') and self.tab_widget is not None:
            self.cleanup()
        
        # Create tab widget for users and groups
        self.tab_widget = QTabWidget()
        
        # Users tab
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        users_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a main container for users tab
        users_main_widget = QWidget()
        users_main_layout = QVBoxLayout(users_main_widget)
        users_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter for users tab
        users_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Users tree
        users_tree_container = QWidget()
        users_tree_layout = QVBoxLayout(users_tree_container)
        users_tree_layout.setContentsMargins(0, 0, 0, 0)
        
        users_tree_label = QLabel("Users")
        users_tree_layout.addWidget(users_tree_label)
        
        self.users_tree = UsersTree()
        users_tree_layout.addWidget(self.users_tree)
        
        # Right side - User details
        users_details_container = QWidget()
        users_details_layout = QVBoxLayout(users_details_container)
        users_details_layout.setContentsMargins(0, 0, 0, 0)
        
        users_details_label = QLabel("User Details")
        users_details_layout.addWidget(users_details_label)
        
        self.users_details_view = DetailsView()
        users_details_layout.addWidget(self.users_details_view)
        
        # Add containers to splitter
        users_splitter.addWidget(users_tree_container)
        users_splitter.addWidget(users_details_container)
        
        # Set splitter sizes (40% left, 60% right)
        users_splitter.setSizes([400, 600])
        
        # Add splitter to main layout with stretch
        users_main_layout.addWidget(users_splitter, 1)
        
        # Create button bar at the bottom
        users_buttons = QHBoxLayout()
        
        self.add_user_button = QPushButton("Add User")
        users_buttons.addWidget(self.add_user_button)
        
        self.edit_user_button = QPushButton("Edit User")
        users_buttons.addWidget(self.edit_user_button)
        
        self.delete_user_button = QPushButton("Delete User")
        users_buttons.addWidget(self.delete_user_button)
        
        self.refresh_users_button = QPushButton("Refresh")
        users_buttons.addWidget(self.refresh_users_button)
        
        # Add button bar to main layout without stretch
        users_main_layout.addLayout(users_buttons, 0)
        
        # Add main widget to users layout
        users_layout.addWidget(users_main_widget)
        
        self.tab_widget.addTab(users_widget, "Users")
        
        # Groups tab
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        groups_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create a main container for groups tab
        groups_main_widget = QWidget()
        groups_main_layout = QVBoxLayout(groups_main_widget)
        groups_main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create horizontal splitter for groups tab
        groups_splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Groups tree
        groups_tree_container = QWidget()
        groups_tree_layout = QVBoxLayout(groups_tree_container)
        groups_tree_layout.setContentsMargins(0, 0, 0, 0)
        
        groups_tree_label = QLabel("Groups")
        groups_tree_layout.addWidget(groups_tree_label)
        
        self.groups_tree = GroupsTree()
        groups_tree_layout.addWidget(self.groups_tree)
        
        # Right side - Group details
        groups_details_container = QWidget()
        groups_details_layout = QVBoxLayout(groups_details_container)
        groups_details_layout.setContentsMargins(0, 0, 0, 0)
        
        groups_details_label = QLabel("Group Details")
        groups_details_layout.addWidget(groups_details_label)
        
        self.groups_details_view = DetailsView()
        groups_details_layout.addWidget(self.groups_details_view)
        
        # Add containers to splitter
        groups_splitter.addWidget(groups_tree_container)
        groups_splitter.addWidget(groups_details_container)
        
        # Set splitter sizes (40% left, 60% right)
        groups_splitter.setSizes([400, 600])
        
        # Add splitter to main layout with stretch
        groups_main_layout.addWidget(groups_splitter, 1)
        
        # Create button bar at the bottom
        groups_buttons = QHBoxLayout()
        
        self.add_group_button = QPushButton("Add Group")
        groups_buttons.addWidget(self.add_group_button)
        
        self.edit_group_button = QPushButton("Edit Group")
        groups_buttons.addWidget(self.edit_group_button)
        
        self.delete_group_button = QPushButton("Delete Group")
        groups_buttons.addWidget(self.delete_group_button)
        
        self.refresh_groups_button = QPushButton("Refresh")
        groups_buttons.addWidget(self.refresh_groups_button)
        
        # Add button bar to main layout without stretch
        groups_main_layout.addLayout(groups_buttons, 0)
        
        # Add main widget to groups layout
        groups_layout.addWidget(groups_main_widget)
        
        self.tab_widget.addTab(groups_widget, "Groups")
        
        # Add tab widget to panel
        self.add_widget(self.tab_widget)
        
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
        self.users_tree.itemSelectionChanged.connect(self.on_user_selected)
        
        # Group tab connections
        self.add_group_button.clicked.connect(self.add_group)
        self.edit_group_button.clicked.connect(self.edit_group)
        self.delete_group_button.clicked.connect(self.delete_group)
        self.refresh_groups_button.clicked.connect(self.refresh_lists)
        self.groups_tree.itemSelectionChanged.connect(self.on_group_selected)
        
    def load_data(self):
        """Load or refresh panel data."""
        self.refresh_lists()
        
    def save_data(self):
        """Save panel data."""
        # No data to save
        pass
        
    # Cleanup method is now implemented above
    
    @pyqtSlot()
    def on_user_selected(self):
        """Handle user selection in the tree."""
        item = self.users_tree.currentItem()
        if item:
            username, full_name, description, disabled = self.users_tree.get_user(item)
            self.users_details_view.show_user_details(username, full_name, description, disabled)
        else:
            self.users_details_view.clear()
    
    @pyqtSlot()
    def on_group_selected(self):
        """Handle group selection in the tree."""
        item = self.groups_tree.currentItem()
        if item:
            name, description, members = self.groups_tree.get_group(item)
            self.groups_details_view.show_group_details(name, description, members)
        else:
            self.groups_details_view.clear()
        
    def refresh_lists(self):
        """Refresh users and groups lists."""
        try:
            # Clear existing lists
            self.users_tree.clear_users()
            self.groups_tree.clear_groups()
            
            # Get users and groups
            users = self.user_manager.get_users()
            groups = self.group_manager.get_groups()
            
            # Add users to tree
            for user in users:
                # Skip system accounts
                if user['name'].endswith('$'):
                    continue
                    
                # Check if this user was imported from configuration
                is_imported = self.is_imported_config_item(f"user:{user['name']}")
                
                # Add user to tree with highlighting if imported
                self.users_tree.add_user(
                    user['name'],
                    user.get('full_name', ''),
                    user.get('comment', ''),
                    bool(user.get('flags', 0) & win32netcon.UF_ACCOUNTDISABLE),
                    is_imported=is_imported
                )
                
            # Add groups to tree
            for group in groups:
                # Check if this group was imported from configuration
                is_imported = self.is_imported_config_item(f"group:{group['name']}")
                
                # Add group to tree with highlighting if imported
                self.groups_tree.add_group(
                    group['name'],
                    group.get('comment', ''),
                    group.get('members', []),
                    is_imported=is_imported
                )
                
            self.logger.info("Refreshed users and groups lists")
            
        except Exception as e:
            self.logger.error(f"Error refreshing users and groups lists: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Error refreshing users and groups lists: {str(e)}"
            )
            
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Enable/disable controls based on connection state
        self.setEnabled(not connected)  # Disable local user management when remote
        
    def apply_config(self, config):
        """Apply configuration to the panel.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if configuration was applied successfully, False otherwise
        """
        self.logger.info("Applying users and groups configuration")
        
        try:
            success = False
            
            # Process users configuration
            if 'users' in config and isinstance(config['users'], dict) and 'create' in config['users']:
                user_list = config['users']['create']
                if isinstance(user_list, list):
                    for user_config in user_list:
                        if not isinstance(user_config, dict):
                            continue
                            
                        # Check required fields
                        if 'username' not in user_config:
                            self.logger.warning("Skipping user without username")
                            continue
                            
                        username = user_config['username']
                        fullname = user_config.get('fullname', '')
                        description = user_config.get('description', '')
                        password = user_config.get('password', '')
                        groups = user_config.get('groups', [])
                        
                        # Check if user exists
                        user_exists = self.user_manager.user_exists(username)
                        
                        if user_exists:
                            # Update existing user
                            self.logger.info(f"Updating existing user: {username}")
                            result = self.user_manager.update_user(
                                username,
                                fullname=fullname,
                                description=description,
                                groups=groups
                            )
                            
                            if not result:
                                self.logger.warning(f"Failed to update user: {username}")
                        else:
                            # Create new user
                            self.logger.info(f"Creating new user: {username}")
                            result = self.user_manager.add_user(
                                username,
                                password=password,
                                fullname=fullname,
                                description=description,
                                groups=groups
                            )
                            
                            if not result:
                                self.logger.warning(f"Failed to create user: {username}")
                        
                        # Mark this user as imported from config for highlighting
                        if result:
                            self.mark_as_imported_config(f"user:{username}")
                        
                        success = success or result
            
            # Process groups configuration
            if 'users' in config and isinstance(config['users'], dict) and 'groups' in config['users']:
                group_list = config['users']['groups']
                if isinstance(group_list, list):
                    for group_config in group_list:
                        if not isinstance(group_config, dict):
                            continue
                            
                        # Check required fields
                        if 'name' not in group_config:
                            self.logger.warning("Skipping group without name")
                            continue
                            
                        name = group_config['name']
                        description = group_config.get('description', '')
                        members = group_config.get('members', [])
                        
                        # Check if group exists
                        group_exists = self.group_manager.group_exists(name)
                        
                        if group_exists:
                            # Update existing group
                            self.logger.info(f"Updating existing group: {name}")
                            result = self.group_manager.update_group(
                                name,
                                description=description,
                                members=members
                            )
                            
                            if not result:
                                self.logger.warning(f"Failed to update group: {name}")
                        else:
                            # Create new group
                            self.logger.info(f"Creating new group: {name}")
                            result = self.group_manager.add_group(
                                name,
                                description=description,
                                members=members
                            )
                            
                            if not result:
                                self.logger.warning(f"Failed to create group: {name}")
                        
                        # Mark this group as imported from config for highlighting
                        if result:
                            self.mark_as_imported_config(f"group:{name}")
                        
                        success = success or result
            
            # Refresh the view to show updated users and groups
            self.refresh_lists()
            return success
            
        except Exception as e:
            self.logger.error(f"Error applying users and groups configuration: {str(e)}")
            return False
            
    def export_config(self):
        """Export panel configuration.
        
        Returns:
            dict: Dictionary containing panel configuration
        """
        self.logger.info("Exporting users and groups configuration")
        
        try:
            config = {
                'users': [],
                'groups': []
            }
            
            # Export users (excluding built-in and system accounts)
            for user in self.user_manager.get_users():
                # Skip system accounts
                if user['name'].endswith('$') or user['name'] in ['Administrator', 'Guest', 'DefaultAccount']:
                    continue
                    
                user_config = {
                    'name': user['name'],
                    'full_name': user.get('full_name', ''),
                    'description': user.get('comment', ''),
                    'disabled': bool(user.get('flags', 0) & win32netcon.UF_ACCOUNTDISABLE)
                }
                
                config['users'].append(user_config)
                
            # Export groups (excluding built-in and system groups)
            for group in self.group_manager.get_groups():
                # Skip system groups
                if group['name'] in ['Administrators', 'Users', 'Guests', 'Power Users']:
                    continue
                    
                group_config = {
                    'name': group['name'],
                    'description': group.get('comment', ''),
                    'members': group.get('members', [])
                }
                
                config['groups'].append(group_config)
                
            return config
            
        except Exception as e:
            self.logger.error(f"Error exporting users and groups configuration: {str(e)}")
            return {'users': [], 'groups': []}

    def mark_config_items(self, config):
        """Mark items from configuration for highlighting without applying changes.
        
        This method identifies and marks users and groups from the configuration
        that would be created or modified by apply_config(), but does not actually
        apply any changes to the system. Items will be visually highlighted in the UI.
        
        Args:
            config: Dictionary containing configuration data
            
        Returns:
            bool: True if items were marked successfully, False otherwise
        """
        self.logger.info("Marking users and groups from configuration for highlighting")
        
        try:
            # Clear previous imported items
            self.imported_config_items.clear()
            
            if not isinstance(config, dict):
                self.logger.error("Invalid configuration format")
                return False
                
            # Extract users configuration
            users_config = config.get('users', {})
            
            if not users_config:
                self.logger.warning("No users configuration found")
                return True
                
            # Mark users to be created
            if 'create' in users_config and isinstance(users_config['create'], list):
                for user_config in users_config['create']:
                    if isinstance(user_config, dict):
                        # The config file uses 'username' key
                        username = user_config.get('username')
                        if username:
                            self.mark_as_imported_config(f"user:{username}")
                            self.logger.info(f"Marked user for creation: {username}")
            
            # Mark users to be modified
            if 'modify' in users_config and isinstance(users_config['modify'], list):
                for user_config in users_config['modify']:
                    if isinstance(user_config, dict) and 'username' in user_config:
                        username = user_config['username']
                        self.mark_as_imported_config(f"user:{username}")
                        self.logger.info(f"Marked user for modification: {username}")
            
            # Mark users to be deleted
            if 'delete' in users_config and isinstance(users_config['delete'], list):
                for username in users_config['delete']:
                    if isinstance(username, str):
                        self.mark_as_imported_config(f"user:{username}")
                        self.logger.info(f"Marked user for deletion: {username}")
            
            # Mark groups to be created or modified
            if 'groups' in users_config and isinstance(users_config['groups'], list):
                for group_config in users_config['groups']:
                    if isinstance(group_config, dict) and 'name' in group_config:
                        name = group_config['name']
                        self.mark_as_imported_config(f"group:{name}")
                        self.logger.info(f"Marked group: {name}")
            
            # Refresh the view to show highlighted users and groups
            self.refresh_lists()
            
            # Check if we need to create virtual entries for users/groups that don't exist yet
            self.add_virtual_entries_for_config(users_config)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error marking users and groups from configuration: {str(e)}")
            return False
            
    def add_virtual_entries_for_config(self, users_config):
        """Add virtual entries for users and groups that don't exist yet.
        
        This method adds entries to the UI for users and groups that are in the
        configuration but don't exist in the system yet.
        
        Args:
            users_config: Dictionary containing users configuration
        """
        try:
            # Add virtual entries for users to be created
            if 'create' in users_config and isinstance(users_config['create'], list):
                for user_config in users_config['create']:
                    if isinstance(user_config, dict):
                        username = user_config.get('username')
                        if username:
                            # Check if user already exists in the system
                            if not self.user_manager.user_exists(username):
                                # Add virtual entry for user
                                self.users_tree.add_user(
                                    username,
                                    user_config.get('fullname', ''),
                                    user_config.get('description', ''),
                                    False,  # Not disabled
                                    is_imported=True  # Mark as imported
                                )
                                self.logger.info(f"Added virtual entry for user: {username}")
            
            # Add virtual entries for groups to be created
            if 'groups' in users_config and isinstance(users_config['groups'], list):
                for group_config in users_config['groups']:
                    if isinstance(group_config, dict):
                        name = group_config.get('name')
                        if name:
                            # Check if group already exists in the system
                            if not self.group_manager.group_exists(name):
                                # Add virtual entry for group
                                self.groups_tree.add_group(
                                    name,
                                    group_config.get('description', ''),
                                    group_config.get('members', []),
                                    is_imported=True  # Mark as imported
                                )
                                self.logger.info(f"Added virtual entry for group: {name}")
                                
        except Exception as e:
            self.logger.error(f"Error adding virtual entries for configuration: {str(e)}")
