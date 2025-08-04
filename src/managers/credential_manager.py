"""Windows credential management."""
import win32cred
import win32con
import pywintypes
from src.core.logger import setup_logger

# Try to import win32credui, but don't fail if it's not available
try:
    import win32credui
    HAS_CREDUI = True
except ImportError:
    HAS_CREDUI = False

class CredentialManager:
    """Manager for Windows credential operations."""
    
    def __init__(self):
        """Initialize credential manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_credentials(self, target_filter=None):
        """Get list of stored credentials.
        
        Args:
            target_filter: Optional filter for credential targets
            
        Returns:
            list: List of credential info dictionaries
        """
        credentials = []
        try:
            # Get all credentials
            creds = win32cred.CredEnumerate(None, 0)
            
            # Filter credentials if target_filter is specified
            if target_filter:
                creds = [c for c in creds if target_filter.lower() in c['TargetName'].lower()]
                
            for cred in creds:
                # Convert binary data to more readable format
                if cred['CredentialBlob']:
                    try:
                        password = cred['CredentialBlob'].decode('utf-16')
                    except UnicodeDecodeError:
                        password = "[Binary data]"
                else:
                    password = ""
                
                # Create credential info dictionary
                credential_info = {
                    'target_name': cred['TargetName'],
                    'username': cred['UserName'] if cred['UserName'] else '',
                    'comment': cred['Comment'] if cred['Comment'] else '',
                    'type': self._get_credential_type_name(cred['Type']),
                    'persist': self._get_persistence_type_name(cred['Persist']),
                    'last_written': cred['LastWritten'],
                    'password': password,
                    'attributes': cred.get('Attributes', [])
                }
                credentials.append(credential_info)
                
            return credentials
        except Exception as e:
            self.logger.error(f"Failed to get credentials: {str(e)}")
            return []
    
    def add_credential(self, target_name, username, password, 
                      credential_type=win32cred.CRED_TYPE_GENERIC, 
                      persistence=win32cred.CRED_PERSIST_LOCAL_MACHINE,
                      comment=""):
        """Add a new credential.
        
        Args:
            target_name: Target name for the credential
            username: Username
            password: Password
            credential_type: Credential type (default: CRED_TYPE_GENERIC)
            persistence: Persistence type (default: CRED_PERSIST_LOCAL_MACHINE)
            comment: Optional comment
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            credential = {
                'Type': credential_type,
                'TargetName': target_name,
                'UserName': username,
                'CredentialBlob': password,
                'Comment': comment,
                'Persist': persistence
            }
            
            win32cred.CredWrite(credential, 0)
            self.logger.info(f"Added credential for target: {target_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add credential: {str(e)}")
            return False
            
    def update_credential(self, target_name, username=None, password=None, 
                         credential_type=None, persistence=None, comment=None):
        """Update an existing credential.
        
        Args:
            target_name: Target name of credential to update
            username: New username (optional)
            password: New password (optional)
            credential_type: New credential type (optional)
            persistence: New persistence type (optional)
            comment: New comment (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get existing credential
            cred = win32cred.CredRead(target_name, win32cred.CRED_TYPE_GENERIC, 0)
            
            # Update fields
            if username is not None:
                cred['UserName'] = username
            if password is not None:
                cred['CredentialBlob'] = password
            if credential_type is not None:
                cred['Type'] = credential_type
            if persistence is not None:
                cred['Persist'] = persistence
            if comment is not None:
                cred['Comment'] = comment
                
            # Write updated credential
            win32cred.CredWrite(cred, 0)
            self.logger.info(f"Updated credential for target: {target_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update credential: {str(e)}")
            return False
            
    def delete_credential(self, target_name, credential_type=win32cred.CRED_TYPE_GENERIC):
        """Delete a credential.
        
        Args:
            target_name: Target name of credential to delete
            credential_type: Type of credential to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32cred.CredDelete(target_name, credential_type, 0)
            self.logger.info(f"Deleted credential for target: {target_name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete credential: {str(e)}")
            return False
            
    def prompt_for_credentials(self, target_name, message="Please enter your credentials"):
        """Show a credential prompt dialog.
        
        Args:
            target_name: Target name for the credential
            message: Message to display in the dialog
            
        Returns:
            tuple: (username, password, save_credential) or (None, None, False) if canceled
        """
        # Check if win32credui is available
        if not HAS_CREDUI:
            self.logger.error("win32credui module is not available. Cannot prompt for credentials.")
            return None, None, False
            
        try:
            flags = win32credui.CREDUI_FLAGS_GENERIC_CREDENTIALS | \
                   win32credui.CREDUI_FLAGS_ALWAYS_SHOW_UI | \
                   win32credui.CREDUI_FLAGS_DO_NOT_PERSIST
                   
            result, cred = win32credui.CredUIPromptForCredentials(
                target_name,
                0,
                "",
                None,
                False,
                flags,
                {})
                
            if result == 0:  # NO_ERROR
                return cred[0], cred[1], cred[2]
            else:
                return None, None, False
        except Exception as e:
            self.logger.error(f"Failed to prompt for credentials: {str(e)}")
            return None, None, False
            
    def _get_credential_type_name(self, type_id):
        """Convert credential type ID to readable name.
        
        Args:
            type_id: Credential type ID
            
        Returns:
            str: Readable credential type name
        """
        types = {
            win32cred.CRED_TYPE_GENERIC: "Generic",
            win32cred.CRED_TYPE_DOMAIN_PASSWORD: "Domain Password",
            win32cred.CRED_TYPE_DOMAIN_CERTIFICATE: "Domain Certificate",
            win32cred.CRED_TYPE_DOMAIN_VISIBLE_PASSWORD: "Domain Visible Password",
            win32cred.CRED_TYPE_GENERIC_CERTIFICATE: "Generic Certificate",
            win32cred.CRED_TYPE_DOMAIN_EXTENDED: "Domain Extended"
        }
        return types.get(type_id, f"Unknown ({type_id})")
        
    def _get_persistence_type_name(self, persist_id):
        """Convert persistence type ID to readable name.
        
        Args:
            persist_id: Persistence type ID
            
        Returns:
            str: Readable persistence type name
        """
        types = {
            win32cred.CRED_PERSIST_SESSION: "Session",
            win32cred.CRED_PERSIST_LOCAL_MACHINE: "Local Machine",
            win32cred.CRED_PERSIST_ENTERPRISE: "Enterprise"
        }
        return types.get(persist_id, f"Unknown ({persist_id})")
