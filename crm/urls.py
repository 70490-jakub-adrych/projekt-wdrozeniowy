from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Strona główna
    path('', views.landing_page, name='landing_page'),
    
    # Autentykacja
    path('register/', views.register, name='register'),
    path('register/pending/', views.register_pending, name='register_pending'),
    path('login/', auth_views.LoginView.as_view(template_name='crm/login.html', 
                                               success_url='custom_login'), name='login'),
    path('custom_login/', views.custom_login_view, name='custom_login'),
    path('logout/', views.custom_logout_view, name='logout'),
    
    # Zatwierdzanie użytkowników
    path('approvals/', views.pending_approvals, name='pending_approvals'),
    path('approvals/approve/<int:user_id>/', views.approve_user, name='approve_user'),
    path('approvals/reject/<int:user_id>/', views.reject_user, name='reject_user'),
    
    # Panel główny
    path('dashboard/', views.dashboard, name='dashboard'),
    
    # Organizacje
    path('organizations/', views.organization_list, name='organization_list'),
    path('organizations/create/', views.organization_create, name='organization_create'),
    path('organizations/<int:pk>/', views.organization_detail, name='organization_detail'),
    path('organizations/<int:pk>/update/', views.organization_update, name='organization_update'),
    
    # Zgłoszenia
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/create/', views.ticket_create, name='ticket_create'),
    path('tickets/<int:pk>/', views.ticket_detail, name='ticket_detail'),
    path('tickets/<int:pk>/update/', views.ticket_update, name='ticket_update'),
    path('tickets/<int:pk>/close/', views.ticket_close, name='ticket_close'),
    path('tickets/<int:pk>/reopen/', views.ticket_reopen, name='ticket_reopen'),
    path('tickets/<int:pk>/assign-to-me/', views.ticket_assign_to_me, name='ticket_assign_to_me'),
    
    # Logi aktywności
    path('logs/', views.activity_logs, name='activity_logs'),
]
