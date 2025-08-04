# WinOpsTool REST API Server

This component provides a REST API server for WinOpsTool remote management operations. It serves as a replacement for PowerShell Remoting, allowing remote management of Windows systems through a secure HTTP API.

## Features

- **System Information**: Get detailed system information from remote machines
- **Services Management**: List, query, start, stop, pause, resume, and restart Windows services
- **Process Management**: List, query, and terminate processes
- **Environment Variables**: List, set, and delete environment variables
- **Registry Operations**: Query, create, modify, and delete registry keys and values
- **Security**: API key authentication for secure access

## Installation

### Prerequisites

- Windows 10/11 or Windows Server 2016+
- Python 3.8 or higher
- Administrator privileges (for service installation)

### Manual Installation

1. Clone the WinOpsTool repository or copy the `src/api_server` directory to the target machine
2. Install the required Python packages:

```
pip install fastapi uvicorn psutil pywin32
```

3. Run the server manually:

```
python src/api_server/server.py
```

The server will start and display the generated API key that you'll need to connect to it.

### Installing as a Windows Service

For production use, it's recommended to install the API server as a Windows service:

1. Run the deployment script with administrator privileges:

```
python src/api_server/deploy_service.py --install
```

2. This will install, configure, and start the service automatically
3. The API key will be displayed and saved to `src/api_server/api_key.txt`

## Configuration

The API server can be configured through environment variables:

- `WINOPSTOOL_API_KEY`: Set a specific API key instead of generating a random one
- `PORT`: Change the default port (8000)

When running as a service, you can generate a new API key at any time:

```
python src/api_server/deploy_service.py --generate-key
```

## Usage

### Service Management

```
# Install the service
python src/api_server/deploy_service.py --install

# Check service status
python src/api_server/deploy_service.py --status

# Start the service
python src/api_server/deploy_service.py --start

# Stop the service
python src/api_server/deploy_service.py --stop

# Uninstall the service
python src/api_server/deploy_service.py --uninstall
```

### API Endpoints

The API server exposes the following endpoints:

#### System Information

- `GET /system`: Get system information

#### Services

- `GET /services`: List all services
- `GET /services/{name}`: Get details for a specific service
- `POST /services/{name}/action`: Perform an action on a service (start, stop, restart, pause, resume)

#### Processes

- `GET /processes`: List all processes
- `GET /processes/{pid}`: Get details for a specific process
- `DELETE /processes/{pid}`: Terminate a process

#### Environment Variables

- `GET /environment`: List all environment variables
- `POST /environment`: Set an environment variable
- `DELETE /environment/{name}`: Delete an environment variable

#### Registry

- `GET /registry`: Get registry values
- `POST /registry`: Set a registry value
- `DELETE /registry`: Delete a registry value
- `PUT /registry/key`: Create a registry key
- `DELETE /registry/key`: Delete a registry key

### Authentication

All API requests require an API key to be included in the `X-API-Key` header:

```
X-API-Key: your-api-key-here
```

## Security Considerations

- The API server listens on all interfaces (0.0.0.0) by default
- In production, consider restricting access using a firewall
- The API key should be kept secure and rotated periodically
- Consider using HTTPS for production deployments

## Troubleshooting

- Check the log files for errors:
  - `api_server.log`: Main API server log
  - `api_service.log`: Service log when running as a Windows service
  - `service_deploy.log`: Deployment script log

- If the service fails to start, check the Windows Event Viewer for more details

## Testing

A test script is provided to verify the API server functionality:

```
python tests/test_rest_api.py
```

This will start a test instance of the API server and run various tests against it.
