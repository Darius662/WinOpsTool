"""Windows Applications Management Panel."""
import os
import psutil
import winreg
import win32api
import win32con
import win32process
import win32security
from datetime import datetime
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout,
                          QMessageBox, QInputDialog, QLineEdit, QComboBox,
                          QFileDialog, QTabWidget, QWidget, QVBoxLayout)
from PyQt6.QtCore import Qt, QTimer
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class ProcessesTab(QWidget):
    """Tab for managing running processes."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Processes tree
        self.processes_tree = QTreeWidget()
        self.processes_tree.setHeaderLabels([
            "Name",
            "PID",
            "Status",
            "CPU %",
            "Memory",
            "User",
            "Started"
        ])
        self.processes_tree.setAlternatingRowColors(True)
        for i, width in enumerate([200, 80, 80, 80, 100, 150, 150]):
            self.processes_tree.setColumnWidth(i, width)
            
        layout.addWidget(self.processes_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.end_btn = QPushButton("End Process")
        self.end_tree_btn = QPushButton("End Process Tree")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.end_btn, self.end_tree_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.end_btn.clicked.connect(self.end_process)
        self.end_tree_btn.clicked.connect(self.end_process_tree)
        self.refresh_btn.clicked.connect(self.refresh_processes)
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_processes)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Initial load
        self.refresh_processes()
        
    def refresh_processes(self):
        """Refresh the processes list."""
        try:
            self.processes_tree.clear()
            
            for proc in psutil.process_iter(['pid', 'name', 'status', 'cpu_percent',
                                          'memory_info', 'create_time', 'username']):
                try:
                    # Get process info
                    info = proc.info
                    
                    # Format memory size
                    mem = info['memory_info'].rss
                    if mem > 1024 * 1024 * 1024:
                        mem_str = f"{mem / (1024 * 1024 * 1024):.1f} GB"
                    else:
                        mem_str = f"{mem / (1024 * 1024):.1f} MB"
                        
                    # Format creation time
                    create_time = datetime.fromtimestamp(info['create_time'])
                    time_str = create_time.strftime("%Y-%m-%d %H:%M:%S")
                    
                    item = QTreeWidgetItem([
                        info['name'],
                        str(info['pid']),
                        info['status'],
                        f"{info['cpu_percent']:.1f}",
                        mem_str,
                        info['username'] or "N/A",
                        time_str
                    ])
                    self.processes_tree.addTopLevelItem(item)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
                    
            self.processes_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh processes: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh processes: {str(e)}")
            
    def end_process(self):
        """End the selected process."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            pid = int(current_item.text(1))
            name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process",
                f"Are you sure you want to end the process '{name}' (PID: {pid})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                proc = psutil.Process(pid)
                proc.terminate()
                self.logger.info(f"Terminated process: {name} (PID: {pid})")
                self.refresh_processes()
                
        except Exception as e:
            self.logger.error(f"Failed to end process: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process: {str(e)}")
            
    def end_process_tree(self):
        """End the selected process and all its children."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            pid = int(current_item.text(1))
            name = current_item.text(0)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process Tree",
                f"Are you sure you want to end the process tree for '{name}' (PID: {pid})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                proc = psutil.Process(pid)
                children = proc.children(recursive=True)
                for child in children:
                    try:
                        child.terminate()
                    except:
                        pass
                proc.terminate()
                self.logger.info(f"Terminated process tree: {name} (PID: {pid})")
                self.refresh_processes()
                
        except Exception as e:
            self.logger.error(f"Failed to end process tree: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process tree: {str(e)}")

class StartupTab(QWidget):
    """Tab for managing startup applications."""
    
    STARTUP_LOCATIONS = [
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"),
        (winreg.HKEY_CURRENT_USER, r"SOFTWARE\Microsoft\Windows\CurrentVersion\RunOnce")
    ]
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Startup tree
        self.startup_tree = QTreeWidget()
        self.startup_tree.setHeaderLabels([
            "Name",
            "Command",
            "Location",
            "Type"
        ])
        self.startup_tree.setAlternatingRowColors(True)
        for i, width in enumerate([200, 300, 150, 100]):
            self.startup_tree.setColumnWidth(i, width)
            
        layout.addWidget(self.startup_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Startup Item")
        self.remove_btn = QPushButton("Remove")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.add_btn, self.remove_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_startup)
        self.remove_btn.clicked.connect(self.remove_startup)
        self.refresh_btn.clicked.connect(self.refresh_startup)
        
        # Initial load
        self.refresh_startup()
        
    def refresh_startup(self):
        """Refresh the startup items list."""
        try:
            self.startup_tree.clear()
            
            # Registry startup items
            for root_key, subkey in self.STARTUP_LOCATIONS:
                try:
                    with winreg.OpenKey(root_key, subkey) as key:
                        index = 0
                        while True:
                            try:
                                name, value, _ = winreg.EnumValue(key, index)
                                item = QTreeWidgetItem([
                                    name,
                                    value,
                                    "HKLM" if root_key == winreg.HKEY_LOCAL_MACHINE else "HKCU",
                                    "RunOnce" if "RunOnce" in subkey else "Run"
                                ])
                                self.startup_tree.addTopLevelItem(item)
                                index += 1
                            except WindowsError:
                                break
                except WindowsError:
                    pass
                    
            # Startup folders
            startup_folders = [
                os.path.join(os.environ["APPDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup"),
                os.path.join(os.environ["PROGRAMDATA"], r"Microsoft\Windows\Start Menu\Programs\Startup")
            ]
            
            for folder in startup_folders:
                if os.path.exists(folder):
                    for item in os.listdir(folder):
                        path = os.path.join(folder, item)
                        if os.path.isfile(path):
                            item = QTreeWidgetItem([
                                os.path.splitext(item)[0],
                                path,
                                "User" if "APPDATA" in folder else "All Users",
                                "Startup Folder"
                            ])
                            self.startup_tree.addTopLevelItem(item)
                            
            self.startup_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh startup items: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh startup items: {str(e)}")
            
    def add_startup(self):
        """Add a new startup item."""
        try:
            # Get application path
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Application",
                "",
                "Applications (*.exe);;All Files (*.*)"
            )
            
            if not file_path:
                return
                
            # Get name
            name, ok = QInputDialog.getText(
                self,
                "Add Startup Item",
                "Enter a name for this startup item:",
                QLineEdit.EchoMode.Normal,
                os.path.splitext(os.path.basename(file_path))[0]
            )
            
            if not ok or not name:
                return
                
            # Get location
            location_dialog = QInputDialog(self)
            location_dialog.setWindowTitle("Add Startup Item")
            location_dialog.setLabelText("Select startup location:")
            location_dialog.setComboBoxItems([
                "Current User (Registry)",
                "All Users (Registry)",
                "Current User (Startup Folder)",
                "All Users (Startup Folder)"
            ])
            
            if location_dialog.exec() != QInputDialog.DialogCode.Accepted:
                return
                
            location = location_dialog.textValue()
            
            # Add startup item
            if "Registry" in location:
                root_key = winreg.HKEY_CURRENT_USER if "Current User" in location else winreg.HKEY_LOCAL_MACHINE
                with winreg.OpenKey(root_key, r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE) as key:
                    winreg.SetValueEx(key, name, 0, winreg.REG_SZ, f'"{file_path}"')
            else:
                startup_folder = os.path.join(
                    os.environ["APPDATA"] if "Current User" in location else os.environ["PROGRAMDATA"],
                    r"Microsoft\Windows\Start Menu\Programs\Startup"
                )
                if not os.path.exists(startup_folder):
                    os.makedirs(startup_folder)
                    
                target_path = os.path.join(startup_folder, f"{name}.lnk")
                shell = win32com.client.Dispatch("WScript.Shell")
                shortcut = shell.CreateShortCut(target_path)
                shortcut.Targetpath = file_path
                shortcut.save()
                
            self.logger.info(f"Added startup item: {name}")
            self.refresh_startup()
            
        except Exception as e:
            self.logger.error(f"Failed to add startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add startup item: {str(e)}")
            
    def remove_startup(self):
        """Remove the selected startup item."""
        try:
            current_item = self.startup_tree.currentItem()
            if not current_item:
                return
                
            name = current_item.text(0)
            location = current_item.text(2)
            type = current_item.text(3)
            
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove the startup item '{name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if type == "Startup Folder":
                    path = current_item.text(1)
                    if os.path.exists(path):
                        os.remove(path)
                else:
                    root_key = winreg.HKEY_LOCAL_MACHINE if location == "HKLM" else winreg.HKEY_CURRENT_USER
                    key_path = r"SOFTWARE\Microsoft\Windows\CurrentVersion\Run"
                    if type == "RunOnce":
                        key_path += "Once"
                        
                    with winreg.OpenKey(root_key, key_path, 0, winreg.KEY_SET_VALUE) as key:
                        winreg.DeleteValue(key, name)
                        
                self.logger.info(f"Removed startup item: {name}")
                self.refresh_startup()
                
        except Exception as e:
            self.logger.error(f"Failed to remove startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove startup item: {str(e)}")

class ApplicationsPanel(BasePanel):
    """Panel for managing running processes and startup applications."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Create tabs
        self.processes_tab = ProcessesTab()
        self.startup_tab = StartupTab()
        
        # Add tabs
        self.tab_widget.addTab(self.processes_tab, "Processes")
        self.tab_widget.addTab(self.startup_tab, "Startup")
        
        # Add tab widget to main layout
        self.add_widget(self.tab_widget)
        
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in the tabs
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        if hasattr(self, 'processes_tab'):
            self.processes_tab.refresh_timer.stop()
