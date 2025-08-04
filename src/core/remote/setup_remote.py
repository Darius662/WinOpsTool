"""
WinOpsTool Remote Setup Utility

This script helps users set up remote connections and integrate the REST API
functionality into their existing WinOpsTool installation.
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path

# Add the parent directory to the path so we can import our modules
script_dir = Path(__file__).parent
sys.path.append(str(script_dir.parent.parent.parent))

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("remote_setup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("remote_setup")

# Import the necessary modules
from src.core.remote.integration import RemoteIntegration
from src.api_server.deploy_remote import create_deployment_package, deploy_to_remote

class RemoteSetup:
    """Setup utility for WinOpsTool remote functionality"""
    
    def __init__(self):
        """Initialize the setup utility"""
        self.remote_integration = RemoteIntegration()
        self.config_file = Path.home() / ".winopstool" / "remote_config.json"
        self.connections = []
        
        # Create the config directory if it doesn't exist
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Load existing connections
        self.load_connections()
    
    def load_connections(self):
        """Load existing connections from the config file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, "r") as f:
                    self.connections = json.load(f)
                logger.info(f"Loaded {len(self.connections)} connections from {self.config_file}")
            except Exception as e:
                logger.error(f"Failed to load connections: {str(e)}")
                self.connections = []
        else:
            logger.info(f"No existing connections found at {self.config_file}")
            self.connections = []
    
    def save_connections(self):
        """Save connections to the config file"""
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.connections, f, indent=2)
            logger.info(f"Saved {len(self.connections)} connections to {self.config_file}")
            return True
        except Exception as e:
            logger.error(f"Failed to save connections: {str(e)}")
            return False
    
    def list_connections(self):
        """List all connections"""
        if not self.connections:
            print("No connections found.")
            return
        
        print("\nRemote Connections:")
        print("-" * 80)
        print(f"{'Name':<20} {'Hostname':<30} {'Port':<10} {'Connected':<10}")
        print("-" * 80)
        
        for conn in self.connections:
            name = conn.get("name", "")
            hostname = conn.get("hostname", "")
            port = conn.get("port", 8000)
            
            # Check if connected
            is_connected = self.remote_integration.is_connected_to_remote(name)
            status = "Yes" if is_connected else "No"
            
            print(f"{name:<20} {hostname:<30} {port:<10} {status:<10}")
        
        print("-" * 80)
    
    def add_connection(self, name, hostname, api_key, port=8000):
        """Add a new connection"""
        # Check if the connection already exists
        for conn in self.connections:
            if conn.get("name") == name:
                logger.error(f"Connection with name '{name}' already exists")
                return False
        
        # Add the connection
        self.connections.append({
            "name": name,
            "hostname": hostname,
            "api_key": api_key,
            "port": port
        })
        
        # Save the connections
        if self.save_connections():
            logger.info(f"Added connection '{name}' to {hostname}:{port}")
            return True
        else:
            logger.error(f"Failed to add connection '{name}'")
            return False
    
    def remove_connection(self, name):
        """Remove a connection"""
        # Check if connected
        if self.remote_integration.is_connected_to_remote(name):
            # Disconnect first
            self.remote_integration.disconnect_from_remote(name)
        
        # Remove the connection
        for i, conn in enumerate(self.connections):
            if conn.get("name") == name:
                self.connections.pop(i)
                
                # Save the connections
                if self.save_connections():
                    logger.info(f"Removed connection '{name}'")
                    return True
                else:
                    logger.error(f"Failed to remove connection '{name}'")
                    return False
        
        logger.error(f"Connection '{name}' not found")
        return False
    
    def connect(self, name):
        """Connect to a remote machine"""
        # Find the connection
        conn = next((c for c in self.connections if c.get("name") == name), None)
        
        if not conn:
            logger.error(f"Connection '{name}' not found")
            return False
        
        # Connect to the remote machine
        result = self.remote_integration.connect_to_remote(
            name=conn.get("name"),
            hostname=conn.get("hostname"),
            api_key=conn.get("api_key"),
            port=conn.get("port", 8000)
        )
        
        if result:
            logger.info(f"Connected to '{name}'")
            return True
        else:
            logger.error(f"Failed to connect to '{name}'")
            return False
    
    def disconnect(self, name):
        """Disconnect from a remote machine"""
        result = self.remote_integration.disconnect_from_remote(name)
        
        if result:
            logger.info(f"Disconnected from '{name}'")
            return True
        else:
            logger.error(f"Failed to disconnect from '{name}'")
            return False
    
    def deploy_server(self, hostname, username=None, password=None):
        """Deploy the API server to a remote machine"""
        # Create a deployment package
        package_path = create_deployment_package()
        
        if not package_path:
            logger.error("Failed to create deployment package")
            return False
        
        # Deploy to the remote machine
        result = deploy_to_remote(hostname, username, password, package_path)
        
        if not result["success"]:
            logger.error(f"Failed to deploy to {hostname}: {result.get('error')}")
            return False
        
        # Add the connection
        api_key = result.get("api_key")
        port = result.get("port", 8000)
        
        if not api_key:
            logger.error("Failed to get API key from deployment")
            return False
        
        # Generate a name for the connection
        name = f"Remote-{hostname}"
        
        # Add the connection
        if self.add_connection(name, hostname, api_key, port):
            logger.info(f"Added connection '{name}' with API key: {api_key}")
            
            # Connect to the remote machine
            if self.connect(name):
                logger.info(f"Connected to '{name}'")
                return True
            else:
                logger.error(f"Failed to connect to '{name}'")
                return False
        else:
            logger.error(f"Failed to add connection '{name}'")
            return False
    
    def test_connection(self, name):
        """Test a connection"""
        # Find the connection
        conn = next((c for c in self.connections if c.get("name") == name), None)
        
        if not conn:
            logger.error(f"Connection '{name}' not found")
            return False
        
        # Connect to the remote machine if not already connected
        if not self.remote_integration.is_connected_to_remote(name):
            result = self.remote_integration.connect_to_remote(
                name=conn.get("name"),
                hostname=conn.get("hostname"),
                api_key=conn.get("api_key"),
                port=conn.get("port", 8000)
            )
            
            if not result:
                logger.error(f"Failed to connect to '{name}'")
                return False
        
        # Get the manager factory
        manager_factory = self.remote_integration.get_manager_factory()
        
        if not manager_factory:
            logger.error("Failed to get manager factory")
            return False
        
        # Test system info
        system_manager = manager_factory.get_system_manager()
        system_info = system_manager.get_system_info()
        
        if not system_info:
            logger.error("Failed to get system info")
            return False
        
        # Print system info
        print(f"\nConnection to '{name}' successful!")
        print(f"System: {system_info.get('os_name')} {system_info.get('os_version')}")
        print(f"Hostname: {system_info.get('hostname')}")
        print(f"Processor: {system_info.get('processor')}")
        
        logger.info(f"Connection test for '{name}' successful")
        return True

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="WinOpsTool Remote Setup Utility")
    
    # Add subparsers for commands
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # List command
    list_parser = subparsers.add_parser("list", help="List all connections")
    
    # Add command
    add_parser = subparsers.add_parser("add", help="Add a new connection")
    add_parser.add_argument("--name", required=True, help="Name of the connection")
    add_parser.add_argument("--hostname", required=True, help="Hostname or IP address")
    add_parser.add_argument("--api-key", required=True, help="API key for authentication")
    add_parser.add_argument("--port", type=int, default=8000, help="Port number (default: 8000)")
    
    # Remove command
    remove_parser = subparsers.add_parser("remove", help="Remove a connection")
    remove_parser.add_argument("--name", required=True, help="Name of the connection")
    
    # Connect command
    connect_parser = subparsers.add_parser("connect", help="Connect to a remote machine")
    connect_parser.add_argument("--name", required=True, help="Name of the connection")
    
    # Disconnect command
    disconnect_parser = subparsers.add_parser("disconnect", help="Disconnect from a remote machine")
    disconnect_parser.add_argument("--name", required=True, help="Name of the connection")
    
    # Deploy command
    deploy_parser = subparsers.add_parser("deploy", help="Deploy the API server to a remote machine")
    deploy_parser.add_argument("--hostname", required=True, help="Hostname or IP address")
    deploy_parser.add_argument("--username", help="Username for authentication")
    deploy_parser.add_argument("--password", help="Password for authentication")
    
    # Test command
    test_parser = subparsers.add_parser("test", help="Test a connection")
    test_parser.add_argument("--name", required=True, help="Name of the connection")
    
    args = parser.parse_args()
    
    # Create the setup utility
    setup = RemoteSetup()
    
    # Process commands
    if args.command == "list":
        setup.list_connections()
    elif args.command == "add":
        setup.add_connection(args.name, args.hostname, args.api_key, args.port)
    elif args.command == "remove":
        setup.remove_connection(args.name)
    elif args.command == "connect":
        setup.connect(args.name)
    elif args.command == "disconnect":
        setup.disconnect(args.name)
    elif args.command == "deploy":
        setup.deploy_server(args.hostname, args.username, args.password)
    elif args.command == "test":
        setup.test_connection(args.name)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
