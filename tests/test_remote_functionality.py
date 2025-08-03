"""Test script for remote functionality in WinOpsTool panels.

This script tests the ability of panels to switch between local and remote modes,
reset and repopulate with data from the connected remote PC.
"""
import sys
import os
import unittest
from unittest.mock import MagicMock, patch
from PyQt6.QtWidgets import QApplication

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.ui.base.base_panel import BasePanel
from src.ui.main.panel_manager import PanelManager
from src.core.remote.manager import RemoteManager

class TestRemoteFunctionality(unittest.TestCase):
    """Test remote functionality in WinOpsTool panels."""
    
    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        # Create QApplication instance for Qt widgets
        cls.app = QApplication([])
    
    def setUp(self):
        """Set up test case."""
        # Create mock parent window
        self.mock_parent = MagicMock()
        
        # Create mock remote manager
        self.remote_manager = MagicMock(spec=RemoteManager)
        self.remote_manager.is_connected.return_value = True
        
        # Create panel manager with mock parent
        self.panel_manager = PanelManager(self.mock_parent)
        
    def test_panel_remote_state_update(self):
        """Test that panels update their remote state correctly."""
        # Test connecting to remote
        self.panel_manager.update_remote_state(True, self.remote_manager)
        
        # Check that each panel has been updated
        for panel_name, panel in self.panel_manager.panels.items():
            if isinstance(panel, BasePanel):
                self.assertTrue(hasattr(panel, 'is_remote_mode'), 
                               f"Panel {panel_name} should have is_remote_mode attribute")
                self.assertTrue(panel.is_remote_mode, 
                               f"Panel {panel_name} should be in remote mode")
                self.assertEqual(panel.remote_manager, self.remote_manager,
                                f"Panel {panel_name} should have remote_manager set")
        
        # Test disconnecting from remote
        self.panel_manager.update_remote_state(False, None)
        
        # Check that each panel has been updated
        for panel_name, panel in self.panel_manager.panels.items():
            if isinstance(panel, BasePanel):
                self.assertFalse(panel.is_remote_mode, 
                                f"Panel {panel_name} should not be in remote mode")
                self.assertIsNone(panel.remote_manager,
                                 f"Panel {panel_name} should have remote_manager set to None")
    
    def test_environment_panel_remote_functionality(self):
        """Test environment panel's remote functionality."""
        # Get environment panel
        env_panel = self.panel_manager.panels.get("Environment Variables")
        if not env_panel:
            self.skipTest("Environment Variables panel not found")
        
        # Mock clear_data and load methods
        env_panel.clear_data = MagicMock()
        env_panel.load_local_data = MagicMock()
        env_panel.load_remote_data = MagicMock()
        
        # Test switching to remote mode
        env_panel.set_remote_mode(True, self.remote_manager)
        
        # Verify methods were called
        env_panel.clear_data.assert_called_once()
        env_panel.load_remote_data.assert_called_once()
        env_panel.load_local_data.assert_not_called()
        
        # Reset mocks
        env_panel.clear_data.reset_mock()
        env_panel.load_remote_data.reset_mock()
        
        # Test switching back to local mode
        env_panel.set_remote_mode(False, None)
        
        # Verify methods were called
        env_panel.clear_data.assert_called_once()
        env_panel.load_local_data.assert_called_once()
        env_panel.load_remote_data.assert_not_called()
    
    def test_apply_remote(self):
        """Test applying changes to remote system."""
        # Get environment panel
        env_panel = self.panel_manager.panels.get("Environment Variables")
        if not env_panel:
            self.skipTest("Environment Variables panel not found")
        
        # Create mock remote connection
        remote_connection = MagicMock()
        remote_connection.process_manager.execute_powershell.return_value = {
            'success': True,
            'output': 'true'
        }
        
        # Mock export_config method
        env_panel.export_config = MagicMock(return_value={
            'environment_variables': {
                'user': {'TEST_VAR': 'test_value'},
                'system': {}
            }
        })
        
        # Test apply_remote method
        result = env_panel.apply_remote(remote_connection)
        
        # Verify result
        self.assertTrue(result, "apply_remote should return True on success")
        env_panel.export_config.assert_called_once()
        remote_connection.process_manager.execute_powershell.assert_called_once()
        
        # Test failure case
        remote_connection.process_manager.execute_powershell.return_value = {
            'success': False,
            'error': 'Test error'
        }
        
        # Reset mock
        env_panel.export_config.reset_mock()
        remote_connection.process_manager.execute_powershell.reset_mock()
        
        # Test apply_remote method with failure
        result = env_panel.apply_remote(remote_connection)
        
        # Verify result
        self.assertFalse(result, "apply_remote should return False on failure")
        env_panel.export_config.assert_called_once()
        remote_connection.process_manager.execute_powershell.assert_called_once()

if __name__ == '__main__':
    unittest.main()
