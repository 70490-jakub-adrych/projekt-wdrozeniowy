from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404

from ...models import Ticket, ActivityLog
from ..helpers import log_activity
from ..error_views import ticket_not_found

@login_required
def ticket_assign_to_me(request, pk):
    """Widok przypisywania zgłoszenia do siebie (tylko dla agentów)"""
    user = request.user
    
    if user.profile.role != 'agent':
        return HttpResponseForbidden("Tylko agenci mogą przypisywać zgłoszenia do siebie")
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Prevent assigning closed tickets
    if ticket.status == 'closed':
        messages.error(request, "Nie można przypisać zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Sprawdź czy zgłoszenie jest już przypisane do kogoś innego
    if ticket.assigned_to and ticket.assigned_to != user:
        return HttpResponseForbidden("To zgłoszenie jest już przypisane do innego agenta")
    
    if request.method == 'POST':
        # Przypisz zgłoszenie do aktualnego użytkownika
        ticket.assigned_to = user
        ticket.save()
        
        log_activity(
            request,
            'ticket_updated',
            ticket,
            f"Przypisano zgłoszenie '{ticket.title}' do {user.username}"
        )
        
        messages.success(request, 'Zgłoszenie zostało przypisane do Ciebie!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_assign.html', {'ticket': ticket})

@login_required
def activity_logs(request):
    """Widok listy logów aktywności (tylko dla adminów i superagentów)"""
    if request.user.profile.role not in ['admin', 'superagent']:
        return forbidden_access(request, "logów aktywności")
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    
    # Start with all logs
    logs = ActivityLog.objects.all()
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    # Paginate results
    paginator = Paginator(logs, 50)  # Show 50 logs per page
    page_number = request.GET.get('page')
    logs = paginator.get_page(page_number)
    
    return render(request, 'crm/logs/activity_logs.html', {
        'logs': logs,
        'action_filter': action_filter,
        'user_filter': user_filter,
    })

@login_required
def activity_log_detail(request, log_id):
    """Widok szczegółów pojedynczego logu (tylko dla adminów i superagentów)"""
    if request.user.profile.role not in ['admin', 'superagent']:
        return forbidden_access(request, "szczegółów logów")
    
    log = get_object_or_404(ActivityLog, id=log_id)
    
    return render(request, 'crm/logs/activity_log_detail.html', {
        'log': log,
    })