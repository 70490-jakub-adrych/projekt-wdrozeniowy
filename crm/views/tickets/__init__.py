"""
Ticket views package - contains all views related to ticket functionality.
This __init__.py file imports and exposes all ticket view functions to maintain
backward compatibility with existing code that imports from ticket_views.py.
"""

from .list_views import ticket_list, debug_tickets
from .detail_views import ticket_detail
from .create_views import ticket_create
from .update_views import ticket_update
from .action_views import ticket_close, ticket_reopen
from .assignment_views import ticket_assign_to_me
from .unassignment_views import ticket_unassign

# Export all functions to maintain backward compatibility
__all__ = [
    'ticket_list',
    'debug_tickets',
    'ticket_detail',
    'ticket_create', 
    'ticket_update',
    'ticket_close',
    'ticket_reopen',
    'ticket_assign_to_me',
    'ticket_unassign',
]
