"""
WinOpsTool REST API Server

This module provides a REST API server that exposes Windows system management 
functionality to remote clients. It serves as a replacement for PowerShell Remoting.
"""

import os
import sys
import uuid
import logging
import subprocess
import uvicorn
import win32api
import win32con
import win32security
import win32service
import win32serviceutil
import psutil
import winreg
from typing import Dict, List, Optional, Any, Union
from fastapi import FastAPI, Depends, HTTPException, status, Security
from fastapi.security import APIKeyHeader
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("api_server.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("api_server")

# Create FastAPI app
app = FastAPI(
    title="WinOpsTool API",
    description="REST API for Windows system management operations",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security setup - API key authentication
API_KEY = os.environ.get("WINOPSTOOL_API_KEY", str(uuid.uuid4()))
api_key_header = APIKeyHeader(name="X-API-Key")

def get_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return api_key

# Base response model
class BaseResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None

# Models for various operations
class ServiceInfo(BaseModel):
    name: str
    display_name: str
    status: str
    start_type: str
    description: Optional[str] = None

class ProcessInfo(BaseModel):
    pid: int
    name: str
    username: Optional[str] = None
    cpu_percent: float
    memory_percent: float
    status: str
    create_time: float

class EnvironmentVariable(BaseModel):
    name: str
    value: str
    is_system: bool = True

class RegistryValue(BaseModel):
    path: str
    name: str
    value: Any
    type: str

class RegistryKeyRequest(BaseModel):
    hkey: str
    key_path: str

class RegistryValueRequest(BaseModel):
    hkey: str
    key_path: str
    value_name: str
    value_data: Any
    value_type: str

class UserInfo(BaseModel):
    username: str
    full_name: Optional[str] = None
    description: Optional[str] = None
    groups: List[str] = []

class GroupInfo(BaseModel):
    name: str
    description: Optional[str] = None
    members: List[str] = []

class FirewallRule(BaseModel):
    name: str
    description: Optional[str] = None
    enabled: bool
    direction: str
    action: str
    protocol: Optional[str] = None
    local_ports: Optional[str] = None
    remote_ports: Optional[str] = None
    local_addresses: Optional[str] = None
    remote_addresses: Optional[str] = None
    profiles: List[str] = []

class SoftwareInfo(BaseModel):
    name: str
    version: Optional[str] = None
    publisher: Optional[str] = None
    install_date: Optional[str] = None
    install_location: Optional[str] = None
    uninstall_string: Optional[str] = None

class SystemInfo(BaseModel):
    hostname: str
    os_name: str
    os_version: str
    system_type: str
    processor: str
    memory_total: int
    memory_available: int
    boot_time: float

# API routes
@app.get("/", response_model=BaseResponse)
async def root(api_key: str = Depends(get_api_key)):
    """Root endpoint - test API connectivity"""
    return {
        "success": True,
        "message": "WinOpsTool API Server is running",
        "data": {"version": "1.0.0"}
    }

@app.get("/system", response_model=BaseResponse)
async def get_system_info(api_key: str = Depends(get_api_key)):
    """Get system information"""
    try:
        info = {
            "hostname": win32api.GetComputerName(),
            "os_name": win32api.GetVersionEx()[0],
            "os_version": f"{win32api.GetVersionEx()[1]}.{win32api.GetVersionEx()[2]}",
            "system_type": "64-bit" if win32api.GetSystemInfo()[0] == 9 else "32-bit",
            "processor": win32api.GetSystemInfo()[9],
            "memory_total": psutil.virtual_memory().total,
            "memory_available": psutil.virtual_memory().available,
            "boot_time": psutil.boot_time()
        }
        return {
            "success": True,
            "message": "System information retrieved successfully",
            "data": info
        }
    except Exception as e:
        logger.error(f"Error getting system info: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get system information: {str(e)}"
        )

# Services endpoints
@app.get("/services", response_model=BaseResponse)
async def get_services(api_key: str = Depends(get_api_key)):
    """Get list of all services"""
    try:
        services = []
        resume = 0
        access = win32service.SC_MANAGER_ENUMERATE_SERVICE
        sc_handle = win32service.OpenSCManager(None, None, access)
        
        try:
            while True:
                services_batch, resume = win32service.EnumServicesStatus(
                    sc_handle, win32service.SERVICE_WIN32, win32service.SERVICE_STATE_ALL, resume
                )
                
                for service in services_batch:
                    name = service[0]
                    display_name = service[1]
                    status = service[2]
                    
                    try:
                        service_handle = win32service.OpenService(
                            sc_handle, name, win32service.SERVICE_QUERY_CONFIG
                        )
                        config = win32service.QueryServiceConfig(service_handle)
                        description = ""
                        start_type = {
                            0: "Boot",
                            1: "System",
                            2: "Auto",
                            3: "Manual",
                            4: "Disabled"
                        }.get(config[2], "Unknown")
                        
                        win32service.CloseServiceHandle(service_handle)
                    except Exception:
                        start_type = "Unknown"
                        description = ""
                    
                    status_text = {
                        1: "Stopped",
                        2: "Starting",
                        3: "Stopping",
                        4: "Running",
                        5: "Continue Pending",
                        6: "Pause Pending",
                        7: "Paused"
                    }.get(status[1], "Unknown")
                    
                    services.append({
                        "name": name,
                        "display_name": display_name,
                        "status": status_text,
                        "start_type": start_type,
                        "description": description
                    })
                
                if resume == 0:
                    break
        finally:
            win32service.CloseServiceHandle(sc_handle)
        
        return {
            "success": True,
            "message": "Services retrieved successfully",
            "data": services
        }
    except Exception as e:
        logger.error(f"Error getting services: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get services: {str(e)}"
        )

@app.get("/services/{service_name}", response_model=BaseResponse)
async def get_service(service_name: str, api_key: str = Depends(get_api_key)):
    """Get information about a specific service"""
    try:
        sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        try:
            service_handle = win32service.OpenService(
                sc_handle, service_name, win32service.SERVICE_QUERY_CONFIG | win32service.SERVICE_QUERY_STATUS
            )
            try:
                config = win32service.QueryServiceConfig(service_handle)
                status = win32service.QueryServiceStatus(service_handle)
                
                start_type = {
                    0: "Boot",
                    1: "System",
                    2: "Auto",
                    3: "Manual",
                    4: "Disabled"
                }.get(config[2], "Unknown")
                
                status_text = {
                    1: "Stopped",
                    2: "Starting",
                    3: "Stopping",
                    4: "Running",
                    5: "Continue Pending",
                    6: "Pause Pending",
                    7: "Paused"
                }.get(status[1], "Unknown")
                
                service_info = {
                    "name": service_name,
                    "display_name": config[0],
                    "status": status_text,
                    "start_type": start_type,
                    "description": ""
                }
                
                return {
                    "success": True,
                    "message": f"Service '{service_name}' retrieved successfully",
                    "data": service_info
                }
            finally:
                win32service.CloseServiceHandle(service_handle)
        finally:
            win32service.CloseServiceHandle(sc_handle)
    except Exception as e:
        logger.error(f"Error getting service '{service_name}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get service '{service_name}': {str(e)}"
        )

class ServiceActionRequest(BaseModel):
    action: str = Field(..., description="Action to perform: start, stop, restart, pause, resume")

@app.post("/services/{service_name}/action", response_model=BaseResponse)
async def service_action(
    service_name: str, 
    request: ServiceActionRequest, 
    api_key: str = Depends(get_api_key)
):
    """Perform an action on a service"""
    try:
        sc_handle = win32service.OpenSCManager(None, None, win32service.SC_MANAGER_ALL_ACCESS)
        try:
            service_handle = win32service.OpenService(
                sc_handle, service_name, win32service.SERVICE_ALL_ACCESS
            )
            try:
                if request.action == "start":
                    win32service.StartService(service_handle, None)
                    message = f"Service '{service_name}' started successfully"
                elif request.action == "stop":
                    win32service.ControlService(service_handle, win32service.SERVICE_CONTROL_STOP)
                    message = f"Service '{service_name}' stopped successfully"
                elif request.action == "restart":
                    try:
                        win32service.ControlService(service_handle, win32service.SERVICE_CONTROL_STOP)
                        win32service.StartService(service_handle, None)
                        message = f"Service '{service_name}' restarted successfully"
                    except Exception:
                        # If service is already stopped, just start it
                        win32service.StartService(service_handle, None)
                        message = f"Service '{service_name}' started successfully"
                elif request.action == "pause":
                    win32service.ControlService(service_handle, win32service.SERVICE_CONTROL_PAUSE)
                    message = f"Service '{service_name}' paused successfully"
                elif request.action == "resume":
                    win32service.ControlService(service_handle, win32service.SERVICE_CONTROL_CONTINUE)
                    message = f"Service '{service_name}' resumed successfully"
                else:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Invalid action: {request.action}"
                    )
                
                return {
                    "success": True,
                    "message": message,
                    "data": None
                }
            finally:
                win32service.CloseServiceHandle(service_handle)
        finally:
            win32service.CloseServiceHandle(sc_handle)
    except Exception as e:
        logger.error(f"Error performing action '{request.action}' on service '{service_name}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to perform action '{request.action}' on service '{service_name}': {str(e)}"
        )

# Processes endpoints
@app.get("/processes", response_model=BaseResponse)
async def get_processes(api_key: str = Depends(get_api_key)):
    """Get list of all processes"""
    try:
        processes = []
        for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time']):
            try:
                pinfo = proc.info
                processes.append({
                    "pid": pinfo['pid'],
                    "name": pinfo['name'],
                    "username": pinfo['username'],
                    "cpu_percent": pinfo['cpu_percent'],
                    "memory_percent": pinfo['memory_percent'],
                    "status": pinfo['status'],
                    "create_time": pinfo['create_time']
                })
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
        
        return {
            "success": True,
            "message": "Processes retrieved successfully",
            "data": processes
        }
    except Exception as e:
        logger.error(f"Error getting processes: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get processes: {str(e)}"
        )

@app.get("/processes/{pid}", response_model=BaseResponse)
async def get_process(pid: int, api_key: str = Depends(get_api_key)):
    """Get information about a specific process"""
    try:
        proc = psutil.Process(pid)
        pinfo = proc.as_dict(attrs=['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'status', 'create_time'])
        
        return {
            "success": True,
            "message": f"Process {pid} retrieved successfully",
            "data": pinfo
        }
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with PID {pid} not found"
        )
    except Exception as e:
        logger.error(f"Error getting process {pid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get process {pid}: {str(e)}"
        )

@app.delete("/processes/{pid}", response_model=BaseResponse)
async def terminate_process(pid: int, api_key: str = Depends(get_api_key)):
    """Terminate a process"""
    try:
        proc = psutil.Process(pid)
        proc.terminate()
        
        return {
            "success": True,
            "message": f"Process {pid} terminated successfully",
            "data": None
        }
    except psutil.NoSuchProcess:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Process with PID {pid} not found"
        )
    except Exception as e:
        logger.error(f"Error terminating process {pid}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to terminate process {pid}: {str(e)}"
        )

# Environment variables endpoints
@app.get("/environment", response_model=BaseResponse)
async def get_environment_variables(api_key: str = Depends(get_api_key)):
    """Get all environment variables"""
    try:
        env_vars = []
        
        # System environment variables
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment")
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                env_vars.append({
                    "name": name,
                    "value": str(value),
                    "is_system": True
                })
                i += 1
            except WindowsError:
                break
        winreg.CloseKey(key)
        
        # User environment variables
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Environment")
        i = 0
        while True:
            try:
                name, value, _ = winreg.EnumValue(key, i)
                env_vars.append({
                    "name": name,
                    "value": str(value),
                    "is_system": False
                })
                i += 1
            except WindowsError:
                break
        winreg.CloseKey(key)
        
        return {
            "success": True,
            "message": "Environment variables retrieved successfully",
            "data": env_vars
        }
    except Exception as e:
        logger.error(f"Error getting environment variables: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get environment variables: {str(e)}"
        )

class EnvironmentVariableRequest(BaseModel):
    name: str
    value: str
    is_system: bool = True

@app.post("/environment", response_model=BaseResponse)
async def set_environment_variable(
    request: EnvironmentVariableRequest, 
    api_key: str = Depends(get_api_key)
):
    """Set an environment variable"""
    try:
        if request.is_system:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, 
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                0, 
                winreg.KEY_SET_VALUE
            )
        else:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Environment", 
                0, 
                winreg.KEY_SET_VALUE
            )
        
        winreg.SetValueEx(key, request.name, 0, winreg.REG_SZ, request.value)
        winreg.CloseKey(key)
        
        # Broadcast WM_SETTINGCHANGE message
        win32api.SendMessage(
            win32con.HWND_BROADCAST, 
            win32con.WM_SETTINGCHANGE, 
            0, 
            "Environment"
        )
        
        return {
            "success": True,
            "message": f"Environment variable '{request.name}' set successfully",
            "data": None
        }
    except Exception as e:
        logger.error(f"Error setting environment variable '{request.name}': {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to set environment variable '{request.name}': {str(e)}"
        )

@app.delete("/environment/{name}", response_model=BaseResponse)
async def delete_environment_variable(
    name: str, 
    is_system: bool = True, 
    api_key: str = Depends(get_api_key)
):
    """Delete an environment variable"""
    try:
        if is_system:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE, 
                r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment", 
                0, 
                winreg.KEY_SET_VALUE
            )
        else:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER, 
                r"Environment", 
                0, 
                winreg.KEY_SET_VALUE
            )
        
        winreg.DeleteValue(key, name)
        winreg.CloseKey(key)
        
        # Broadcast WM_SETTINGCHANGE message
        win32api.SendMessage(
            win32con.HWND_BROADCAST, 
            win32con.WM_SETTINGCHANGE, 
            0, 
            "Environment"
        )
        
        return {
            "success": True,
            "message": f"Environment variable '{name}' deleted successfully",
            "data": None
        }
    except Exception as e:
        logger.error(f"Error deleting environment variable '{name}': {str(e)}")

# Main entry point
if __name__ == "__main__":
    # Print the API key for initial setup
    print(f"API Key: {API_KEY}")
    
    # Start the server
    uvicorn.run(app, host="0.0.0.0", port=8000)