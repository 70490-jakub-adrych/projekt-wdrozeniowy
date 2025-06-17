from .user import (
    UserProfile, EmailVerification, 
    EmailNotificationSettings, ViewPermission,
    GroupViewPermission, UserViewPermission
)
from .organization import Organization
from .tickets import (
    Ticket, TicketComment, TicketAttachment,
    TicketStatistics, AgentWorkLog, WorkHours
)
from .activity import ActivityLog
from .group_settings import GroupSettings
from .two_factor import TwoFactorAuth, TrustedDevice  # Add this import

# Export all models
__all__ = [
    'UserProfile', 'EmailVerification', 'EmailNotificationSettings',
    'ViewPermission', 'GroupViewPermission', 'UserViewPermission',
    'Organization',
    'Ticket', 'TicketComment', 'TicketAttachment',
    'TicketStatistics', 'AgentWorkLog', 'WorkHours',
    'ActivityLog',
    'GroupSettings',
    'TwoFactorAuth', 'TrustedDevice'  # Add these models
]
