from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404

from ..models import UserProfile, Organization, Ticket
from ..forms import OrganizationForm
from .error_views import organization_not_found, organization_access_forbidden, forbidden_access


@login_required
def organization_list(request):
    """Widok listy organizacji"""
    # Clients should not access the organizations list page at all
    if request.user.profile.role == 'client':
        return forbidden_access(request, "listy organizacji")
    
    # Only admin and superagent can see all organizations
    if request.user.profile.role in ['admin', 'superagent']:
        organizations = Organization.objects.all()
    else:
        # Agent can only see their organizations
        organizations = request.user.profile.organizations.all()
    
    return render(request, 'crm/organizations/organization_list.html', {'organizations': organizations})


@login_required
def organization_detail(request, pk):
    """Widok szczegółów organizacji"""
    try:
        organization = get_object_or_404(Organization, pk=pk)
    except Http404:
        return organization_not_found(request, pk)
    
    # Sprawdzenie uprawnień
    if request.user.profile.role in ['admin', 'superagent']:
        # Admin i superagent ma dostęp do wszystkich organizacji
        pass
    elif request.user.profile.role == 'agent':
        # Agent ma dostęp tylko do swoich organizacji
        if organization not in request.user.profile.organizations.all():
            return organization_access_forbidden(request, pk)
    elif organization not in request.user.profile.organizations.all():
        # Klient ma dostęp tylko do swoich organizacji
        return organization_access_forbidden(request, pk)
    
    members = UserProfile.objects.filter(organizations=organization)
    tickets = Ticket.objects.filter(organization=organization)
    
    # Liczenie biletów według statusu
    new_tickets_count = tickets.filter(status='new').count()
    in_progress_tickets_count = tickets.filter(status='in_progress').count()
    resolved_tickets_count = tickets.filter(status='resolved').count()
    
    context = {
        'organization': organization,
        'members': members,
        'tickets': tickets,
        'new_tickets_count': new_tickets_count,
        'in_progress_tickets_count': in_progress_tickets_count,
        'resolved_tickets_count': resolved_tickets_count,
    }
    
    return render(request, 'crm/organizations/organization_detail.html', context)


@login_required
def organization_create(request):
    """Widok tworzenia organizacji"""
    # Admin i superagent mogą tworzyć organizacje
    if request.user.profile.role not in ['admin', 'superagent']:
        return forbidden_access(request, "funkcji tworzenia organizacji")
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            messages.success(request, 'Organizacja została utworzona!')
            return redirect('organization_detail', pk=organization.pk)
    else:
        form = OrganizationForm()
    
    return render(request, 'crm/organizations/organization_form.html', {'form': form})


@login_required
def organization_update(request, pk):
    """Widok aktualizacji organizacji"""
    # Admin i superagent mogą aktualizować organizacje
    if request.user.profile.role not in ['admin', 'superagent']:
        return forbidden_access(request, "funkcji edycji organizacji")
    
    try:
        organization = get_object_or_404(Organization, pk=pk)
    except Http404:
        return organization_not_found(request, pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organizacja została zaktualizowana!')
            return redirect('organization_detail', pk=organization.pk)
        
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'crm/organizations/organization_form.html', {'form': form, 'organization': organization})
