"""Windows Registry management."""
import winreg
from typing import Optional, Dict, List, Tuple, Any
from src.core.logger import setup_logger

class RegistryManager:
    """Manager for Windows Registry operations."""
    
    # Root key mapping
    ROOT_KEYS = {
        'HKEY_CLASSES_ROOT': winreg.HKEY_CLASSES_ROOT,
        'HKEY_CURRENT_USER': winreg.HKEY_CURRENT_USER,
        'HKEY_LOCAL_MACHINE': winreg.HKEY_LOCAL_MACHINE,
        'HKEY_USERS': winreg.HKEY_USERS,
        'HKEY_CURRENT_CONFIG': winreg.HKEY_CURRENT_CONFIG
    }
    
    # Value type mapping
    VALUE_TYPES = {
        winreg.REG_SZ: 'REG_SZ',
        winreg.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
        winreg.REG_BINARY: 'REG_BINARY',
        winreg.REG_DWORD: 'REG_DWORD',
        winreg.REG_QWORD: 'REG_QWORD',
        winreg.REG_MULTI_SZ: 'REG_MULTI_SZ',
        winreg.REG_NONE: 'REG_NONE'
    }
    
    def __init__(self):
        """Initialize registry manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_root_keys(self) -> List[str]:
        """Get list of root keys.
        
        Returns:
            list: List of root key names
        """
        return list(self.ROOT_KEYS.keys())
        
    def open_key(self, root_key: str, sub_key: str, write: bool = False) -> Optional[winreg.HKEYType]:
        """Open a registry key.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            write: True to open with write access
            
        Returns:
            winreg.HKEYType: Registry key handle or None if failed
        """
        try:
            root = self.ROOT_KEYS.get(root_key)
            if not root:
                self.logger.error(f"Invalid root key: {root_key}")
                return None
                
            access = winreg.KEY_READ | winreg.KEY_WRITE if write else winreg.KEY_READ
            key = winreg.OpenKey(root, sub_key, 0, access)
            return key
            
        except WindowsError as e:
            self.logger.error(f"Failed to open key {root_key}\\{sub_key}: {str(e)}")
            return None
            
    def list_subkeys(self, root_key: str, sub_key: str) -> List[str]:
        """List subkeys of a registry key.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            
        Returns:
            list: List of subkey names
        """
        try:
            key = self.open_key(root_key, sub_key)
            if not key:
                return []
                
            try:
                subkeys = []
                index = 0
                
                while True:
                    try:
                        subkey = winreg.EnumKey(key, index)
                        subkeys.append(subkey)
                        index += 1
                    except WindowsError:
                        break
                        
                return sorted(subkeys)
                
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(f"Failed to list subkeys of {root_key}\\{sub_key}: {str(e)}")
            return []
            
    def list_values(self, root_key: str, sub_key: str) -> List[Dict[str, Any]]:
        """List values in a registry key.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            
        Returns:
            list: List of value dictionaries with name, type, and data
        """
        try:
            key = self.open_key(root_key, sub_key)
            if not key:
                return []
                
            try:
                values = []
                index = 0
                
                while True:
                    try:
                        name, data, type_ = winreg.EnumValue(key, index)
                        
                        # Format binary data
                        if type_ == winreg.REG_BINARY:
                            data = ' '.join([f'{b:02x}' for b in data])
                            
                        # Format multi-string data
                        elif type_ == winreg.REG_MULTI_SZ:
                            data = '\n'.join(data)
                            
                        values.append({
                            'name': name or '(Default)',
                            'type': self.VALUE_TYPES.get(type_, 'Unknown'),
                            'data': str(data)
                        })
                        
                        index += 1
                        
                    except WindowsError:
                        break
                        
                return sorted(values, key=lambda v: v['name'])
                
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(f"Failed to list values in {root_key}\\{sub_key}: {str(e)}")
            return []
            
    def get_value(self, root_key: str, sub_key: str, value_name: str) -> Optional[Tuple[Any, str]]:
        """Get a registry value.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            value_name: Value name
            
        Returns:
            tuple: (value data, value type) or None if failed
        """
        try:
            key = self.open_key(root_key, sub_key)
            if not key:
                return None
                
            try:
                data, type_ = winreg.QueryValueEx(key, value_name)
                
                # Format binary data
                if type_ == winreg.REG_BINARY:
                    data = ' '.join([f'{b:02x}' for b in data])
                    
                # Format multi-string data
                elif type_ == winreg.REG_MULTI_SZ:
                    data = '\n'.join(data)
                    
                return data, self.VALUE_TYPES.get(type_, 'Unknown')
                
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(
                f"Failed to get value {value_name} from {root_key}\\{sub_key}: {str(e)}"
            )
            return None
            
    def set_value(self, root_key: str, sub_key: str, name: str,
                data: Any, type_name: str) -> bool:
        """Set a registry value.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            name: Value name
            data: Value data
            type_name: Value type name (e.g. 'REG_SZ')
            
        Returns:
            bool: True if successful
        """
        try:
            key = self.open_key(root_key, sub_key, write=True)
            if not key:
                return False
                
            try:
                # Get type constant from name
                type_const = None
                for k, v in self.VALUE_TYPES.items():
                    if v == type_name:
                        type_const = k
                        break
                        
                if type_const is None:
                    self.logger.error(f"Invalid value type: {type_name}")
                    return False
                    
                # Convert data based on type
                if type_const == winreg.REG_BINARY:
                    # Convert hex string to bytes
                    try:
                        data = bytes.fromhex(data.replace(' ', ''))
                    except ValueError:
                        self.logger.error("Invalid binary data format")
                        return False
                        
                elif type_const == winreg.REG_MULTI_SZ:
                    # Convert newline-separated string to list
                    data = data.split('\n')
                    
                elif type_const == winreg.REG_DWORD:
                    # Convert string to integer
                    try:
                        data = int(data)
                    except ValueError:
                        self.logger.error("Invalid DWORD value")
                        return False
                        
                elif type_const == winreg.REG_QWORD:
                    # Convert string to integer
                    try:
                        data = int(data)
                    except ValueError:
                        self.logger.error("Invalid QWORD value")
                        return False
                        
                winreg.SetValueEx(key, name, 0, type_const, data)
                return True
                
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(
                f"Failed to set value {name} in {root_key}\\{sub_key}: {str(e)}"
            )
            return False
            
    def delete_value(self, root_key: str, sub_key: str, name: str) -> bool:
        """Delete a registry value.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            name: Value name
            
        Returns:
            bool: True if successful
        """
        try:
            key = self.open_key(root_key, sub_key, write=True)
            if not key:
                return False
                
            try:
                winreg.DeleteValue(key, name)
                return True
                
            finally:
                winreg.CloseKey(key)
                
        except WindowsError as e:
            self.logger.error(
                f"Failed to delete value {name} from {root_key}\\{sub_key}: {str(e)}"
            )
            return False
            
    def create_key(self, root_key: str, sub_key: str) -> bool:
        """Create a new registry key.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            
        Returns:
            bool: True if successful
        """
        try:
            root = self.ROOT_KEYS.get(root_key)
            if not root:
                self.logger.error(f"Invalid root key: {root_key}")
                return False
                
            winreg.CreateKey(root, sub_key)
            return True
            
        except WindowsError as e:
            self.logger.error(f"Failed to create key {root_key}\\{sub_key}: {str(e)}")
            return False
            
    def delete_key(self, root_key: str, sub_key: str) -> bool:
        """Delete a registry key.
        
        Args:
            root_key: Root key name
            sub_key: Sub key path
            
        Returns:
            bool: True if successful
        """
        try:
            root = self.ROOT_KEYS.get(root_key)
            if not root:
                self.logger.error(f"Invalid root key: {root_key}")
                return False
                
            winreg.DeleteKey(root, sub_key)
            return True
            
        except WindowsError as e:
            self.logger.error(f"Failed to delete key {root_key}\\{sub_key}: {str(e)}")
            return False
