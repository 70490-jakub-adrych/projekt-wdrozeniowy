from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404

from ...models import Ticket
from ..helpers import log_activity
from ..error_views import ticket_not_found
from ...services.email_service import EmailNotificationService  # Add this import if missing

@login_required
def ticket_assign_to_me(request, pk):
    """Widok przypisywania zgłoszenia do siebie (dla agentów i superagentów)"""
    user = request.user
    
    if user.profile.role not in ['agent', 'superagent']:
        return HttpResponseForbidden("Tylko agenci i superagenci mogą przypisywać zgłoszenia do siebie")
    
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
        
        # Send email notification about the assignment
        EmailNotificationService.notify_ticket_stakeholders('assigned', ticket, triggered_by=user)
        
        messages.success(request, 'Zgłoszenie zostało przypisane do Ciebie!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_assign.html', {'ticket': ticket})
