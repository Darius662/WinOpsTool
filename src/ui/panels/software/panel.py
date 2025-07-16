"""Windows Software management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox, QComboBox, QFileDialog)
from PyQt6.QtCore import Qt
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import SoftwareTree
from .manager import SoftwareManager

class SoftwarePanel(BasePanel):
    """Panel for managing Windows installed software."""
    
    def __init__(self, parent=None):
        """Initialize software panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = SoftwareManager()
        self.setup_ui()
        self.refresh_software()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Filter controls
        filter_layout = QHBoxLayout()
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Software",
            "System Software",
            "User Software"
        ])
        self.filter_combo.currentTextChanged.connect(self.refresh_software)
        filter_layout.addWidget(self.filter_combo)
        
        # Action buttons
        self.install_btn = QPushButton("Install Software")
        self.uninstall_btn = QPushButton("Uninstall")
        self.repair_btn = QPushButton("Repair")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.install_btn, self.uninstall_btn, self.repair_btn, self.refresh_btn]:
            filter_layout.addWidget(btn)
            
        layout.addLayout(filter_layout)
        
        # Software tree
        self.software_tree = SoftwareTree()
        self.software_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.software_tree)
        
        # Connect signals
        self.install_btn.clicked.connect(self.install_software)
        self.uninstall_btn.clicked.connect(self.uninstall_software)
        self.repair_btn.clicked.connect(self.repair_software)
        self.refresh_btn.clicked.connect(self.refresh_software)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.software_tree.selectedItems())
        self.uninstall_btn.setEnabled(has_selection)
        self.repair_btn.setEnabled(has_selection)
        
    def refresh_software(self):
        """Refresh the software list."""
        try:
            # Map combo text to filter type
            filter_map = {
                "All Software": "All",
                "System Software": "System",
                "User Software": "User"
            }
            filter_type = filter_map[self.filter_combo.currentText()]
            
            # Clear and repopulate tree
            self.software_tree.clear_software()
            software_list = self.manager.get_installed_software(filter_type)
            
            for software in software_list:
                self.software_tree.add_software(
                    software['name'],
                    software['version'],
                    software['publisher'],
                    software['install_date'],
                    software['size'],
                    software['location']
                )
                
            self.logger.info("Refreshed software list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh software: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh software list")
            
    def install_software(self, remote_pc=None):
        """Install new software.
        
        Args:
            remote_pc: Optional remote PC to install on
        """
        try:
            # Get installation file
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Select Installation File{' for ' + remote_pc.name if remote_pc else ''}",
                "",
                "Installation Files (*.exe *.msi);;All Files (*.*)"
            )
            
            if not file_path:
                return False
                
            if remote_pc:
                # TODO: Copy file to remote PC and execute
                pass
            else:
                if self.manager.install_software(file_path):
                    self.logger.info(f"Started installation of: {file_path}")
                    return True
                else:
                    QMessageBox.critical(self, "Error", "Failed to start installation")
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to install software: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to install software: {str(e)}")
            return False
            
    def uninstall_software(self):
        """Uninstall selected software."""
        try:
            current_item = self.software_tree.currentItem()
            if not current_item:
                return
                
            name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm Uninstall",
                f"Are you sure you want to uninstall '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Get software details
                software_list = self.manager.get_installed_software()
                software = next((s for s in software_list if s['name'] == name), None)
                
                if software and software['uninstall_string']:
                    if self.manager.uninstall_software(software['uninstall_string']):
                        self.logger.info(f"Started uninstallation of: {name}")
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to uninstall {name}")
                else:
                    QMessageBox.warning(self, "Warning", f"Could not find uninstall information for {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to uninstall software: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to uninstall software: {str(e)}")
            
    def repair_software(self):
        """Repair selected software."""
        try:
            current_item = self.software_tree.currentItem()
            if not current_item:
                return
                
            name = current_item.text(0)
            success, result = self.manager.repair_software(name)
            
            if success:
                subprocess.Popen(result, shell=True)
                self.logger.info(f"Started repair of: {name}")
            else:
                QMessageBox.warning(self, "Warning", f"Could not repair {name}: {result}")
                
        except Exception as e:
            self.logger.error(f"Failed to repair software: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to repair software: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed
        
    def apply_remote(self, remote_pc):
        """Apply software installation to a remote PC.
        
        Args:
            remote_pc: Remote PC to install on
            
        Returns:
            bool: True if successful
        """
        return self.install_software(remote_pc)
