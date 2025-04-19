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
            logger.warning(f"Access denied: Agent {user.username} tried to access ticket #{ticket.id} from org {ticket.organization.name}")
            return forbidden_access(request, 'zgłoszenia', ticket.id)
    
    comments = ticket.comments.all().order_by('created_at')
    attachments = ticket.attachments.all()
    
    # Check if the ticket is closed
    is_closed = ticket.status == 'closed'
    
    # No actions allowed on closed tickets except viewing and reopening
    # Wszyscy mogą komentować - if ticket is not closed
    can_comment = not is_closed
    
    # Sprawdzanie uprawnień do dodawania załączników - if ticket is not closed
    if is_closed:
        can_attach = False
    elif role == 'client':
        can_attach = user == ticket.created_by
    else:
        can_attach = True  # Admin i agent mogą dodawać załączniki
    
    # Sprawdzanie uprawnień do edycji - if ticket is not closed
    if is_closed:
        can_edit = False
    elif role == 'admin':
        can_edit = True
    elif role == 'agent':
        # Agent może edytować tylko nieprzypisane zgłoszenia lub przypisane do niego
        can_edit = not ticket.assigned_to or ticket.assigned_to == user
    else:  # client
        can_edit = user == ticket.created_by
    
    # Sprawdzanie uprawnień do zamykania - not applicable if already closed
    if is_closed:
        can_close = False
    elif role == 'admin':
        can_close = ticket.assigned_to is not None  # Admin can only close if ticket is assigned
    elif role == 'agent':
        # Agent can only close tickets that are assigned to them
        can_close = ticket.assigned_to == user
    else:  # client
        can_close = False  # Clients can no longer close tickets
    
    # Tylko admin i przypisany agent mogą ponownie otwierać
    can_reopen = is_closed and (role == 'admin' or (role == 'agent' and ticket.assigned_to == user))
    
    # Możliwość przypisania do siebie (tylko dla agentów, gdy zgłoszenie nieprzypisane i nie jest zamknięte)
    can_assign_to_self = not is_closed and role == 'agent' and not ticket.assigned_to
    
    # Formularz komentarza
    if request.method == 'POST':
        # Reject any POST actions if ticket is closed
        if is_closed:
            messages.error(request, "Nie można modyfikować zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
            return redirect('ticket_detail', pk=ticket.pk)
            
        if 'submit_comment' in request.POST and can_comment:
            comment_form = TicketCommentForm(request.POST)
            attachment_form = TicketAttachmentForm()
            
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                log_activity(request, 'ticket_commented', ticket, f"Dodano komentarz do zgłoszenia '{ticket.title}'")
                messages.success(request, 'Komentarz został dodany!')
                return redirect('ticket_detail', pk=ticket.pk)
        elif 'submit_attachment' in request.POST and can_attach:
            comment_form = TicketCommentForm()
            attachment_form = TicketAttachmentForm(request.POST, request.FILES)
            
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.filename = os.path.basename(attachment.file.name)
                attachment.accepted_policy = attachment_form.cleaned_data['accepted_policy']
                attachment.save()
                log_activity(request, 'ticket_attachment_added', ticket=ticket, 
                            description=f"Added attachment: {attachment.filename}")
                messages.success(request, 'Załącznik został dodany!')
                return redirect('ticket_detail', pk=ticket.pk)
        else:
            # Nieautoryzowana próba dodania komentarza lub załącznika
            return HttpResponseForbidden("Brak uprawnień do wykonania tej akcji")
    else:
        comment_form = TicketCommentForm()
        attachment_form = TicketAttachmentForm()
    
    # Get ticket activities for history
    ticket_activities = ActivityLog.objects.filter(
        ticket=ticket
    ).order_by('created_at')
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'can_comment': can_comment,
        'can_attach': can_attach,
        'can_edit': can_edit,
        'can_close': can_close,
        'can_reopen': can_reopen,
        'can_assign_to_self': can_assign_to_self,
        'is_closed': is_closed,
        'ticket_activities': ticket_activities,
    }
    
    return render(request, 'crm/tickets/ticket_detail.html', context)
