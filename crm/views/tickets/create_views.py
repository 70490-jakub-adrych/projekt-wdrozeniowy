from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import os

from ...models import Organization, TicketAttachment
from ...forms import TicketForm, ClientTicketForm, TicketAttachmentForm
from ..helpers import log_activity
from ...utils.category_suggestion import should_suggest_category

@login_required
def ticket_create(request):
    """Widok tworzenia nowego zgłoszenia"""
    user = request.user
    
    # Initialize the attachment form
    attachment_form = TicketAttachmentForm()
    
    if request.method == 'POST':
        # Use different form based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm(request.POST)
        else:
            form = ClientTicketForm(request.POST)
        
        # Handle file upload
        attachment_form = TicketAttachmentForm(request.POST, request.FILES)
            
        # Check if this is an AJAX request asking for category suggestion
        if 'suggest_category' in request.POST and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
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
        
        # Check if a file was uploaded
        has_attachment = bool(request.FILES.get('file'))
        accepted_policy = request.POST.get('accepted_policy') == 'on'
        
        # First validate the main form
        form_valid = form.is_valid()
        
        # For attachments, only validate policy acceptance if a file exists
        attachment_valid = True
        if has_attachment and not accepted_policy:
            attachment_valid = False
            # Add error directly to the attachment form
            attachment_form.add_error('accepted_policy', 'Musisz zaakceptować regulamin, aby dodać załącznik.')
        
        if form_valid and attachment_valid:
            ticket = form.save(commit=False)
            ticket.created_by = user
            
            # Check if we should override the category based on suggestion
            if form.cleaned_data.get('suggested_category') and form.cleaned_data.get('category') != form.cleaned_data.get('suggested_category'):
                # User accepted the suggestion - override category
                ticket.category = form.cleaned_data.get('suggested_category')
            
            # Set default priority for clients
            if user.profile.role == 'client':
                ticket.priority = 'medium'  # Default priority for client tickets
            
            # Get the organization for the current user or from form
            if 'organization' in request.POST and request.POST['organization'] and user.profile.role in ['admin', 'agent']:
                # Admin/agent can select organization
                org_id = request.POST.get('organization')
                try:
                    organization = Organization.objects.get(id=org_id)
                    
                    # Check if agent is part of the selected organization
                    if user.profile.role == 'agent' and organization not in user.profile.organizations.all():
                        messages.error(request, "Nie możesz utworzyć zgłoszenia w organizacji, do której nie jesteś przypisany.")
                        return redirect('ticket_create')
                    
                    ticket.organization = organization
                except Organization.DoesNotExist:
                    messages.error(request, "Wybrana organizacja nie istnieje.")
                    return redirect('ticket_create')
            else:
                # Regular users use their first organization
                user_orgs = user.profile.organizations.all()
                if user_orgs.exists():
                    ticket.organization = user_orgs.first()
                else:
                    messages.error(request, "Nie można utworzyć zgłoszenia: Brak organizacji przypisanej do Twojego konta.")
                    return redirect('dashboard')
                
            ticket.save()
            log_activity(request, 'ticket_created', ticket, f"Utworzono zgłoszenie: '{ticket.title}'")
            
            # Handle attachment upload if provided
            if has_attachment:
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = user
                attachment.filename = os.path.basename(attachment.file.name)
                attachment.accepted_policy = True  # User agreed to terms
                attachment.save()
                log_activity(request, 'ticket_attachment_added', ticket=ticket, 
                            description=f"Added attachment: {attachment.filename}")
                messages.success(request, 'Zgłoszenie oraz załącznik zostały utworzone!')
            else:
                messages.success(request, 'Zgłoszenie zostało utworzone!')
                
            return redirect('ticket_detail', pk=ticket.pk)
        else:
            # Let the form validation errors display inline - no need for explicit messages
            pass
    else:
        # Also use different form for GET requests based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm()
        else:
            form = ClientTicketForm()
    
    # Dodanie pola wyboru organizacji dla admina, superagenta i agenta
    organizations = []
    if user.profile.role in ['admin', 'superagent']:
        # Admin i superagent widzą wszystkie organizacje
        organizations = Organization.objects.all()
    elif user.profile.role == 'agent':
        # Agent widzi tylko organizacje, do których należy
        organizations = user.profile.organizations.all()
    
    context = {
        'form': form,
        'attachment_form': attachment_form,
        'organizations': organizations,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
