"""Windows user and group management."""
import win32net
import win32netcon
from src.core.logger import setup_logger

class UserManager:
    """Manager for Windows user accounts."""
    
    def __init__(self):
        """Initialize user manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_users(self):
        """Get list of user accounts.
        
        Returns:
            list: List of user info dictionaries
        """
        users = []
        try:
            resume = 0
            while True:
                user_list, _, resume = win32net.NetUserEnum(
                    None, 1, win32netcon.FILTER_NORMAL_ACCOUNT, resume
                )
                users.extend(user_list)
                if not resume:
                    break
            return users
        except Exception as e:
            self.logger.error(f"Failed to get users: {str(e)}")
            return []
            
    def add_user(self, username, password, full_name, description, disabled=False):
        """Add a new user account.
        
        Args:
            username: Username
            password: Password
            full_name: Full name
            description: Account description
            disabled: Whether account is disabled
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            user_info = {
                'name': username,
                'password': password,
                'comment': description,
                'full_name': full_name,
                'flags': (win32netcon.UF_NORMAL_ACCOUNT |
                         win32netcon.UF_SCRIPT |
                         (win32netcon.UF_ACCOUNTDISABLE if disabled else 0))
            }
            win32net.NetUserAdd(None, 1, user_info)
            self.logger.info(f"Added user: {username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add user: {str(e)}")
            return False
            
    def update_user(self, username, password=None, full_name=None,
                   description=None, disabled=None):
        """Update an existing user account.
        
        Args:
            username: Username to update
            password: New password (optional)
            full_name: New full name (optional)
            description: New description (optional)
            disabled: New disabled state (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current user info
            user_info = win32net.NetUserGetInfo(None, username, 1)
            
            # Update fields
            if password is not None:
                user_info['password'] = password
            if full_name is not None:
                user_info['full_name'] = full_name
            if description is not None:
                user_info['comment'] = description
            if disabled is not None:
                flags = user_info['flags']
                if disabled:
                    flags |= win32netcon.UF_ACCOUNTDISABLE
                else:
                    flags &= ~win32netcon.UF_ACCOUNTDISABLE
                user_info['flags'] = flags
                
            win32net.NetUserSetInfo(None, username, 1, user_info)
            self.logger.info(f"Updated user: {username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update user: {str(e)}")
            return False
            
    def delete_user(self, username):
        """Delete a user account.
        
        Args:
            username: Username to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32net.NetUserDel(None, username)
            self.logger.info(f"Deleted user: {username}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete user: {str(e)}")
            return False

class GroupManager:
    """Manager for Windows user groups."""
    
    def __init__(self):
        """Initialize group manager."""
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_groups(self):
        """Get list of user groups.
        
        Returns:
            list: List of group info dictionaries
        """
        groups = []
        try:
            resume = 0
            while True:
                group_list, _, resume = win32net.NetLocalGroupEnum(None, 1, resume)
                for group in group_list:
                    # Get group members
                    members = []
                    try:
                        member_resume = 0
                        while True:
                            member_list, _, member_resume = win32net.NetLocalGroupGetMembers(
                                None, group['name'], 3, member_resume
                            )
                            members.extend([m['domainandname'] for m in member_list])
                            if not member_resume:
                                break
                    except Exception:
                        pass  # Group might be empty
                        
                    group['members'] = members
                    groups.append(group)
                if not resume:
                    break
            return groups
        except Exception as e:
            self.logger.error(f"Failed to get groups: {str(e)}")
            return []
            
    def add_group(self, name, description, members=None):
        """Add a new user group.
        
        Args:
            name: Group name
            description: Group description
            members: List of member usernames (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            group_info = {
                'name': name,
                'comment': description
            }
            win32net.NetLocalGroupAdd(None, 1, group_info)
            
            # Add members if specified
            if members:
                for member in members:
                    try:
                        win32net.NetLocalGroupAddMembers(None, name, 3, [{
                            'domainandname': member
                        }])
                    except Exception as e:
                        self.logger.error(f"Failed to add member {member} to group {name}: {str(e)}")
                        
            self.logger.info(f"Added group: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to add group: {str(e)}")
            return False
            
    def update_group(self, name, description=None, members=None):
        """Update an existing user group.
        
        Args:
            name: Group name to update
            description: New description (optional)
            members: New list of member usernames (optional)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if description is not None:
                group_info = {
                    'name': name,
                    'comment': description
                }
                win32net.NetLocalGroupSetInfo(None, name, 1, group_info)
                
            if members is not None:
                # Get current members
                current_members = []
                try:
                    member_resume = 0
                    while True:
                        member_list, _, member_resume = win32net.NetLocalGroupGetMembers(
                            None, name, 3, member_resume
                        )
                        current_members.extend([m['domainandname'] for m in member_list])
                        if not member_resume:
                            break
                except Exception:
                    pass  # Group might be empty
                    
                # Remove members not in new list
                for member in current_members:
                    if member not in members:
                        try:
                            win32net.NetLocalGroupDelMembers(None, name, 3, [{
                                'domainandname': member
                            }])
                        except Exception as e:
                            self.logger.error(f"Failed to remove member {member} from group {name}: {str(e)}")
                            
                # Add new members
                for member in members:
                    if member not in current_members:
                        try:
                            win32net.NetLocalGroupAddMembers(None, name, 3, [{
                                'domainandname': member
                            }])
                        except Exception as e:
                            self.logger.error(f"Failed to add member {member} to group {name}: {str(e)}")
                            
            self.logger.info(f"Updated group: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to update group: {str(e)}")
            return False
            
    def delete_group(self, name):
        """Delete a user group.
        
        Args:
            name: Group name to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            win32net.NetLocalGroupDel(None, name)
            self.logger.info(f"Deleted group: {name}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to delete group: {str(e)}")
            return False
