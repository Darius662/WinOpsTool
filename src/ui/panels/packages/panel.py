"""Windows Package management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import PackagesTree
from .dialogs import WingetSearchDialog
from .manager import PackageManager

class PackagesPanel(BasePanel):
    """Panel for managing Windows installed programs and packages."""
    
    def __init__(self, parent=None):
        """Initialize packages panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = PackageManager()
        self.setup_ui()
        self.refresh_programs()
        
    def setup_ui(self):
        """Set up the panel UI."""
        layout = QVBoxLayout(self)
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_programs)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Action buttons
        self.uninstall_button = QPushButton("Uninstall")
        self.uninstall_button.clicked.connect(self.uninstall_program)
        search_layout.addWidget(self.uninstall_button)
        
        self.install_button = QPushButton("Install (Winget)")
        self.install_button.clicked.connect(self.install_package)
        search_layout.addWidget(self.install_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_programs)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Programs tree
        self.programs_tree = PackagesTree()
        self.programs_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.programs_tree)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.programs_tree.selectedItems())
        self.uninstall_button.setEnabled(has_selection)
        
    def refresh_programs(self):
        """Refresh the programs list."""
        try:
            # Clear and repopulate tree
            self.programs_tree.clear_programs()
            programs = self.manager.get_installed_programs()
            
            for program in programs:
                self.programs_tree.add_program(
                    program['name'],
                    program['version'],
                    program['publisher'],
                    program['install_date'],
                    program['install_location'],
                    program['registry_key']
                )
                
            # Reapply filter if search text exists
            if self.search_edit.text():
                self.filter_programs(self.search_edit.text())
                
            self.logger.info("Refreshed programs list")
        except Exception as e:
            self.logger.error(f"Failed to refresh programs: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh programs list")
            
    def filter_programs(self, text):
        """Filter programs by name or publisher.
        
        Args:
            text: Search text
        """
        for i in range(self.programs_tree.topLevelItemCount()):
            item = self.programs_tree.topLevelItem(i)
            name = item.text(0).lower()
            publisher = item.text(2).lower()
            search = text.lower()
            item.setHidden(search not in name and search not in publisher)
            
    def uninstall_program(self):
        """Uninstall selected program."""
        item = self.programs_tree.selectedItems()[0]
        program = self.programs_tree.get_program(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Uninstall",
            f"Are you sure you want to uninstall '{program['name']}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get uninstall string from registry
                key = winreg.OpenKey(
                    winreg.HKEY_LOCAL_MACHINE,
                    f'Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\{program["registry_key"]}'
                )
                uninstall_string = winreg.QueryValueEx(key, 'UninstallString')[0]
                winreg.CloseKey(key)
                
                if self.manager.uninstall_program(uninstall_string):
                    self.refresh_programs()
                else:
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to uninstall '{program['name']}'"
                    )
                    
            except WindowsError as e:
                self.logger.error(f"Failed to get uninstall string: {str(e)}")
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to get uninstall information for '{program['name']}'"
                )
                
    def install_package(self):
        """Install a winget package."""
        dialog = WingetSearchDialog(self)
        
        # Override search function
        def search():
            try:
                packages = self.manager.get_winget_packages()
                dialog.set_packages(packages)
            except Exception as e:
                self.logger.error(f"Failed to search winget packages: {str(e)}")
                QMessageBox.critical(
                    dialog,
                    "Error",
                    "Failed to search winget packages"
                )
                
        dialog.search_packages = search
        
        if dialog.exec():
            package_id = dialog.get_selected_package()
            if package_id:
                try:
                    if self.manager.install_winget_package(package_id):
                        self.refresh_programs()
                    else:
                        QMessageBox.critical(
                            self,
                            "Error",
                            f"Failed to install package '{package_id}'"
                        )
                except Exception as e:
                    self.logger.error(f"Failed to install package: {str(e)}")
                    QMessageBox.critical(
                        self,
                        "Error",
                        f"Failed to install package: {str(e)}"
                    )
