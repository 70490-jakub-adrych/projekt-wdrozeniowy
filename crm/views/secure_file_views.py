from django.http import HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.utils.text import slugify
from django.core.exceptions import PermissionDenied
from ..models import TicketAttachment

@login_required
@require_GET
def serve_attachment(request, attachment_id):
    """Serve an encrypted attachment securely"""
    attachment = get_object_or_404(TicketAttachment, id=attachment_id)
    
    # Check if user has permission to view this attachment
    user = request.user
    ticket = attachment.ticket
    
    # Determine if user has appropriate permissions
    can_view = False
    
    # User can view if they are admin or agent
    if user.profile.role in ['admin', 'agent']:
        can_view = True
    
    # User can view if they created the ticket or belong to the ticket's organization
    elif user == ticket.created_by:
        can_view = True
    
    # User can view if they belong to the ticket's organization
    elif ticket.organization in user.profile.organizations.all():
        can_view = True
    
    if not can_view:
        raise PermissionDenied("You don't have permission to view this file")
    
    # Get decrypted file content
    file_content = attachment.get_decrypted_content()
    
    # Prepare response
    response = HttpResponse(file_content, content_type='application/octet-stream')
    
    # Set filename
    filename = slugify(attachment.filename) if attachment.filename else f"attachment-{attachment_id}"
    if not filename.endswith(attachment.filename.split('.')[-1]):
        filename += '.' + attachment.filename.split('.')[-1]
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response
