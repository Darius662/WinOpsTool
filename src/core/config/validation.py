"""Configuration validation."""
from src.core.logger import setup_logger

class ConfigValidationError(ValueError):
    """Configuration validation error."""
    pass

def validate_config(config):
    """Validate configuration structure and values.
    
    Args:
        config: Configuration dictionary to validate
        
    Raises:
        ConfigValidationError: If configuration is invalid
    """
    logger = setup_logger("ConfigValidation")
    
    if not isinstance(config, dict):
        raise ConfigValidationError("Configuration must be a dictionary")
        
    # Check required sections
    required_sections = [
        'environment',
        'registry',
        'users',
        'services',
        'firewall',
        'software',
        'permissions',
        'applications'
    ]
    
    for section in required_sections:
        if section not in config:
            raise ConfigValidationError(f"Missing required section: {section}")
            
    # Validate each section
    try:
        validate_environment(config['environment'])
        validate_registry(config['registry'])
        validate_users(config['users'])
        validate_services(config['services'])
        validate_firewall(config['firewall'])
        validate_software(config['software'])
        validate_permissions(config['permissions'])
        validate_applications(config['applications'])
    except ConfigValidationError as e:
        logger.error(f"Configuration validation failed: {str(e)}")
        raise
        
def validate_environment(config):
    """Validate environment variables configuration."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Environment section must be a dictionary")
        
    for var_type in ['system', 'user']:
        if var_type not in config:
            raise ConfigValidationError(
                f"Missing {var_type} section in environment variables"
            )
        if not isinstance(config[var_type], dict):
            raise ConfigValidationError(
                f"Environment {var_type} section must be a dictionary"
            )
            
def validate_registry(config):
    """Validate registry configuration."""
    if not isinstance(config, list):
        raise ConfigValidationError("Registry section must be a list")
        
    for entry in config:
        if not isinstance(entry, dict):
            raise ConfigValidationError("Registry entry must be a dictionary")
        for key in ['path', 'name', 'type', 'value']:
            if key not in entry:
                raise ConfigValidationError(
                    f"Missing {key} in registry entry"
                )
                
def validate_users(config):
    """Validate users configuration."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Users section must be a dictionary")
        
    for section in ['users', 'groups']:
        if section not in config:
            raise ConfigValidationError(f"Missing {section} section")
        if not isinstance(config[section], list):
            raise ConfigValidationError(f"{section} must be a list")
            
def validate_services(config):
    """Validate services configuration."""
    if not isinstance(config, list):
        raise ConfigValidationError("Services section must be a list")
        
    for service in config:
        if not isinstance(service, dict):
            raise ConfigValidationError("Service entry must be a dictionary")
        for key in ['name', 'startup_type', 'state']:
            if key not in service:
                raise ConfigValidationError(
                    f"Missing {key} in service entry"
                )
                
def validate_firewall(config):
    """Validate firewall configuration."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Firewall section must be a dictionary")
        
    for rule_type in ['inbound', 'outbound']:
        if rule_type not in config:
            raise ConfigValidationError(f"Missing {rule_type} rules section")
        if not isinstance(config[rule_type], list):
            raise ConfigValidationError(f"{rule_type} rules must be a list")
            
def validate_software(config):
    """Validate software configuration."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Software section must be a dictionary")
        
    for action in ['install', 'uninstall']:
        if action not in config:
            raise ConfigValidationError(f"Missing {action} section")
        if not isinstance(config[action], list):
            raise ConfigValidationError(f"{action} section must be a list")
            
def validate_permissions(config):
    """Validate permissions configuration."""
    if not isinstance(config, list):
        raise ConfigValidationError("Permissions section must be a list")
        
    for entry in config:
        if not isinstance(entry, dict):
            raise ConfigValidationError("Permission entry must be a dictionary")
        for key in ['path', 'user', 'permissions']:
            if key not in entry:
                raise ConfigValidationError(
                    f"Missing {key} in permission entry"
                )
                
def validate_applications(config):
    """Validate applications configuration."""
    if not isinstance(config, dict):
        raise ConfigValidationError("Applications section must be a dictionary")
        
    for section in ['startup', 'processes']:
        if section not in config:
            raise ConfigValidationError(f"Missing {section} section")
        if not isinstance(config[section], list):
            raise ConfigValidationError(f"{section} section must be a list")
