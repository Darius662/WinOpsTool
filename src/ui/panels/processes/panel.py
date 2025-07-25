"""Windows Process management panel."""
from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                          QLineEdit, QLabel, QMessageBox)
from PyQt6.QtCore import Qt, QTimer
from src.core.logger import setup_logger
from src.ui.base.base_panel import BasePanel
from .tree_widget import ProcessesTree
from .dialogs import PriorityDialog
from .manager import ProcessManager

class ProcessesPanel(BasePanel):
    """Panel for managing Windows Processes."""
    
    def __init__(self, parent=None):
        """Initialize processes panel.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ProcessManager()
        
        # Set up refresh timer (2 seconds)
        self.refresh_timer = QTimer(self)
        self.refresh_timer.timeout.connect(self.refresh_processes)
        
        # Defer initial refresh and timer start
        # This will prevent blocking the UI during startup
        QTimer.singleShot(1000, self.delayed_start)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Use the main_layout from BasePanel instead of creating a new layout
        layout = self.main_layout
        
        # Search controls
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_edit = QLineEdit()
        self.search_edit.textChanged.connect(self.filter_processes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_edit)
        
        # Action buttons
        self.terminate_button = QPushButton("Terminate")
        self.terminate_button.clicked.connect(self.terminate_process)
        search_layout.addWidget(self.terminate_button)
        
        self.priority_button = QPushButton("Set Priority")
        self.priority_button.clicked.connect(self.change_priority)
        search_layout.addWidget(self.priority_button)
        
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_processes)
        search_layout.addWidget(self.refresh_button)
        
        layout.addLayout(search_layout)
        
        # Processes tree
        self.processes_tree = ProcessesTree()
        self.processes_tree.itemSelectionChanged.connect(self.update_buttons)
        layout.addWidget(self.processes_tree)
        
        # Initial button state
        self.update_buttons()
        
    def update_buttons(self):
        """Update button enabled states based on selection."""
        has_selection = bool(self.processes_tree.selectedItems())
        self.terminate_button.setEnabled(has_selection)
        self.priority_button.setEnabled(has_selection)
        
    def refresh_processes(self):
        """Refresh the processes list."""
        try:
            # Get current selection
            selected_pid = None
            if self.processes_tree.selectedItems():
                selected_pid = int(self.processes_tree.selectedItems()[0].text(0))
                
            # Clear and repopulate tree
            self.processes_tree.clear_processes()
            processes = self.manager.get_processes()
            
            for proc in processes:
                self.processes_tree.add_process(
                    proc['pid'],
                    proc['name'],
                    proc['cpu_percent'],
                    proc['memory_percent'],
                    proc['status'],
                    proc['threads'],
                    proc['username'],
                    proc['priority']
                )
                
            # Reapply filter if search text exists
            if self.search_edit.text():
                self.filter_processes(self.search_edit.text())
                
            # Restore selection if process still exists
            if selected_pid:
                item = self.processes_tree.find_process(selected_pid)
                if item:
                    item.setSelected(True)
                    
            self.logger.debug("Refreshed processes list")
        except Exception as e:
            self.logger.error(f"Failed to refresh processes: {str(e)}")
            
    def filter_processes(self, text):
        """Filter processes by PID or name.
        
        Args:
            text: Search text
        """
        for i in range(self.processes_tree.topLevelItemCount()):
            item = self.processes_tree.topLevelItem(i)
            pid = item.text(0)
            name = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in pid and search not in name)
            
    def terminate_process(self):
        """Terminate selected process."""
        item = self.processes_tree.selectedItems()[0]
        process = self.processes_tree.get_process(item)
        
        reply = QMessageBox.question(
            self,
            "Confirm Terminate",
            f"Are you sure you want to terminate process '{process['name']}' (PID: {process['pid']})?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.manager.terminate_process(process['pid']):
                self.refresh_processes()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to terminate process '{process['name']}' (PID: {process['pid']})"
                )
                
    def change_priority(self):
        """Change priority of selected process."""
        item = self.processes_tree.selectedItems()[0]
        process = self.processes_tree.get_process(item)
        
        dialog = PriorityDialog(self, process['priority'])
        if dialog.exec():
            priority = dialog.get_priority()
            if priority == "Realtime":
                # Extra confirmation for Realtime
                reply = QMessageBox.warning(
                    self,
                    "Warning",
                    "Setting Realtime priority can make the system unresponsive!\n\n"
                    "Are you absolutely sure?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    return
                    
            if self.manager.set_priority(process['pid'], priority):
                self.refresh_processes()
            else:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to change priority for process '{process['name']}' (PID: {process['pid']})"
                )
                
    def delayed_start(self):
        """Delayed initialization to prevent blocking the UI during startup."""
        self.logger.info('Starting delayed initialization of ProcessesPanel')
        self.refresh_processes()
        # Auto-refresh timer removed - refresh only happens manually via button
        self.logger.info('ProcessesPanel initialization complete')
        
    def setup_connections(self):
        """Set up signal-slot connections."""
        # Connections already set up in setup_ui method
        # This method is required by BasePanel but implementation is kept here
        # for consistency with the BasePanel interface
        pass
