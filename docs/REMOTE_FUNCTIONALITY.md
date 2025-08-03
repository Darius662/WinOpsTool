# WinOpsTool Remote Functionality

This document describes how remote functionality is implemented in WinOpsTool, focusing on how panels reset and repopulate with data from connected remote PCs.

## Architecture Overview

The remote functionality in WinOpsTool follows these key principles:

1. **Consistent UI Experience**: Panels maintain the same UI and functionality whether operating locally or remotely.
2. **Dynamic Data Source Switching**: Panels can switch between local and remote data sources seamlessly.
3. **Centralized Remote Management**: The `RemoteManager` class handles all remote operations.
4. **Panel Independence**: Each panel is responsible for its own remote data handling.

## Core Components

### BasePanel

The `BasePanel` class has been enhanced to support remote operations:

- **Remote Mode Flag**: `is_remote_mode` indicates whether the panel is operating in remote mode.
- **Remote Manager Reference**: `remote_manager` holds a reference to the `RemoteManager` instance.
- **Data Source Methods**:
  - `load_data()`: Loads data from either local or remote source based on `is_remote_mode`.
  - `load_local_data()`: Loads data from the local system.
  - `load_remote_data()`: Loads data from the remote system.
  - `save_local_data()`: Saves data to the local system.
  - `save_remote_data()`: Saves data to the remote system.
  - `clear_data()`: Clears all data in the panel.
- **Remote Mode Switching**: `set_remote_mode(is_remote, remote_manager)` handles switching between local and remote modes.
- **Remote Application**: `apply_remote(remote_connection)` applies panel changes to a remote system.

### PanelManager

The `PanelManager` coordinates remote state updates across all panels:

- **Remote State Updates**: `update_remote_state(connected, remote_manager)` updates all panels' remote state.
- **Panel Refresh**: Forces a refresh of the current tab after remote state changes.

### RemoteHandler

The `RemoteHandler` manages remote connections and notifies panels of state changes:

- **Connection Management**: Handles connecting to and disconnecting from remote systems.
- **Panel Notification**: Calls `panel_manager.update_remote_state()` when connection state changes.
- **Remote Manager Access**: Provides panels with access to the `RemoteManager` instance.

## Remote Workflow

### Connection Establishment

1. User initiates a remote connection via the UI.
2. `RemoteHandler.connect()` shows a connection dialog and establishes the connection.
3. On successful connection, `RemoteHandler.enable_remote_features()` is called.
4. `RemoteHandler` calls `panel_manager.update_remote_state(True, remote_manager)`.
5. `PanelManager` iterates through all panels and calls `panel.set_remote_mode(True, remote_manager)`.
6. Each panel clears its data and loads remote data.

### Remote Data Loading

When a panel is in remote mode:

1. `panel.load_data()` calls `panel.load_remote_data()`.
2. `load_remote_data()` uses the `remote_manager` to fetch data from the remote system.
3. Panel UI is updated with remote data.

### Disconnection

1. User initiates disconnection via the UI.
2. `RemoteHandler.disconnect()` disconnects from the remote system.
3. `RemoteHandler.disable_remote_features()` is called.
4. `RemoteHandler` calls `panel_manager.update_remote_state(False, None)`.
5. `PanelManager` iterates through all panels and calls `panel.set_remote_mode(False, None)`.
6. Each panel clears its data and loads local data.

## Implementing Remote Support in Panels

To add remote support to a panel:

1. **Inherit from BasePanel**: Ensure your panel inherits from `BasePanel`.

2. **Implement Required Methods**:
   ```python
   def clear_data(self):
       """Clear all data in the panel."""
       # Clear UI components and data structures
       
   def load_local_data(self):
       """Load data from the local system."""
       # Fetch and display local data
       
   def load_remote_data(self):
       """Load data from the remote system."""
       # Use self.remote_manager to fetch remote data
       # Update UI with remote data
   ```

3. **Implement Remote Operations** (optional):
   ```python
   def apply_remote(self, remote_connection):
       """Apply panel changes to a remote system."""
       # Apply changes to the remote system
       # Return True on success, False on failure
   ```

## Example: Environment Panel

The Environment Panel demonstrates a complete implementation of remote functionality:

```python
def clear_data(self):
    """Clear all data in the panel."""
    if self.variables_view:
        self.variables_view.clear()
    
def load_local_data(self):
    """Load environment variables from the local system."""
    try:
        user_vars = self.manager.get_user_variables()
        system_vars = self.manager.get_system_variables()
        self.variables_view.update_variables(user_vars, system_vars)
    except Exception as e:
        self.logger.error(f"Error loading local environment variables: {str(e)}")
        self.show_error(f"Failed to load environment variables: {str(e)}")

def load_remote_data(self):
    """Load environment variables from the remote system."""
    if not self.remote_manager or not self.remote_manager.is_connected():
        self.logger.error("No remote connection available")
        self.show_error("No remote connection available")
        return
        
    try:
        # Execute PowerShell to get environment variables remotely
        ps_script = """
        $userVars = [Environment]::GetEnvironmentVariables('User') | ConvertTo-Json
        $systemVars = [Environment]::GetEnvironmentVariables('Machine') | ConvertTo-Json
        $result = @{
            'UserVars' = $userVars
            'SystemVars' = $systemVars
        } | ConvertTo-Json
        return $result
        """
        
        result = self.remote_manager.process_manager.execute_powershell(ps_script)
        if result and result.get('success', False):
            # Parse and display remote environment variables
            # ...
        else:
            # Handle error
            # ...
    except Exception as e:
        self.logger.error(f"Error loading remote environment variables: {str(e)}")
        self.show_error(f"Failed to load remote environment variables: {str(e)}")
```

## Testing Remote Functionality

A test suite is available in `tests/test_remote_functionality.py` to verify that panels correctly handle remote mode switching and data loading.

## Best Practices

1. **Clear Before Loading**: Always clear panel data before loading new data.
2. **Error Handling**: Implement robust error handling in remote operations.
3. **UI Feedback**: Provide clear feedback to users during remote operations.
4. **Consistent Interface**: Maintain consistent UI behavior between local and remote modes.
5. **Remote Manager Usage**: Always use the provided `remote_manager` for remote operations.
6. **Data Separation**: Keep clear separation between local and remote data sources.
