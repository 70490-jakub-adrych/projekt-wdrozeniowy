# Import all views and helpers to expose them at the package level

from .helpers import get_client_ip, log_activity
from .auth_views import register, custom_login_view, custom_logout_view, landing_page
from .dashboard_views import dashboard
from .organization_views import (
    organization_list, organization_detail, 
    organization_create, organization_update
)
from .ticket_views import (
    ticket_list, ticket_detail, ticket_create, ticket_update,
    ticket_close, ticket_reopen
)
from .log_views import activity_logs

# Define all exported symbols
__all__ = [
    'get_client_ip',
    'log_activity',
    'register',
    'custom_login_view',
    'custom_logout_view',
    'landing_page',
    'dashboard',
    'organization_list',
    'organization_detail',
    'organization_create',
    'organization_update',
    'ticket_list',
    'ticket_detail',
    'ticket_create',
    'ticket_update',
    'ticket_close',
    'ticket_reopen',
    'activity_logs',
]
