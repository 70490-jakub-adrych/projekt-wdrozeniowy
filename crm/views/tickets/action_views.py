from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from django.utils import timezone

from ...models import Ticket
from ..helpers import log_activity
from ..error_views import ticket_not_found
from ...services.email_service import EmailNotificationService  # Add this import
from ...services.email.ticket import notify_ticket_stakeholders  # Import the function directly

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
        
        messages.success(request, 'Zgłosenie zostało zamknięte!')
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
        # Store the old status for the log
        old_status = ticket.status
        
        # Change to unresolved instead of in_progress
        ticket.status = 'unresolved'  # Changed from 'in_progress' to 'unresolved'
        ticket.closed_at = None
        ticket.save()
        
        # Log reopening
        log_activity(
            request, 
            'ticket_reopened', 
            ticket, 
            f"Ponownie otwarto zgłoszenie '{ticket.title}' (zmiana statusu z '{old_status}' na 'Nierozwiązany')"
        )
        
        # Send email notification
        EmailNotificationService.notify_ticket_stakeholders('reopened', ticket, triggered_by=user, old_status=old_status)
        
        messages.success(request, 'Zgłoszenie zostało ponownie otwarte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_reopen.html', {'ticket': ticket})

@login_required
def ticket_confirm_solution(request, pk):
    """Widok dla klientów do potwierdzania lub odrzucania rozwiązania zgłoszenia"""
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Tylko autor zgłoszenia może potwierdzić/odrzucić rozwiązanie
    if ticket.created_by != request.user:
        return HttpResponseForbidden("Tylko autor zgłoszenia może potwierdzić rozwiązanie")
    
    # Tylko rozwiązane zgłoszenia mogą być potwierdzane
    if ticket.status != 'resolved':
        messages.error(request, "Tylko rozwiązane zgłoszenia mogą być potwierdzane.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        old_status = ticket.status
        
        if action == 'accept':
            # Klient akceptuje rozwiązanie, zamknij zgłoszenie
            ticket.status = 'closed'
            ticket.closed_at = timezone.now()
            ticket.save()
            
            log_activity(
                request,
                'ticket_closed',
                ticket,
                f"Klient potwierdził rozwiązanie zgłoszenia '{ticket.title}'"
            )
            
            # Wyślij powiadomienie e-mail o akceptacji przez klienta
            EmailNotificationService.notify_ticket_stakeholders(
                'closed', ticket, triggered_by=request.user, 
                old_status=old_status, client_confirmed=True
            )
            
            messages.success(request, 'Dziękujemy za potwierdzenie! Zgłoszenie zostało zamknięte.')
            
        elif action == 'deny':
            # Klient odrzuca rozwiązanie, otwórz ponownie jako nierozwiązane
            ticket.status = 'unresolved'  # Zmieniono na status 'nierozwiązany'
            ticket.save()
            
            log_activity(
                request,
                'ticket_reopened',
                ticket,
                f"Klient oznaczył zgłoszenie '{ticket.title}' jako nierozwiązane"
            )
            
            # Wyślij powiadomienie e-mail o odrzuceniu przez klienta
            EmailNotificationService.notify_ticket_stakeholders(
                'reopened', ticket, triggered_by=request.user, 
                old_status=old_status, client_confirmed=False
            )
            
            messages.warning(request, 'Zgłoszenie zostało ponownie otwarte jako nierozwiązane.')
        
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Jeśli osiągnięto metodą GET, przekieruj na stronę szczegółów
    return redirect('ticket_detail', pk=ticket.pk)

@login_required
def ticket_mark_resolved(request, pk):
    """View for marking a ticket as resolved"""
    user = request.user
    role = user.profile.role
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Check permissions
    if role == 'client':
        return HttpResponseForbidden("Nie możesz oznaczyć tego zgłoszenia jako rozwiązane")
    elif role == 'agent':
        # Agent can only mark tickets assigned to them
        if ticket.assigned_to != user:
            return HttpResponseForbidden("Możesz oznaczyć jako rozwiązane tylko zgłoszenia przypisane do Ciebie")
    elif role == 'admin':
        # Admin needs to have a ticket assigned
        if ticket.assigned_to is None:
            return HttpResponseForbidden("Nie można oznaczyć jako rozwiązane nieprzypisanego zgłoszenia")
    elif role == 'superagent':
        if ticket.assigned_to is None:
            return HttpResponseForbidden("Nie można oznaczyć jako rozwiązane nieprzypisanego zgłoszenia")
    
    if request.method == 'POST':
        # Store the old status for the log
        old_status = ticket.status
        
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        # Log the status change
        log_activity(
            request, 
            'ticket_resolved', 
            ticket, 
            f"Oznaczono zgłoszenie '{ticket.title}' jako rozwiązane (zmiana statusu z '{old_status}' na 'resolved')"
        )
        
        # Send email notification about the ticket being resolved
        notify_ticket_stakeholders('resolved', ticket, triggered_by=user, old_status=old_status)
        
        messages.success(request, 'Zgłoszenie zostało oznaczone jako rozwiązane!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_resolve.html', {'ticket': ticket})
