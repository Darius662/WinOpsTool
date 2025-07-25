"""Task Scheduler manager for Windows scheduled tasks."""
import subprocess
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from src.core.logger import setup_logger

class SchedulerManager:
    """Manager for Windows Task Scheduler operations."""
    
    def __init__(self):
        self.logger = setup_logger(self.__class__.__name__)
        
    def get_scheduled_tasks(self):
        """Get list of all scheduled tasks."""
        try:
            # Use schtasks command to get task list
            result = subprocess.run([
                'schtasks', '/query', '/fo', 'csv', '/v'
            ], capture_output=True, text=True, check=True)
            
            tasks = []
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                headers = [h.strip('"') for h in lines[0].split('","')]
                for line in lines[1:]:
                    if line.strip():
                        values = [v.strip('"') for v in line.split('","')]
                        if len(values) >= len(headers):
                            task_data = dict(zip(headers, values))
                            tasks.append({
                                'name': task_data.get('TaskName', ''),
                                'status': task_data.get('Status', ''),
                                'next_run': task_data.get('Next Run Time', ''),
                                'last_run': task_data.get('Last Run Time', ''),
                                'last_result': task_data.get('Last Result', ''),
                                'author': task_data.get('Author', ''),
                                'task_to_run': task_data.get('Task To Run', ''),
                                'start_in': task_data.get('Start In', ''),
                                'comment': task_data.get('Comment', ''),
                                'scheduled_task_state': task_data.get('Scheduled Task State', ''),
                                'idle_time': task_data.get('Idle Time', ''),
                                'power_management': task_data.get('Power Management', ''),
                                'run_as_user': task_data.get('Run As User', ''),
                                'delete_task_if_not_rescheduled': task_data.get('Delete Task If Not Rescheduled', ''),
                                'stop_task_if_runs_x_hours_and_x_mins': task_data.get('Stop Task If Runs X Hours and X Mins', ''),
                                'schedule': task_data.get('Schedule', ''),
                                'schedule_type': task_data.get('Schedule Type', ''),
                                'start_time': task_data.get('Start Time', ''),
                                'start_date': task_data.get('Start Date', ''),
                                'end_date': task_data.get('End Date', ''),
                                'days': task_data.get('Days', ''),
                                'months': task_data.get('Months', ''),
                                'repeat_every': task_data.get('Repeat: Every', ''),
                                'repeat_until_time': task_data.get('Repeat: Until: Time', ''),
                                'repeat_until_duration': task_data.get('Repeat: Until: Duration', ''),
                                'repeat_stop_if_still_running': task_data.get('Repeat: Stop If Still Running', '')
                            })
            
            self.logger.debug(f"Retrieved {len(tasks)} scheduled tasks")
            return tasks
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get scheduled tasks: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error getting scheduled tasks: {e}")
            return []
    
    def get_task_details(self, task_name):
        """Get detailed information about a specific task."""
        try:
            # Get task XML definition
            result = subprocess.run([
                'schtasks', '/query', '/tn', task_name, '/xml'
            ], capture_output=True, text=True, check=True)
            
            # Parse XML to get detailed information
            root = ET.fromstring(result.stdout)
            
            # Extract key information from XML
            details = {
                'name': task_name,
                'xml_content': result.stdout
            }
            
            # Try to extract common elements
            try:
                registration_info = root.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}RegistrationInfo')
                if registration_info is not None:
                    author = registration_info.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Author')
                    if author is not None:
                        details['author'] = author.text
                    
                    description = registration_info.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Description')
                    if description is not None:
                        details['description'] = description.text
                
                # Get triggers
                triggers = root.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Triggers')
                if triggers is not None:
                    details['triggers'] = []
                    for trigger in triggers:
                        trigger_info = {
                            'type': trigger.tag.split('}')[-1] if '}' in trigger.tag else trigger.tag
                        }
                        # Add trigger-specific details as needed
                        details['triggers'].append(trigger_info)
                
                # Get actions
                actions = root.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Actions')
                if actions is not None:
                    details['actions'] = []
                    for action in actions:
                        action_info = {
                            'type': action.tag.split('}')[-1] if '}' in action.tag else action.tag
                        }
                        exec_elem = action.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Command')
                        if exec_elem is not None:
                            action_info['command'] = exec_elem.text
                        
                        args_elem = action.find('.//{http://schemas.microsoft.com/windows/2004/02/mit/task}Arguments')
                        if args_elem is not None:
                            action_info['arguments'] = args_elem.text
                            
                        details['actions'].append(action_info)
                        
            except Exception as e:
                self.logger.debug(f"Error parsing task XML details: {e}")
            
            return details
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to get task details for {task_name}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error getting task details for {task_name}: {e}")
            return None
    
    def run_task(self, task_name):
        """Run a scheduled task immediately."""
        try:
            subprocess.run([
                'schtasks', '/run', '/tn', task_name
            ], check=True, capture_output=True)
            
            self.logger.info(f"Successfully ran task: {task_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to run task {task_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error running task {task_name}: {e}")
            return False
    
    def enable_task(self, task_name):
        """Enable a scheduled task."""
        try:
            subprocess.run([
                'schtasks', '/change', '/tn', task_name, '/enable'
            ], check=True, capture_output=True)
            
            self.logger.info(f"Successfully enabled task: {task_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to enable task {task_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error enabling task {task_name}: {e}")
            return False
    
    def disable_task(self, task_name):
        """Disable a scheduled task."""
        try:
            subprocess.run([
                'schtasks', '/change', '/tn', task_name, '/disable'
            ], check=True, capture_output=True)
            
            self.logger.info(f"Successfully disabled task: {task_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to disable task {task_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error disabling task {task_name}: {e}")
            return False
    
    def delete_task(self, task_name):
        """Delete a scheduled task."""
        try:
            subprocess.run([
                'schtasks', '/delete', '/tn', task_name, '/f'
            ], check=True, capture_output=True)
            
            self.logger.info(f"Successfully deleted task: {task_name}")
            return True
            
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Failed to delete task {task_name}: {e}")
            return False
        except Exception as e:
            self.logger.error(f"Error deleting task {task_name}: {e}")
            return False
