"""Windows Services Management Panel."""
import win32serviceutil
import win32service
import win32con
from PyQt6.QtWidgets import (QTreeWidget, QTreeWidgetItem, QPushButton, QHBoxLayout,
                          QMessageBox, QInputDialog, QLineEdit, QComboBox)
from PyQt6.QtCore import Qt
from ..base.base_panel import BasePanel
from src.core.logger import setup_logger

class ServicesPanel(BasePanel):
    """Panel for managing Windows services."""
    
    SERVICE_STATES = {
        win32service.SERVICE_STOPPED: "Stopped",
        win32service.SERVICE_START_PENDING: "Starting",
        win32service.SERVICE_STOP_PENDING: "Stopping",
        win32service.SERVICE_RUNNING: "Running",
        win32service.SERVICE_CONTINUE_PENDING: "Continuing",
        win32service.SERVICE_PAUSE_PENDING: "Pausing",
        win32service.SERVICE_PAUSED: "Paused"
    }
    
    START_TYPES = {
        win32service.SERVICE_AUTO_START: "Automatic",
        win32service.SERVICE_DEMAND_START: "Manual",
        win32service.SERVICE_DISABLED: "Disabled",
        win32service.SERVICE_BOOT_START: "Boot",
        win32service.SERVICE_SYSTEM_START: "System"
    }
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = setup_logger(self.__class__.__name__)
        
    def setup_ui(self):
        """Initialize the UI components."""
        # Services tree
        self.services_tree = QTreeWidget()
        self.services_tree.setHeaderLabels([
            "Name",
            "Display Name",
            "Status",
            "Start Type",
            "Description"
        ])
        self.services_tree.setAlternatingRowColors(True)
        for i, width in enumerate([150, 200, 100, 100, 300]):
            self.services_tree.setColumnWidth(i, width)
            
        self.add_widget(self.services_tree)
        
        # Filter
        self.filter_combo = QComboBox()
        self.filter_combo.addItems([
            "All Services",
            "Running Only",
            "Stopped Only",
            "Automatic Start",
            "Manual Start",
            "Disabled"
        ])
        self.filter_combo.currentTextChanged.connect(self.refresh_services)
        self.add_widget(self.filter_combo)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_btn = QPushButton("Start")
        self.stop_btn = QPushButton("Stop")
        self.restart_btn = QPushButton("Restart")
        self.set_startup_btn = QPushButton("Set Startup Type")
        self.refresh_btn = QPushButton("Refresh")
        
        for btn in [self.start_btn, self.stop_btn, self.restart_btn,
                   self.set_startup_btn, self.refresh_btn]:
            button_layout.addWidget(btn)
            
        self.add_layout(button_layout)
        
        # Connect signals
        self.start_btn.clicked.connect(self.start_service)
        self.stop_btn.clicked.connect(self.stop_service)
        self.restart_btn.clicked.connect(self.restart_service)
        self.set_startup_btn.clicked.connect(self.set_startup_type)
        self.refresh_btn.clicked.connect(self.refresh_services)
        
        # Initial load
        self.refresh_services()
        
    def refresh_services(self):
        """Refresh the services list."""
        try:
            self.services_tree.clear()
            
            sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
            services = win32service.EnumServicesStatus(sc_handle, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL)
            
            for service in services:
                try:
                    service_name = service[0]
                    display_name = service[1]
                    status = service[2]
                    
                    # Get additional info
                    service_config = win32service.QueryServiceConfig(
                        win32service.OpenService(
                            sc_handle,
                            service_name,
                            win32service.SERVICE_QUERY_CONFIG
                        )
                    )
                    start_type = service_config[1]  # Index 1 is start type
                    
                    # Get description
                    try:
                        description = win32serviceutil.QueryServiceConfig2(
                            service_name,
                            win32service.SERVICE_CONFIG_DESCRIPTION
                        )[0] or ""
                    except:
                        description = ""
                        
                    # Apply filter
                    filter_text = self.filter_combo.currentText()
                    if filter_text == "Running Only" and status[1] != win32service.SERVICE_RUNNING:
                        continue
                    elif filter_text == "Stopped Only" and status[1] != win32service.SERVICE_STOPPED:
                        continue
                    elif filter_text == "Automatic Start" and start_type != win32service.SERVICE_AUTO_START:
                        continue
                    elif filter_text == "Manual Start" and start_type != win32service.SERVICE_DEMAND_START:
                        continue
                    elif filter_text == "Disabled" and start_type != win32service.SERVICE_DISABLED:
                        continue
                        
                    item = QTreeWidgetItem([
                        service_name,
                        display_name,
                        self.SERVICE_STATES.get(status[1], "Unknown"),
                        self.START_TYPES.get(start_type, "Unknown"),
                        description
                    ])
                    self.services_tree.addTopLevelItem(item)
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get info for service {service_name}: {str(e)}")
                    
            self.services_tree.sortItems(0, Qt.SortOrder.AscendingOrder)
            
        except Exception as e:
            self.logger.error(f"Failed to refresh services: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to refresh services: {str(e)}")
            
    def get_selected_service(self):
        """Get the name of the currently selected service."""
        current_item = self.services_tree.currentItem()
        if not current_item:
            return None
        return current_item.text(0)
        
    def start_service(self):
        """Start the selected service."""
        try:
            service_name = self.get_selected_service()
            if not service_name:
                return
                
            win32serviceutil.StartService(service_name)
            self.logger.info(f"Started service: {service_name}")
            self.refresh_services()
            
        except Exception as e:
            self.logger.error(f"Failed to start service: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to start service: {str(e)}")
            
    def stop_service(self):
        """Stop the selected service."""
        try:
            service_name = self.get_selected_service()
            if not service_name:
                return
                
            reply = QMessageBox.question(
                self,
                "Confirm Stop",
                f"Are you sure you want to stop the service '{service_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                win32serviceutil.StopService(service_name)
                self.logger.info(f"Stopped service: {service_name}")
                self.refresh_services()
                
        except Exception as e:
            self.logger.error(f"Failed to stop service: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to stop service: {str(e)}")
            
    def restart_service(self):
        """Restart the selected service."""
        try:
            service_name = self.get_selected_service()
            if not service_name:
                return
                
            reply = QMessageBox.question(
                self,
                "Confirm Restart",
                f"Are you sure you want to restart the service '{service_name}'?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                win32serviceutil.RestartService(service_name)
                self.logger.info(f"Restarted service: {service_name}")
                self.refresh_services()
                
        except Exception as e:
            self.logger.error(f"Failed to restart service: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to restart service: {str(e)}")
            
    def set_startup_type(self):
        """Set the startup type for the selected service."""
        try:
            service_name = self.get_selected_service()
            if not service_name:
                return
                
            startup_types = {
                "Automatic": win32service.SERVICE_AUTO_START,
                "Manual": win32service.SERVICE_DEMAND_START,
                "Disabled": win32service.SERVICE_DISABLED
            }
            
            dialog = QInputDialog(self)
            dialog.setWindowTitle("Set Startup Type")
            dialog.setLabelText(f"Select startup type for {service_name}:")
            dialog.setComboBoxItems(list(startup_types.keys()))
            
            if dialog.exec() == QInputDialog.DialogCode.Accepted:
                startup_type = startup_types[dialog.textValue()]
                win32serviceutil.ChangeServiceConfig(
                    service_name,
                    startType=startup_type
                )
                self.logger.info(f"Changed startup type for {service_name} to {dialog.textValue()}")
                self.refresh_services()
                
        except Exception as e:
            self.logger.error(f"Failed to set startup type: {str(e)}")
            QMessageBox.critical(self, "Error", f"Failed to set startup type: {str(e)}")
            
    def setup_connections(self):
        """Set up signal/slot connections."""
        pass  # All connections are set up in setup_ui
        
    def cleanup(self):
        """Perform cleanup before panel is destroyed."""
        pass  # No cleanup needed for this panel
