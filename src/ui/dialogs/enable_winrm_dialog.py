"""Dialog for enabling WinRM remotely."""
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, QLineEdit,
                          QPushButton, QMessageBox, QFormLayout,
                          QCheckBox, QProgressBar)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import subprocess
import os
import tempfile
import time

class WinRMEnablerThread(QThread):
    """Thread for enabling WinRM remotely."""
    progress_update = pyqtSignal(str)
    finished_signal = pyqtSignal(bool, str)
    
    def __init__(self, hostname, username, password, use_psexec=False):
        super().__init__()
        self.hostname = hostname
        self.username = username
        self.password = password
        self.use_psexec = use_psexec
        
    def run(self):
        """Run the WinRM enablement process."""
        try:
            if self.use_psexec:
                self._enable_with_psexec()
            else:
                self._enable_with_admin_share()
        except Exception as e:
            self.finished_signal.emit(False, str(e))
            
    def _enable_with_admin_share(self):
        """Enable WinRM using admin share."""
        self.progress_update.emit("Connecting to admin share...")
        
        # Create a temporary script file with improved PowerShell commands
        with tempfile.NamedTemporaryFile(suffix='.ps1', delete=False) as temp:
            temp_path = temp.name
            script = """
            # Enable PowerShell Remoting with more robust settings
            try {
                # Force enable PS Remoting with SkipNetworkProfileCheck to work in all network conditions
                Enable-PSRemoting -Force -SkipNetworkProfileCheck
                
                # Configure firewall to allow WinRM
                $FirewallParams = @{
                    DisplayName = 'Windows Remote Management (HTTP-In)'
                    Direction = 'Inbound'
                    LocalPort = 5985
                    Protocol = 'TCP'
                    Action = 'Allow'
                    Program = 'System'
                }
                New-NetFirewallRule @FirewallParams -ErrorAction SilentlyContinue
                
                # Configure trusted hosts
                Set-Item WSMan:\\localhost\\Client\\TrustedHosts -Value "*" -Force
                
                # Restart the service to apply changes
                Restart-Service WinRM -Force
                
                # Create success marker file
                "SUCCESS" | Out-File "C:\\winrm_setup_success.txt"
            }
            catch {
                "ERROR: $($_.Exception.Message)" | Out-File "C:\\winrm_setup_error.txt"
                exit 1
            }
            """
            temp.write(script.encode('utf-8'))
            
        try:
            # Map network drive with explicit credentials
            self.progress_update.emit("Mapping network drive...")
            net_use_cmd = f'net use \\\\{self.hostname}\\admin$ /user:{self.username} {self.password}'
            map_result = subprocess.run(net_use_cmd, shell=True, capture_output=True, text=True)
            
            if map_result.returncode != 0:
                self.finished_signal.emit(False, f"Failed to connect to admin share: {map_result.stderr or map_result.stdout}")
                return
                
            # Copy script to remote PC
            self.progress_update.emit("Copying script to remote PC...")
            remote_script_path = f'\\\\{self.hostname}\\admin$\\winrm_setup.ps1'
            copy_cmd = f'copy "{temp_path}" "{remote_script_path}"'
            copy_result = subprocess.run(copy_cmd, shell=True, capture_output=True, text=True)
            
            if copy_result.returncode != 0:
                self.finished_signal.emit(False, f"Failed to copy script: {copy_result.stderr or copy_result.stdout}")
                return
                
            # Create a scheduled task with proper timing and parameters
            self.progress_update.emit("Creating scheduled task on remote PC...")
            current_time = time.localtime(time.time() + 60)  # Schedule 1 minute from now
            scheduled_time = time.strftime("%H:%M", current_time)
            
            task_cmd = (
                f'schtasks /create /s {self.hostname} /u {self.username} /p {self.password} '
                f'/tn "WinRMSetup" /tr "powershell.exe -ExecutionPolicy Bypass -File C:\\winrm_setup.ps1" '
                f'/sc once /st {scheduled_time} /ru SYSTEM /f'
            )
            task_result = subprocess.run(task_cmd, shell=True, capture_output=True, text=True)
            
            if task_result.returncode != 0:
                self.finished_signal.emit(False, f"Failed to create scheduled task: {task_result.stderr or task_result.stdout}")
                return
                
            # Run the task
            self.progress_update.emit("Running scheduled task...")
            run_task_cmd = f'schtasks /run /s {self.hostname} /u {self.username} /p {self.password} /tn "WinRMSetup"'
            run_result = subprocess.run(run_task_cmd, shell=True, capture_output=True, text=True)
            
            if run_result.returncode != 0:
                self.finished_signal.emit(False, f"Failed to run scheduled task: {run_result.stderr or run_result.stdout}")
                return
                
            # Wait for task to complete with progress updates
            self.progress_update.emit("Waiting for WinRM setup to complete...")
            for i in range(1, 11):  # Wait up to 10 seconds with updates
                time.sleep(1)
                if i % 2 == 0:
                    self.progress_update.emit(f"Waiting for WinRM setup to complete... ({i}s)")
                    
            # Check for success marker file
            self.progress_update.emit("Verifying WinRM setup...")
            if os.path.exists(f'\\\\{self.hostname}\\admin$\\winrm_setup_success.txt'):
                self.progress_update.emit("WinRM setup completed successfully!")
            
            # Clean up
            self.progress_update.emit("Cleaning up...")
            try:
                # Delete the task
                del_task_cmd = f'schtasks /delete /s {self.hostname} /u {self.username} /p {self.password} /tn "WinRMSetup" /f'
                subprocess.run(del_task_cmd, shell=True, capture_output=True)
                
                # Delete the script and marker files
                subprocess.run(f'del "\\\\{self.hostname}\\admin$\\winrm_setup.ps1"', shell=True, capture_output=True)
                subprocess.run(f'del "\\\\{self.hostname}\\admin$\\winrm_setup_success.txt"', shell=True, capture_output=True)
                subprocess.run(f'del "\\\\{self.hostname}\\admin$\\winrm_setup_error.txt"', shell=True, capture_output=True)
            except Exception as e:
                self.progress_update.emit(f"Cleanup warning: {str(e)}")
                
            # Disconnect network drive
            net_del_cmd = f'net use \\\\{self.hostname}\\admin$ /delete'
            subprocess.run(net_del_cmd, shell=True, capture_output=True)
            
            # Test WinRM
            self.progress_update.emit("Testing WinRM connection...")
            test_cmd = f'powershell Test-WSMan -ComputerName {self.hostname}'
            result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                self.finished_signal.emit(True, "WinRM successfully enabled!")
            else:
                self.finished_signal.emit(False, f"WinRM setup completed but test failed: {result.stderr}")
                
        except subprocess.CalledProcessError as e:
            self.finished_signal.emit(False, f"Command failed: {e.stderr.decode() if hasattr(e, 'stderr') else str(e)}")
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    def _enable_with_psexec(self):
        """Enable WinRM using PsExec."""
        self.progress_update.emit("Using PsExec to enable WinRM...")
        
        try:
            # Check if PsExec is available
            psexec_check = subprocess.run('where psexec', shell=True, capture_output=True)
            if psexec_check.returncode != 0:
                self.finished_signal.emit(False, "PsExec not found. Please install PsExec from Sysinternals.")
                return
                
            # Execute command
            cmd = f'psexec \\\\{self.hostname} -u {self.username} -p {self.password} -h -d powershell.exe -Command "Enable-PSRemoting -Force; Set-Item WSMan:\\localhost\\Client\\TrustedHosts -Value \\"*\\" -Force; Restart-Service WinRM"'
            self.progress_update.emit("Executing PsExec command...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Test WinRM
                self.progress_update.emit("Testing WinRM connection...")
                test_cmd = f'powershell Test-WSMan -ComputerName {self.hostname}'
                test_result = subprocess.run(test_cmd, shell=True, capture_output=True, text=True)
                
                if test_result.returncode == 0:
                    self.finished_signal.emit(True, "WinRM successfully enabled!")
                else:
                    self.finished_signal.emit(False, f"WinRM setup completed but test failed: {test_result.stderr}")
            else:
                self.finished_signal.emit(False, f"PsExec command failed: {result.stderr}")
                
        except Exception as e:
            self.finished_signal.emit(False, str(e))

class EnableWinRMDialog(QDialog):
    """Dialog for enabling WinRM remotely."""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Enable WinRM Remotely")
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize the dialog UI."""
        layout = QVBoxLayout(self)
        
        # Info label
        info_label = QLabel(
            "<b>Enable PowerShell Remoting (WinRM) Remotely</b><br><br>"
            "This tool will help you enable PowerShell Remoting on a remote PC.<br>"
            "You must have administrator access to the remote PC."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Form layout
        form_layout = QFormLayout()
        
        self.hostname_edit = QLineEdit()
        self.username_edit = QLineEdit()
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        
        form_layout.addRow("Hostname:", self.hostname_edit)
        form_layout.addRow("Username:", self.username_edit)
        form_layout.addRow("Password:", self.password_edit)
        
        # Method selection
        self.psexec_checkbox = QCheckBox("Use PsExec (must be installed separately)")
        form_layout.addRow("", self.psexec_checkbox)
        
        layout.addLayout(form_layout)
        
        # Progress
        self.progress_label = QLabel("Ready")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        # Buttons
        button_layout = QVBoxLayout()
        
        self.enable_btn = QPushButton("Enable WinRM")
        self.enable_btn.clicked.connect(self.enable_winrm)
        
        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        
        button_layout.addWidget(self.enable_btn)
        button_layout.addWidget(self.close_btn)
        
        layout.addLayout(button_layout)
        
        # Set dialog size
        self.resize(400, 300)
        
    def enable_winrm(self):
        """Enable WinRM on the remote PC."""
        hostname = self.hostname_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        use_psexec = self.psexec_checkbox.isChecked()
        
        if not all([hostname, username, password]):
            QMessageBox.warning(self, "Warning", "Please fill in all fields")
            return
            
        # Confirm
        reply = QMessageBox.question(
            self,
            "Confirm Action",
            f"This will enable PowerShell Remoting on {hostname}.\n\nContinue?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
            
        # Disable UI
        self.enable_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_label.setText("Starting...")
        
        # Start thread
        self.thread = WinRMEnablerThread(hostname, username, password, use_psexec)
        self.thread.progress_update.connect(self.update_progress)
        self.thread.finished_signal.connect(self.process_finished)
        self.thread.start()
        
    def update_progress(self, message):
        """Update progress label."""
        self.progress_label.setText(message)
        
    def process_finished(self, success, message):
        """Handle process completion."""
        self.progress_bar.setVisible(False)
        self.enable_btn.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
            
        self.progress_label.setText("Ready")
