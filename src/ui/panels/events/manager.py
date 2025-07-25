"""Event Viewer manager for Windows event logs."""
import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from src.core.logger import setup_logger

class EventsManager:
    """Manager for Windows Event Viewer operations."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_event_logs(self):
        """Get list of available event logs."""
        try:
            # Use wevtutil to get list of logs
            result = subprocess.run([
                'wevtutil', 'el'
            ], capture_output=True, text=True, check=True)
            
            logs = []
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    logs.append(line.strip())
            
            self.logger.debug(f"Retrieved {len(logs)} event logs")
            return logs
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get event logs: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting event logs: {e}")
            return []
    
    def get_events(self, log_name="System", max_events=100, level_filter=None, hours_back=24):
        """Get events from a specific log."""
        try:
            # Try multiple approaches to get events, starting with the most basic
            result = None
            
            # Approach 1: Very basic query - just get recent events
            try:
                cmd = ['wevtutil', 'qe', log_name, f'/count:{max_events}', '/format:xml']
                self.logger.debug(f"Trying basic query: {' '.join(cmd)}")
                result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
                self.logger.debug(f"Basic query succeeded for {log_name}")
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                self.logger.warning(f"Basic query failed for {log_name}: {e}")
                
                # Approach 2: Try with reverse direction
                try:
                    cmd = ['wevtutil', 'qe', log_name, f'/count:{min(max_events, 50)}', '/rd:true', '/format:xml']
                    self.logger.debug(f"Trying reverse query: {' '.join(cmd)}")
                    result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
                    self.logger.debug(f"Reverse query succeeded for {log_name}")
                except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                    self.logger.warning(f"Reverse query failed for {log_name}: {e}")
                    
                    # Approach 3: Try with minimal parameters
                    try:
                        cmd = ['wevtutil', 'qe', log_name, '/count:10', '/format:xml']
                        self.logger.debug(f"Trying minimal query: {' '.join(cmd)}")
                        result = subprocess.run(cmd, capture_output=True, text=True, check=True, timeout=30)
                        self.logger.debug(f"Minimal query succeeded for {log_name}")
                    except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
                        self.logger.error(f"All query approaches failed for {log_name}: {e}")
                        return []
            
            if not result:
                self.logger.error(f"No successful query result for {log_name}")
                return []
            
            events = []
            if result.stdout.strip():
                self.logger.debug(f"Raw XML output length: {len(result.stdout)}")
                
                # Parse XML events - handle namespace issues
                try:
                    # Try parsing individual events directly (since wevtutil outputs multiple root elements)
                    event_xmls = result.stdout.split('</Event>')
                    for event_xml in event_xmls:
                        if '<Event' in event_xml and event_xml.strip():
                            try:
                                # Complete the event XML if needed
                                if not event_xml.strip().endswith('</Event>'):
                                    event_xml += '</Event>'
                                
                                # Parse the individual event
                                event_elem = ET.fromstring(event_xml)
                                event_data = self.parse_event_xml(event_elem)
                                if event_data:
                                    events.append(event_data)
                                    
                            except ET.XMLSyntaxError as e:
                                self.logger.warning(f"Failed to parse individual event XML: {e}")
                                continue
                                
                except Exception as e:
                    self.logger.error(f"Error processing XML events: {e}")
                    
                    # Final fallback: try wrapping in root element
                    try:
                        xml_content = f"<Events>{result.stdout}</Events>"
                        root = ET.fromstring(xml_content)
                        
                        # Handle namespace
                        namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
                        for event_elem in root.findall('.//ns:Event', namespace) or root.findall('.//Event'):
                            event_data = self.parse_event_xml(event_elem)
                            if event_data:
                                events.append(event_data)
                                
                    except ET.XMLSyntaxError as e:
                        self.logger.error(f"Final XML parsing fallback failed: {e}")
            
            self.logger.debug(f"Retrieved {len(events)} events from {log_name}")
            return events
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get events from {log_name}: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting events from {log_name}: {e}")
            return []
    
    def parse_event_xml(self, event_elem):
        """Parse an individual event XML element."""
        try:
            event_data = {}
            
            # Define namespace for XML parsing (handle default namespace)
            namespace = {'ns': 'http://schemas.microsoft.com/win/2004/08/events/event'}
            
            # Get System information - handle default namespace properly
            system_elem = event_elem.find('./ns:System', namespace)
            if system_elem is None:
                # Try without namespace (fallback)
                system_elem = event_elem.find('./System')
            if system_elem is not None:
                # Event ID
                event_id_elem = system_elem.find('./ns:EventID', namespace)
                if event_id_elem is None:
                    event_id_elem = system_elem.find('./EventID')
                if event_id_elem is not None:
                    event_data['event_id'] = event_id_elem.text
                
                # Level
                level_elem = system_elem.find('./ns:Level', namespace)
                if level_elem is None:
                    level_elem = system_elem.find('./Level')
                if level_elem is not None:
                    level_num = level_elem.text
                    level_map = {
                        '1': 'Critical',
                        '2': 'Error', 
                        '3': 'Warning',
                        '4': 'Information',
                        '5': 'Verbose'
                    }
                    event_data['level'] = level_map.get(level_num, f'Level {level_num}')
                    event_data['level_num'] = level_num
                
                # Time Created
                time_elem = system_elem.find('./ns:TimeCreated', namespace)
                if time_elem is None:
                    time_elem = system_elem.find('./TimeCreated')
                if time_elem is not None:
                    system_time = time_elem.get('SystemTime')
                    if system_time:
                        try:
                            # Parse ISO format datetime
                            dt = datetime.fromisoformat(system_time.replace('Z', '+00:00'))
                            event_data['time_created'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                        except:
                            event_data['time_created'] = system_time
                
                # Provider
                provider_elem = system_elem.find('./ns:Provider', namespace)
                if provider_elem is None:
                    provider_elem = system_elem.find('./Provider')
                if provider_elem is not None:
                    event_data['provider'] = provider_elem.get('Name', '')
                
                # Computer
                computer_elem = system_elem.find('./ns:Computer', namespace)
                if computer_elem is None:
                    computer_elem = system_elem.find('./Computer')
                if computer_elem is not None:
                    event_data['computer'] = computer_elem.text
                
                # Task Category
                task_elem = system_elem.find('./ns:Task', namespace)
                if task_elem is None:
                    task_elem = system_elem.find('./Task')
                if task_elem is not None:
                    event_data['task'] = task_elem.text
                
                # Keywords
                keywords_elem = system_elem.find('./ns:Keywords', namespace)
                if keywords_elem is None:
                    keywords_elem = system_elem.find('./Keywords')
                if keywords_elem is not None:
                    event_data['keywords'] = keywords_elem.text
            
            # Get EventData
            event_data_elem = event_elem.find('./ns:EventData', namespace)
            if event_data_elem is None:
                event_data_elem = event_elem.find('./EventData')
            if event_data_elem is not None:
                data_items = []
                # Try namespace-aware data element search first
                data_elements = event_data_elem.findall('./ns:Data', namespace)
                if not data_elements:
                    data_elements = event_data_elem.findall('./Data')
                
                for data_elem in data_elements:
                    name = data_elem.get('Name', '')
                    value = data_elem.text or ''
                    if name:
                        data_items.append(f"{name}: {value}")
                    else:
                        data_items.append(value)
                event_data['event_data'] = '\n'.join(data_items)
            
            # Get UserData (alternative to EventData)
            if 'event_data' not in event_data:
                user_data_elem = event_elem.find('./ns:UserData', namespace)
                if user_data_elem is None:
                    user_data_elem = event_elem.find('./UserData')
                if user_data_elem is not None:
                    # Convert UserData to string representation
                    event_data['event_data'] = ET.tostring(user_data_elem, encoding='unicode')
            
            # Default values
            event_data.setdefault('event_id', 'Unknown')
            event_data.setdefault('level', 'Information')
            event_data.setdefault('time_created', 'Unknown')
            event_data.setdefault('provider', 'Unknown')
            event_data.setdefault('computer', 'Unknown')
            event_data.setdefault('task', '')
            event_data.setdefault('event_data', '')
            
            return event_data
            
        except Exception as e:
            self.logger.error(f"Error parsing event XML: {e}")
            return None
    
    def get_event_details(self, log_name, event_id, provider=None):
        """Get detailed information about a specific event."""
        try:
            # Build query for specific event
            query = f"*[System[EventID={event_id}]]"
            if provider:
                query = f"*[System[EventID={event_id} and Provider[@Name='{provider}']]]"
            
            cmd = [
                'wevtutil', 'qe', log_name,
                '/q', query,
                '/c', '1',
                '/f', 'xml'
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            
            if result.stdout.strip():
                event_elem = ET.fromstring(result.stdout)
                return self.parse_event_xml(event_elem)
            
            return None
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get event details: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting event details: {e}")
            return None
    
    def clear_event_log(self, log_name):
        """Clear all events from a specific log."""
        try:
            subprocess.run([
                'wevtutil', 'cl', log_name
            ], check=True, capture_output=True)
            
            self.logger.info(f"Successfully cleared log: {log_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to clear log {log_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error clearing log {log_name}: {e}")
            return False
    
    def export_events(self, log_name, file_path, query="*"):
        """Export events to a file."""
        try:
            cmd = [
                'wevtutil', 'epl', log_name, file_path,
                '/q', query
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            
            self.logger.info(f"Successfully exported {log_name} to {file_path}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to export log {log_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error exporting log {log_name}: {e}")
            return False
