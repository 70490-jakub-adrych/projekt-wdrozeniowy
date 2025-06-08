from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages

from ..models import ActivityLog
from .error_views import log_not_found, logs_access_forbidden


@login_required
def activity_logs(request):
    """Widok logów aktywności"""
    user = request.user
    role = user.profile.role
    
    # Tylko admin i superagent mogą oglądać wszystkie logi
    if role not in ['admin', 'superagent']:
        return logs_access_forbidden(request)
    
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


@login_required
def activity_log_detail(request, log_id):
    """Widok szczegółów pojedynczego logu"""
    user = request.user
    role = user.profile.role
    
    # Tylko admin i superagent mogą oglądać szczegóły logów
    if role not in ['admin', 'superagent']:
        return logs_access_forbidden(request)
    
    # Try to get the log, use custom 404 handler if not found
    try:
        log = get_object_or_404(ActivityLog, id=log_id)
    except:
        return log_not_found(request, log_id)
    
    context = {
        'log': log,
    }
    
    return render(request, 'crm/logs/activity_log_detail.html', context)
