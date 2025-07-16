"""Windows Network management."""
import psutil
import wmi
from src.core.logger import setup_logger

class NetworkManager:
    """Manager for Windows Network interfaces and connections."""
    
    def __init__(self):
        """Initialize network manager."""
        self.logger = setup_logger(self.__class__.__name__)
        self.wmi = wmi.WMI()
        
    def get_interfaces(self):
        """Get list of network interfaces.
        
        Returns:
            list: List of interface dictionaries with properties
        """
        try:
            interfaces = []
            stats = psutil.net_if_stats()
            addrs = psutil.net_if_addrs()
            io_counters = psutil.net_io_counters(pernic=True)
            
            # Get WMI network adapters for additional info
            wmi_adapters = {
                adapter.NetConnectionID: adapter
                for adapter in self.wmi.Win32_NetworkAdapter(PhysicalAdapter=True)
                if adapter.NetConnectionID
            }
            
            for name, stats_info in stats.items():
                try:
                    # Get addresses
                    addresses = addrs.get(name, {})
                    ipv4 = ""
                    ipv6 = ""
                    mac = ""
                    
                    for addr in addresses:
                        if addr.family == psutil.AF_LINK:
                            mac = addr.address
                        elif addr.family == 2:  # IPv4
                            ipv4 = addr.address
                        elif addr.family == 23:  # IPv6
                            ipv6 = addr.address
                            
                    # Get IO counters
                    io = io_counters.get(name, None)
                    bytes_sent = io.bytes_sent if io else 0
                    bytes_recv = io.bytes_recv if io else 0
                    
                    # Get additional info from WMI
                    wmi_info = wmi_adapters.get(name, None)
                    adapter_type = wmi_info.AdapterType if wmi_info else "Unknown"
                    manufacturer = wmi_info.Manufacturer if wmi_info else "Unknown"
                    
                    interfaces.append({
                        'name': name,
                        'type': adapter_type,
                        'manufacturer': manufacturer,
                        'mac': mac,
                        'ipv4': ipv4,
                        'ipv6': ipv6,
                        'speed': stats_info.speed,
                        'mtu': stats_info.mtu,
                        'up': stats_info.isup,
                        'bytes_sent': bytes_sent,
                        'bytes_recv': bytes_recv
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get details for interface {name}: {str(e)}")
                    continue
                    
            return interfaces
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate network interfaces: {str(e)}")
            return []
            
    def get_connections(self):
        """Get list of active network connections.
        
        Returns:
            list: List of connection dictionaries with properties
        """
        try:
            connections = []
            for conn in psutil.net_connections(kind='inet'):
                try:
                    # Get process info
                    try:
                        process = psutil.Process(conn.pid) if conn.pid else None
                        process_name = process.name() if process else "Unknown"
                    except (psutil.NoSuchProcess, psutil.AccessDenied):
                        process_name = "Unknown"
                        
                    # Format addresses
                    local_addr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else ""
                    remote_addr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else ""
                    
                    # Map status
                    status = {
                        psutil.CONN_ESTABLISHED: "ESTABLISHED",
                        psutil.CONN_SYN_SENT: "SYN_SENT",
                        psutil.CONN_SYN_RECV: "SYN_RECV",
                        psutil.CONN_FIN_WAIT1: "FIN_WAIT1",
                        psutil.CONN_FIN_WAIT2: "FIN_WAIT2",
                        psutil.CONN_TIME_WAIT: "TIME_WAIT",
                        psutil.CONN_CLOSE: "CLOSE",
                        psutil.CONN_CLOSE_WAIT: "CLOSE_WAIT",
                        psutil.CONN_LAST_ACK: "LAST_ACK",
                        psutil.CONN_LISTEN: "LISTENING",
                        psutil.CONN_CLOSING: "CLOSING",
                        psutil.CONN_NONE: "NONE"
                    }.get(conn.status, "UNKNOWN")
                    
                    connections.append({
                        'protocol': 'TCP' if conn.type == 1 else 'UDP',
                        'local_address': local_addr,
                        'remote_address': remote_addr,
                        'status': status,
                        'pid': conn.pid or 0,
                        'process': process_name
                    })
                    
                except Exception as e:
                    self.logger.warning(f"Failed to get details for connection: {str(e)}")
                    continue
                    
            return connections
            
        except Exception as e:
            self.logger.error(f"Failed to enumerate network connections: {str(e)}")
            return []
            
    def get_interface_stats(self, name):
        """Get detailed statistics for a network interface.
        
        Args:
            name: Interface name
            
        Returns:
            dict: Interface statistics or None if failed
        """
        try:
            stats = psutil.net_if_stats()[name]
            io = psutil.net_io_counters(pernic=True)[name]
            
            return {
                'speed': stats.speed,
                'mtu': stats.mtu,
                'up': stats.isup,
                'bytes_sent': io.bytes_sent,
                'bytes_recv': io.bytes_recv,
                'packets_sent': io.packets_sent,
                'packets_recv': io.packets_recv,
                'errin': io.errin,
                'errout': io.errout,
                'dropin': io.dropin,
                'dropout': io.dropout
            }
            
        except Exception as e:
            self.logger.error(f"Failed to get stats for interface {name}: {str(e)}")
            return None
