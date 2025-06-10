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
    
    # Get attachment access level from group settings
    access_level = 'own'  # Default to most restrictive
    
    # Check if the user belongs to a group with settings
    user_groups = user.groups.all()
    if user_groups.exists():
        group = user_groups.first()
        try:
            group_settings = group.settings
            access_level = group_settings.attachments_access_level
            logger.debug(f"User {user.username} has attachment access level: {access_level} from group {group.name}")
        except Exception as e:
            logger.warning(f"Error getting group settings for user {user.username}: {str(e)}")
    
    # Determine if user has appropriate permissions based on access level
    can_view = False
    
    if access_level == 'all':
        # Admin/Superagent can view any attachment
        can_view = True
        logger.debug(f"User {user.username} granted 'all' access to attachment {attachment_id}")
    
    elif access_level == 'organization':
        # Can view attachments from tickets in their organizations
        if ticket.organization in user_orgs:
            can_view = True
            logger.debug(f"User {user.username} granted 'organization' access to attachment {attachment_id}")
        else:
            logger.warning(f"User {user.username} attempted to access attachment {attachment_id} from organization {ticket.organization.name} they don't belong to")
    
    else:  # access_level == 'own'
        # Can ONLY view attachments they uploaded OR from tickets they created
        if user == attachment.uploaded_by:
            can_view = True
            logger.debug(f"User {user.username} granted 'own' access as uploader of attachment {attachment_id}")
        elif user == ticket.created_by:
            can_view = True
            logger.debug(f"User {user.username} granted 'own' access as creator of ticket {ticket.id}")
        else:
            logger.warning(f"User {user.username} denied 'own' access to attachment {attachment_id} - neither uploader nor ticket creator")
    
    if not can_view:
        logger.warning(f"Access denied: User {user.username} ({user.profile.role}) tried to access unauthorized attachment {attachment_id}")
        return forbidden_access(request, "załącznika", attachment_id)
        
    # User has permission, serve the file
    try:
        # Get decrypted content
        file_content = attachment.get_decrypted_content()
        
        # Prepare response with appropriate content type
        content_type, encoding = mimetypes.guess_type(attachment.filename)
        content_type = content_type or 'application/octet-stream'
        
        response = HttpResponse(file_content, content_type=content_type)
        
        # Add content disposition header for download
        response['Content-Disposition'] = f'inline; filename="{attachment.filename}"'
        
        # Log successful access
        logger.info(f"User {user.username} ({user.profile.role}) successfully accessed attachment {attachment_id}")
        
        return response
    except Exception as e:
        logger.error(f"Error serving attachment {attachment_id}: {str(e)}")
        messages.error(request, f"Wystąpił błąd podczas pobierania załącznika: {str(e)}")
        return redirect('ticket_detail', pk=ticket.pk)
