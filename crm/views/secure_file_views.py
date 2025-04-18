from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from django.contrib import messages
import os
import mimetypes
from ..models import TicketAttachment
import logging
from .error_views import attachment_not_found, forbidden_access

# Configure logger
logger = logging.getLogger(__name__)

@login_required
@require_GET
def serve_attachment(request, attachment_id):
    """Serve an encrypted attachment securely"""
    try:
        attachment = get_object_or_404(TicketAttachment, id=attachment_id)
    except Http404:
        return attachment_not_found(request, attachment_id)
        
    # Check if user has permission to view this attachment
    user = request.user
    ticket = attachment.ticket
    user_orgs = user.profile.organizations.all()
    
    # Log access attempt for security auditing
    logger.info(f"User {user.username} ({user.profile.role}) attempting to access attachment {attachment_id} from ticket {ticket.id}")
    
    # Determine if user has appropriate permissions
    can_view = False
    
    # Admin can view any attachment
    if user.profile.role == 'admin':
        can_view = True
        logger.debug(f"Admin access granted for attachment {attachment_id}")
    
    # Agent can only view attachments from tickets in their organizations
    elif user.profile.role == 'agent':
        if ticket.organization in user_orgs:
            can_view = True
            logger.debug(f"Agent access granted - belongs to ticket's organization")
        else:
            logger.warning(f"Agent {user.username} attempted to access attachment {attachment_id} from organization {ticket.organization.name} they don't belong to")
    
    # Client can ONLY view attachments they uploaded OR from tickets they created
    elif user.profile.role == 'client':
        if user == attachment.uploaded_by:
            can_view = True
            logger.debug(f"Client access granted - uploaded the attachment")
        elif user == ticket.created_by:
            can_view = True
            logger.debug(f"Client access granted - created the ticket")
        else:
            logger.warning(f"Client {user.username} attempted unauthorized access to attachment {attachment_id} from ticket {ticket.id} created by {ticket.created_by.username}")
    
    if not can_view:
        logger.warning(f"Access denied: User {user.username} ({user.profile.role}) tried to access unauthorized attachment {attachment_id}")
        return forbidden_access(request, "załącznika", attachment_id)
    
    # Get decrypted file content
    file_content = attachment.get_decrypted_content()
    
    # Try to guess content type
    content_type, _ = mimetypes.guess_type(attachment.filename)
    if not content_type:
        content_type = 'application/octet-stream'
    
    # Prepare response
    response = HttpResponse(file_content, content_type=content_type)
    
    # Extract original filename parts
    original_filename = attachment.filename
    
    # Set proper filename for download
    response['Content-Disposition'] = f'attachment; filename="{original_filename}"'
    return response
