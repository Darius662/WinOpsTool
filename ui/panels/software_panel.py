from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, 
                               QPushButton, QListWidget, QLabel,
                               QLineEdit, QMessageBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import win32com.client
import winreg
import os
import subprocess

class SoftwareInstaller(QThread):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal(bool, str)
    
    def __init__(self, installer_path):
        super().__init__()
        self.installer_path = installer_path
        
    def run(self):
        try:
            # Basic implementation - expand based on installer type
            if self.installer_path.endswith('.msi'):
                result = subprocess.run(['msiexec', '/i', self.installer_path, '/quiet'],
                                     capture_output=True, text=True)
            else:
                result = subprocess.run([self.installer_path, '/S'], 
                                      capture_output=True, text=True)
                
            if result.returncode == 0:
                self.finished.emit(True, "Installation completed successfully")
            else:
                self.finished.emit(False, f"Installation failed: {result.stderr}")
        except Exception as e:
            self.finished.emit(False, f"Error during installation: {str(e)}")

class SoftwarePanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_installed_software()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Search bar
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search installed software...")
        self.search_input.textChanged.connect(self.filter_software)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Software list
        self.software_list = QListWidget()
        layout.addWidget(self.software_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        self.install_btn = QPushButton("Install Software")
        self.uninstall_btn = QPushButton("Uninstall Selected")
        self.refresh_btn = QPushButton("Refresh List")
        
        self.install_btn.clicked.connect(self.install_software)
        self.uninstall_btn.clicked.connect(self.uninstall_software)
        self.refresh_btn.clicked.connect(self.load_installed_software)
        
        button_layout.addWidget(self.install_btn)
        button_layout.addWidget(self.uninstall_btn)
        button_layout.addWidget(self.refresh_btn)
        layout.addLayout(button_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
    def load_installed_software(self):
        self.software_list.clear()
        
        # Get installed software from registry
        keys = [
            r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
            r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
        ]
        
        for key_path in keys:
            try:
                key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, 
                                   winreg.KEY_READ | winreg.KEY_WOW64_64KEY)
                
                for i in range(winreg.QueryInfoKey(key)[0]):
                    try:
                        subkey_name = winreg.EnumKey(key, i)
                        subkey = winreg.OpenKey(key, subkey_name)
                        try:
                            display_name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                            self.software_list.addItem(display_name)
                        except:
                            continue
                        finally:
                            winreg.CloseKey(subkey)
                    except:
                        continue
                winreg.CloseKey(key)
            except:
                continue
                
    def filter_software(self, text):
        for i in range(self.software_list.count()):
            item = self.software_list.item(i)
            item.setHidden(text.lower() not in item.text().lower())
            
    def install_software(self):
        # Implement file dialog and installation logic
        pass
        
    def uninstall_software(self):
        if not self.software_list.currentItem():
            QMessageBox.warning(self, "Warning", "Please select software to uninstall")
            return
            
        reply = QMessageBox.question(self, "Confirm Uninstall", 
                                   f"Are you sure you want to uninstall "
                                   f"{self.software_list.currentItem().text()}?",
                                   QMessageBox.StandardButton.Yes | 
                                   QMessageBox.StandardButton.No)
                                   
        if reply == QMessageBox.StandardButton.Yes:
            # Implement uninstallation logic
            pass
