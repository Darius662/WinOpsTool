"""Tree widgets for users and groups."""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger

class UsersTree(QTreeWidget):
    """Tree widget for displaying user accounts."""
    
    def __init__(self, parent=None):
        """Initialize users tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setHeaderLabels([
            "Username",
            "Full Name",
            "Description",
            "Status"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 150)  # Username
        self.setColumnWidth(1, 200)  # Full Name
        self.setColumnWidth(2, 250)  # Description
        self.setColumnWidth(3, 100)  # Status
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_user(self, username, full_name, description, disabled=False):
        """Add a user account to the tree.
        
        Args:
            username: Username
            full_name: Full name
            description: Account description
            disabled: Whether account is disabled
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        status = "Disabled" if disabled else "Enabled"
        item = QTreeWidgetItem([
            username,
            full_name,
            description,
            status
        ])
        self.addTopLevelItem(item)
        return item
        
    def update_user(self, item, username=None, full_name=None,
                  description=None, disabled=None):
        """Update an existing user account.
        
        Args:
            item: QTreeWidgetItem to update
            username: New username (optional)
            full_name: New full name (optional)
            description: New description (optional)
            disabled: New disabled state (optional)
        """
        if username is not None:
            item.setText(0, username)
        if full_name is not None:
            item.setText(1, full_name)
        if description is not None:
            item.setText(2, description)
        if disabled is not None:
            item.setText(3, "Disabled" if disabled else "Enabled")
            
    def get_user(self, item):
        """Get user account details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            tuple: (username, full_name, description, disabled)
        """
        return (
            item.text(0),  # username
            item.text(1),  # full_name
            item.text(2),  # description
            item.text(3) == "Disabled"  # disabled
        )
        
    def clear_users(self):
        """Clear all user accounts from the tree."""
        self.clear()
        
class GroupsTree(QTreeWidget):
    """Tree widget for displaying user groups."""
    
    def __init__(self, parent=None):
        """Initialize groups tree.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the tree widget UI."""
        self.setHeaderLabels([
            "Name",
            "Description",
            "Members"
        ])
        
        # Set column widths
        self.setColumnWidth(0, 200)  # Name
        self.setColumnWidth(1, 300)  # Description
        self.setColumnWidth(2, 200)  # Members
        
        # Enable sorting
        self.setSortingEnabled(True)
        self.sortByColumn(0, Qt.SortOrder.AscendingOrder)
        
    def add_group(self, name, description, members=None):
        """Add a user group to the tree.
        
        Args:
            name: Group name
            description: Group description
            members: List of member usernames
            
        Returns:
            QTreeWidgetItem: Created tree item
        """
        members_str = ", ".join(members) if members else ""
        item = QTreeWidgetItem([
            name,
            description,
            members_str
        ])
        self.addTopLevelItem(item)
        return item
        
    def update_group(self, item, name=None, description=None, members=None):
        """Update an existing user group.
        
        Args:
            item: QTreeWidgetItem to update
            name: New group name (optional)
            description: New description (optional)
            members: New list of member usernames (optional)
        """
        if name is not None:
            item.setText(0, name)
        if description is not None:
            item.setText(1, description)
        if members is not None:
            item.setText(2, ", ".join(members))
            
    def get_group(self, item):
        """Get group details from tree item.
        
        Args:
            item: QTreeWidgetItem to get details from
            
        Returns:
            tuple: (name, description, members)
        """
        return (
            item.text(0),  # name
            item.text(1),  # description
            [m.strip() for m in item.text(2).split(",") if m.strip()]  # members
        )
        
    def clear_groups(self):
        """Clear all groups from the tree."""
        self.clear()
