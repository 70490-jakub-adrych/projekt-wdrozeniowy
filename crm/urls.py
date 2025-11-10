from django.urls import path
from django.contrib.auth.views import LogoutView
from django.urls import reverse_lazy  # Add this missing import
from .views import (
    landing_page, register, register_pending,
    CustomLoginView, custom_login_success, custom_logout_view,
    dashboard, 
    organization_list, organization_create, organization_detail, organization_update,
    ticket_list, ticket_detail, ticket_create, ticket_update, 
    ticket_close, ticket_reopen, ticket_assign_to_me,
    activity_logs, activity_log_detail,
    pending_approvals, approve_user, reject_user,
    ticket_display_view, get_tickets_update
)
from .views.auth_views import (
    unlock_user, HTMLEmailPasswordResetView, EnhancedPasswordResetConfirmView, 
    custom_password_reset_complete, custom_password_change_view
)
from .views.tickets.action_views import (ticket_confirm_solution, ticket_close, ticket_reopen, ticket_mark_resolved)  # Add this import
from .views.tickets.calendar_views import assign_ticket_to_calendar, get_calendar_assignments
from .views.duty_views import generate_duties, change_duty
from . import views
from .views import secure_file_views, log_views  # Add log_views import here
from django.contrib.auth import views as auth_views
from .views.statistics_views import statistics_dashboard, update_agent_work_log, generate_statistics_report, generate_organization_report
from .views.tickets.unassignment_views import ticket_unassign
from .views.tickets.assignment_views import ticket_assign_to_other
from .views.two_factor_views import setup_2fa, setup_2fa_success, disable_2fa, verify_2fa, recovery_code
from .views.api_views import (
    user_contact_info, toggle_theme, agent_tickets,
    calendar_notes_api, calendar_note_create, calendar_note_update, calendar_note_delete
)

urlpatterns = [
    # Landing and authentication
    path('', landing_page, name='landing_page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login/success/', custom_login_success, name='custom_login_success'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', register, name='register'),
    path('verify-email/', views.auth_views.verify_email, name='verify_email'),  # Email verification step
    path('register/pending/', register_pending, name='register_pending'),
    
    # Dashboard
    path('dashboard/', dashboard, name='dashboard'),
    
    # Organizations
    path('organizations/', organization_list, name='organization_list'),
    path('organizations/create/', organization_create, name='organization_create'),
    path('organizations/<int:pk>/', organization_detail, name='organization_detail'),
    path('organizations/<int:pk>/update/', organization_update, name='organization_update'),
    
    # Tickets
    path('tickets/', ticket_list, name='ticket_list'),
    path('tickets/create/', ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/update/', ticket_update, name='ticket_update'),
    
    # Ticket actions
    path('tickets/<int:pk>/assign/', ticket_assign_to_me, name='ticket_assign_to_me'),
    path('tickets/<int:pk>/assign-to-other/', ticket_assign_to_other, name='ticket_assign_to_other'),
    path('tickets/<int:pk>/unassign/', ticket_unassign, name='ticket_unassign'),
    path('tickets/<int:pk>/close/', ticket_close, name='ticket_close'),
    path('tickets/<int:pk>/reopen/', ticket_reopen, name='ticket_reopen'),
    path('tickets/<int:pk>/mark-resolved/', ticket_mark_resolved, name='ticket_mark_resolved'),
    
    # Calendar assignments
    path('tickets/<int:ticket_id>/assign-to-calendar/', assign_ticket_to_calendar, name='assign_ticket_to_calendar'),
    path('calendar/assignments/', get_calendar_assignments, name='get_calendar_assignments'),
    
    # Calendar duties
    path('calendar/generate-duties/', generate_duties, name='generate_duties'),
    path('calendar/change-duty/', change_duty, name='change_duty'),
    
    path('tickets/display/', ticket_display_view, name='ticket_display'),
    
    # Activity logs (for admins)
    path('logs/', activity_logs, name='activity_logs'),
    path('logs/<int:log_id>/', activity_log_detail, name='activity_log_detail'),
    path('logs/wipe/', log_views.activity_logs_wipe, name='activity_logs_wipe'),  # This line is now properly imported
    
    # User approvals
    path('approvals/', pending_approvals, name='pending_approvals'),
    path('approvals/<int:user_id>/approve/', approve_user, name='approve_user'),
    path('approvals/<int:user_id>/reject/', reject_user, name='reject_user'),
    path('approvals/<int:user_id>/unlock/', unlock_user, name='unlock_user'),

    # Secure files
    path('secure-file/<int:attachment_id>/', secure_file_views.serve_attachment, name='serve_attachment'),

    # Test error pages
    path('test-404/', views.error_views.test_404_page, name='test_404_page'),
    path('test-403/', views.error_views.test_403_page, name='test_403_page'),

    # Password management - unified flow
    path('password/change/', custom_password_change_view, name='password_change'),
    path('password/change/done/', auth_views.PasswordChangeDoneView.as_view(
        template_name='emails/password_change_done.html'
    ), name='password_change_done'),
    
    # Password reset flow (both for logged-in users and forgotten passwords)
    path('password_reset/', HTMLEmailPasswordResetView.as_view(
        template_name='emails/password_reset_form.html',
        email_template_name='emails/password_reset_email.txt',
        html_email_template_name='emails/password_reset_email.html',
        success_url=reverse_lazy('password_reset_done')
    ), name='password_reset'),
    
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='emails/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('reset/<uidb64>/<token>/', EnhancedPasswordResetConfirmView.as_view(
        template_name='emails/password_reset_confirm.html',
        success_url=reverse_lazy('password_reset_complete')
    ), name='password_reset_confirm'),
    
    path('reset/done/', custom_password_reset_complete, name='password_reset_complete'),

    # Statistics URLs
    path('statistics/', statistics_dashboard, name='statistics_dashboard'),
    path('statistics/update-work-log/', update_agent_work_log, name='update_work_log'),
    path('statistics/generate-report/', generate_statistics_report, name='generate_statistics_report'),
    path('statistics/organization-report/', generate_organization_report, name='generate_organization_report'),

    path('get_tickets_update/', get_tickets_update, name='get_tickets_update'),

    # Ticket solution confirmation
    path('tickets/<int:pk>/confirm-solution/', ticket_confirm_solution, name='ticket_confirm_solution'),

    # 2FA URLs
    path('2fa/setup/', setup_2fa, name='setup_2fa'),
    path('2fa/success/', setup_2fa_success, name='setup_2fa_success'),
    path('2fa/disable/', disable_2fa, name='disable_2fa'),
    path('2fa/verify/', verify_2fa, name='verify_2fa'),
    path('2fa/recovery/', recovery_code, name='recovery_code'),

    # API URLs
    path('api/user-contact/<int:user_id>/', user_contact_info, name='user_contact_info'),
    path('api/agent-tickets/<int:agent_id>/', agent_tickets, name='agent_tickets'),
    path('api/toggle-theme/', toggle_theme, name='toggle_theme'),
    
    # Calendar Notes API
    path('api/calendar-notes/', calendar_notes_api, name='calendar_notes_api'),
    path('api/calendar-notes/create/', calendar_note_create, name='calendar_note_create'),
    path('api/calendar-notes/<int:note_id>/update/', calendar_note_update, name='calendar_note_update'),
    path('api/calendar-notes/<int:note_id>/delete/', calendar_note_delete, name='calendar_note_delete'),

]
