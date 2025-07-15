"""Default configuration values."""

def get_default_config():
    """Get default configuration.
    
    Returns:
        dict: Default configuration structure
    """
    return {
        'environment': {
            'system': {},
            'user': {}
        },
        'registry': [],
        'users': {
            'users': [],
            'groups': []
        },
        'services': [],
        'firewall': {
            'inbound': [],
            'outbound': []
        },
        'software': {
            'install': [],
            'uninstall': []
        },
        'permissions': [],
        'applications': {
            'startup': [],
            'processes': []
        }
    }

def get_default_registry_entry():
    """Get default registry entry structure.
    
    Returns:
        dict: Default registry entry
    """
    return {
        'path': '',
        'name': '',
        'type': 'REG_SZ',
        'value': ''
    }

def get_default_user():
    """Get default user entry structure.
    
    Returns:
        dict: Default user entry
    """
    return {
        'username': '',
        'password': '',
        'full_name': '',
        'description': '',
        'groups': [],
        'disabled': False,
        'never_expires': True
    }

def get_default_group():
    """Get default group entry structure.
    
    Returns:
        dict: Default group entry
    """
    return {
        'name': '',
        'description': '',
        'members': []
    }

def get_default_service():
    """Get default service entry structure.
    
    Returns:
        dict: Default service entry
    """
    return {
        'name': '',
        'display_name': '',
        'description': '',
        'path': '',
        'startup_type': 'auto',
        'state': 'running',
        'dependencies': []
    }

def get_default_firewall_rule():
    """Get default firewall rule structure.
    
    Returns:
        dict: Default firewall rule
    """
    return {
        'name': '',
        'description': '',
        'direction': 'inbound',
        'action': 'allow',
        'protocol': 'TCP',
        'local_ports': [],
        'remote_ports': [],
        'local_addresses': [],
        'remote_addresses': [],
        'program': '',
        'service': '',
        'enabled': True
    }

def get_default_software_install():
    """Get default software installation entry structure.
    
    Returns:
        dict: Default software installation entry
    """
    return {
        'path': '',
        'arguments': '',
        'wait': True,
        'success_codes': [0],
        'method': 'msi'  # or 'exe'
    }

def get_default_permission():
    """Get default permission entry structure.
    
    Returns:
        dict: Default permission entry
    """
    return {
        'path': '',
        'user': '',
        'permissions': {
            'read': True,
            'write': False,
            'execute': False,
            'modify': False,
            'full_control': False
        },
        'inherit': True,
        'propagate': True
    }

def get_default_startup_app():
    """Get default startup application entry structure.
    
    Returns:
        dict: Default startup application entry
    """
    return {
        'name': '',
        'path': '',
        'arguments': '',
        'run_as': '',
        'wait': False
    }

def get_default_process():
    """Get default process entry structure.
    
    Returns:
        dict: Default process entry
    """
    return {
        'name': '',
        'path': '',
        'arguments': '',
        'working_dir': '',
        'run_as': '',
        'wait': True,
        'window': 'normal'  # normal, minimized, maximized, hidden
    }
