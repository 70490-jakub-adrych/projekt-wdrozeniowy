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

        form_valid = form.is_valid()
        attachment_valid = attachment_form.is_valid()
        uploaded_files = attachment_form.cleaned_data.get('files', []) if attachment_valid else []

        if form_valid and attachment_valid:
                updated_ticket = form.save()
                
                # Create list of changes for activity log
                changes = []
                if original_status != updated_ticket.status:
                    changes.append(f"status: {original_status} → {updated_ticket.status}")
                if original_priority != updated_ticket.priority:
                    original_priority_display = dict(Ticket.PRIORITY_CHOICES).get(original_priority, original_priority)
                    updated_priority_display = dict(Ticket.PRIORITY_CHOICES).get(updated_ticket.priority, updated_ticket.priority)
                    changes.append(f"priorytet: {original_priority_display} → {updated_priority_display}")
                
                if original_category != updated_ticket.category:
                    original_category_display = dict(Ticket.CATEGORY_CHOICES).get(original_category, original_category)
                    updated_category_display = dict(Ticket.CATEGORY_CHOICES).get(updated_ticket.category, updated_ticket.category)
                    changes.append(f"kategoria: {original_category_display} → {updated_category_display}")
                
                if original_assigned_to != updated_ticket.assigned_to:
                    old_assignee = original_assigned_to.username if original_assigned_to else 'nieprzypisane'
                    new_assignee = updated_ticket.assigned_to.username if updated_ticket.assigned_to else 'nieprzypisane'
                    changes.append(f"przypisanie: {old_assignee} → {new_assignee}")
                
                if original_title != updated_ticket.title:
                    changes.append(f"tytuł: '{original_title}' → '{updated_ticket.title}'")
                
                if original_description != updated_ticket.description:
                    changes.append("zmieniona treść zgłoszenia")
                
                changes_text = ", ".join(changes)
                log_activity(
                    request,
                    'ticket_updated',
                    ticket=updated_ticket,
                    description=f"Zaktualizowano zgłoszenie #{updated_ticket.pk}: {changes_text}"
                )
                
                # Handle attachment upload if provided
                if uploaded_files:
                    attachment_names = []
                    for uploaded_file in uploaded_files:
                        attachment = TicketAttachment(
                            ticket=updated_ticket,
                            uploaded_by=user,
                            file=uploaded_file,
                            filename=os.path.basename(uploaded_file.name),
                            accepted_policy=True
                        )
                        attachment.save()
                        attachment_names.append(attachment.filename)
                        log_activity(
                            request,
                            'ticket_attachment_added',
                            ticket=updated_ticket,
                            description=f"Dodano załącznik: {attachment.filename}"
                        )

                    messages.success(
                        request,
                        f"Zgłoszenie oraz {len(attachment_names)} załącznik(i) zostały zaktualizowane!"
                    )
                else:
                    messages.success(request, 'Zgłoszenie zostało zaktualizowane!')
                
                # Send email notifications about the update
                if changes:
                    EmailNotificationService.notify_ticket_stakeholders('updated', updated_ticket, triggered_by=user, changes=changes_text)
                
                return redirect('ticket_detail', pk=updated_ticket.pk)
        else:
            if not form_valid:
                messages.error(request, 'Wystąpił błąd. Sprawdź formularz i spróbuj ponownie.')
            if not attachment_valid:
                messages.error(request, 'Wystąpił błąd z załącznikami. Sprawdź formularz i spróbuj ponownie.')
    else:
        form = ModeratorTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
        'attachment_form': attachment_form,
        'attachment_enabled': True,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
