"""Windows Disk management."""
import psutil
import wmi
import win32api
from src.core.logger import setup_logger

class DiskManager:
    """Manager for Windows Disks and Volumes."""
    
    def __init__(self):
        """Initialize disk manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.wmi = wmi.WMI()
        
    def get_disks(self):
        """Get list of physical disks.
        
        Returns:
            list: List of disk dictionaries with properties
        """
        try:
            disks = []
            
            # Get physical disks from WMI
            for disk in self.wmi.Win32_DiskDrive():
                try:
                    disks.append({
                        'name': disk.Caption,
                        'device_id': disk.DeviceID,
                        'model': disk.Model,
                        'interface': disk.InterfaceType,
                        'size': disk.Size,
                        'partitions': disk.Partitions,
                        'status': disk.Status,
                        'serial': disk.SerialNumber or "",
                        'firmware': disk.FirmwareRevision or ""
                    })
                except Exception as e:
                    self.logger.warning(f"Failed to get details for disk {disk.DeviceID}: {str(e)}")
                    continue
                    
            return disks
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate disks: {str(e)}")
            return []
            
    def get_volumes(self):
        """Get list of volumes (drives).
        
        Returns:
            list: List of volume dictionaries with properties
        """
        try:
            volumes = []
            
            # Get partitions from psutil
            partitions = psutil.disk_partitions(all=True)
            
            # Get volume info from WMI for additional details
            wmi_volumes = {
                vol.DeviceID.rstrip('\\'): vol
                for vol in self.wmi.Win32_LogicalDisk()
            }
            
            for part in partitions:
                try:
                    # Get usage info
                    usage = psutil.disk_usage(part.mountpoint) if part.mountpoint else None
                    
                    # Get WMI volume info
                    device_id = part.device.rstrip('\\')
                    wmi_vol = wmi_volumes.get(device_id)
                    
                    volumes.append({
                        'device': part.device,
                        'mountpoint': part.mountpoint,
                        'fstype': part.fstype,
                        'opts': part.opts,
                        'total': usage.total if usage else 0,
                        'used': usage.used if usage else 0,
                        'free': usage.free if usage else 0,
                        'label': wmi_vol.VolumeName if wmi_vol else "",
                        'type': self._get_drive_type(wmi_vol.DriveType if wmi_vol else 0)
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get details for volume {part.device}: {str(e)}")
                    continue
                    
            return volumes
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate volumes: {str(e)}")
            return []
            
    def _get_drive_type(self, type_id):
        """Convert WMI drive type to string.
        
        Args:
            type_id: WMI drive type ID
            
        Returns:
            str: Drive type description
        """
        return {
            0: "Unknown",
            1: "No Root Directory",
            2: "Removable Disk",
            3: "Local Disk",
            4: "Network Drive",
            5: "Compact Disc",
            6: "RAM Disk"
        }.get(type_id, "Unknown")
        
    def get_disk_performance(self, device_id):
        """Get disk performance metrics.
        
        Args:
            device_id: Disk device ID
            
        Returns:
            dict: Performance metrics or None if failed
        """
        try:
            # Get disk IO counters
            disk_name = device_id.split('\\')[-1]  # Convert PhysicalDrive0 to 0
            io = psutil.disk_io_counters(perdisk=True).get(disk_name)
            
            if not io:
                return None
                
            return {
                'read_count': io.read_count,
                'write_count': io.write_count,
                'read_bytes': io.read_bytes,
                'write_bytes': io.write_bytes,
                'read_time': io.read_time,
                'write_time': io.write_time
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get performance for disk {device_id}: {str(e)}")
            return None
            
    def get_volume_info(self, mountpoint):
        """Get detailed volume information.
        
        Args:
            mountpoint: Volume mount point (e.g., "C:\\")
            
        Returns:
            dict: Volume information or None if failed
        """
        try:
            # Get basic disk usage
            usage = psutil.disk_usage(mountpoint)
            
            # Get filesystem info
            fsinfo = win32api.GetVolumeInformation(mountpoint)
            
            return {
                'total': usage.total,
                'used': usage.used,
                'free': usage.free,
                'percent': usage.percent,
                'volume_name': fsinfo[0],
                'serial_number': fsinfo[1],
                'max_path_length': fsinfo[2],
                'filesystem': fsinfo[3],
                'flags': fsinfo[4]
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get info for volume {mountpoint}: {str(e)}")
            return None
