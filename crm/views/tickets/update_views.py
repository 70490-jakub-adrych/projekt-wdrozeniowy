from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404, JsonResponse

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
    
    # Save original values to compare for logging changes
    original_status = ticket.status
    original_priority = ticket.priority
    original_category = ticket.category
    original_assigned_to = ticket.assigned_to
    original_title = ticket.title
    original_description = ticket.description
    
    if request.method == 'POST':
        # Handle AJAX category suggestion requests
        if 'suggest_category' in request.POST and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            from ...utils.category_suggestion import should_suggest_category
            title = request.POST.get('title', '')
            description = request.POST.get('description', '')
            selected_category = request.POST.get('category', '')
            
            should_suggest, suggested_category, confidence, match_details = \
                should_suggest_category(selected_category, title, description)
                
            return JsonResponse({
                'should_suggest': should_suggest,
                'suggested_category': suggested_category,
                'confidence': confidence,
                'selected_category': selected_category,
                'match_details': {k: [(word, score) for word, score in v] 
                                for k, v in match_details.items()}
            })
        
        # Regular form submission
        if role in ['admin', 'agent']:
            form = ModeratorTicketForm(request.POST, instance=ticket)
        else:
            # Klient używa ograniczonego formularza
            form = ClientTicketForm(request.POST, instance=ticket)
            
        if form.is_valid():
            # Przypisanie zgłoszenia do agenta, jeśli nie jest przypisane
            updated_ticket = form.save(commit=False)
            
            # Assign ticket to agent if unassigned - but don't recreate the form
            if role == 'agent' and not ticket.assigned_to:
                updated_ticket.assigned_to = user
                messages.info(request, "Zgłoszenie zostało automatycznie przypisane do Ciebie.")
            
            # Save changes
            updated_ticket.save()
            
            # Log all significant changes
            changes = []
            
            # Check for status change
            if original_status != updated_ticket.status:
                changes.append(f"zmiana statusu z '{ticket.get_status_display()}' na '{updated_ticket.get_status_display()}'")
            
            # Check for priority change
            if original_priority != updated_ticket.priority:
                changes.append(f"zmiana priorytetu z '{ticket.get_priority_display()}' na '{updated_ticket.get_priority_display()}'")
            
            # Check for category change
            if original_category != updated_ticket.category:
                changes.append(f"zmiana kategorii z '{ticket.get_category_display()}' na '{updated_ticket.get_category_display()}'")
            
            # Check for assignment change
            if original_assigned_to != updated_ticket.assigned_to:
                if updated_ticket.assigned_to:
                    changes.append(f"przypisanie do '{updated_ticket.assigned_to.username}'")
                else:
                    changes.append("usunięcie przypisania")
            
            # Check for title/description changes
            if original_title != updated_ticket.title:
                changes.append("aktualizacja tytułu")
            
            if original_description != updated_ticket.description:
                changes.append("aktualizacja opisu")
            
            # Log detailed changes
            if changes:
                change_description = ", ".join(changes)
                log_activity(
                    request, 
                    'ticket_updated', 
                    updated_ticket, 
                    f"Zaktualizowano zgłoszenie '{updated_ticket.title}': {change_description}"
                )
            else:
                log_activity(request, 'ticket_updated', updated_ticket, f"Zgłoszenie '{updated_ticket.title}' zostało otwarte do edycji, ale nie wprowadzono zmian")
            
            messages.success(request, 'Zgłoszenie zostało zaktualizowane!')
            return redirect('ticket_detail', pk=updated_ticket.pk)
        else:
            # Show validation errors
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Błąd w polu {field}: {error}")
    else:
        # GET request - initialize form
        if role in ['admin', 'agent']:
            form = ModeratorTicketForm(instance=ticket)
        else:
            # Klient widzi ograniczony formularz
            form = ClientTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
