"""Processes list component."""
from PyQt6.QtWidgets import QWidget, QVBoxLayout
from PyQt6.QtCore import pyqtSignal, QTimer

from src.ui.panels.applications.tree_widget import ProcessesTree
from src.ui.panels.applications.manager import ProcessManager
from .button_bar import ButtonBar


class ProcessesList(QWidget):
    """Component combining processes tree and action buttons."""
    
    # Signals for process operations
    process_selected = pyqtSignal(dict)
    process_ended = pyqtSignal(int)  # PID of ended process
    process_tree_ended = pyqtSignal(int)  # PID of ended process tree
    processes_refreshed = pyqtSignal()
    
    def __init__(self, parent=None):
        """Initialize the processes list component.
        
        Args:
            parent: Parent widget
        """
        super().__init__(parent)
        self.manager = ProcessManager()
        self._setup_ui()
        self._connect_signals()
        
        # Auto-refresh timer
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_processes)
        self.refresh_timer.start(5000)  # Refresh every 5 seconds
        
        # Initial load
        self.refresh_processes()
        
    def _setup_ui(self):
        """Set up the UI components."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Processes tree
        self.processes_tree = ProcessesTree()
        layout.addWidget(self.processes_tree)
        
        # Button bar
        self.button_bar = ButtonBar()
        layout.addWidget(self.button_bar)
        
    def _connect_signals(self):
        """Connect signals between components."""
        # Tree signals
        self.processes_tree.itemSelectionChanged.connect(self._on_selection_changed)
        
        # Button bar signals
        self.button_bar.end_process_clicked.connect(self.end_process)
        self.button_bar.end_process_tree_clicked.connect(self.end_process_tree)
        self.button_bar.refresh_clicked.connect(self.refresh_processes)
        
    def _on_selection_changed(self):
        """Handle selection change in the processes tree."""
        has_selection = bool(self.processes_tree.selectedItems())
        self.button_bar.update_button_states(has_selection)
        
        if has_selection:
            process = self.get_selected_process()
            if process:
                self.process_selected.emit(process)
                
    def get_selected_process(self):
        """Get the currently selected process.
        
        Returns:
            dict: Selected process data or None if no selection
        """
        current_item = self.processes_tree.currentItem()
        if current_item:
            return self.processes_tree.get_process(current_item)
        return None
        
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
                
            self.processes_refreshed.emit()
            
        except Exception as e:
            # Signal error to parent
            self.error_occurred.emit(str(e))
            
    def end_process(self):
        """End the selected process."""
        process = self.get_selected_process()
        if process:
            if self.manager.end_process(process['pid']):
                self.process_ended.emit(process['pid'])
                self.refresh_processes()
            else:
                self.error_occurred.emit(f"Failed to end process {process['pid']}")
                
    def end_process_tree(self):
        """End the selected process and its children."""
        process = self.get_selected_process()
        if process:
            if self.manager.end_process_tree(process['pid']):
                self.process_tree_ended.emit(process['pid'])
                self.refresh_processes()
            else:
                self.error_occurred.emit(f"Failed to end process tree {process['pid']}")
                
    def stop_timer(self):
        """Stop the refresh timer."""
        if self.refresh_timer.isActive():
            self.refresh_timer.stop()
            
    # Add missing signal
    error_occurred = pyqtSignal(str)
