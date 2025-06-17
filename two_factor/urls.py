from django.urls import path
from . import views

urlpatterns = [
    path('setup/', views.setup_2fa, name='two_factor_setup'),
    path('verify/', views.verify_2fa, name='two_factor_verify'),
    path('recovery/', views.recovery_2fa, name='two_factor_recovery'),
    path('regenerate-recovery-code/', views.regenerate_recovery_code, name='two_factor_regenerate_code'),
    path('disable/', views.disable_2fa, name='two_factor_disable'),
]
