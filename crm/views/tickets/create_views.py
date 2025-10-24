from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
import os

from ...models import Organization, TicketAttachment
from ...forms import TicketForm, ClientTicketForm, TicketAttachmentForm
from ..helpers import log_activity
from ...utils.category_suggestion import should_suggest_category
from ...services.email_service import EmailNotificationService  # Add this import

@login_required
def ticket_create(request):
    """Widok tworzenia nowego zgłoszenia"""
    user = request.user
    
    # Check if agent/superagent has organizations
    user_orgs = user.profile.organizations.all()
    if user.profile.role in ['agent', 'superagent'] and not user_orgs.exists():
        messages.error(request, 'Nie możesz tworzyć zgłoszeń, ponieważ Twoje konto nie jest przypisane do żadnej organizacji. Skontaktuj się z administratorem.')
        return redirect('dashboard')
    
    # Initialize the attachment form
    attachment_form = TicketAttachmentForm()
    
    if request.method == 'POST':
        # Use different form based on user role
        if user.profile.role in ['admin', 'superagent', 'agent']:
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
        
        # Check if files were uploaded
        uploaded_files = request.FILES.getlist('file')
        has_attachments = bool(uploaded_files)
        accepted_policy = request.POST.get('accepted_policy') == 'on'
        
        # First validate the main form
        form_valid = form.is_valid()
        
        # For attachments, only validate policy acceptance if files exist
        attachment_valid = True
        if has_attachments and not accepted_policy:
            attachment_valid = False
            # Add error directly to the attachment form
            attachment_form.add_error('accepted_policy', 'Musisz zaakceptować regulamin, aby dodać załączniki.')
        
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
            if 'organization' in request.POST and request.POST['organization'] and user.profile.role in ['admin', 'superagent', 'agent']:
                # Admin/superagent/agent can select organization
                org_id = request.POST.get('organization')
                try:
                    organization = Organization.objects.get(id=org_id)
                    
                    # Check if agent is part of the selected organization (superagent can access all)
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
            
            # Send email notifications to relevant stakeholders
            EmailNotificationService.notify_ticket_stakeholders('created', ticket, triggered_by=user)
            
            # Handle multiple attachment uploads if provided
            attachments_count = 0
            if has_attachments:
                for uploaded_file in uploaded_files:
                    attachment = TicketAttachment(
                        ticket=ticket,
                        uploaded_by=user,
                        file=uploaded_file,
                        filename=os.path.basename(uploaded_file.name),
                        accepted_policy=True  # User agreed to terms
                    )
                    attachment.save()
                    log_activity(request, 'ticket_attachment_added', ticket=ticket, 
                                description=f"Added attachment: {attachment.filename}")
                    attachments_count += 1
                
                messages.success(request, f'Zgłoszenie oraz {attachments_count} załącznik(ów) zostały utworzone! Odpowiednie osoby zostały powiadomione e-mailem.')
            else:
                messages.success(request, 'Zgłoszenie zostało utworzone! Odpowiednie osoby zostały powiadomione e-mailem.')
                
            return redirect('ticket_detail', pk=ticket.pk)
        else:
            if not form_valid:
                messages.error(request, 'Wystąpił błąd w formularzu zgłoszenia. Sprawdź dane i spróbuj ponownie.')
            if not attachment_valid:
                messages.error(request, 'Wystąpił błąd z załącznikiem. Sprawdź dane i spróbuj ponownie.')
    else:
        # Also use different form for GET requests based on user role
        if user.profile.role in ['admin', 'superagent', 'agent']:
            form = TicketForm()
        else:
            form = ClientTicketForm()
        
        # Check for organization parameter in URL
        org_id = request.GET.get('organization')
        if org_id and user.profile.role in ['admin', 'superagent', 'agent']:
            try:
                # Verify the organization exists and user has access
                organization = Organization.objects.get(id=org_id)
                if user.profile.role in ['admin', 'superagent'] or organization in user.profile.organizations.all():
                    # Pre-select the organization in the form's initial data
                    form.initial['organization'] = org_id
            except (Organization.DoesNotExist, ValueError):
                # Invalid organization ID, ignore
                pass
    
    # Dodanie pola wyboru organizacji dla admina, superagenta i agenta
    organizations = []
    selected_organization = None
    
    if user.profile.role in ['admin', 'superagent']:
        organizations = Organization.objects.all()
    elif user.profile.role == 'agent':
        organizations = user.profile.organizations.all()
    
    # Get pre-selected organization info for context
    org_id = request.GET.get('organization')
    if org_id:
        try:
            selected_organization = Organization.objects.get(id=org_id)
        except (Organization.DoesNotExist, ValueError):
            pass

    context = {
        'form': form,
        'attachment_form': attachment_form,
        'organizations': organizations,
        'selected_organization': selected_organization,
        'attachment_enabled': True,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
