from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from django.utils import timezone

from ...models import Ticket
from ..helpers import log_activity
from ..error_views import ticket_not_found
from ...services.email_service import EmailNotificationService  # Add this import

@login_required
def ticket_close(request, pk):
    """Widok zamykania zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Sprawdzenie uprawnień
    if role == 'client':
        if ticket.created_by != user:
            return HttpResponseForbidden("Nie możesz zamknąć tego zgłoszenia")
    elif role == 'agent':
        # Agent może zamykać tylko zgłoszenia przypisane do niego
        if ticket.assigned_to != user:
            return HttpResponseForbidden("Możesz zamknąć tylko zgłoszenia przypisane do Ciebie")
    elif role == 'admin':
        # Admin może zamykać tylko przypisane zgłoszenia
        if ticket.assigned_to is None:
            return HttpResponseForbidden("Nie można zamknąć nieprzypisanego zgłoszenia")
    elif role == 'superagent':
        # Superagent może zamykać każde zgłoszenie (jak admin)
        if ticket.assigned_to is None:
            return HttpResponseForbidden("Nie można zamknąć nieprzypisanego zgłoszenia")
    
    if request.method == 'POST':
        # Store the old status for the log
        old_status = ticket.status
        
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        # Log closing with detailed information
        log_activity(
            request, 
            'ticket_closed', 
            ticket, 
            f"Zamknięto zgłoszenie '{ticket.title}' (zmiana statusu z '{old_status}' na 'closed')"
        )
        
        # Send email notification about the ticket closure
        EmailNotificationService.notify_ticket_stakeholders('closed', ticket, triggered_by=user, old_status=old_status)
        
        messages.success(request, 'Zgłoszenie zostało zamknięte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_close.html', {'ticket': ticket})


@login_required
def ticket_reopen(request, pk):
    """Widok ponownego otwierania zamkniętego zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Admin, superagent i przypisany agent mogą ponownie otworzyć zgłoszenie
    if role == 'admin':
        pass  # Admin może wszystko
    elif role == 'superagent':
        pass  # Superagent może wszystko co agent
    elif role == 'agent':
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia przypisanego do innego agenta")
    else:
        return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia")
    
    if request.method == 'POST':
        old_status = ticket.status
        ticket.status = 'new'
        ticket.closed_at = None
        ticket.save()
        
        log_activity(
            request, 
            'ticket_reopened', 
            ticket, 
            f"Ponownie otwarto zgłoszenie '{ticket.title}' (zmiana statusu z '{old_status}' na '{ticket.status}')"
        )
        
        # Send email notification about the ticket reopening
        EmailNotificationService.notify_ticket_stakeholders('reopened', ticket, triggered_by=user, old_status=old_status)
        
        messages.success(request, 'Zgłoszenie zostało ponownie otwarte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_reopen.html', {'ticket': ticket})
