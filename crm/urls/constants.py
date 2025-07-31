"""
Constants file for URL names used throughout the application.
This ensures consistency and helps prevent URL resolution errors.
"""

# Main navigation
DASHBOARD_URL = 'dashboard'
PROFILE_URL = 'dashboard'  # Fallback for any 'profile' references

# Authentication
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# Two-factor authentication
VERIFY_2FA_URL = 'verify_2fa'
SETUP_2FA_URL = 'setup_2fa'
SETUP_2FA_SUCCESS_URL = 'setup_2fa_success'
RECOVERY_CODE_URL = 'recovery_code'
DEBUG_2FA_URL = 'debug_2fa'

# User management
PENDING_APPROVALS_URL = 'pending_approvals'
