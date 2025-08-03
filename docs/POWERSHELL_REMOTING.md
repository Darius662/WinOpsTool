# PowerShell Remoting for WinOpsTool

This document explains how to use PowerShell Remoting for remote PC management in WinOpsTool.

## Overview

WinOpsTool now uses PowerShell Remoting (WinRM) for remote PC connections instead of WMI. This provides several advantages:

- More stable and reliable connections
- Better security with encrypted communications
- No need for manual intervention on remote PCs (once WinRM is enabled)
- Full PowerShell scripting capabilities
- Improved file transfer capabilities
- Better error handling and diagnostics

## Requirements

To use PowerShell Remoting with WinOpsTool, you need:

1. Windows 10/11 on both the local and remote PCs
2. Administrator privileges on both PCs
3. PowerShell 5.1 or higher (included with Windows 10/11)
4. WinRM enabled on the remote PC

## Setting Up WinRM on Remote PCs

Before you can connect to a remote PC, you need to enable WinRM on that PC. This only needs to be done once per PC.

### Quick Setup (Single PC)

1. Open PowerShell as Administrator on the remote PC
2. Run the following command:

```powershell
Enable-PSRemoting -Force
```

This command:
- Starts the WinRM service
- Sets the service startup type to automatic
- Creates a firewall exception
- Enables all required firewall rules
- Configures a basic listener for WS-Management requests

### Remote Enablement

You can also enable WinRM remotely using WinOpsTool or other methods:

#### Using WinOpsTool

WinOpsTool can help enable WinRM on remote PCs that are accessible through other means (like admin shares):

1. Connect to the remote PC using an administrative share (e.g., C$)
2. Go to Remote → Enable WinRM
3. Follow the prompts to enable WinRM remotely

#### Using Group Policy or SCCM

For domain-joined computers, you can enable WinRM remotely using Group Policy or SCCM by deploying a script that runs:

```powershell
Enable-PSRemoting -Force
```

#### Using PsExec

If you have access to the remote PC via PsExec:

```cmd
psexec \\remotemachine -s powershell Enable-PSRemoting -Force
```

### Enterprise Setup (Multiple PCs)

For enterprise environments, you can use Group Policy to enable WinRM on multiple PCs:

1. Open Group Policy Management Console
2. Create or edit a policy for your target computers
3. Navigate to: Computer Configuration → Policies → Administrative Templates → Windows Components → Windows Remote Management (WinRM) → WinRM Service
4. Enable "Allow remote server management through WinRM"
5. Configure the IPv4 and IPv6 filters as needed

### Troubleshooting WinRM Setup

If you encounter issues with WinRM setup, try the following:

1. Check if the WinRM service is running:
```powershell
Get-Service WinRM
```

2. Check WinRM configuration:
```powershell
winrm quickconfig
```

3. Check WinRM listeners:
```powershell
winrm enumerate winrm/config/listener
```

4. Test WinRM connectivity:
```powershell
Test-WSMan -ComputerName <remote-pc-name>
```

5. For domain environments, ensure that the appropriate firewall rules are enabled:
```powershell
Enable-NetFirewallRule -DisplayGroup "Windows Remote Management"
```

## Using PowerShell Remoting in WinOpsTool

### Connecting to Remote PCs

1. Open WinOpsTool
2. Go to Remote → Manage Connections
3. Enter the following information:
   - Name: A friendly name for the connection
   - Hostname: The hostname or IP address of the remote PC
   - Username: A username with administrator privileges on the remote PC
   - Password: The password for the specified user
4. Click "Add Connection"
5. Use the Connect/Disconnect buttons to manage connections
6. Use the test buttons (Ping Test, Credential Test, WinRM Test) to verify connectivity

### Executing Remote Commands

Once connected to a remote PC, you can execute PowerShell commands directly:

1. Go to Remote → Execute Command
2. Enter a PowerShell command
3. Click "Execute"

### File Transfer

To transfer files between the local and remote PC:

1. Go to Remote → File Transfer
2. Select the source and destination paths
3. Click "Transfer"

## Security Considerations

PowerShell Remoting uses the following security measures:

1. **Authentication**: By default, WinOpsTool uses Negotiate authentication, which selects the best available authentication method.
2. **Encryption**: All communications are encrypted using SSL/TLS.
3. **Authorization**: Only users with appropriate permissions can connect and execute commands.

### Enhancing Security

For enhanced security:

1. Use HTTPS instead of HTTP for WinRM:
```powershell
# Create a self-signed certificate
$cert = New-SelfSignedCertificate -DnsName "RemoteComputer" -CertStoreLocation "cert:\LocalMachine\My"

# Configure WinRM to use HTTPS
winrm create winrm/config/Listener?Address=*+Transport=HTTPS "@{Hostname=`"RemoteComputer`"; CertificateThumbprint=`"$($cert.Thumbprint)`"}"
```

2. Restrict WinRM to specific IP addresses:
```powershell
Set-Item WSMan:\localhost\Service\IPv4Filter -Value "10.0.0.0/24"
```

3. Use constrained endpoints for limited access:
```powershell
Register-PSSessionConfiguration -Name "RestrictedEndpoint" -ShowSecurityDescriptorUI
```

## Troubleshooting

### Common Issues

1. **Connection Refused**
   - Ensure WinRM is enabled on the remote PC
   - Check firewall settings
   - Verify the hostname/IP is correct

2. **Authentication Failed**
   - Verify username and password
   - Ensure the user has administrator privileges

3. **Command Execution Failed**
   - Check if the command is valid PowerShell syntax
   - Verify the user has permissions to execute the command

### Diagnostic Commands

Use these commands to diagnose issues:

```powershell
# Test WinRM connectivity
Test-WSMan -ComputerName <remote-pc-name>

# Check WinRM configuration
Get-Item WSMan:\localhost\Client\*
Get-Item WSMan:\localhost\Service\*

# View WinRM listeners
Get-ChildItem WSMan:\localhost\Listener

# Check WinRM firewall rules
Get-NetFirewallRule | Where-Object {$_.DisplayName -like "*WinRM*"}
```

## Testing PowerShell Remoting

WinOpsTool includes a test script to verify PowerShell Remoting functionality:

```bash
python test_ps_remote.py
```

This script tests:
- WinRM availability
- Connection establishment
- Command execution
- Script execution
- File transfer

## References

- [Microsoft Documentation: PowerShell Remoting](https://docs.microsoft.com/en-us/powershell/scripting/learn/remoting/running-remote-commands)
- [Microsoft Documentation: WinRM Service](https://docs.microsoft.com/en-us/windows/win32/winrm/portal)
- [PowerShell Team Blog: PowerShell Remoting Security Considerations](https://devblogs.microsoft.com/powershell/powershell-remoting-security-considerations/)
