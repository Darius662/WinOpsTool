# WinOpsTool REST API Guide

## Overview

This guide explains the REST API architecture for WinOpsTool, which replaces PowerShell Remoting for remote system management. The REST API approach provides a more reliable, secure, and flexible way to manage remote Windows systems.

## Architecture

### Components

1. **REST API Server**: Runs on the remote machine and exposes system management functionality via HTTP endpoints
2. **REST API Client**: Integrated into the main WinOpsTool application to communicate with the server
3. **Remote Manager Classes**: Proxy classes that maintain the same interface as local managers but use the REST API
4. **Manager Factory**: Selects appropriate manager implementations based on local or remote context

### Flow

```
┌─────────────────┐                ┌─────────────────┐
│                 │                │                 │
│   WinOpsTool    │                │   Remote PC     │
│   (Client)      │                │   (Server)      │
│                 │                │                 │
└────────┬────────┘                └────────┬────────┘
         │                                  │
         │                                  │
┌────────▼────────┐                ┌────────▼────────┐
│                 │    HTTP/REST   │                 │
│  Remote Manager ├─────────────────►  REST API      │
│  Classes        │                │  Server         │
│                 │◄─────────────────                │
└────────┬────────┘                └────────┬────────┘
         │                                  │
         │                                  │
┌────────▼────────┐                ┌────────▼────────┐
│                 │                │                 │
│  Manager        │                │  Windows        │
│  Factory        │                │  System APIs    │
│                 │                │                 │
└─────────────────┘                └─────────────────┘
```

## REST API Server

### Installation

#### As a Windows Service (Recommended)

1. Deploy the API server to the remote machine:

```
python src/api_server/deploy_remote.py --deploy --host REMOTE_HOSTNAME --username USERNAME --password PASSWORD
```

2. This will:
   - Copy the necessary files to the remote machine
   - Install required dependencies
   - Install and start the Windows service
   - Generate and display an API key

#### Manual Installation

1. Copy the `src/api_server` directory to the remote machine
2. Install dependencies: `pip install fastapi uvicorn psutil pywin32`
3. Install as a service: `python src/api_server/deploy_service.py --install`
4. Or run directly: `python src/api_server/server.py`

### Configuration

- **API Key**: Generated automatically or set via `WINOPSTOOL_API_KEY` environment variable
- **Port**: Default is 8000, can be changed via `PORT` environment variable
- **Logging**: Logs to `api_server.log` and console

## Client-Side Integration

### Connecting to Remote Machines

1. Use the Remote Connection Panel to add and manage connections:
   - Provide a name, hostname/IP, port, and API key
   - Click "Connect" to establish a connection

2. Programmatically:

```python
from src.core.remote.integration import RemoteIntegration

# Initialize the remote integration
remote_integration = RemoteIntegration()

# Connect to a remote machine
remote_integration.connect_to_remote(
    name="Remote PC",
    hostname="192.168.1.100",
    api_key="your-api-key",
    port=8000
)

# Get the manager factory
manager_factory = remote_integration.get_manager_factory()

# Use managers as usual - they will automatically use remote operations
service_manager = manager_factory.get_service_manager()
services = service_manager.get_services()
```

### Using Remote Managers

The remote managers maintain the same interface as their local counterparts, so existing code can use them without modification:

```python
# This code works with both local and remote managers
service_manager = manager_factory.get_service_manager()
services = service_manager.get_services()

for service in services:
    print(f"{service['name']} - {service['status']}")

# Start a service
service_manager.start_service("wuauserv")
```

## API Endpoints

### System Information

- `GET /system`: Get system information

```json
{
  "success": true,
  "message": "System information retrieved",
  "data": {
    "hostname": "DESKTOP-ABC123",
    "os_name": "Windows",
    "os_version": "10.0.19044",
    "system_type": "x64-based PC",
    "processor": "Intel(R) Core(TM) i7-10700 CPU @ 2.90GHz",
    "memory_total": 16777216,
    "memory_available": 8388608,
    "boot_time": 1628097600.0
  }
}
```

### Services

- `GET /services`: List all services
- `GET /services/{name}`: Get details for a specific service
- `POST /services/{name}/action`: Perform an action on a service

```json
// Request body for service action
{
  "action": "start" // or "stop", "restart", "pause", "resume"
}
```

### Processes

- `GET /processes`: List all processes
- `GET /processes/{pid}`: Get details for a specific process
- `DELETE /processes/{pid}`: Terminate a process

### Environment Variables

- `GET /environment`: List all environment variables
- `POST /environment`: Set an environment variable

```json
// Request body for setting environment variable
{
  "name": "MY_VAR",
  "value": "my_value",
  "is_system": true
}
```

- `DELETE /environment/{name}`: Delete an environment variable

### Registry

- `GET /registry`: Get registry values
- `POST /registry`: Set a registry value

```json
// Request body for setting registry value
{
  "hkey": "HKEY_LOCAL_MACHINE",
  "key_path": "SOFTWARE\\MyApp",
  "value_name": "Version",
  "value_data": "1.0.0",
  "value_type": "REG_SZ"
}
```

- `DELETE /registry`: Delete a registry value
- `PUT /registry/key`: Create a registry key
- `DELETE /registry/key`: Delete a registry key

## Security Considerations

### Authentication

All API requests require an API key passed in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

### Network Security

- The API server listens on all interfaces (0.0.0.0) by default
- Consider restricting access using Windows Firewall rules
- For production use, consider implementing HTTPS

### Best Practices

1. **API Key Management**:
   - Generate unique API keys for each remote machine
   - Rotate API keys periodically
   - Store API keys securely

2. **Network Security**:
   - Use a firewall to restrict access to the API server
   - Consider using a VPN for connections over the internet

3. **Monitoring**:
   - Check the API server logs regularly
   - Monitor for unauthorized access attempts

## Troubleshooting

### Common Issues

1. **Connection Refused**:
   - Ensure the API server is running on the remote machine
   - Check firewall settings
   - Verify the hostname/IP and port are correct

2. **Authentication Failed**:
   - Verify the API key is correct
   - Check if the API key has been rotated

3. **Service Won't Start**:
   - Check the Windows Event Viewer for service errors
   - Verify Python and dependencies are installed correctly

### Logging

- API Server: `api_server.log`
- Service: `api_service.log`
- Deployment: `service_deploy.log` and `remote_deploy.log`

## Testing

A test script is provided to verify the API server functionality:

```
python tests/test_rest_api.py
```

This will start a test instance of the API server and run various tests against it.

## Migrating from PowerShell Remoting

### Advantages of REST API

1. **Reliability**: More stable connection compared to PowerShell Remoting
2. **Flexibility**: Works across different networks and firewall configurations
3. **Security**: API key authentication instead of Windows credentials
4. **Performance**: Lightweight HTTP requests instead of PowerShell sessions

### Migration Steps

1. Deploy the REST API server to remote machines
2. Update connection settings to use REST API instead of PowerShell Remoting
3. Use the same manager interfaces - no code changes required for existing panels

## Conclusion

The REST API approach provides a modern, reliable, and secure way to manage remote Windows systems with WinOpsTool. By maintaining the same manager interfaces, existing code can seamlessly switch between local and remote operations without modification.
