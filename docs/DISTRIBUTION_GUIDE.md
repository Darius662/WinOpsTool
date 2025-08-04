# WinOpsTool REST API Service Distribution Guide

This guide explains how to distribute and deploy the WinOpsTool REST API service to remote machines.

## Distribution Methods

There are three main methods to deploy the REST API service:

### 1. Using the Standalone Installer (Recommended)

The standalone installer is the simplest method for end users as it bundles Python and all dependencies.

#### Building the Installer

1. On your development machine, run:
   ```
   python src/api_server/create_installer.py
   ```

2. The installer will be created at `dist/WinOpsToolAPI_Setup.exe`

#### Distributing the Installer

1. Copy `WinOpsToolAPI_Setup.exe` to the target machine
2. Run the installer with administrator privileges
3. Follow the installation wizard
4. Note the API key displayed at the end of installation

### 2. Using the Remote Deployment Script

For automated deployment to multiple machines, use the remote deployment script.

#### Prerequisites

- PsExec from Microsoft Sysinternals installed on your machine
- Administrative access to remote machines
- Python 3.8+ installed on remote machines

#### Deployment Steps

1. Run the remote deployment script:
   ```
   python src/api_server/deploy_remote.py --deploy --host REMOTE_HOSTNAME --username USERNAME --password PASSWORD
   ```

2. The script will:
   - Create a deployment package
   - Copy it to the remote machine
   - Install dependencies
   - Install and start the service
   - Generate and display an API key

3. The connection details will be automatically saved to your local configuration

### 3. Manual Installation

For advanced users who prefer manual control over the installation process.

#### Prerequisites

- Python 3.8+ installed on the target machine
- Administrative privileges

#### Installation Steps

1. Copy the `src/api_server` directory to the target machine
2. Install dependencies:
   ```
   pip install fastapi uvicorn psutil pywin32 requests
   ```

3. Install as a service:
   ```
   python src/api_server/deploy_service.py --install
   ```

4. Note the API key displayed during installation

## Connecting to Remote Machines

After deploying the REST API service, you need to configure WinOpsTool to connect to it.

### Using the Remote Setup Utility

1. Run the remote setup utility:
   ```
   python src/core/remote/setup_remote.py add --name "Remote PC" --hostname REMOTE_HOSTNAME --api-key API_KEY --port 8000
   ```

2. Test the connection:
   ```
   python src/core/remote/setup_remote.py test --name "Remote PC"
   ```

3. The connection details will be saved for future use

### Using the Remote Connection Panel

1. Open WinOpsTool
2. Navigate to the Remote Connection panel
3. Click "Add" and enter the connection details:
   - Name: A friendly name for the remote machine
   - Hostname: The hostname or IP address
   - API Key: The API key generated during installation
   - Port: 8000 (default)
4. Click "Connect" to establish the connection

## Managing Multiple Remote Machines

For environments with multiple remote machines:

1. Create a CSV file with connection details:
   ```
   Name,Hostname,ApiKey,Port
   Server1,192.168.1.100,api-key-1,8000
   Server2,192.168.1.101,api-key-2,8000
   ```

2. Import connections:
   ```
   python src/core/remote/setup_remote.py import --file connections.csv
   ```

3. Connect to all machines:
   ```
   python src/core/remote/setup_remote.py connect-all
   ```

## Security Considerations

### API Key Management

- Store API keys securely
- Rotate API keys periodically:
  ```
  python src/api_server/deploy_service.py --generate-key
  ```

### Network Security

- The API server listens on all interfaces (0.0.0.0) by default
- Consider restricting access using Windows Firewall:
  ```
  netsh advfirewall firewall add rule name="WinOpsTool API" dir=in action=allow protocol=TCP localport=8000 remoteip=LOCAL_SUBNET
  ```

### HTTPS Configuration (Advanced)

For production environments, consider enabling HTTPS:

1. Generate a self-signed certificate:
   ```
   openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout server.key -out server.crt
   ```

2. Configure the API server to use HTTPS by modifying `server.py`

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure the service is running: `sc query WinOpsToolAPI`
   - Check firewall settings
   - Verify hostname/IP and port

2. **Authentication Failed**
   - Verify the API key
   - Check if the API key has been rotated

3. **Service Won't Start**
   - Check Windows Event Viewer
   - Review service logs in the installation directory

### Logging

- API Server: `api_server.log`
- Service: `api_service.log`
- Deployment: `service_deploy.log` and `remote_deploy.log`

## Updating the Service

To update the service after code changes:

1. Stop the service:
   ```
   sc stop WinOpsToolAPI
   ```

2. Replace the files in the installation directory

3. Start the service:
   ```
   sc start WinOpsToolAPI
   ```

## Uninstalling

### Using the Installer

If installed with the standalone installer:

1. Use Windows Control Panel "Add or Remove Programs"
2. Or run the uninstaller from the installation directory

### Using the Deployment Script

If installed with the deployment script:

```
python src/api_server/deploy_service.py --uninstall
```

## Conclusion

The WinOpsTool REST API service provides a reliable and secure way to manage remote Windows systems. By following this distribution guide, you can easily deploy and manage the service across your network.
