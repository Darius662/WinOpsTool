"""Service operations for Services Panel."""
from PyQt6.QtWidgets import QDialog
from src.core.logger import setup_logger
from ..manager import ServiceManager

class ServiceOperations:
    """Encapsulates service operations for the Services Panel."""
    
    def __init__(self, panel):
        """Initialize service operations.
        
        Args:
            panel: Parent ServicesPanel instance
        """
        self.panel = panel
        self.logger = setup_logger(self.__class__.__name__)
        self.manager = ServiceManager()
        
    @property
    def services_tree(self):
        """Get the services tree widget.
        
        Returns:
            ServicesTree: The services tree widget
        """
        if hasattr(self.panel, 'services_tree') and self.panel.services_tree is not None:
            return self.panel.services_tree
        return None
        
    @property
    def dialog_factory(self):
        """Get the dialog factory.
        
        Returns:
            DialogFactory: The dialog factory
        """
        if hasattr(self.panel, 'dialog_factory') and self.panel.dialog_factory is not None:
            return self.panel.dialog_factory
        return None
        
    def refresh_services(self):
        """Refresh the services list."""
        try:
            # Clear and repopulate tree
            if not self.services_tree:
                self.logger.error("Services tree not initialized")
                return
                
            self.services_tree.clear_services()
            services = self.manager.get_services()
            
            for service in services:
                self.services_tree.add_service(
                    service['name'],
                    service['display_name'],
                    service['description'],
                    service['state'],
                    service['start_type'],
                    service['path'],
                    service['account']
                )
                
            # Reapply filter if search text exists
            if hasattr(self.panel, 'search_edit') and self.panel.search_edit.text():
                self.filter_services(self.panel.search_edit.text())
                
            self.logger.info("Refreshed services list")
        except Exception as e:
            self.logger.error(f"Failed to refresh services: {str(e)}")
            if self.dialog_factory:
                self.dialog_factory.show_error("Failed to refresh services list")
    
    def refresh_services_with_highlighting(self):
        """Refresh the services list with highlighting for imported items."""
        try:
            # Clear and repopulate tree
            if not self.services_tree:
                self.logger.error("Services tree not initialized")
                return
                
            self.services_tree.clear_services()
            services = self.manager.get_services()
            
            for service in services:
                # Check if this service was imported from configuration
                is_imported = False
                if hasattr(self.panel, 'is_imported_config_item'):
                    is_imported = self.panel.is_imported_config_item(f"service:{service['name']}")
                
                # Add service to tree with highlighting if imported
                self.services_tree.add_service(
                    service['name'],
                    service['display_name'],
                    service['description'],
                    service['state'],
                    service['start_type'],
                    service['path'],
                    service['account'],
                    is_imported=is_imported
                )
                
            # Reapply filter if search text exists
            if hasattr(self.panel, 'search_edit') and self.panel.search_edit.text():
                self.filter_services(self.panel.search_edit.text())
                
            self.logger.info("Refreshed services list with highlighting")
        except Exception as e:
            self.logger.error(f"Failed to refresh services: {str(e)}")
            if self.dialog_factory:
                self.dialog_factory.show_error("Failed to refresh services list")
            
    def filter_services(self, text):
        """Filter services by name or display name.
        
        Args:
            text: Search text
        """
        if not self.services_tree:
            self.logger.error("Services tree not initialized")
            return
            
        for i in range(self.services_tree.topLevelItemCount()):
            item = self.services_tree.topLevelItem(i)
            name = item.text(0).lower()
            display_name = item.text(1).lower()
            search = text.lower()
            item.setHidden(search not in name and search not in display_name)
            
    def start_service(self):
        """Start selected service."""
        if not self.services_tree or not self.services_tree.selectedItems():
            self.logger.error("No service selected")
            return
            
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        if self.manager.start_service(name):
            self.refresh_services()
            # Find and select the service again
            item = self.services_tree.find_service(name)
            if item:
                item.setSelected(True)
        else:
            if self.dialog_factory:
                self.dialog_factory.show_error(f"Failed to start service '{name}'")
            
    def stop_service(self):
        """Stop selected service."""
        if not self.services_tree or not self.services_tree.selectedItems():
            self.logger.error("No service selected")
            return
            
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        if self.dialog_factory and self.dialog_factory.confirm_action(
            "Confirm Stop",
            f"Are you sure you want to stop service '{name}'?"
        ):
            if self.manager.stop_service(name):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(name)
                if item:
                    item.setSelected(True)
            else:
                self.dialog_factory.show_error(f"Failed to stop service '{name}'")
                
    def restart_service(self):
        """Restart selected service."""
        if not self.services_tree or not self.services_tree.selectedItems():
            self.logger.error("No service selected")
            return
            
        item = self.services_tree.selectedItems()[0]
        name = item.text(0)
        
        if self.dialog_factory and self.dialog_factory.confirm_action(
            "Confirm Restart",
            f"Are you sure you want to restart service '{name}'?"
        ):
            if self.manager.restart_service(name):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(name)
                if item:
                    item.setSelected(True)
            else:
                self.dialog_factory.show_error(f"Failed to restart service '{name}'")
                
    def change_startup(self):
        """Change startup type of selected service."""
        if not self.services_tree or not self.services_tree.selectedItems():
            self.logger.error("No service selected")
            return
            
        item = self.services_tree.selectedItems()[0]
        service = self.services_tree.get_service(item)
        
        if not self.dialog_factory:
            self.logger.error("Dialog factory not initialized")
            return
            
        dialog = self.dialog_factory.create_startup_type_dialog(service['start_type'])
        if dialog.exec():
            start_type = dialog.get_startup_type()
            if self.manager.set_startup_type(service['name'], start_type):
                self.refresh_services()
                # Find and select the service again
                item = self.services_tree.find_service(service['name'])
                if item:
                    item.setSelected(True)
            else:
                self.dialog_factory.show_error(f"Failed to change startup type for '{service['name']}'")
                
    def edit_service(self):
        """Edit selected service properties.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Check if a service is selected
            if not self.services_tree or not self.services_tree.selectedItems():
                self.logger.error("No service selected")
                return False
                
            # Get selected service
            item = self.services_tree.selectedItems()[0]
            service = self.services_tree.get_service(item)
            service_name = service['name']
                
            # Create and show dialog
            dialog = self.dialog_factory.create_edit_service_dialog(service)
            if dialog.exec() != QDialog.DialogCode.Accepted:
                return False
                
            # Get updated data
            updated_data = dialog.get_service_data()
            self.logger.info(f"Editing service {service_name} with data: {updated_data}")
            
            # Track changes for success message
            changes_made = []
            errors = []
            
            # Update service properties
            # 1. Update startup type if changed
            if updated_data['start_type'] != service.get('start_type'):
                success = self.manager.set_startup_type(
                    service_name, updated_data['start_type']
                )
                if success:
                    changes_made.append(f"Startup type changed to {updated_data['start_type']}")
                else:
                    errors.append("Failed to update startup type")
            
            # 2. Update delayed auto-start if changed
            if 'delayed_start' in updated_data:
                current_delayed = service.get('delayed_start', False)
                if updated_data['delayed_start'] != current_delayed:
                    success = self.manager.set_delayed_auto_start(
                        service_name, updated_data['delayed_start']
                    )
                    if success:
                        status = "enabled" if updated_data['delayed_start'] else "disabled"
                        changes_made.append(f"Delayed auto-start {status}")
                    else:
                        errors.append("Failed to update delayed auto-start setting")
            
            # 3. Update display name if changed
            if updated_data['display_name'] != service.get('display_name'):
                success = self.manager.set_display_name(
                    service_name, updated_data['display_name']
                )
                if success:
                    changes_made.append("Display name updated")
                else:
                    errors.append("Failed to update display name")
            
            # 4. Update description if changed
            if updated_data['description'] != service.get('description'):
                success = self.manager.set_description(
                    service_name, updated_data['description']
                )
                if success:
                    changes_made.append("Description updated")
                else:
                    errors.append("Failed to update description")
            
            # 5. Update path if changed
            if updated_data['path'] != service.get('path'):
                success = self.manager.set_path(
                    service_name, updated_data['path']
                )
                if success:
                    changes_made.append("Binary path updated")
                else:
                    errors.append("Failed to update binary path")
            
            # 6. Update account if changed
            if updated_data['account'] != service.get('account'):
                success = self.manager.set_account(
                    service_name, 
                    updated_data['account'],
                    updated_data.get('password')
                )
                if success:
                    changes_made.append("Logon account updated")
                else:
                    errors.append("Failed to update logon account")
            
            # 7. Update recovery options if provided
            if 'recovery' in updated_data:
                recovery = updated_data['recovery']
                success = self.manager.set_recovery_options(
                    service_name,
                    first_action=recovery['first_action'],
                    second_action=recovery['second_action'],
                    third_action=recovery['subsequent_action'],
                    reset_period=recovery['reset_period']
                )
                if success:
                    changes_made.append("Recovery options updated")
                else:
                    errors.append("Failed to update recovery options")
            
            # Show results dialog
            if changes_made:
                changes_text = "\n- ".join([""] + changes_made)
                message = f"Service {service_name} updated successfully.{changes_text}"
                
                if errors:
                    errors_text = "\n- ".join([""] + errors)
                    message += f"\n\nSome changes could not be applied:{errors_text}"
                    
                self.dialog_factory.show_info(message)
            elif errors:
                errors_text = "\n- ".join([""] + errors)
                self.dialog_factory.show_error(f"Failed to update service:{errors_text}")
            else:
                self.dialog_factory.show_info("No changes were made to the service.")
            
            # Refresh services list
            self.refresh_services()
            
            # Find and select the service again
            item = self.services_tree.find_service(service_name)
            if item:
                item.setSelected(True)
            
            return len(errors) == 0
            
        except Exception as e:
            self.logger.error(f"Error editing service: {str(e)}")
            self.dialog_factory.show_error(f"Failed to edit service: {str(e)}")
            return False
