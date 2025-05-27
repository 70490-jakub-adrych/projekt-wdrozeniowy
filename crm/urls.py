from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    landing_page, register, register_pending,
    CustomLoginView, custom_login_success, custom_logout_view,
    dashboard, 
    organization_list, organization_create, organization_detail, organization_update,
    ticket_list, ticket_detail, ticket_create, ticket_update, 
    ticket_close, ticket_reopen, ticket_assign_to_me,
    activity_logs, activity_log_detail,
    pending_approvals, approve_user, reject_user
)
from .views.auth_views import unlock_user
from . import views
from .views import secure_file_views
from django.contrib.auth import views as auth_views
from .views.auth_views import custom_password_change_view

urlpatterns = [
    # Landing and authentication
    path('', landing_page, name='landing_page'),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('login/success/', custom_login_success, name='custom_login_success'),
    path('logout/', custom_logout_view, name='logout'),
    path('register/', register, name='register'),
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
    path('tickets/<int:pk>/close/', ticket_close, name='ticket_close'),
    path('tickets/<int:pk>/reopen/', ticket_reopen, name='ticket_reopen'),
    path('tickets/<int:pk>/assign/', ticket_assign_to_me, name='ticket_assign_to_me'),
    
    # Activity logs (for admins)
    path('logs/', activity_logs, name='activity_logs'),
    path('logs/<int:log_id>/', activity_log_detail, name='activity_log_detail'),
    
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

    # Password change
    path('password/change/', custom_password_change_view, name='password_change'),
    
    # Password reset
    path('password/reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt',
        success_url='/password/reset/done/'
    ), name='password_reset'),
    
    path('password/reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    
    path('password/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html',
        success_url='/password/reset/complete/'
    ), name='password_reset_confirm'),
    
    path('password/reset/complete/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
]
