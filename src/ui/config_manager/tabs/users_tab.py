"""Users and Groups configuration tab."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLabel, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QCheckBox, QTabWidget)
from .base_tab import BaseConfigTab

class UsersTab(BaseConfigTab):
    """Tab for configuring users and groups."""
    def __init__(self, config_handler):
        super().__init__(config_handler, "users")
        
    def setup_ui(self):
        """Set up the tab's user interface."""
        # Create tabs for Users and Groups
        tabs = QTabWidget()
        
        # Users tab
        users_widget = QWidget()
        users_layout = QVBoxLayout(users_widget)
        
        # Users tree
        users_label = QLabel("Users to Create")
        users_layout.addWidget(users_label)
        
        self.users_tree = QTreeWidget()
        self.users_tree.setHeaderLabels([
            "Username", "Full Name", "Password", "Description", "Groups"
        ])
        self.users_tree.setColumnWidth(0, 150)
        self.users_tree.setColumnWidth(1, 150)
        self.users_tree.setColumnWidth(4, 200)
        users_layout.addWidget(self.users_tree)
        
        # User input fields
        user_input = QWidget()
        user_input_layout = QVBoxLayout(user_input)
        
        # Username
        username_layout = QHBoxLayout()
        username_label = QLabel("Username:")
        username_layout.addWidget(username_label)
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        user_input_layout.addLayout(username_layout)
        
        # Full Name
        fullname_layout = QHBoxLayout()
        fullname_label = QLabel("Full Name:")
        fullname_layout.addWidget(fullname_label)
        self.fullname_edit = QLineEdit()
        fullname_layout.addWidget(self.fullname_edit)
        user_input_layout.addLayout(fullname_layout)
        
        # Password
        password_layout = QHBoxLayout()
        password_label = QLabel("Password:")
        password_layout.addWidget(password_label)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        user_input_layout.addLayout(password_layout)
        
        # Description
        description_layout = QHBoxLayout()
        description_label = QLabel("Description:")
        description_layout.addWidget(description_label)
        self.description_edit = QLineEdit()
        description_layout.addWidget(self.description_edit)
        user_input_layout.addLayout(description_layout)
        
        # Groups
        groups_layout = QHBoxLayout()
        groups_label = QLabel("Groups:")
        groups_layout.addWidget(groups_label)
        self.groups_edit = QLineEdit()
        self.groups_edit.setPlaceholderText("Comma-separated list of groups")
        groups_layout.addWidget(self.groups_edit)
        user_input_layout.addLayout(groups_layout)
        
        users_layout.addWidget(user_input)
        
        # User buttons
        user_buttons = QHBoxLayout()
        add_user = QPushButton("Add User")
        add_user.clicked.connect(self.add_user)
        user_buttons.addWidget(add_user)
        
        delete_user = QPushButton("Delete User")
        delete_user.clicked.connect(self.delete_user)
        user_buttons.addWidget(delete_user)
        
        users_layout.addLayout(user_buttons)
        tabs.addTab(users_widget, "Users")
        
        # Groups tab
        groups_widget = QWidget()
        groups_layout = QVBoxLayout(groups_widget)
        
        # Groups tree
        groups_label = QLabel("Groups to Create")
        groups_layout.addWidget(groups_label)
        
        self.groups_tree = QTreeWidget()
        self.groups_tree.setHeaderLabels(["Group Name", "Description", "Members"])
        self.groups_tree.setColumnWidth(0, 150)
        self.groups_tree.setColumnWidth(2, 200)
        groups_layout.addWidget(self.groups_tree)
        
        # Group input fields
        group_input = QWidget()
        group_input_layout = QVBoxLayout(group_input)
        
        # Group name
        group_name_layout = QHBoxLayout()
        group_name_label = QLabel("Group Name:")
        group_name_layout.addWidget(group_name_label)
        self.group_name_edit = QLineEdit()
        group_name_layout.addWidget(self.group_name_edit)
        group_input_layout.addLayout(group_name_layout)
        
        # Group description
        group_desc_layout = QHBoxLayout()
        group_desc_label = QLabel("Description:")
        group_desc_layout.addWidget(group_desc_label)
        self.group_desc_edit = QLineEdit()
        group_desc_layout.addWidget(self.group_desc_edit)
        group_input_layout.addLayout(group_desc_layout)
        
        # Group members
        members_layout = QHBoxLayout()
        members_label = QLabel("Members:")
        members_layout.addWidget(members_label)
        self.members_edit = QLineEdit()
        self.members_edit.setPlaceholderText("Comma-separated list of users")
        members_layout.addWidget(self.members_edit)
        group_input_layout.addLayout(members_layout)
        
        groups_layout.addWidget(group_input)
        
        # Group buttons
        group_buttons = QHBoxLayout()
        add_group = QPushButton("Add Group")
        add_group.clicked.connect(self.add_group)
        group_buttons.addWidget(add_group)
        
        delete_group = QPushButton("Delete Group")
        delete_group.clicked.connect(self.delete_group)
        group_buttons.addWidget(delete_group)
        
        groups_layout.addLayout(group_buttons)
        tabs.addTab(groups_widget, "Groups")
        
        self.layout.addWidget(tabs)
        
    def add_user(self):
        """Add a user to the tree."""
        username = self.username_edit.text().strip()
        fullname = self.fullname_edit.text().strip()
        password = self.password_edit.text()
        description = self.description_edit.text().strip()
        groups = [g.strip() for g in self.groups_edit.text().split(",") if g.strip()]
        
        if not username:
            QMessageBox.warning(self, "Warning", "Username is required.")
            return
            
        if not password:
            QMessageBox.warning(self, "Warning", "Password is required.")
            return
            
        item = QTreeWidgetItem([
            username,
            fullname,
            "*" * len(password),  # Don't show actual password
            description,
            ", ".join(groups)
        ])
        item.password = password  # Store actual password
        self.users_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.username_edit.clear()
        self.fullname_edit.clear()
        self.password_edit.clear()
        self.description_edit.clear()
        self.groups_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_user(self):
        """Delete selected user."""
        item = self.users_tree.currentItem()
        if item:
            self.users_tree.takeTopLevelItem(
                self.users_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def add_group(self):
        """Add a group to the tree."""
        name = self.group_name_edit.text().strip()
        description = self.group_desc_edit.text().strip()
        members = [m.strip() for m in self.members_edit.text().split(",") if m.strip()]
        
        if not name:
            QMessageBox.warning(self, "Warning", "Group name is required.")
            return
            
        item = QTreeWidgetItem([
            name,
            description,
            ", ".join(members)
        ])
        self.groups_tree.addTopLevelItem(item)
        
        # Clear input fields
        self.group_name_edit.clear()
        self.group_desc_edit.clear()
        self.members_edit.clear()
        
        self.update_config_from_ui()
        
    def delete_group(self):
        """Delete selected group."""
        item = self.groups_tree.currentItem()
        if item:
            self.groups_tree.takeTopLevelItem(
                self.groups_tree.indexOfTopLevelItem(item)
            )
            self.update_config_from_ui()
            
    def update_config_from_ui(self):
        """Update configuration from UI elements."""
        config = {
            "create": [],
            "groups": []
        }
        
        # Get users
        for i in range(self.users_tree.topLevelItemCount()):
            item = self.users_tree.topLevelItem(i)
            config["create"].append({
                "username": item.text(0),
                "fullname": item.text(1),
                "password": getattr(item, "password", ""),  # Get actual password
                "description": item.text(3),
                "groups": [g.strip() for g in item.text(4).split(",") if g.strip()]
            })
            
        # Get groups
        for i in range(self.groups_tree.topLevelItemCount()):
            item = self.groups_tree.topLevelItem(i)
            config["groups"].append({
                "name": item.text(0),
                "description": item.text(1),
                "members": [m.strip() for m in item.text(2).split(",") if m.strip()]
            })
            
        self.update_config(config)
        
    def on_config_changed(self):
        """Handle configuration changes."""
        config = self.get_config()
        
        # Clear existing items
        self.users_tree.clear()
        self.groups_tree.clear()
        
        # Add users
        for user in config.get("create", []):
            item = QTreeWidgetItem([
                user["username"],
                user.get("fullname", ""),
                "*" * len(user["password"]),
                user.get("description", ""),
                ", ".join(user.get("groups", []))
            ])
            item.password = user["password"]  # Store actual password
            self.users_tree.addTopLevelItem(item)
            
        # Add groups
        for group in config.get("groups", []):
            item = QTreeWidgetItem([
                group["name"],
                group.get("description", ""),
                ", ".join(group.get("members", []))
            ])
            self.groups_tree.addTopLevelItem(item)
