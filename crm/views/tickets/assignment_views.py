from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from ...models import Ticket
from ..helpers import log_activity

@login_required
def ticket_assign_to_me(request, pk):
    """Widok przypisywania zgłoszenia do siebie (tylko dla agentów)"""
    user = request.user
    
    if user.profile.role != 'agent':
        return HttpResponseForbidden("Tylko agenci mogą przypisywać zgłoszenia do siebie")
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
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
