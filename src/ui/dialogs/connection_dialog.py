"""Remote PC Connection Dialog."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
                          QPushButton, QLineEdit, QTreeWidget, QTreeWidgetItem,
                          QMessageBox, QLabel, QCheckBox, QGroupBox, QGridLayout)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QColor
import subprocess
import socket
import time
from src.core.remote.ps_remote_manager import PSRemoteManager
from src.ui.dialogs.enable_winrm_dialog import EnableWinRMDialog

class PingTestThread(QThread):
    """Thread for running ping tests."""
    result_signal = pyqtSignal(bool, str)
    
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname
        
    def run(self):
        """Run the ping test."""
        try:
            # Try to resolve hostname first
            try:
                socket.gethostbyname(self.hostname)
            except socket.gaierror:
                self.result_signal.emit(False, f"Could not resolve hostname {self.hostname}")
                return
                
            # Try ping command
            ping_param = "-n" if subprocess.os.name == "nt" else "-c"
            ping_cmd = ["ping", ping_param, "2", self.hostname]
            result = subprocess.run(ping_cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.result_signal.emit(True, f"Successfully pinged {self.hostname}")
            else:
                self.result_signal.emit(False, f"Host {self.hostname} could not be pinged. This could be due to firewall settings or the host is offline.")
                
        except Exception as e:
            self.result_signal.emit(False, f"Error during ping test: {str(e)}")

class CredentialTestThread(QThread):
    """Thread for testing credentials."""
    result_signal = pyqtSignal(bool, str)
    
    def __init__(self, hostname, username, password):
        super().__init__()
        self.hostname = hostname
        self.username = username
        self.password = password
        
    def run(self):
        """Run the credential test."""
        try:
            # Use net use command to check if the user exists on the target PC
            # This doesn't require WinRM to be enabled
            
            # First check if we can reach the admin share (requires admin rights)
            admin_check_cmd = f'net use \\\\{self.hostname}\\admin$ /user:{self.username} {self.password} /persistent:no'
            admin_result = subprocess.run(admin_check_cmd, shell=True, capture_output=True, text=True)
            is_admin = admin_result.returncode == 0
            
            # Then try the IPC$ share which just tests credentials
            cmd = f'net use \\\\{self.hostname}\\IPC$ /user:{self.username} {self.password} /persistent:no'
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            # Clean up the connection regardless of result
            cleanup_cmd = f'net use \\\\{self.hostname}\\IPC$ /delete /y'
            subprocess.run(cleanup_cmd, shell=True, capture_output=True)
            
            if is_admin:
                # Also clean up admin share connection
                admin_cleanup_cmd = f'net use \\\\{self.hostname}\\admin$ /delete /y'
                subprocess.run(admin_cleanup_cmd, shell=True, capture_output=True)
            
            if result.returncode == 0:
                admin_status = "with administrator privileges" if is_admin else "without administrator privileges"
                self.result_signal.emit(True, f"Successfully authenticated to {self.hostname} as {self.username} {admin_status}.")
            else:
                error_msg = result.stderr.strip() if result.stderr else result.stdout.strip()
                if "System error 5" in error_msg:
                    self.result_signal.emit(False, f"Authentication failed: Access denied. The user exists but the password may be incorrect.")
                elif "System error 1326" in error_msg:
                    self.result_signal.emit(False, f"Authentication failed: The user name or password is incorrect.")
                elif "System error 53" in error_msg or "System error 1231" in error_msg:
                    self.result_signal.emit(False, f"Network error: Cannot reach {self.hostname}. The computer may be offline or blocking access.")
                else:
                    self.result_signal.emit(False, f"Authentication failed: {error_msg}")
                
        except Exception as e:
            self.result_signal.emit(False, f"Error during credential test: {str(e)}")

class WinRMTestThread(QThread):
    """Thread for testing WinRM connectivity."""
    result_signal = pyqtSignal(bool, str)
    
    def __init__(self, hostname):
        super().__init__()
        self.hostname = hostname
        
    def run(self):
        """Run the WinRM test."""
        try:
            # Try to connect to WinRM port
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(3)
                s.connect((self.hostname, 5985))
                s.close()
                port_open = True
            except:
                port_open = False
                
            if not port_open:
                self.result_signal.emit(False, f"WinRM port (5985) is not accessible on {self.hostname}. WinRM may not be enabled.")
                return
                
            # Test WinRM using Test-WSMan
            ps_cmd = f"Test-WSMan -ComputerName {self.hostname} -ErrorAction SilentlyContinue"
            result = subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True, text=True)
            
            if result.returncode == 0 and "wsmid" in result.stdout.lower():
                self.result_signal.emit(True, f"WinRM is enabled and accessible on {self.hostname}")
            else:
                self.result_signal.emit(False, f"WinRM port is open but service test failed on {self.hostname}. WinRM may be partially configured.")
                
        except Exception as e:
            self.result_signal.emit(False, f"Error testing WinRM: {str(e)}")

class AddConnectionThread(QThread):
    """Thread for adding a connection without blocking the UI."""
    
    result_signal = pyqtSignal(bool, str)
    
    def __init__(self, remote_manager, name, hostname, username, password):
        super().__init__()
        self.remote_manager = remote_manager
        self.name = name
        self.hostname = hostname
        self.username = username
        self.password = password
        
    def run(self):
        """Run the connection process."""
        try:
            success = self.remote_manager.add_connection(self.name, self.hostname, self.username, self.password)
            if success:
                self.result_signal.emit(True, f"Successfully connected to {self.hostname}")
            else:
                self.result_signal.emit(False, f"Failed to connect to {self.hostname}")
        except Exception as e:
            self.result_signal.emit(False, f"Error connecting to {self.hostname}: {str(e)}")


class ConnectThread(QThread):
    """Thread for connecting to a PC without blocking the UI."""
    
    result_signal = pyqtSignal(str, bool, str)  # name, success, message
    
    def __init__(self, remote_manager, name):
        super().__init__()
        self.remote_manager = remote_manager
        self.name = name
        
    def run(self):
        """Run the connection process."""
        try:
            success = self.remote_manager.ps_remote.connect(self.name)
            if success:
                self.result_signal.emit(self.name, True, f"Successfully connected to {self.name}")
            else:
                self.result_signal.emit(self.name, False, f"Failed to connect to {self.name}")
        except Exception as e:
            self.result_signal.emit(self.name, False, f"Error connecting to {self.name}: {str(e)}")


class DisconnectThread(QThread):
    """Thread for disconnecting from a PC without blocking the UI."""
    
    result_signal = pyqtSignal(str, bool, str)  # name, success, message
    
    def __init__(self, remote_manager, name, is_current=False):
        super().__init__()
        self.remote_manager = remote_manager
        self.name = name
        self.is_current = is_current
        
    def run(self):
        """Run the disconnection process."""
        try:
            if self.is_current:
                success = self.remote_manager.ps_remote.disconnect()
                if success:
                    self.result_signal.emit(self.name, True, f"Successfully disconnected from {self.name}")
                else:
                    self.result_signal.emit(self.name, False, f"Failed to disconnect from {self.name}")
            else:
                # Just mark as disconnected if it's not the current connection
                conn = self.remote_manager.ps_remote.get_connection(self.name)
                if conn:
                    conn.is_connected = False
                    self.result_signal.emit(self.name, True, f"Marked {self.name} as disconnected")
                else:
                    self.result_signal.emit(self.name, False, f"Connection {self.name} not found")
        except Exception as e:
            self.result_signal.emit(self.name, False, f"Error disconnecting from {self.name}: {str(e)}")


class ConnectionDialog(QDialog):
    """Dialog for managing remote PC connections."""
    
    def __init__(self, remote_manager, parent=None):
        super().__init__(parent)
        self.remote_manager = remote_manager
        # Create PSRemoteManager instance if not already available
        if not hasattr(self.remote_manager, 'ps_remote'):
            self.remote_manager.ps_remote = PSRemoteManager()
        self.setWindowTitle("Remote PC Connections")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # PowerShell Remoting info
        info_label = QLabel(
            "<b>PowerShell Remoting Connection</b><br>"
            "Ensure WinRM is enabled on the remote PC with:<br>"
            "<code>Enable-PSRemoting -Force</code>"
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Connection list
        self.connections_tree = QTreeWidget()
        self.connections_tree.setHeaderLabels([
            "Name",
            "Hostname",
            "Username",
            "Status"
        ])
        self.connections_tree.setAlternatingRowColors(True)
        for i, width in enumerate([150, 150, 150, 100]):
            self.connections_tree.setColumnWidth(i, width)
            
        layout.addWidget(self.connections_tree)
        
        # Connect/Disconnect buttons
        conn_buttons_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Connect")
        self.connect_btn.clicked.connect(self.connect_selected)
        conn_buttons_layout.addWidget(self.connect_btn)
        
        self.disconnect_btn = QPushButton("Disconnect")
        self.disconnect_btn.clicked.connect(self.disconnect_selected)
        conn_buttons_layout.addWidget(self.disconnect_btn)
        
        # Add spacer to push buttons to the left
        conn_buttons_layout.addStretch()
        
        layout.addLayout(conn_buttons_layout)
        
        # Add connection form in a group box
        connection_group = QGroupBox("Connection Details")
        form_layout = QFormLayout()
        
        self.name_edit = QLineEdit()
        self.hostname_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Name:", self.name_edit)
        form_layout.addRow("Hostname:", self.hostname_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", self.password_edit)
        
        connection_group.setLayout(form_layout)
        layout.addWidget(connection_group)
        
        # Test logs panel
        test_group = QGroupBox("Test Logs")
        test_layout = QVBoxLayout()
        
        # Test buttons layout
        buttons_layout = QHBoxLayout()
        
        self.ping_btn = QPushButton("Ping Test")
        self.ping_btn.clicked.connect(self.ping_test)
        buttons_layout.addWidget(self.ping_btn)
        
        self.cred_test_btn = QPushButton("Credential Test")
        self.cred_test_btn.clicked.connect(self.credential_test)
        buttons_layout.addWidget(self.cred_test_btn)
        
        self.winrm_test_btn = QPushButton("WinRM Test")
        self.winrm_test_btn.clicked.connect(self.winrm_test)
        buttons_layout.addWidget(self.winrm_test_btn)
        
        self.enable_winrm_btn = QPushButton("Enable WinRM Remotely")
        self.enable_winrm_btn.clicked.connect(self.enable_winrm_remotely)
        buttons_layout.addWidget(self.enable_winrm_btn)
        
        test_layout.addLayout(buttons_layout)
        
        # Log output area - using QTextEdit instead of QLabel to make it selectable
        from PyQt6.QtWidgets import QTextEdit
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)  # Make it read-only but selectable
        self.log_output.setText("Test results will appear here...")
        self.log_output.setStyleSheet(
            "background-color: #f0f0f0; padding: 5px; border: 1px solid #ccc; color: #333;"
        )
        self.log_output.setMinimumHeight(120)
        
        # No need for separate scroll area as QTextEdit has built-in scrolling
        test_layout.addWidget(self.log_output)
        
        test_group.setLayout(test_layout)
        layout.addWidget(test_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.add_btn = QPushButton("Add Connection")
        self.remove_btn = QPushButton("Remove Connection")
        self.refresh_btn = QPushButton("Refresh")
        self.close_btn = QPushButton("Close")
        
        for btn in [self.add_btn, self.remove_btn, self.refresh_btn, self.close_btn]:
            button_layout.addWidget(btn)
            
        layout.addLayout(button_layout)
        
        # Connect signals
        self.add_btn.clicked.connect(self.add_connection)
        self.remove_btn.clicked.connect(self.remove_connection)
        self.refresh_btn.clicked.connect(self.refresh_connections)
        self.close_btn.clicked.connect(self.accept)
        
        # Initial load
        self.refresh_connections()
        
    def add_connection(self):
        """Add a new remote PC connection."""
        name = self.name_edit.text().strip()
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not all([name, hostname, username, password]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return
        
        # Update log to show we're connecting
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Connecting to {hostname} using PowerShell Remoting...")
        
        # Disable the add button to prevent multiple attempts
        self.add_btn.setEnabled(False)
        self.add_btn.setText("Connecting...")
        
        # Start connection in a background thread
        self.add_thread = AddConnectionThread(self.remote_manager, name, hostname, username, password)
        self.add_thread.result_signal.connect(self._handle_add_connection_result)
        self.add_thread.start()
    
    def _handle_add_connection_result(self, success, message):
        """Handle connection result."""
        # Re-enable the add button
        self.add_btn.setEnabled(True)
        self.add_btn.setText("Add Connection")
        
        if success:
            # Clear the form fields
            self.name_edit.clear()
            self.hostname_edit.clear()
            self.username_edit.clear()
            self.password_edit.clear()
            
            # Refresh the connections list
            self.refresh_connections()
            
            # Update log with success message
            self.log_output.setHtml(f"<span style='color: green;'>[SUCCESS]</span> {message}")
        else:
            # Update log with error message
            self.log_output.setHtml(f"<span style='color: red;'>[FAILED]</span> {message}\n\n"
                                  "Please ensure that:\n"
                                  "1. The hostname is correct\n"
                                  "2. WinRM is enabled on the remote PC\n"
                                  "3. The credentials are valid")
            
            
    def remove_connection(self):
        """Remove the selected connection."""
        current_item = self.connections_tree.currentItem()
        if not current_item:
            return
            
        name = current_item.text(0)
        
        reply = QMessageBox.question(
            self,
            "Confirm Remove",
            f"Are you sure you want to remove the connection to '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.remote_manager.remove_connection(name):
                self.refresh_connections()
            else:
                QMessageBox.critical(self, "Error", f"Failed to remove connection to {name}")
                
    def refresh_connections(self):
        """Refresh the connections list."""
        self.connections_tree.clear()
        self.remote_manager.refresh_connections()
        
        for pc in self.remote_manager.get_connections():
            item = QTreeWidgetItem([
                pc.name,
                pc.hostname,
                pc.username,
                "Connected" if pc.is_connected else "Disconnected"
            ])
            self.connections_tree.addTopLevelItem(item)
            
    def ping_test(self):
        """Test ping to the specified hostname."""
        hostname = self.hostname_edit.text().strip()
        if not hostname:
            QMessageBox.warning(self, "Warning", "Please enter a hostname")
            return
            
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Pinging {hostname}...")
            
        # Start ping test in a separate thread - simplified to just ping, not check WinRM port
        self.ping_thread = PingTestThread(hostname)
        self.ping_thread.result_signal.connect(self._handle_ping_result)
        self.ping_btn.setEnabled(False)
        self.ping_btn.setText("Pinging...")
        self.ping_thread.start()
        
    def _handle_ping_result(self, success, message):
        """Handle ping test results."""
        self.ping_btn.setEnabled(True)
        self.ping_btn.setText("Ping Test")
        
        if success:
            self.log_output.setHtml(f"<span style='color: green;'>[SUCCESS] Ping Test:</span> {message}")
        else:
            self.log_output.setHtml(f"<span style='color: red;'>[FAILED] Ping Test:</span> {message}")
            
    def credential_test(self):
        """Test credentials on the specified hostname."""
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not all([hostname, username, password]):
            QMessageBox.warning(self, "Warning", "Please fill in hostname, username, and password")
            return
            
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Testing credentials for {username}@{hostname}...")
            
        # Start credential test in a separate thread - using credentials from the form
        self.cred_thread = CredentialTestThread(hostname, username, password)
        self.cred_thread.result_signal.connect(self._handle_credential_result)
        self.cred_test_btn.setEnabled(False)
        self.cred_test_btn.setText("Testing...")
        self.cred_thread.start()
        
    def _handle_credential_result(self, success, message):
        """Handle credential test results."""
        self.cred_test_btn.setEnabled(True)
        self.cred_test_btn.setText("Credential Test")
        
        if success:
            self.log_output.setHtml(f"<span style='color: green;'>[SUCCESS] Credential Test:</span> {message}")
        else:
            self.log_output.setHtml(f"<span style='color: red;'>[FAILED] Credential Test:</span> {message}")
            
    def winrm_test(self):
        """Test if WinRM is enabled on the remote PC."""
        hostname = self.hostname_edit.text().strip()
        if not hostname:
            QMessageBox.warning(self, "Warning", "Please enter a hostname")
            return
            
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Testing WinRM on {hostname}...")
            
        # Start WinRM test in a separate thread
        self.winrm_thread = WinRMTestThread(hostname)
        self.winrm_thread.result_signal.connect(self._handle_winrm_result)
        self.winrm_test_btn.setEnabled(False)
        self.winrm_test_btn.setText("Testing...")
        self.winrm_thread.start()
        
    def _handle_winrm_result(self, success, message):
        """Handle WinRM test results."""
        self.winrm_test_btn.setEnabled(True)
        self.winrm_test_btn.setText("WinRM Test")
        
        if success:
            self.log_output.setHtml(f"<span style='color: green;'>[SUCCESS] WinRM Test:</span> {message}")
        else:
            self.log_output.setHtml(f"<span style='color: red;'>[FAILED] WinRM Test:</span> {message}")
    
    def enable_winrm_remotely(self):
        """Enable WinRM directly from the Connection Dialog."""
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not all([hostname, username, password]):
            QMessageBox.warning(self, "Warning", "Please fill in hostname, username, and password")
            return
        
        # Confirm action
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            f"This will enable PowerShell Remoting on {hostname}.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            self.log_output.setHtml(f"<span style='color: orange;'>[CANCELLED]</span> WinRM enablement cancelled by user")
            return
        
        # Disable button and update log
        self.enable_winrm_btn.setEnabled(False)
        self.enable_winrm_btn.setText("Enabling...")
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Enabling WinRM on {hostname}...")
        
        # Start WinRM enablement in a separate thread
        from src.ui.dialogs.enable_winrm_dialog import WinRMEnablerThread
        self.winrm_enabler_thread = WinRMEnablerThread(hostname, username, password, False)  # Not using PsExec by default
        self.winrm_enabler_thread.progress_update.connect(self._update_winrm_progress)
        self.winrm_enabler_thread.finished_signal.connect(self._handle_winrm_enable_result)
        self.winrm_enabler_thread.start()
    
    def _update_winrm_progress(self, message):
        """Update WinRM enablement progress in the log."""
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> {message}")
    
    def _handle_winrm_enable_result(self, success, message):
        """Handle WinRM enablement result."""
        self.enable_winrm_btn.setEnabled(True)
        self.enable_winrm_btn.setText("Enable WinRM Remotely")
        
        if success:
            self.log_output.setHtml(f"<span style='color: green;'>[SUCCESS]</span> WinRM has been enabled successfully: {message}")
        else:
            self.log_output.setHtml(f"<span style='color: red;'>[FAILED]</span> WinRM enablement failed: {message}")
            
    def connect_selected(self):
        """Connect to the selected PC(s) using background threads."""
        selected_items = self.connections_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select one or more PCs to connect to")
            return
            
        # Disable the connect button while operations are in progress
        self.connect_btn.setEnabled(False)
        self.connect_btn.setText("Connecting...")
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Connecting to selected PCs...")
        
        # Track results
        self.connect_results = []
        self.connect_total = len(selected_items)
        self.connect_completed = 0
        self.connect_success = 0
        self.connect_fail = 0
        
        # Create and start a thread for each connection
        self.connect_threads = []
        for item in selected_items:
            name = item.text(0)  # First column is the name
            thread = ConnectThread(self.remote_manager, name)
            thread.result_signal.connect(self.handle_connect_result)
            self.connect_threads.append(thread)
            thread.start()
        
    def disconnect_selected(self):
        """Disconnect from the selected PC(s) using background threads."""
        selected_items = self.connections_tree.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "Warning", "Please select one or more PCs to disconnect from")
            return
            
        # Disable the disconnect button while operations are in progress
        self.disconnect_btn.setEnabled(False)
        self.disconnect_btn.setText("Disconnecting...")
        self.log_output.setHtml(f"<span style='color: blue;'>[RUNNING]</span> Disconnecting from selected PCs...")
        
        # Track results
        self.disconnect_results = []
        self.disconnect_total = len(selected_items)
        self.disconnect_completed = 0
        self.disconnect_success = 0
        self.disconnect_fail = 0
        
        # Create and start a thread for each disconnection
        self.disconnect_threads = []
        for item in selected_items:
            name = item.text(0)  # First column is the name
            # Check if this PC is the current connection
            current_conn = self.remote_manager.ps_remote.current_connection
            is_current = current_conn and current_conn.name == name
            
            thread = DisconnectThread(self.remote_manager, name, is_current)
            thread.result_signal.connect(self.handle_disconnect_result)
            self.disconnect_threads.append(thread)
            thread.start()
            
    def handle_connect_result(self, name, success, message):
        """Handle the result of a connect operation."""
        self.connect_completed += 1
        
        # Update the status in the tree widget
        for i in range(self.connections_tree.topLevelItemCount()):
            item = self.connections_tree.topLevelItem(i)
            if item.text(0) == name:
                if success:
                    item.setText(3, "Connected")
                    item.setForeground(3, QColor(0, 128, 0))  # Green
                else:
                    item.setText(3, "Failed to connect")
                    item.setForeground(3, QColor(255, 0, 0))  # Red
                break
        
        if success:
            self.connect_success += 1
            self.connect_results.append(f"<span style='color: green;'>[SUCCESS]</span> {message}")
        else:
            self.connect_fail += 1
            self.connect_results.append(f"<span style='color: red;'>[FAILED]</span> {message}")
            
        # Update progress in the log
        progress = f"<span style='color: blue;'>[PROGRESS]</span> {self.connect_completed}/{self.connect_total} connections processed"
        self.log_output.setHtml(progress + "<br>" + "<br>".join(self.connect_results))
        
        # If all operations are complete, update the UI
        if self.connect_completed == self.connect_total:
            # Re-enable the connect button
            self.connect_btn.setEnabled(True)
            self.connect_btn.setText("Connect")
            
            # Update final summary
            summary = f"<span style='color: blue;'>[SUMMARY]</span> Connected to {self.connect_success} PCs, {self.connect_fail} failed"
            self.log_output.setHtml(summary + "<br>" + "<br>".join(self.connect_results))
            
    def handle_disconnect_result(self, name, success, message):
        """Handle the result of a disconnect operation."""
        self.disconnect_completed += 1
        
        # Update the status in the tree widget
        for i in range(self.connections_tree.topLevelItemCount()):
            item = self.connections_tree.topLevelItem(i)
            if item.text(0) == name:
                if success:
                    item.setText(3, "Disconnected")
                    item.setForeground(3, QColor(128, 128, 128))  # Gray
                else:
                    item.setText(3, "Failed to disconnect")
                    item.setForeground(3, QColor(255, 0, 0))  # Red
                break
        
        if success:
            self.disconnect_success += 1
            self.disconnect_results.append(f"<span style='color: green;'>[SUCCESS]</span> {message}")
        else:
            self.disconnect_fail += 1
            self.disconnect_results.append(f"<span style='color: red;'>[FAILED]</span> {message}")
            
        # Update progress in the log
        progress = f"<span style='color: blue;'>[PROGRESS]</span> {self.disconnect_completed}/{self.disconnect_total} disconnections processed"
        self.log_output.setHtml(progress + "<br>" + "<br>".join(self.disconnect_results))
        
        # If all operations are complete, update the UI
        if self.disconnect_completed == self.disconnect_total:
            # Re-enable the disconnect button
            self.disconnect_btn.setEnabled(True)
            self.disconnect_btn.setText("Disconnect")
            
            # Update final summary
            summary = f"<span style='color: blue;'>[SUMMARY]</span> Disconnected from {self.disconnect_success} PCs, {self.disconnect_fail} failed"
            self.log_output.setHtml(summary + "<br>" + "<br>".join(self.disconnect_results))
