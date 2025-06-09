from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
import os
import logging

# Configure logger
logger = logging.getLogger(__name__)

from ...models import Ticket, TicketComment, TicketAttachment, ActivityLog
from ...forms import TicketCommentForm, TicketAttachmentForm
from ..helpers import log_activity
from ..error_views import ticket_not_found, forbidden_access
from ...services.email_service import EmailNotificationService

@login_required
def ticket_detail(request, pk):
    """Widok szczegółów zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    user_orgs = user.profile.organizations.all()
    
    # Sprawdzenie uprawnień dostępu do zgłoszenia
    if role == 'client':
        # Klient może widzieć tylko zgłoszenia ze swoich organizacji lub utworzone przez siebie
        if ticket.organization not in user_orgs and user != ticket.created_by:
            logger.warning(f"Access denied: Client {user.username} tried to access ticket #{ticket.id}")
            return forbidden_access(request, 'zgłoszenia', ticket.id)
    elif role == 'agent':
        # Agent może widzieć wszystkie zgłoszenia z organizacji, do których należy
        if ticket.organization not in user_orgs:
            logger.warning(f"Access denied: Agent {user.username} tried to access ticket #{ticket.id} from outside their organizations")
            return forbidden_access(request, 'zgłoszenia', ticket.id)
    
    comments = ticket.comments.all().order_by('created_at')
    attachments = ticket.attachments.all()
    
    # Check if the ticket is closed
    is_closed = ticket.status == 'closed'
    
    # Initialize forms
    comment_form = TicketCommentForm()
    attachment_form = TicketAttachmentForm()
    
    # Process forms if this is a POST request and ticket is not closed
    if request.method == 'POST' and not is_closed:
        # Handle comment submission
        if 'add_comment' in request.POST:
            comment_form = TicketCommentForm(request.POST)
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = user
                comment.save()
                
                # Log the comment
                log_activity(request, 'ticket_comment_added', ticket=ticket, 
                            description=f"Added comment to #{ticket.id}: {comment.content[:50]}...")
                
                # Send email notification about the comment
                EmailNotificationService.notify_ticket_stakeholders('commented', ticket, triggered_by=user, comment=comment)
                
                messages.success(request, 'Komentarz został dodany!')
                return redirect('ticket_detail', pk=ticket.pk)
        
        # Handle attachment upload
        elif 'add_attachment' in request.POST:
            attachment_form = TicketAttachmentForm(request.POST, request.FILES)
            
            # Check if a file was uploaded
            has_attachment = bool(request.FILES.get('file'))
            accepted_policy = request.POST.get('accepted_policy') == 'on'
            
            if has_attachment and attachment_form.is_valid():
                if accepted_policy:
                    attachment = attachment_form.save(commit=False)
                    attachment.ticket = ticket
                    attachment.uploaded_by = user
                    attachment.filename = os.path.basename(attachment.file.name)
                    attachment.accepted_policy = True
                    attachment.save()
                    
                    # Log the attachment
                    log_activity(request, 'ticket_attachment_added', ticket=ticket, 
                                description=f"Added attachment: {attachment.filename}")
                    
                    # Send email notification about the attachment
                    EmailNotificationService.notify_ticket_stakeholders('updated', ticket, 
                                                                     triggered_by=user, 
                                                                     update_type='attachment_added',
                                                                     attachment_name=attachment.filename)
                    
                    messages.success(request, 'Załącznik został dodany!')
                    return redirect('ticket_detail', pk=ticket.pk)
                else:
                    messages.error(request, 'Musisz zaakceptować regulamin, aby dodać załącznik.')
            else:
                if not has_attachment:
                    messages.error(request, 'Nie wybrano pliku do przesłania.')
                else:
                    messages.error(request, 'Wystąpił błąd z załącznikiem. Sprawdź formularz i spróbuj ponownie.')
    
    # Check if user can edit this ticket
    can_edit = (role == 'admin' or
                (role == 'superagent') or
                (role == 'agent' and ticket.assigned_to == user))
    
    # Check if user can close/reopen this ticket
    can_close = False
    can_reopen = False
    
    if ticket.status != 'closed':
        if role in ['admin', 'superagent']:
            can_close = ticket.assigned_to is not None
        elif role == 'agent':
            can_close = ticket.assigned_to == user
        elif role == 'client':
            can_close = ticket.created_by == user
    else:
        if role in ['admin', 'superagent']:
            can_reopen = True
        elif role == 'agent':
            can_reopen = ticket.assigned_to == user
    
    # Check if this ticket can be assigned to the current user
    can_assign = False
    if ticket.status != 'closed' and role in ['agent', 'superagent']:
        if ticket.assigned_to is None or ticket.assigned_to != user:
            if role == 'superagent':
                can_assign = True
            elif role == 'agent' and ticket.organization in user_orgs:
                can_assign = True
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'can_edit': can_edit,
        'can_close': can_close,
        'can_reopen': can_reopen,
        'can_assign': can_assign,
        'is_closed': is_closed,
    }
    
    return render(request, 'crm/tickets/ticket_detail.html', context)
