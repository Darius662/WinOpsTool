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
