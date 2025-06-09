from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404, JsonResponse
import os

from ...models import Ticket, TicketAttachment
from ...forms import ModeratorTicketForm, ClientTicketForm, TicketAttachmentForm
from ..helpers import log_activity
from ..error_views import ticket_not_found, ticket_edit_forbidden
from ...services.email_service import EmailNotificationService
from ...decorators import admin_required

@login_required
@admin_required  # Add this decorator to ensure only admins can access
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
    
    # Save original values to compare for logging changes
    original_status = ticket.status
    original_priority = ticket.priority
    original_category = ticket.category
    original_assigned_to = ticket.assigned_to
    original_title = ticket.title
    original_description = ticket.description
    
    # Initialize the attachment form
    attachment_form = TicketAttachmentForm()
    
    # If this is a POST request, process the form data
    if request.method == 'POST':
        form = ModeratorTicketForm(request.POST, instance=ticket)
        
        # Handle file upload as well
        attachment_form = TicketAttachmentForm(request.POST, request.FILES)
        
        # Check if a file was uploaded
        has_attachment = bool(request.FILES.get('file'))
        policy_accepted = request.POST.get('accepted_policy') == 'on'
        
        # First validate the ticket form
        if form.is_valid():
            # Check if attachment form is valid if a file was uploaded
            attachment_valid = True
            if has_attachment:
                attachment_valid = attachment_form.is_valid() and policy_accepted
            
            if attachment_valid:
                updated_ticket = form.save()
                
                # Create list of changes for activity log
                changes = []
                if original_status != updated_ticket.status:
                    changes.append(f"status: {original_status} → {updated_ticket.status}")
                if original_priority != updated_ticket.priority:
                    changes.append(f"priorytet: {original_priority} → {updated_ticket.priority}")
                if original_category != updated_ticket.category:
                    changes.append(f"kategoria: {original_category} → {updated_ticket.category}")
                if original_assigned_to != updated_ticket.assigned_to:
                    old_assignee = original_assigned_to.username if original_assigned_to else 'nieprzypisane'
                    new_assignee = updated_ticket.assigned_to.username if updated_ticket.assigned_to else 'nieprzypisane'
                    changes.append(f"przypisanie: {old_assignee} → {new_assignee}")
                if original_title != updated_ticket.title:
                    changes.append(f"tytuł: '{original_title}' → '{updated_ticket.title}'")
                if original_description != updated_ticket.description:
                    changes.append("zawartość zgłoszenia została zmodyfikowana")
                
                changes_text = ", ".join(changes)
                log_activity(
                    request,
                    'ticket_updated',
                    ticket=updated_ticket,
                    description=f"Zaktualizowano zgłoszenie #{updated_ticket.pk}: {changes_text}"
                )
                
                # Handle attachment upload if provided
                if has_attachment:
                    attachment = attachment_form.save(commit=False)
                    attachment.ticket = updated_ticket
                    attachment.uploaded_by = user
                    attachment.filename = os.path.basename(attachment.file.name)
                    attachment.accepted_policy = True
                    attachment.save()
                    
                    log_activity(request, 'ticket_attachment_added', ticket=updated_ticket, 
                                description=f"Added attachment: {attachment.filename}")
                    
                    messages.success(request, 'Zgłoszenie oraz załącznik zostały zaktualizowane!')
                else:
                    messages.success(request, 'Zgłoszenie zostało zaktualizowane!')
                
                # Send email notifications about the update
                if changes:
                    EmailNotificationService.notify_ticket_stakeholders('updated', updated_ticket, triggered_by=user, changes=changes_text)
                
                return redirect('ticket_detail', pk=updated_ticket.pk)
            else:
                if has_attachment and not policy_accepted:
                    messages.error(request, 'Musisz zaakceptować regulamin, aby dodać załącznik.')
                else:
                    messages.error(request, 'Wystąpił błąd z załącznikiem. Sprawdź formularz i spróbuj ponownie.')
        else:
            messages.error(request, 'Wystąpił błąd. Sprawdź formularz i spróbuj ponownie.')
    else:
        form = ModeratorTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
        'attachment_form': attachment_form,
        'attachment_enabled': True,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
