# Import all views and helpers to expose them at the package level

from .helpers import get_client_ip, log_activity

# Import dashboard views
from .dashboard_views import dashboard

# Import authentication views
from .auth_views import (
    landing_page, 
    register, 
    register_pending, 
    CustomLoginView,
    custom_login_success, 
    custom_logout_view, 
    pending_approvals, 
    approve_user, 
    reject_user,
    unlock_user,
    custom_password_change_view
)

# Import ticket views
from .tickets.list_views import ticket_list, debug_tickets
from .tickets.create_views import ticket_create
from .tickets.detail_views import ticket_detail
from .tickets.update_views import ticket_update
from .tickets.action_views import ticket_close, ticket_reopen
from .tickets.assignment_views import ticket_assign_to_me

# Import log views
from .log_views import activity_logs, activity_log_detail

# Import organization views
from .organization_views import organization_list, organization_create, organization_detail, organization_update

# Import error views as a module
from . import error_views

# Import new ticket display views
from .ticket_display_views import ticket_display_view, get_tickets_update

# Import statistics views
from .statistics_views import statistics_dashboard, update_agent_work_log, generate_statistics_report

# Define all exported symbols
__all__ = [
    'get_client_ip',
    'log_activity',
    'register',
    'register_pending',
    'CustomLoginView',
    'custom_login_success',
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
    'activity_log_detail',
    'pending_approvals',
    'approve_user',
    'reject_user',
    'unlock_user',
    'custom_password_change_view',
    'ticket_display_view',
    'get_tickets_update',
    'statistics_dashboard',
    'update_agent_work_log',
    'generate_statistics_report'
]
