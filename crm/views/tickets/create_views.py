from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from ...models import Organization
from ...forms import TicketForm, ClientTicketForm
from ..helpers import log_activity

@login_required
def ticket_create(request):
    """Widok tworzenia nowego zgłoszenia"""
    user = request.user
    
    if request.method == 'POST':
        # Use different form based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm(request.POST)
        else:
            form = ClientTicketForm(request.POST)
            
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = user
            
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
            messages.success(request, 'Zgłoszenie zostało utworzone!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        # Also use different form for GET requests based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm()
        else:
            form = ClientTicketForm()
    
    # Dodanie pola wyboru organizacji dla admina i agenta
    organizations = []
    if user.profile.role == 'admin':
        # Admin sees all organizations
        organizations = Organization.objects.all()
    elif user.profile.role == 'agent':
        # Agent sees only organizations they belong to
        organizations = user.profile.organizations.all()
    
    context = {
        'form': form,
        'organizations': organizations,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)
