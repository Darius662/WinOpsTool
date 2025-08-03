"""Tree widget for displaying credentials in Windows Credential Manager style.

This module provides a tree widget that displays credentials in a categorized view,
similar to the Windows Credential Manager. Credentials are grouped into categories:
- Windows Credentials
- Certificate-Based Credentials
- Generic Credentials

The tree supports filtering, sorting, and selection of credentials.
"""
from PyQt6.QtWidgets import QTreeWidget, QTreeWidgetItem
from PyQt6.QtCore import Qt, pyqtSignal
from src.core.logger import setup_logger

class CredentialsTree(QTreeWidget):
    """Tree widget for displaying credentials in a categorized view.
    
    This tree widget organizes credentials into categories based on their type:
    - Windows Credentials: System credentials used by Windows services and applications
    - Certificate-Based Credentials: Credentials that use certificates for authentication
    - Generic Credentials: Other credential types that don't fit into the above categories
    
    Features:
    - Automatic categorization of credentials based on type
    - Filtering credentials by target name, username, or type
    - Sorting credentials within categories
    - Selection and emission of signals for selected credentials
    - Clear visual distinction between category headers and credential items
    """
    
    # Signal emitted when an item is selected
    item_selected = pyqtSignal(object)
    
    # Credential type categories
    CATEGORY_WINDOWS = "Windows Credentials"
    CATEGORY_CERTIFICATE = "Certificate-Based Credentials"
    CATEGORY_GENERIC = "Generic Credentials"
    
    def __init__(self, parent=None):
        """Initialize the credentials tree widget."""
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Set up columns
        self.setColumnCount(3)
        self.setHeaderLabels(["Target", "Username", "Type"])
        
        # Store all credentials for filtering
        self._all_items = []
        self._filter_text = ""
        
        # Create category items
        self._category_items = {}
        
        # Enable sorting
        self.setSortingEnabled(True)
        
        # Set selection behavior
        self.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)
        self.setSelectionBehavior(QTreeWidget.SelectionBehavior.SelectRows)
        
        # Set up appearance
        self.setAlternatingRowColors(True)
        self.setUniformRowHeights(True)
        self.setSortingEnabled(True)
        
        # Connect signals
        self.itemSelectionChanged.connect(self._on_selection_changed)
        
    def _on_selection_changed(self):
        """Handle selection changes."""
        selected_items = self.selectedItems()
        if selected_items:
            self.item_selected.emit(selected_items[0])
            
    def _ensure_category_exists(self, category):
        """Ensure a category item exists in the tree.
        
        Args:
            category: Category name
            
        Returns:
            QTreeWidgetItem: Category item
        """
        if category not in self._category_items:
            category_item = QTreeWidgetItem(self)
            category_item.setText(0, category)
            category_item.setFirstColumnSpanned(True)
            category_item.setExpanded(True)
            font = category_item.font(0)
            font.setBold(True)
            category_item.setFont(0, font)
            self._category_items[category] = category_item
        
        return self._category_items[category]
    
    def _get_category_for_credential_type(self, credential_type):
        """Get the category for a credential type.
        
        Args:
            credential_type: Credential type
            
        Returns:
            str: Category name
        """
        credential_type = credential_type.lower()
        
        if "windows" in credential_type:
            return self.CATEGORY_WINDOWS
        elif "certificate" in credential_type:
            return self.CATEGORY_CERTIFICATE
        else:
            return self.CATEGORY_GENERIC
    
    def add_credential(self, target_name, username, credential_type):
        """Add a credential to the tree.
        
        Args:
            target_name: Target name of the credential
            username: Username
            credential_type: Type of credential
            
        Returns:
            QTreeWidgetItem: The added item
        """
        # Get or create category item
        category = self._get_category_for_credential_type(credential_type)
        category_item = self._ensure_category_exists(category)
        
        # Create credential item under category
        item = QTreeWidgetItem(category_item)
        item.setText(0, target_name)
        item.setText(1, username)
        item.setText(2, credential_type)
        
        # Store data for retrieval
        item.setData(0, Qt.ItemDataRole.UserRole, target_name)
        
        # Store item for filtering
        self._all_items.append((item, target_name.lower(), username.lower(), credential_type.lower(), category))
        
        # Apply current filter
        if self._filter_text and not self._item_matches_filter(target_name, username, credential_type):
            category_item.removeChild(item)
        
        # Sort items
        self.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        return item
        
    def clear_credentials(self):
        """Clear all credentials from the tree."""
        self.clear()
        self._all_items = []
        self._category_items = {}
        self._filter_text = ""
        
    def filter_credentials(self, filter_text):
        """Filter credentials by text.
        
        Args:
            filter_text: Text to filter by
        """
        self._filter_text = filter_text.lower()
        
        # Clear current items
        self.clear()
        self._category_items = {}
        
        # Add matching items
        for item, target, username, cred_type, category in self._all_items:
            if not filter_text or self._text_matches(target, username, cred_type):
                # Get or create category item
                category_item = self._ensure_category_exists(category)
                
                # Create a new item with the same data under the category
                new_item = QTreeWidgetItem(category_item)
                new_item.setText(0, item.text(0))
                new_item.setText(1, item.text(1))
                new_item.setText(2, item.text(2))
                
                # Store data for retrieval
                new_item.setData(0, Qt.ItemDataRole.UserRole, item.text(0))
        
        # Sort items
        self.sortItems(0, Qt.SortOrder.AscendingOrder)
        
        # Remove empty categories
        for category, category_item in list(self._category_items.items()):
            if category_item.childCount() == 0:
                self.invisibleRootItem().removeChild(category_item)
                del self._category_items[category]
        
    def _text_matches(self, target, username, cred_type):
        """Check if item matches the filter text.
        
        Args:
            target: Target name (lowercase)
            username: Username (lowercase)
            cred_type: Credential type (lowercase)
            
        Returns:
            bool: True if matches, False otherwise
        """
        return (self._filter_text in target or 
                self._filter_text in username or 
                self._filter_text in cred_type)
                
    def _item_matches_filter(self, target_name, username, credential_type):
        """Check if item matches the current filter.
        
        Args:
            target_name: Target name
            username: Username
            credential_type: Credential type
            
        Returns:
            bool: True if matches, False otherwise
        """
        if not self._filter_text:
            return True
            
        target = target_name.lower()
        username = username.lower()
        cred_type = credential_type.lower()
        
        return self._text_matches(target, username, cred_type)
        
    def update_credential(self, item, target_name=None, username=None, credential_type=None):
        """Update a credential item.
        
        Args:
            item: QTreeWidgetItem to update
            target_name: New target name (optional)
            username: New username (optional)
            credential_type: New credential type (optional)
        """
        if target_name is not None:
            item.setText(0, target_name)
            item.setData(0, Qt.ItemDataRole.UserRole, target_name)
        if username is not None:
            item.setText(1, username)
        if credential_type is not None:
            item.setText(2, credential_type)
            
    def get_credential(self, item):
        """Get credential data from an item.
        
        Args:
            item: QTreeWidgetItem to get data from
            
        Returns:
            tuple: (target_name, username, credential_type)
        """
        target_name = item.text(0)
        username = item.text(1)
        credential_type = item.text(2)
        
        return target_name, username, credential_type
        
    def clear_credentials(self):
        """Clear all credentials from the tree."""
        self.clear()
        
    def find_credential_item(self, target_name):
        """Find a credential item by target name.
        
        Args:
            target_name: Target name to find
            
        Returns:
            QTreeWidgetItem or None: Found item or None if not found
        """
        for i in range(self.topLevelItemCount()):
            item = self.topLevelItem(i)
            if item.data(0, Qt.ItemDataRole.UserRole) == target_name:
                return item
        return None
