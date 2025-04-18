# Import all views and helpers to expose them at the package level

from .helpers import get_client_ip, log_activity
from .auth_views import (
    register,
    register_pending,
    custom_login_view,
    custom_logout_view,
    landing_page,
    pending_approvals,
    approve_user,
    reject_user
)
from .dashboard_views import dashboard
from .organization_views import (
    organization_list, organization_detail, 
    organization_create, organization_update
)
# Import from the tickets package instead of ticket_views
from .tickets import (
    ticket_list, ticket_detail, ticket_create, ticket_update,
    ticket_close, ticket_reopen, ticket_assign_to_me, debug_tickets
)
from .log_views import activity_logs
from .error_views import ticket_not_found, handle_custom_404

# Define all exported symbols
__all__ = [
    'get_client_ip',
    'log_activity',
    'register',
    'register_pending',
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
    'ticket_assign_to_me',
    'debug_tickets',
    'activity_logs',
    'pending_approvals',
    'approve_user',
    'reject_user',
    'ticket_not_found',
    'handle_custom_404'
]
