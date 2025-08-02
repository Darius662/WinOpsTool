"""Credential management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QSplitter,
                           QLabel, QMessageBox)
from PyQt6.QtCore import Qt, pyqtSlot
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from src.managers.credential_manager import CredentialManager, HAS_CREDUI
from .tree_widget import CredentialsTree
from .dialogs import CredentialDialog
from .components.details_view import DetailsView
from .components.button_bar import CredentialButtonBar
from .components.search_bar import SearchBar
from .components.tab_widget import CredentialTabWidget

class CredentialsPanel(BasePanel):
    """Credentials panel for managing Windows credentials.
    
    This panel provides a Windows Credential Manager-like interface with separate tabs for
    Web Credentials and Windows Credentials. Windows Credentials are further categorized into
    Windows Credentials, Certificate-Based Credentials, and Generic Credentials.
    
    Features:
    - View, add, edit, and delete credentials
    - Search/filter credentials by target name, username, or type
    - Display credential details
    - Show/hide passwords
    - Separate tabs for Web and Windows credentials
    - Categorization of Windows credentials by type
    """
    
    def __init__(self, main_window):
        """Initialize credentials panel.
        
        Args:
            main_window: MainWindow instance
        """
        # Initialize manager
        self.credential_manager = CredentialManager()
        
        # Call parent constructor
        super().__init__(main_window)
        self.logger = setup_logger(self.__class__.__name__)
        
        # Load data
        self.load_data()
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed.
        
        Override of BasePanel.cleanup to handle specific cleanup tasks.
        """
        # Clear references to UI elements to avoid memory leaks
        if hasattr(self, 'credentials_tree') and self.credentials_tree is not None:
            try:
                self.credentials_tree.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        if hasattr(self, 'details_view') and self.details_view is not None:
            try:
                self.details_view.clear()
            except RuntimeError:
                # Widget might have been deleted already
                pass
                
        # Call the parent class cleanup to clear the main layout
        super().cleanup()
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Clear any existing layout if this is not the initial setup
        if hasattr(self, 'main_widget') and self.main_widget is not None:
            self.cleanup()
            
        # Create main container
        self.main_widget = QWidget()
        main_layout = QVBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Show warning if win32credui is not available
        if not HAS_CREDUI:
            warning_label = QLabel("Note: Some credential features are limited because the win32credui module is not available.")
            warning_label.setStyleSheet("color: #FF6600; font-weight: bold; padding: 5px; background-color: #FFFAF0; border: 1px solid #FFE4C4;")
            main_layout.addWidget(warning_label)
        
        # Create horizontal splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - Credentials tree
        tree_container = QWidget()
        tree_layout = QVBoxLayout(tree_container)
        tree_layout.setContentsMargins(0, 0, 0, 0)
        
        tree_label = QLabel("Stored Credentials")
        tree_layout.addWidget(tree_label)
        
        # Add credential tab widget with Web and Windows credential tabs
        self.credential_tabs = CredentialTabWidget()
        tree_layout.addWidget(self.credential_tabs)
        
        # Add tree container to left side of splitter
        splitter.addWidget(tree_container)
        
        # Right side - Credential details
        details_container = QWidget()
        details_layout = QVBoxLayout(details_container)
        details_layout.setContentsMargins(0, 0, 0, 0)
        
        details_label = QLabel("Credential Details")
        details_layout.addWidget(details_label)
        
        self.details_view = DetailsView()
        details_layout.addWidget(self.details_view)
        
        # Add containers to splitter
        splitter.addWidget(tree_container)
        splitter.addWidget(details_container)
        
        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([400, 600])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter, 1)
        
        # Create button bar at the bottom
        self.button_bar = CredentialButtonBar()
        main_layout.addWidget(self.button_bar, 0)
        
        # Add main widget to panel
        self.add_widget(self.main_widget)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        # Connect tree signals for Web Credentials tab
        web_tree = self.credential_tabs.get_web_credentials_tree()
        web_tree.item_selected.connect(self.on_credential_selected)
        
        # Connect tree signals for Windows Credentials tab
        windows_tree = self.credential_tabs.get_windows_credentials_tree()
        windows_tree.item_selected.connect(self.on_credential_selected)
        
        # Connect tab widget signals
        self.credential_tabs.currentChanged.connect(self.on_tab_changed)
        
        # Connect button bar signals
        self.button_bar.add_clicked.connect(self.add_credential)
        self.button_bar.edit_clicked.connect(self.edit_credential)
        self.button_bar.delete_clicked.connect(self.delete_credential)
        self.button_bar.refresh_clicked.connect(self.refresh_credentials)
        
        # Connect details view signals
        self.details_view.show_password_clicked.connect(self.show_password)
        
    def load_data(self):
        """Load or refresh panel data."""
        self.refresh_credentials()
        
    def save_data(self):
        """Save panel data."""
        # No data to save
        pass
        
    @pyqtSlot(int)
    def on_tab_changed(self, index):
        """Handle tab change event.
        
        Args:
            index: New tab index
        """
        # Clear details view
        self.details_view.clear()
        
        # Disable item buttons
        self.button_bar.enable_item_buttons(False)
        
    @pyqtSlot()
    def refresh_credentials(self):
        """Refresh credentials from credential manager."""
        try:
            # Clear trees
            self.credential_tabs.clear_all()
            
            # Clear details view
            self.details_view.clear()
            
            # Disable item buttons
            self.button_bar.enable_item_buttons(False)
            
            # Get credentials
            credentials = self.credential_manager.get_credentials()
            
            # Add to appropriate trees based on credential type
            for cred in credentials:
                target_name = cred.get('TargetName', '')
                username = cred.get('UserName', '')
                cred_type = cred.get('Type', '')
                
                # Determine if web or windows credential
                if target_name.startswith('http://') or target_name.startswith('https://'):
                    # Web credential
                    web_tree = self.credential_tabs.get_web_credentials_tree()
                    web_tree.add_credential(target_name, username, cred_type)
                else:
                    # Windows credential
                    windows_tree = self.credential_tabs.get_windows_credentials_tree()
                    windows_tree.add_credential(target_name, username, cred_type)
                
            self.logger.debug(f"Refreshed {len(credentials)} credentials")
        except Exception as e:
            self.logger.error(f"Failed to refresh credentials: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to refresh credentials: {str(e)}"
            )
            
    @pyqtSlot(object)
    def on_credential_selected(self, item):
        """Handle credential selection.
        
        Args:
            item: Selected tree item
        """
        try:
            # Skip category items
            if item.parent() is None and item.childCount() > 0:
                self.details_view.clear()
                self.button_bar.enable_item_buttons(False)
                return
                
            # Get target name from item
            target_name = item.data(0, Qt.ItemDataRole.UserRole)
            
            # Get credential details
            credential = self.credential_manager.get_credential(target_name)
            
            if credential:
                # Update details view
                self.details_view.set_credential(credential)
                
                # Enable item buttons
                self.button_bar.enable_item_buttons(True)
                
                self.logger.debug(f"Selected credential: {target_name}")
            else:
                self.logger.warning(f"Failed to get credential details: {target_name}")
                self.details_view.clear()
                self.button_bar.enable_item_buttons(False)
        except Exception as e:
            self.logger.error(f"Failed to handle credential selection: {str(e)}")
            self.details_view.clear()
            self.button_bar.enable_item_buttons(False)
            
    @pyqtSlot()
    def add_credential(self):
        """Add a new credential."""
        try:
            # Show add credential dialog
            dialog = CredentialDialog(self)
            if dialog.exec():
                # Get credential data
                target_name, username, password, credential_type = dialog.get_credential()
                
                # Add credential
                self.credential_manager.add_credential(
                    target_name, 
                    username, 
                    password, 
                    credential_type
                )
                
                # Refresh credentials
                self.refresh_credentials()
                
                # Switch to appropriate tab based on credential type
                if target_name.startswith('http://') or target_name.startswith('https://'):
                    self.credential_tabs.setCurrentIndex(0)  # Web Credentials tab
                else:
                    self.credential_tabs.setCurrentIndex(1)  # Windows Credentials tab
                
                self.logger.debug(f"Added credential: {target_name}")
        except Exception as e:
            self.logger.error(f"Failed to add credential: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to add credential: {str(e)}"
            )
                
    def edit_credential(self):
        """Edit selected credential."""
        try:
            # Get current tree based on active tab
            current_tree = self.credential_tabs.get_current_tree()
            
            # Get selected item
            item = current_tree.currentItem()
            if not item:
                return
                
            # Skip category items
            if item.parent() is None and item.childCount() > 0:
                return
                
            # Get target name from item
            target_name = item.data(0, Qt.ItemDataRole.UserRole)
            username = item.text(1)
            
            # Get full credential info
            credentials = self.credential_manager.get_credentials(target_name)
            if not credentials:
                return
                
            cred = credentials[0]
        
            dialog = CredentialDialog(
                self,
                target_name=cred['target_name'],
                username=cred['username'],
                password="",  # Don't show password in dialog
                credential_type=0,  # Will be disabled in edit mode
                persistence=0,  # Will be set from current value
                comment=cred.get('comment', ''),
                edit_mode=True
            )
            
            if dialog.exec():
                _, new_username, new_password, _, new_persistence, new_comment = dialog.get_credential()
                
                # Only update if password is provided
                if self.credential_manager.update_credential(
                    target_name,
                    username=new_username,
                    password=new_password if new_password else None,
                    persistence=new_persistence,
                    comment=new_comment
                ):
                    # Refresh credentials to update both tabs
                    self.refresh_credentials()
                    
                    # Switch to appropriate tab based on credential type
                    if target_name.startswith('http://') or target_name.startswith('https://'):
                        self.credential_tabs.setCurrentIndex(0)  # Web Credentials tab
                    else:
                        self.credential_tabs.setCurrentIndex(1)  # Windows Credentials tab
                    
                    self.logger.debug(f"Updated credential: {target_name}")
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to update credential: {target_name}"
                    )
        except Exception as e:
            self.logger.error(f"Failed to edit credential: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to edit credential: {str(e)}"
            )
                
    def delete_credential(self):
        """Delete selected credential."""
        try:
            # Get current tree based on active tab
            current_tree = self.credential_tabs.get_current_tree()
            
            # Get selected item
            item = current_tree.currentItem()
            if not item:
                return
                
            # Skip category items
            if item.parent() is None and item.childCount() > 0:
                return
                
            # Get target name from item
            target_name = item.data(0, Qt.ItemDataRole.UserRole)
            
            reply = QMessageBox.question(
                self,
                "Confirm Delete",
                f"Are you sure you want to delete credential '{target_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.credential_manager.delete_credential(target_name):
                    # Refresh credentials to update both tabs
                    self.refresh_credentials()
                    
                    self.logger.debug(f"Deleted credential: {target_name}")
                    
                    # Clear details view
                    self.details_view.clear()
                    
                    # Disable item buttons
                    self.button_bar.enable_item_buttons(False)
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to delete credential: {target_name}"
                    )
        except Exception as e:
            self.logger.error(f"Failed to delete credential: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to delete credential: {str(e)}"
            )
                
    def show_password(self, target_name):
        """Show password for a credential.
        
        Args:
            target_name: Target name of credential
        """
        try:
            # Get credential
            credentials = self.credential_manager.get_credentials(target_name)
            if credentials:
                # Show password in details view
                self.details_view.show_password(credentials[0]['password'])
        except Exception as e:
            self.logger.error(f"Failed to show password: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to show password: {str(e)}"
            )
            
    def filter_credentials(self, search_text):
        """Filter credentials based on search text.
        
        Args:
            search_text: Text to search for
        """
        try:
            # Filter both trees
            web_tree = self.credential_tabs.get_web_credentials_tree()
            windows_tree = self.credential_tabs.get_windows_credentials_tree()
            
            web_tree.filter_credentials(search_text)
            windows_tree.filter_credentials(search_text)
            
            # Clear details view
            self.details_view.clear()
            self.button_bar.enable_item_buttons(False)
                
            self.logger.debug(f"Filtered credentials with text: '{search_text}'")
        except Exception as e:
            self.logger.error(f"Failed to filter credentials: {str(e)}")
            
    def update_remote_state(self, connected):
        """Update UI based on remote connection state.
        
        Args:
            connected: True if connected to remote system, False otherwise
        """
        # Disable local credential management when remote
        self.setEnabled(not connected)
