"""Windows Permissions management."""
import os
import win32security
import win32api
import win32con
import ntsecuritycon
from typing import List, Dict, Any, Tuple
from src.core.logger import setup_logger

class PermissionsManager:
    """Manager for Windows file and folder permissions."""
    
    # Common permission masks
    PERMISSION_MASKS = {
        "Full Control": ntsecuritycon.FILE_ALL_ACCESS,
        "Modify": ntsecuritycon.FILE_GENERIC_WRITE | ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
        "Read & Execute": ntsecuritycon.FILE_GENERIC_READ | ntsecuritycon.FILE_GENERIC_EXECUTE,
        "List Folder Contents": ntsecuritycon.FILE_LIST_DIRECTORY,
        "Read": ntsecuritycon.FILE_GENERIC_READ,
        "Write": ntsecuritycon.FILE_GENERIC_WRITE
    }
    
    def __init__(self):
        """Initialize permissions manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_permissions(self, path: str) -> List[Dict[str, Any]]:
        """Get permissions for a path.
        
        Args:
            path: Path to get permissions for
            
        Returns:
            list: List of permission dictionaries with properties
        """
        try:
            permissions = []
            
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Get DACL
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                return permissions
                
            # Get ACEs
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                sid = ace[2]
                mask = ace[1]
                
                try:
                    name, domain, type = win32security.LookupAccountSid(None, sid)
                    type_str = win32security.ConvertSidToStringSid(sid)
                    
                    # Get permission names
                    perm_names = []
                    for perm_name, perm_mask in self.PERMISSION_MASKS.items():
                        if mask & perm_mask == perm_mask:
                            perm_names.append(perm_name)
                            
                    permissions.append({
                        'name': name,
                        'domain': domain,
                        'type': type_str,
                        'permissions': perm_names,
                        'mask': mask
                    })
                    
                except win32security.error:
                    continue
                    
            return sorted(permissions, key=lambda p: p['name'].lower())
            
        except Exception as e:
            self.logger.error(f"Failed to get permissions for {path}: {str(e)}")
            return []
            
    def add_permission(self, path: str, name: str, mask: int) -> bool:
        """Add a permission.
        
        Args:
            path: Path to add permission to
            name: User/group name
            mask: Permission mask
            
        Returns:
            bool: True if successful
        """
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Get DACL
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                dacl = win32security.ACL()
                
            # Get SID for user/group
            try:
                domain = win32security.LookupAccountName(None, name)[0]
            except win32security.error:
                self.logger.error(f"User or group '{name}' not found")
                return False
                
            # Add ACE
            dacl.AddAccessAllowedAce(
                win32security.ACL_REVISION,
                mask,
                domain
            )
            
            # Set DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
            self.logger.info(f"Added permission for {name} on {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to add permission: {str(e)}")
            return False
            
    def edit_permission(self, path: str, name: str, mask: int) -> bool:
        """Edit a permission.
        
        Args:
            path: Path to edit permission on
            name: User/group name
            mask: New permission mask
            
        Returns:
            bool: True if successful
        """
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Get DACL
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                return False
                
            # Get SID for user/group
            try:
                domain = win32security.LookupAccountName(None, name)[0]
            except win32security.error:
                self.logger.error(f"User or group '{name}' not found")
                return False
                
            # Find and replace ACE
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                sid = ace[2]
                if sid == domain:
                    dacl.DeleteAce(i)
                    dacl.AddAccessAllowedAce(
                        win32security.ACL_REVISION,
                        mask,
                        domain
                    )
                    break
                    
            # Set DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
            self.logger.info(f"Updated permission for {name} on {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to edit permission: {str(e)}")
            return False
            
    def remove_permission(self, path: str, name: str) -> bool:
        """Remove a permission.
        
        Args:
            path: Path to remove permission from
            name: User/group name
            
        Returns:
            bool: True if successful
        """
        try:
            # Get security descriptor
            sd = win32security.GetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION
            )
            
            # Get DACL
            dacl = sd.GetSecurityDescriptorDacl()
            if dacl is None:
                return False
                
            # Get SID for user/group
            try:
                domain = win32security.LookupAccountName(None, name)[0]
            except win32security.error:
                self.logger.error(f"User or group '{name}' not found")
                return False
                
            # Find and remove ACE
            for i in range(dacl.GetAceCount()):
                ace = dacl.GetAce(i)
                sid = ace[2]
                if sid == domain:
                    dacl.DeleteAce(i)
                    break
                    
            # Set DACL
            sd.SetSecurityDescriptorDacl(1, dacl, 0)
            win32security.SetFileSecurity(
                path,
                win32security.DACL_SECURITY_INFORMATION,
                sd
            )
            
            self.logger.info(f"Removed permission for {name} on {path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to remove permission: {str(e)}")
            return False
