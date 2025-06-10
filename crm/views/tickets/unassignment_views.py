from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404

from ...models import Ticket
from ..helpers import log_activity
from ..error_views import ticket_not_found
from ...services.email_service import EmailNotificationService

@login_required
def ticket_unassign(request, pk):
    """View for unassigning a ticket from the current user"""
    user = request.user
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Check permissions - only the assigned user can unassign (with proper permissions)
    # or admin/superagent can unassign anyone's ticket
    if ticket.assigned_to != user and user.profile.role not in ['admin', 'superagent']:
        messages.error(request, "Nie możesz cofnąć przypisania tego zgłoszenia, ponieważ nie jest ono do Ciebie przypisane.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Check if the user has permission to unassign tickets
    if user.profile.role not in ['admin', 'superagent']:
        # For regular agents, check their group settings
        user_groups = user.groups.all()
        if user_groups.exists():
            group = user_groups.first()
            if hasattr(group, 'settings'):
                if not group.settings.can_unassign_own_tickets:
                    messages.error(request, "Nie masz uprawnień do cofania przypisania zgłoszeń.")
                    return redirect('ticket_detail', pk=ticket.pk)
            else:
                messages.error(request, "Nie masz uprawnień do cofania przypisania zgłoszeń.")
                return redirect('ticket_detail', pk=ticket.pk)
    
    # Prevent unassigning closed tickets
    if ticket.status == 'closed':
        messages.error(request, "Nie można cofnąć przypisania zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
        return redirect('ticket_detail', pk=ticket.pk)
        
    if request.method == 'POST':
        # Store the old information for logging
        old_assigned_to = ticket.assigned_to
        old_status = ticket.status
        
        # Update ticket - remove assignment
        ticket.assigned_to = None
        
        # If in progress, change back to new
        if ticket.status == 'in_progress':
            ticket.status = 'new'
        
        ticket.save()
        
        # Create activity log
        log_text = f"Cofnięto przypisanie zgłoszenia '{ticket.title}' od użytkownika {old_assigned_to.username}"
        if old_status != ticket.status:
            log_text += f" i zmieniono status z '{old_status}' na '{ticket.status}'"
            
        log_activity(
            request,
            'ticket_updated',
            ticket,
            log_text
        )
        
        # Send email notification about the unassignment
        EmailNotificationService.notify_ticket_stakeholders(
            'updated', 
            ticket, 
            triggered_by=user,
            update_type='unassigned',
            previous_owner=old_assigned_to.username
        )
        
        messages.success(request, 'Cofnięto przypisanie zgłoszenia!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_unassign.html', {'ticket': ticket})
