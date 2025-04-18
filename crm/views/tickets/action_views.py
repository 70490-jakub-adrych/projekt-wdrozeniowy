from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.utils import timezone

from ...models import Ticket
from ..helpers import log_activity

@login_required
def ticket_close(request, pk):
    """Widok zamykania zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdzenie uprawnień
    if role == 'client':
        if ticket.created_by != user:
            return HttpResponseForbidden("Nie możesz zamknąć tego zgłoszenia")
    elif role == 'agent':
        # Agent może zamykać tylko nieprzypisane zgłoszenia lub przypisane do niego
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz zamknąć zgłoszenia przypisanego do innego agenta")
    
    if request.method == 'POST':
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        log_activity(request, 'ticket_closed', ticket, f"Zamknięto zgłoszenie '{ticket.title}'")
        messages.success(request, 'Zgłoszenie zostało zamknięte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_close.html', {'ticket': ticket})


@login_required
def ticket_reopen(request, pk):
    """Widok ponownego otwierania zamkniętego zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Tylko admin i przypisany agent mogą ponownie otworzyć zgłoszenie
    if role == 'admin':
        pass  # Admin może wszystko
    elif role == 'agent':
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia przypisanego do innego agenta")
    else:
        return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia")
    
    if request.method == 'POST':
        ticket.status = 'new'
        ticket.closed_at = None
        ticket.save()
        
        log_activity(request, 'ticket_reopened', ticket, f"Ponownie otwarto zgłoszenie '{ticket.title}'")
        messages.success(request, 'Zgłoszenie zostało ponownie otwarte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_reopen.html', {'ticket': ticket})
