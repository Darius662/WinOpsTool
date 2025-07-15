"""Windows Software Management Panel."""
import winreg
import subprocess
import os
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout,
                          QMessageBox, QInputDialog, QLineEdit, QComboBox,
                          QFileDialog)
from PyQt6.QtCore import Qt
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class SoftwarePanel(BasePanel):
    """Panel for managing installed software."""
    
    UNINSTALL_KEYS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall")
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Software tree
        self.software_tree = QTreeWidget()
        self.software_tree.setHeaderLabels([
            "Name",
            "Version",
            "Publisher",
            "Install Date",
            "Size",
            "Location"
        ])
        self.software_tree.setAlternatingRowColors(True)
        for i, width in enumerate([200, 100, 150, 100, 100, 300]):
            self.software_tree.setColumnWidth(i, width)
            
        self.add_widget(self.software_tree)
        
        # Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Software",
            "System Software",
            "User Software"
        ])
        self.filter_combo.currentTextChanged.connect(self.refresh_software)
        self.add_widget(self.filter_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.install_btn = QPushButton("Install Software")
        self.uninstall_btn = QPushButton("Uninstall")
        self.repair_btn = QPushButton("Repair")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.install_btn, self.uninstall_btn, self.repair_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.install_btn.clicked.connect(self.install_software)
        self.uninstall_btn.clicked.connect(self.uninstall_software)
        self.repair_btn.clicked.connect(self.repair_software)
        self.refresh_btn.clicked.connect(self.refresh_software)
        
        # Initial load
        self.refresh_software()
        
    def refresh_software(self):
        """Refresh the installed software list."""
        try:
            self.software_tree.clear()
            filter_text = self.filter_combo.currentText()
            
            for root_key, subkey in self.UNINSTALL_KEYS:
                # Skip user software if filtering for system software
                if filter_text == "System Software" and root_key == winreg.HKEY_CURRENT_USER:
                    continue
                # Skip system software if filtering for user software
                if filter_text == "User Software" and root_key == winreg.HKEY_LOCAL_MACHINE:
                    continue
                    
                try:
                    with winreg.OpenKey(root_key, subkey) as key:
                        index = 0
                        while True:
                            try:
                                app_key = winreg.EnumKey(key, index)
                                with winreg.OpenKey(key, app_key) as app:
                                    try:
                                        name = winreg.QueryValueEx(app, "DisplayName")[0]
                                        # Skip entries without display name
                                        if not name:
                                            index += 1
                                            continue
                                            
                                        # Get additional info
                                        try:
                                            version = winreg.QueryValueEx(app, "DisplayVersion")[0]
                                        except:
                                            version = "Unknown"
                                            
                                        try:
                                            publisher = winreg.QueryValueEx(app, "Publisher")[0]
                                        except:
                                            publisher = "Unknown"
                                            
                                        try:
                                            install_date = winreg.QueryValueEx(app, "InstallDate")[0]
                                        except:
                                            install_date = "Unknown"
                                            
                                        try:
                                            size = winreg.QueryValueEx(app, "EstimatedSize")[0]
                                            size = f"{size/1024:.1f} MB"
                                        except:
                                            size = "Unknown"
                                            
                                        try:
                                            location = winreg.QueryValueEx(app, "InstallLocation")[0]
                                        except:
                                            location = "Unknown"
                                            
                                        item = QTreeWidgetItem([
                                            name,
                                            version,
                                            publisher,
                                            install_date,
                                            size,
                                            location
                                        ])
                                        self.software_tree.addTopLevelItem(item)
                                        
                                    except WindowsError:
                                        pass
                                        
                                index += 1
                                
                            except WindowsError:
                                break
                                
                except WindowsError:
                    self.logger.warning(f"Failed to open registry key: {subkey}")
                    
            self.software_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh software list: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh software list: {str(e)}")
            
    def install_software(self, remote_pc=None):
        """Install new software."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Installation File",
                "",
                "Installation Files (*.exe *.msi);;All Files (*.*)"
            )
            
            if file_path:
                if remote_pc:
                    # Transfer file to remote PC first
                    remote_path = f"C:\\Windows\\Temp\\{os.path.basename(file_path)}"
                    
                    # Use admin$ share to transfer file
                    try:
                        win32wnet.WNetAddConnection2(
                            0,  # Type: disk
                            None,  # Local device
                            f"\\\\{remote_pc.hostname}\\admin$",  # Remote path
                            None,  # Provider
                            remote_pc.username,
                            remote_pc.password
                        )
                        
                        # Copy file
                        shutil.copy2(file_path, remote_path.replace('C:', 'C:\\Windows'))
                        
                        # Run installation on remote PC
                        if file_path.lower().endswith('.msi'):
                            cmd = f'msiexec /i "{remote_path}" /qn'
                        else:
                            cmd = f'"{remote_path}" /S'
                            
                        # Use WMI to run command on remote PC
                        import wmi
                        c = wmi.WMI(remote_pc.hostname, user=remote_pc.username, password=remote_pc.password)
                        process_id, result = c.Win32_Process.Create(CommandLine=cmd)
                        
                        if result == 0:
                            self.logger.info(f"Started remote installation on {remote_pc.name}: {remote_path}")
                            return True
                        else:
                            self.logger.error(f"Failed to start remote installation on {remote_pc.name}: Error {result}")
                            return False
                            
                    except Exception as e:
                        self.logger.error(f"Failed to install on remote PC {remote_pc.name}: {str(e)}")
                        return False
                        
                    finally:
                        try:
                            win32wnet.WNetCancelConnection2(f"\\\\{remote_pc.hostname}\\admin$", 0, 0)
                        except:
                            pass
                            
                else:
                    # Local installation
                    if file_path.lower().endswith('.msi'):
                        cmd = ['msiexec', '/i', file_path]
                    else:
                        cmd = [file_path]
                        
                    subprocess.Popen(cmd)
                    self.logger.info(f"Started local installation of: {file_path}")
                    return True
                    
        except Exception as e:
            self.logger.error(f"Failed to start installation: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to start installation: {str(e)}")
            return False
            
    def uninstall_software(self):
        """Uninstall the selected software."""
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
                # Find uninstall string in registry
                uninstall_string = None
                for root_key, subkey in self.UNINSTALL_KEYS:
                    try:
                        with winreg.OpenKey(root_key, subkey) as key:
                            index = 0
                            while True:
                                try:
                                    app_key = winreg.EnumKey(key, index)
                                    with winreg.OpenKey(key, app_key) as app:
                                        try:
                                            if winreg.QueryValueEx(app, "DisplayName")[0] == name:
                                                uninstall_string = winreg.QueryValueEx(app, "UninstallString")[0]
                                                break
                                        except WindowsError:
                                            pass
                                    index += 1
                                except WindowsError:
                                    break
                        if uninstall_string:
                            break
                    except WindowsError:
                        continue
                        
                if uninstall_string:
                    # For MSI uninstall strings
                    if "msiexec" in uninstall_string.lower():
                        cmd = uninstall_string
                    # For other uninstall strings
                    else:
                        cmd = f'"{uninstall_string}"'
                        
                    subprocess.Popen(cmd, shell=True)
                    self.logger.info(f"Started uninstallation of: {name}")
                else:
                    QMessageBox.warning(self, "Warning", f"Could not find uninstall information for {name}")
                    
        except Exception as e:
            self.logger.error(f"Failed to start uninstallation: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to start uninstallation: {str(e)}")
            
    def repair_software(self):
        """Repair the selected software."""
        try:
            current_item = self.software_tree.currentItem()
            if not current_item:
                return
                
            name = current_item.text(0)
            
            # Find repair string in registry
            repair_string = None
            for root_key, subkey in self.UNINSTALL_KEYS:
                try:
                    with winreg.OpenKey(root_key, subkey) as key:
                        index = 0
                        while True:
                            try:
                                app_key = winreg.EnumKey(key, index)
                                with winreg.OpenKey(key, app_key) as app:
                                    try:
                                        if winreg.QueryValueEx(app, "DisplayName")[0] == name:
                                            try:
                                                repair_string = winreg.QueryValueEx(app, "ModifyPath")[0]
                                            except WindowsError:
                                                # Try Windows Installer repair
                                                try:
                                                    product_code = winreg.QueryValueEx(app, "WindowsInstaller")[0]
                                                    if product_code:
                                                        repair_string = f"msiexec /f {{{product_code}}}"
                                                except WindowsError:
                                                    pass
                                            break
                                    except WindowsError:
                                        pass
                                index += 1
                            except WindowsError:
                                break
                    if repair_string:
                        break
                except WindowsError:
                    continue
                    
            if repair_string:
                subprocess.Popen(repair_string, shell=True)
                self.logger.info(f"Started repair of: {name}")
            else:
                QMessageBox.warning(self, "Warning", f"Could not find repair information for {name}")
                
        except Exception as e:
            self.logger.error(f"Failed to start repair: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to start repair: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
        
    def apply_remote(self, remote_pc):
        """Apply software installation to a remote PC."""
        try:
            # Ask what to install on remote PC
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                f"Select Installation File for {remote_pc.name}",
                "",
                "Installation Files (*.exe *.msi);;All Files (*.*)"
            )
            
            if file_path:
                return self.install_software(remote_pc)
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to apply software to {remote_pc.name}: {str(e)}")
            return False
