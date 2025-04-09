from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='tickets/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.dashboard, name='dashboard'),
    path('ticket/<int:ticket_id>/', views.ticket_detail, name='ticket_detail'),
    path('ticket/create/', views.ticket_create, name='ticket_create'),
    path('ticket/<int:ticket_id>/edit/', views.ticket_edit, name='ticket_edit'),
    path('ticket/<int:ticket_id>/close/', views.ticket_close, name='ticket_close'),
]
