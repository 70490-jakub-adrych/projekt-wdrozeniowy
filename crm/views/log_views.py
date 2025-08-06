from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib import messages
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import timedelta
from collections import defaultdict
import logging

from ..models import ActivityLog
from .error_views import log_not_found, logs_access_forbidden
from .helpers import log_activity  # Import the log_activity function

# Configure logger
logger = logging.getLogger(__name__)


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
    
    # Ograniczenie do 1000 ostatnich wpisów przed grupowaniem (zwiększone dla paginacji)
    logs = logs[:1000]
    
    # Grupowanie podobnych logów
    grouped_logs = group_similar_logs(logs)
    
    # Paginacja
    per_page = request.GET.get('per_page', '15')
    # Handle mobile per_page parameter
    if not per_page or per_page == '':
        per_page = request.GET.get('per_page_mobile', '15')
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 15, 25, 50, 100]:
            per_page = 15
    except (ValueError, TypeError):
        per_page = 15
    
    paginator = Paginator(grouped_logs, per_page)
    page = request.GET.get('page', 1)
    
    try:
        grouped_logs_page = paginator.page(page)
    except PageNotAnInteger:
        grouped_logs_page = paginator.page(1)
    except EmptyPage:
        grouped_logs_page = paginator.page(paginator.num_pages)
    
    # Przygotuj parametry URL dla zachowania filtrów w paginacji
    url_params = {}
    if action_filter:
        url_params['action'] = action_filter
    if user_filter:
        url_params['user'] = user_filter
    if per_page != 15:
        url_params['per_page'] = per_page
    
    context = {
        'grouped_logs': grouped_logs_page,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'per_page': per_page,
        'url_params': url_params,
        'total_groups': paginator.count,
    }
    
    return render(request, 'crm/logs/activity_logs.html', context)


def group_similar_logs(logs):
    """
    Grupuje podobne logi na podstawie akcji, IP i czasu
    Zwraca listę słowników z danymi grup
    """
    groups = []
    current_group = None
    
    # Akcje które powinny być grupowane
    GROUPABLE_ACTIONS = ['404_error', '403_error', 'login_failed']
    
    for log in logs:
        should_group = False
        
        if current_group and log.action_type in GROUPABLE_ACTIONS:
            # Sprawdź czy można dodać do aktualnej grupy
            time_diff = (current_group['logs'][0].created_at - log.created_at).total_seconds()
            
            # Grupuj jeśli:
            # - Ta sama akcja
            # - Ten sam IP (lub oba brak IP)
            # - Różnica czasu mniejsza niż 10 sekund
            # - Ten sam użytkownik (lub oba anonimowi)
            if (current_group['action_type'] == log.action_type and
                current_group['ip_address'] == (log.ip_address or None) and
                time_diff <= 10 and
                current_group['user_id'] == (log.user.id if log.user else None)):
                should_group = True
        
        if should_group:
            # Dodaj do aktualnej grupy
            current_group['logs'].append(log)
            current_group['count'] = len(current_group['logs'])
            # Zaktualizuj czas końcowy
            current_group['time_span'] = (
                current_group['logs'][0].created_at - 
                current_group['logs'][-1].created_at
            ).total_seconds()
        else:
            # Rozpocznij nową grupę
            current_group = {
                'logs': [log],
                'count': 1,
                'action_type': log.action_type,
                'ip_address': log.ip_address or None,
                'user_id': log.user.id if log.user else None,
                'time_span': 0,
                'is_grouped': False,
                'main_log': log  # Główny log do wyświetlenia
            }
            groups.append(current_group)
    
    # Oznacz grupy z więcej niż jednym logiem jako grupowane
    for group in groups:
        if group['count'] > 1:
            group['is_grouped'] = True
    
    return groups


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
