"""Windows Software management panel."""
from PyQt6.QtWidgets import QMessageBox, QFileDialog
import subprocess
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .manager import SoftwareManager
from .components.software_list import SoftwareList

class SoftwarePanel(BasePanel):
    """Panel for managing Windows installed software."""
    
    def __init__(self, parent=None):
        """Initialize software panel.
        
        Args:
            parent: Parent widget
        """
        # Initialize manager before calling super().__init__ which will call setup_ui
        self.manager = SoftwareManager()
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create software list component
        self.software_list = SoftwareList()
        self.add_widget(self.software_list)
        
        # Initial refresh
        self.refresh_software("All")
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        # This is now handled by the SoftwareList component
        pass
        
    def refresh_software(self, filter_type):
        """Refresh the software list.
        
        Args:
            filter_type: Filter type ("All", "System", "User")
        """
        try:
            # Get software list from manager
            software_list = self.manager.get_installed_software(filter_type)
            
            # Update software list component
            self.software_list.add_software(software_list)
                
            self.logger.info("Refreshed software list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh software: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh software list")
            
    def install_software(self, filter_type, remote_pc=None):
        """Install new software.
        
        Args:
            filter_type: Current filter type
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
                    # Refresh after installation
                    self.refresh_software(filter_type)
                    return True
                else:
                    QMessageBox.critical(self, "Error", "Failed to start installation")
                    
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to install software: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to install software: {str(e)}")
            return False
            
    def uninstall_software(self, filter_type):
        """Uninstall selected software.
        
        Args:
            filter_type: Current filter type
        """
        try:
            # Get selected software from component
            selected_software = self.software_list.get_selected_software()
            if not selected_software:
                return
                
            name = selected_software['name']
            
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
                        # Refresh after uninstallation
                        self.refresh_software(filter_type)
                    else:
                        QMessageBox.critical(self, "Error", f"Failed to uninstall {name}")
                else:
                    QMessageBox.warning(self, "Warning", f"Could not find uninstall information for {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to uninstall software: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to uninstall software: {str(e)}")
            
    def repair_software(self, filter_type):
        """Repair selected software.
        
        Args:
            filter_type: Current filter type
        """
        try:
            # Get selected software from component
            selected_software = self.software_list.get_selected_software()
            if not selected_software:
                return
                
            name = selected_software['name']
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
        # Connect software list signals
        self.software_list.install_software.connect(self.install_software)
        self.software_list.uninstall_software.connect(self.uninstall_software)
        self.software_list.repair_software.connect(self.repair_software)
        self.software_list.refresh_software.connect(self.refresh_software)
        self.software_list.filter_changed.connect(self.refresh_software)
        
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
        return self.install_software("All", remote_pc)
