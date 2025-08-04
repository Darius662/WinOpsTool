# WinOpsTool REST API Service Installer Guide

This document outlines the different approaches available for building and distributing the WinOpsTool REST API service installer. The installer bundles Python and all required dependencies, making it easy to deploy the service on remote Windows machines without requiring manual installation of dependencies.

## Option 1: Full Installer with Inno Setup (Recommended)

This approach creates a professional Windows installer that handles service installation, API key generation, and provides a clean user interface.

### Prerequisites:
- Python 3.8 or higher
- Inno Setup installed (https://jrsoftware.org/isdl.php)

### Steps:
1. Run the installer creation script:
   ```
   python src/api_server/create_installer.py
   ```

2. The script will:
   - Install required dependencies
   - Create a service launcher
   - Build a standalone executable
   - Create an Inno Setup script
   - Build the final installer

3. The installer will be available at:
   ```
   dist/WinOpsToolAPI_Setup.exe
   ```

## Option 2: Executable-Only Build

If you don't have Inno Setup or just need the executable without a full installer, you can use this approach.

### Prerequisites:
- Python 3.8 or higher

### Steps:
1. Run the executable-only build:
   ```
   python src/api_server/create_installer.py --exe-only
   ```

2. The executable will be available at:
   ```
   dist/WinOpsToolAPI/WinOpsToolAPI.exe
   ```

3. You can manually copy this executable and its dependencies to target machines.

## Option 3: Simplified Build Process

For the most reliable build process, especially if you're experiencing issues with the other options.

### Prerequisites:
- Python 3.8 or higher

### Steps:
1. Run the simplified build script:
   ```
   python src/api_server/simple_build.py
   ```

2. The standalone executable will be available at:
   ```
   dist/WinOpsToolAPI.exe
   ```

## Manual Installer Creation

If you've built the executable using Option 2 or 3 and want to create an installer manually:

1. Download and install Inno Setup from https://jrsoftware.org/isdl.php

2. Create a file named `installer.iss` with the following content:
   ```
   #define MyAppName "WinOpsTool REST API Service"
   #define MyAppVersion "1.0.0"
   #define MyAppPublisher "WinOpsTool Team"
   #define MyAppExeName "WinOpsToolAPI.exe"

   [Setup]
   AppId={{8A7D8AE3-9F0D-4C8B-B6A1-17E457CA8F9A}
   AppName={#MyAppName}
   AppVersion={#MyAppVersion}
   AppPublisher={#MyAppPublisher}
   DefaultDirName={autopf}\WinOpsToolAPI
   DefaultGroupName={#MyAppName}
   AllowNoIcons=yes
   OutputDir=dist
   OutputBaseFilename=WinOpsToolAPI_Setup
   Compression=lzma
   SolidCompression=yes
   PrivilegesRequired=admin

   [Languages]
   Name: "english"; MessagesFile: "compiler:Default.isl"

   [Tasks]
   Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

   [Files]
   Source: "dist\WinOpsToolAPI.exe"; DestDir: "{app}"; Flags: ignoreversion
   Source: "docs\REST_API_GUIDE.md"; DestDir: "{app}\docs"; Flags: ignoreversion
   Source: "src\api_server\README.md"; DestDir: "{app}"; Flags: ignoreversion isreadme

   [Icons]
   Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
   Name: "{group}\Documentation"; Filename: "{app}\docs\REST_API_GUIDE.md"
   Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon
   ```

3. Run the Inno Setup Compiler:
   ```
   iscc.exe installer.iss
   ```

4. The installer will be created at:
   ```
   dist/WinOpsToolAPI_Setup.exe
   ```

## Troubleshooting

### Common Issues:

1. **Missing Dependencies**
   - If you encounter errors about missing Python packages, run:
     ```
     python -m pip install fastapi uvicorn psutil pywin32 requests pyinstaller
     ```

2. **PyInstaller Errors**
   - If PyInstaller fails, try running with the `--clean` flag:
     ```
     python -m PyInstaller --clean your_spec_file.spec
     ```

3. **Inno Setup Not Found**
   - If the script can't find Inno Setup, set the environment variable:
     ```
     set INNO_SETUP_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
     ```
   - Or use one of the executable-only build options.

4. **Service Installation Issues**
   - If the service doesn't install correctly, run the executable manually with admin privileges:
     ```
     WinOpsToolAPI.exe --install
     ```

5. **Service Won't Start**
   - Check Windows Event Viewer for more details
   - Verify the log files in the installation directory

6. **Port Conflict**
   - The service uses port 8000 by default, make sure it's not in use
   - You can modify the port in the configuration file if needed

7. **Permission Issues**
   - Make sure you're running the installer and service with administrator privileges

### Log Files

If you encounter issues, check these log files:

- `api_service_launcher.log`: Main service launcher log
- `api_service.log`: Service operation log
- `api_server.log`: API server log

## Using the Installer

The installer provides a simple wizard interface:

1. Run `WinOpsToolAPI_Setup.exe` on the target machine
2. Follow the installation wizard
3. Choose whether to install as a Windows service (recommended)
4. Complete the installation

After installation:

- The service will be installed and started automatically if you selected that option
- The API key will be displayed and saved to the installation directory
- You can manage the service using the installed executable:

```
"C:\Program Files\WinOpsToolAPI\WinOpsToolAPI.exe" --status
"C:\Program Files\WinOpsToolAPI\WinOpsToolAPI.exe" --stop
"C:\Program Files\WinOpsToolAPI\WinOpsToolAPI.exe" --start
"C:\Program Files\WinOpsToolAPI\WinOpsToolAPI.exe" --generate-key
```

## Dependencies Included in the Installer

The installer bundles the following components:

1. **Python 3.8+**: Full Python runtime environment
2. **FastAPI**: Web framework for building APIs
3. **Uvicorn**: ASGI server for running FastAPI
4. **Psutil**: For system information and process management
5. **PyWin32**: For Windows-specific operations (services, registry, etc.)
6. **Requests**: For HTTP operations

## Distribution

Once you've created the installer or executable:

1. Copy the installer/executable to the target machine
2. Run with administrator privileges
3. Follow the installation wizard (if using the installer)
4. Note the API key that is displayed during installation

For more detailed distribution instructions, see [DISTRIBUTION_GUIDE.md](DISTRIBUTION_GUIDE.md).

## Uninstalling

To uninstall the service:

1. Use the Windows Control Panel "Add or Remove Programs" feature
2. Or run the uninstaller directly from the installation directory

The uninstaller will automatically stop and remove the service before removing files.

## Conclusion

Choose the approach that best fits your environment and requirements:
- Option 1 for a full, professional installer experience
- Option 2 for just the executable with its dependencies
- Option 3 for the most reliable build process
- Manual installer creation if you need more control over the process

All approaches will produce a working REST API service that can be installed and run on Windows systems.
