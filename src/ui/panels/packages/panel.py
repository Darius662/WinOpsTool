"""Windows Package management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import PackagesTree
from .dialogs import WingetSearchDialog
from .manager import PackageManager

class ProgramsWorker(QThread):
    """Background worker for loading programs."""
    programs_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, manager):
        super().__init__()
        self.manager = manager
        
    def run(self):
        """Load programs in background thread."""
        try:
            programs = self.manager.get_installed_programs()
            self.programs_loaded.emit(programs)
        except Exception as e:
            self.error_occurred.emit(str(e))

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
        self.worker = None
        
        # Defer initial refresh with longer delay to reduce resource contention
        # This will prevent blocking the UI during startup
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(5000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
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
        """Refresh the programs list using background thread."""
        try:
            # Don't start new worker if one is already running
            if self.worker and self.worker.isRunning():
                return
                
            # Clear tree and show loading state
            self.programs_tree.clear_programs()
            
            # Create and start worker thread
            self.worker = ProgramsWorker(self.manager)
            self.worker.programs_loaded.connect(self.on_programs_loaded)
            self.worker.error_occurred.connect(self.on_programs_error)
            self.worker.start()
            
            self.logger.info("Started loading programs in background")
        except Exception as e:
            self.logger.error(f"Failed to start programs refresh: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to start programs refresh")
            
    def on_programs_loaded(self, programs):
        """Handle programs loaded from background thread."""
        try:
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
                
            self.logger.info(f"Loaded {len(programs)} programs successfully")
        except Exception as e:
            self.logger.error(f"Failed to populate programs tree: {str(e)}")
            
    def on_programs_error(self, error_msg):
        """Handle error from background thread."""
        self.logger.error(f"Failed to load programs: {error_msg}")
        QMessageBox.critical(self, "Error", f"Failed to load programs: {error_msg}")
            
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
                    
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of PackagesPanel')
        self.refresh_programs()
        self.logger.info('PackagesPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
