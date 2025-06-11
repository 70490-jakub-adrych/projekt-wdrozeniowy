from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST

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


@login_required
@staff_member_required
def activity_logs_wipe(request):
    """Widok dla administratora do usunięcia wszystkich logów aktywności z potwierdzeniem kodu sekretnego"""
    user = request.user
    role = user.profile.role
    
    # Tylko admin może uzyskać dostęp do tej funkcjonalności
    if role != 'admin':
        return logs_access_forbidden(request)
    
    if request.method == 'POST':
        secret_code = request.POST.get('secret_code')
        confirmation = request.POST.get('confirmation')
        
        if secret_code and confirmation == 'WIPE_LOGS':
            # Sprawdź, czy podany kod sekretu pasuje do tego w ustawieniach
            if secret_code == settings.LOG_WIPE_SECRET_CODE:
                try:
                    # Zlicz logi przed ich usunięciem w celach informacyjnych
                    log_count = ActivityLog.objects.count()
                    
                    # Utwórz końcowy wpis logu dotyczący operacji usunięcia
                    log_activity(
                        request=request,
                        action_type='logs_wiped',
                        description=f"Logi aktywności usunięte przez administratora: {request.user.username}. Usunięto {log_count} logów."
                    )
                    
                    # Usuń wszystkie logi z wyjątkiem tego, który właśnie utworzyliśmy
                    latest_log = ActivityLog.objects.latest('created_at')
                    ActivityLog.objects.exclude(id=latest_log.id).delete()
                    
                    messages.success(request, f"Pomyślnie usunięto {log_count} logów aktywności.")
                except Exception as e:
                    logger.error(f"Wystąpił błąd podczas usuwania logów: {str(e)}")
                    messages.error(request, f"Wystąpił błąd podczas usuwania logów: {str(e)}")
            else:
                messages.error(request, "Nieprawidłowy kod sekretu. Logi nie zostały usunięte.")
        else:
            messages.error(request, "Wymagane są zarówno kod sekretu, jak i tekst potwierdzenia.")
    
    return render(request, 'crm/logs/activity_logs_wipe.html')
