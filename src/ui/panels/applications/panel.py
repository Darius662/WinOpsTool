"""Windows Applications management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QMessageBox, QFileDialog, QTabWidget)
from PyQt6.QtCore import Qt, QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ProcessesTree, StartupTree
from .manager import ProcessManager, StartupManager

class ProcessesTab(QWidget):
    """Tab for managing running processes."""
    
    def __init__(self, parent=None):
        """Initialize processes tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ProcessManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Processes tree
        self.processes_tree = ProcessesTree()
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
            self.processes_tree.clear_processes()
            processes = self.manager.get_processes()
            
            for proc in processes:
                self.processes_tree.add_process(
                    proc['name'],
                    proc['pid'],
                    proc['status'],
                    proc['cpu_percent'],
                    proc['memory'],
                    proc['username'],
                    proc['create_time']
                )
                
            self.logger.info("Refreshed processes list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh processes: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh processes list")
            
    def end_process(self):
        """End selected process."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            process = self.processes_tree.get_process(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process",
                f"Are you sure you want to end process '{process['name']}' (PID {process['pid']})?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.end_process(process['pid']):
                    self.refresh_processes()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to end process {process['pid']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to end process: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process: {str(e)}")
            
    def end_process_tree(self):
        """End selected process and its children."""
        try:
            current_item = self.processes_tree.currentItem()
            if not current_item:
                return
                
            process = self.processes_tree.get_process(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm End Process Tree",
                f"Are you sure you want to end process '{process['name']}' (PID {process['pid']}) and all its children?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.end_process_tree(process['pid']):
                    self.refresh_processes()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to end process tree {process['pid']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to end process tree: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to end process tree: {str(e)}")

class StartupTab(QWidget):
    """Tab for managing startup applications."""
    
    def __init__(self, parent=None):
        """Initialize startup tab.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = StartupManager()
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the UI components."""
        layout = QVBoxLayout(self)
        
        # Startup tree
        self.startup_tree = StartupTree()
        layout.addWidget(self.startup_tree)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add")
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
            self.startup_tree.clear_startup_items()
            items = self.manager.get_startup_items()
            
            for item in items:
                self.startup_tree.add_startup_item(
                    item['name'],
                    item['command'],
                    item['location'],
                    item['type']
                )
                
            self.logger.info("Refreshed startup items list")
            
        except Exception as e:
            self.logger.error(f"Failed to refresh startup items: {str(e)}")
            QMessageBox.critical(self, "Error", "Failed to refresh startup items list")
            
    def add_startup(self):
        """Add a new startup item."""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Select Program",
                "",
                "Programs (*.exe);;All Files (*.*)"
            )
            
            if file_path:
                name = QInputDialog.getText(
                    self,
                    "Add Startup Item",
                    "Enter name for startup item:",
                    text=os.path.splitext(os.path.basename(file_path))[0]
                )[0]
                
                if name:
                    location = QInputDialog.getItem(
                        self,
                        "Add Startup Item",
                        "Select startup location:",
                        ["Current User", "All Users"],
                        0,
                        False
                    )[0]
                    
                    if self.manager.add_startup_item(name, file_path, location):
                        self.refresh_startup()
                    else:
                        QMessageBox.critical(self, "Error", "Failed to add startup item")
                        
        except Exception as e:
            self.logger.error(f"Failed to add startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to add startup item: {str(e)}")
            
    def remove_startup(self):
        """Remove selected startup item."""
        try:
            current_item = self.startup_tree.currentItem()
            if not current_item:
                return
                
            item = self.startup_tree.get_startup_item(current_item)
            
            reply = QMessageBox.question(
                self,
                "Confirm Remove",
                f"Are you sure you want to remove startup item '{item['name']}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                if self.manager.remove_startup_item(
                    item['name'],
                    item['location'],
                    item['type']
                ):
                    self.refresh_startup()
                else:
                    QMessageBox.critical(self, "Error", f"Failed to remove startup item {item['name']}")
                    
        except Exception as e:
            self.logger.error(f"Failed to remove startup item: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to remove startup item: {str(e)}")

class ApplicationsPanel(BasePanel):
    """Panel for managing running processes and startup applications."""
    
    def __init__(self, parent=None):
        """Initialize applications panel.
        
        Args:
            parent: Parent widget
        """
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
