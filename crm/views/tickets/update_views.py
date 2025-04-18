from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404

from ...models import Ticket
from ...forms import ModeratorTicketForm, ClientTicketForm
from ..helpers import log_activity
from ..error_views import ticket_not_found, ticket_edit_forbidden

@login_required
def ticket_update(request, pk):
    """Widok aktualizacji zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Prevent editing closed tickets
    if ticket.status == 'closed':
        messages.error(request, "Nie można edytować zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Sprawdzenie uprawnień do edycji
    if role == 'client':
        # Klient może edytować tylko swoje zgłoszenia
        if ticket.created_by != user:
            return ticket_edit_forbidden(request, pk)
    elif role == 'agent':
        # Agent może edytować tylko nieprzypisane zgłoszenia lub przypisane do niego
        if ticket.assigned_to and ticket.assigned_to != user:
            return ticket_edit_forbidden(request, pk)
    
    if request.method == 'POST':
        # Inny formularz w zależności od roli
        if role == 'admin':
            form = ModeratorTicketForm(request.POST, instance=ticket)
        elif role == 'agent':
            form = ModeratorTicketForm(request.POST, instance=ticket)
            
            # Jeśli zgłoszenie nie jest przypisane, a agent je edytuje, przypisz do niego automatycznie
            if not ticket.assigned_to:
                old_form = form.save(commit=False)
                old_form.assigned_to = user
                form = ModeratorTicketForm(instance=old_form)
        else:
            # Klient używa ograniczonego formularza
            form = ClientTicketForm(request.POST, instance=ticket)
            
        if form.is_valid():
            old_status = ticket.status
            
            # Przypisanie zgłoszenia do agenta, jeśli nie jest przypisane
            updated_ticket = form.save(commit=False)
            if role == 'agent' and not ticket.assigned_to:
                updated_ticket.assigned_to = user
                messages.info(request, "Zgłoszenie zostało automatycznie przypisane do Ciebie.")
            
            updated_ticket.save()
            
            # Logowanie zmiany statusu
            if old_status != updated_ticket.status:
                log_activity(
                    request, 
                    'ticket_updated', 
                    ticket, 
                    f"Zmieniono status zgłoszenia '{ticket.title}' z '{old_status}' na '{updated_ticket.status}'"
                )
            else:
                log_activity(request, 'ticket_updated', ticket, f"Zaktualizowano zgłoszenie '{ticket.title}'")
            
            messages.success(request, 'Zgłoszenie zostało zaktualizowane!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        if role == 'admin' or role == 'agent':
            form = ModeratorTicketForm(instance=ticket)
        else:
            # Klient widzi ograniczony formularz
            form = ClientTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
