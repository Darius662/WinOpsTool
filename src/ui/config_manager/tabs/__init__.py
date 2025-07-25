"""WinOpsInit tabs package."""

from .welcome_tab import WelcomeTab
from .environment_tab import EnvironmentTab
from .registry_tab import RegistryTab
from .users_tab import UsersTab
from .services_tab import ServicesTab
from .firewall_tab import FirewallTab
from .software_tab import SoftwareTab
from .permissions_tab import PermissionsTab
from .applications_tab import ApplicationsTab
from .disk_tab import DiskTab
from .drivers_tab import DriversTab
from .network_tab import NetworkTab
from .packages_tab import PackagesTab
from .processes_tab import ProcessesTab
from .scheduler_tab import SchedulerTab
from .events_tab import EventsTab

__all__ = [
    'WelcomeTab',
    'EnvironmentTab',
    'RegistryTab',
    'UsersTab',
    'ServicesTab',
    'FirewallTab',
    'SoftwareTab',
    'PermissionsTab',
    'ApplicationsTab',
    'DiskTab',
    'DriversTab',
    'NetworkTab',
    'PackagesTab',
    'ProcessesTab',
    'SchedulerTab',
    'EventsTab'
]
