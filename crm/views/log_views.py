from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden

from ..models import ActivityLog


@login_required
def activity_logs(request):
    """Widok logów aktywności"""
    user = request.user
    role = user.profile.role
    
    # Tylko admin może oglądać wszystkie logi
    if role != 'admin':
        return HttpResponseForbidden("Brak dostępu do logów")
    
    logs = ActivityLog.objects.all().order_by('-created_at')
    
    # Filtrowanie
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    context = {
        'logs': logs[:100],  # Ograniczenie do 100 ostatnich wpisów
        'action_filter': action_filter,
        'user_filter': user_filter,
    }
    
    return render(request, 'crm/logs/activity_logs.html', context)
