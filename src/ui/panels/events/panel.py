"""Events panel for Windows Event Viewer functionality."""
from PyQt6.QtWidgets import (QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
                          QMessageBox, QSplitter, QTextEdit, QWidget,
                          QComboBox, QProgressBar, QTreeWidget, QTreeWidgetItem)
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from src.ui.base.base_panel import BasePanel
from .manager import EventsManager
from .tree_widget import EventsTreeWidget
from .dialogs import EventDetailsDialog, EventFilterDialog, ExportEventsDialog
from src.core.logger import setup_logger

class EventLoadWorker(QThread):
    """Worker thread for loading events in the background."""
    
    events_loaded = pyqtSignal(list)
    error_occurred = pyqtSignal(str)
    
    def __init__(self, manager, log_name, filter_settings):
        super().__init__()
        self.manager = manager
        self.log_name = log_name
        self.filter_settings = filter_settings
        
    def run(self):
        """Load events in background thread."""
        try:
            events = self.manager.get_events(
                log_name=self.log_name,
                max_events=self.filter_settings.get('max_events', 100),
                level_filter=self.filter_settings.get('level_filter'),
                hours_back=self.filter_settings.get('hours_back', 24)
            )
            self.events_loaded.emit(events)
        except Exception as e:
            self.error_occurred.emit(str(e))

class EventsPanel(BasePanel):
    """Panel for viewing Windows event logs."""
    
    def __init__(self, parent=None):
        self.manager = EventsManager()
        self.current_log = "System"
        self.filter_settings = {
            'hours_back': 24,
            'level_filter': [1, 2, 3, 4],  # Critical, Error, Warning, Information
            'max_events': 100
        }
        self.load_worker = None
        super().__init__(parent)
        
    def setup_ui(self):
        """Set up the panel UI."""
        # Create main horizontal splitter (like Registry Editor)
        self.splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Create left widget for event logs tree
        self.left_widget = QWidget()
        self.left_layout = QVBoxLayout(self.left_widget)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label for event logs tree
        self.logs_label = QLabel("Event Logs")
        self.logs_label.setStyleSheet("font-weight: bold;")
        self.left_layout.addWidget(self.logs_label)
        
        # Create tree widget for event logs
        self.logs_tree = QTreeWidget()
        self.logs_tree.setHeaderLabels(["Log Name"])
        self.logs_tree.itemSelectionChanged.connect(self.on_log_selection_changed)
        self.left_layout.addWidget(self.logs_tree)
        
        # Create right widget for events view
        self.right_widget = QWidget()
        self.right_layout = QVBoxLayout(self.right_widget)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create label and controls for events view
        controls_layout = QHBoxLayout()
        self.events_label = QLabel("Events")
        self.events_label.setStyleSheet("font-weight: bold;")
        controls_layout.addWidget(self.events_label)
        
        controls_layout.addStretch()
        
        # Progress bar for loading
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setMaximumWidth(200)
        controls_layout.addWidget(self.progress_bar)
        
        self.right_layout.addLayout(controls_layout)
        
        # Create events tree
        self.event_tree = EventsTreeWidget()
        self.event_tree.itemSelectionChanged.connect(self.on_event_selection_changed)
        self.event_tree.itemDoubleClicked.connect(self.show_event_details)
        self.right_layout.addWidget(self.event_tree)
        
        # Create bottom section for event details
        self.details_label = QLabel("Event Details")
        self.details_label.setStyleSheet("font-weight: bold;")
        self.right_layout.addWidget(self.details_label)
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setMaximumHeight(150)
        self.info_text.setPlainText("Select an event to view details...")
        self.right_layout.addWidget(self.info_text)
        
        # Add widgets to splitter
        self.splitter.addWidget(self.left_widget)
        self.splitter.addWidget(self.right_widget)
        
        # Set initial sizes (30% for logs tree, 70% for events)
        self.splitter.setSizes([300, 700])
        
        # Create main widget to contain splitter and buttons
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        # Add splitter to main layout with stretch factor
        main_layout.addWidget(self.splitter, 1)
        
        # Create button bar at bottom
        self.button_bar = self.create_button_bar()
        main_layout.addWidget(self.button_bar, 0)
        
        # Add the main widget to the panel
        self.main_layout.addWidget(main_widget)
        
        # Load initial data with deferred initialization
        QTimer.singleShot(1500, self.deferred_initialization)
        
    def create_button_bar(self):
        """Create the button bar at the bottom (like Registry Editor)."""
        button_widget = QWidget()
        layout = QHBoxLayout(button_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Control buttons
        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.clicked.connect(self.refresh_events)
        layout.addWidget(self.refresh_button)
        
        self.filter_button = QPushButton("Filter")
        self.filter_button.clicked.connect(self.show_filter_dialog)
        layout.addWidget(self.filter_button)
        
        self.details_button = QPushButton("Details")
        self.details_button.clicked.connect(self.show_event_details)
        self.details_button.setEnabled(False)
        layout.addWidget(self.details_button)
        
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export_events)
        layout.addWidget(self.export_button)
        
        self.clear_button = QPushButton("Clear Log")
        self.clear_button.clicked.connect(self.clear_current_log)
        self.clear_button.setStyleSheet("QPushButton { background-color: #d32f2f; color: white; }")
        layout.addWidget(self.clear_button)
        
        # Add stretch to push buttons to the left
        layout.addStretch()
        
        return button_widget
        
    def setup_connections(self):
        """Set up signal connections."""
        # This method is required by BasePanel
        pass
        
    def on_log_selection_changed(self):
        """Handle log selection changes from the left tree."""
        selected_items = self.logs_tree.selectedItems()
        if selected_items:
            item = selected_items[0]
            # Only process if the item has actual log data (not a category)
            log_name = item.data(0, Qt.ItemDataRole.UserRole)
            if log_name and log_name != self.current_log:
                self.current_log = log_name
                self.refresh_events()
            elif not log_name:
                # If it's a category, don't change the current log
                # but expand/collapse the category
                item.setExpanded(not item.isExpanded())
        
    def deferred_initialization(self):
        """Perform deferred initialization to improve startup responsiveness."""
        self.logger.info("Starting delayed initialization of EventsPanel")
        try:
            # Load available event logs
            self.load_event_logs()
            # Load initial events
            self.refresh_events()
            self.logger.info("EventsPanel initialization complete")
        except Exception as e:
            self.logger.error(f"Error during EventsPanel initialization: {e}")
            
    def load_event_logs(self):
        """Load the list of available event logs in hierarchical structure like Windows Event Viewer."""
        try:
            logs = self.manager.get_event_logs()
            self.logs_tree.clear()
            
            # Create root node
            root_item = QTreeWidgetItem(["Event Viewer (Local)"])
            root_item.setExpanded(True)
            self.logs_tree.addTopLevelItem(root_item)
            
            # Create Custom Views category
            custom_views = QTreeWidgetItem(["Custom Views"])
            custom_views.setExpanded(False)
            root_item.addChild(custom_views)
            
            # Create Windows Logs category
            windows_logs = QTreeWidgetItem(["Windows Logs"])
            windows_logs.setExpanded(True)
            root_item.addChild(windows_logs)
            
            # Define Windows system logs
            system_logs = ["Application", "Security", "Setup", "System"]
            
            # Add Windows system logs
            for log in system_logs:
                if log in logs:
                    item = QTreeWidgetItem([log])
                    item.setData(0, Qt.ItemDataRole.UserRole, log)  # Store actual log name
                    windows_logs.addChild(item)
                    logs.remove(log)
                    # Select default log
                    if log == self.current_log:
                        self.logs_tree.setCurrentItem(item)
            
            # Create Applications and Services Logs category
            app_services_logs = QTreeWidgetItem(["Applications and Services Logs"])
            app_services_logs.setExpanded(False)
            root_item.addChild(app_services_logs)
            
            # Categorize remaining logs
            microsoft_logs = []
            other_logs = []
            
            for log in sorted(logs):
                if "Microsoft" in log or "Windows" in log:
                    microsoft_logs.append(log)
                else:
                    other_logs.append(log)
            
            # Add Microsoft subcategory if there are Microsoft logs
            if microsoft_logs:
                microsoft_category = QTreeWidgetItem(["Microsoft"])
                microsoft_category.setExpanded(False)
                app_services_logs.addChild(microsoft_category)
                
                # Add Microsoft logs
                for log in microsoft_logs:
                    item = QTreeWidgetItem([log])
                    item.setData(0, Qt.ItemDataRole.UserRole, log)
                    microsoft_category.addChild(item)
                    if log == self.current_log:
                        self.logs_tree.setCurrentItem(item)
            
            # Add other application logs directly
            for log in other_logs:
                item = QTreeWidgetItem([log])
                item.setData(0, Qt.ItemDataRole.UserRole, log)
                app_services_logs.addChild(item)
                if log == self.current_log:
                    self.logs_tree.setCurrentItem(item)
                
        except Exception as e:
            self.logger.error(f"Error loading event logs: {e}")
            QMessageBox.warning(self, "Warning", f"Failed to load event logs:\n{str(e)}")
            
    def on_log_changed(self, log_name):
        """Handle log selection change."""
        if log_name and log_name != self.current_log:
            self.current_log = log_name
            self.refresh_events()
            
    def refresh_events(self):
        """Refresh the list of events."""
        if not self.current_log:
            return
            
        try:
            # Show progress bar
            self.progress_bar.setVisible(True)
            self.progress_bar.setRange(0, 0)  # Indeterminate progress
            self.refresh_button.setEnabled(False)
            
            # Stop any existing worker
            if self.load_worker and self.load_worker.isRunning():
                self.load_worker.terminate()
                self.load_worker.wait()
            
            # Start background loading
            self.load_worker = EventLoadWorker(self.manager, self.current_log, self.filter_settings)
            self.load_worker.events_loaded.connect(self.on_events_loaded)
            self.load_worker.error_occurred.connect(self.on_load_error)
            self.load_worker.start()
            
        except Exception as e:
            self.logger.error(f"Error starting event refresh: {e}")
            self.on_load_error(str(e))
            
    def on_events_loaded(self, events):
        """Handle events loaded from background thread."""
        try:
            self.event_tree.populate_events(events)
            self.info_text.setPlainText(f"Loaded {len(events)} events from {self.current_log} log.")
            self.logger.debug(f"Refreshed events from {self.current_log}")
        except Exception as e:
            self.logger.error(f"Error processing loaded events: {e}")
        finally:
            # Hide progress bar and re-enable button
            self.progress_bar.setVisible(False)
            self.refresh_button.setEnabled(True)
            
    def on_load_error(self, error_message):
        """Handle error during event loading."""
        self.logger.error(f"Error loading events: {error_message}")
        QMessageBox.critical(self, "Error", f"Failed to load events:\n{error_message}")
        
        # Hide progress bar and re-enable button
        self.progress_bar.setVisible(False)
        self.refresh_button.setEnabled(True)
        
    def on_event_selection_changed(self):
        """Handle event selection changes."""
        selected_event = self.event_tree.get_selected_event()
        has_selection = selected_event is not None
        
        # Enable/disable details button
        self.details_button.setEnabled(has_selection)
        
        if selected_event:
            # Update info text with basic event information
            info_text = f"Event ID: {selected_event.get('event_id', 'N/A')}\n"
            info_text += f"Level: {selected_event.get('level', 'N/A')}\n"
            info_text += f"Date and Time: {selected_event.get('time_created', 'N/A')}\n"
            info_text += f"Source: {selected_event.get('provider', 'N/A')}\n"
            info_text += f"Computer: {selected_event.get('computer', 'N/A')}\n"
            info_text += f"Task Category: {selected_event.get('task', 'N/A')}\n\n"
            
            event_data = selected_event.get('event_data', '')
            if event_data:
                info_text += f"Event Data:\n{event_data[:500]}"
                if len(event_data) > 500:
                    info_text += "... (truncated)"
            else:
                info_text += "No additional event data available."
                
            self.info_text.setPlainText(info_text)
        else:
            self.info_text.setPlainText("Select an event to view details...")
            
    def show_filter_dialog(self):
        """Show the event filter dialog."""
        dialog = EventFilterDialog(self)
        
        # Set current filter values
        dialog.hours_back.setValue(self.filter_settings.get('hours_back', 24))
        dialog.max_events.setValue(self.filter_settings.get('max_events', 100))
        
        # Set level checkboxes
        level_filter = self.filter_settings.get('level_filter', [])
        dialog.critical_check.setChecked(1 in level_filter)
        dialog.error_check.setChecked(2 in level_filter)
        dialog.warning_check.setChecked(3 in level_filter)
        dialog.information_check.setChecked(4 in level_filter)
        dialog.verbose_check.setChecked(5 in level_filter)
        
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            self.filter_settings = dialog.get_filter_settings()
            self.refresh_events()
            
    def show_event_details(self):
        """Show detailed information about the selected event."""
        selected_event = self.event_tree.get_selected_event()
        if not selected_event:
            return
            
        try:
            dialog = EventDetailsDialog(selected_event, self)
            dialog.exec()
            
        except Exception as e:
            self.logger.error(f"Error showing event details: {e}")
            QMessageBox.critical(self, "Error", f"Error showing event details:\n{str(e)}")
            
    def clear_current_log(self):
        """Clear all events from the current log."""
        if not self.current_log:
            return
            
        reply = QMessageBox.question(
            self,
            "Clear Event Log",
            f"Are you sure you want to clear all events from the {self.current_log} log?\n\n"
            "This action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.manager.clear_event_log(self.current_log):
                    QMessageBox.information(self, "Success", f"The {self.current_log} log has been cleared.")
                    self.refresh_events()
                else:
                    QMessageBox.warning(self, "Failed", f"Failed to clear the {self.current_log} log.")
            except Exception as e:
                self.logger.error(f"Error clearing log: {e}")
                QMessageBox.critical(self, "Error", f"Error clearing log:\n{str(e)}")
                
    def export_events(self):
        """Export events to a file."""
        dialog = ExportEventsDialog(self)
        if dialog.exec() == QMessageBox.StandardButton.Yes:
            settings = dialog.get_export_settings()
            file_path = settings.get('file_path')
            
            if not file_path:
                QMessageBox.warning(self, "Warning", "Please select a file path for export.")
                return
                
            try:
                # For now, export as .evtx format using the manager
                if self.manager.export_events(self.current_log, file_path):
                    QMessageBox.information(self, "Success", f"Events exported to {file_path}")
                else:
                    QMessageBox.warning(self, "Failed", "Failed to export events.")
            except Exception as e:
                self.logger.error(f"Error exporting events: {e}")
                QMessageBox.critical(self, "Error", f"Error exporting events:\n{str(e)}")
                
    def cleanup(self):
        """Clean up resources when the panel is destroyed."""
        try:
            # Stop any running worker threads
            if self.load_worker and self.load_worker.isRunning():
                self.load_worker.terminate()
                self.load_worker.wait()
        except Exception as e:
            self.logger.error(f"Error during cleanup: {e}")
