from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from ..models import UserProfile, Organization, Ticket
from ..forms import OrganizationForm


@login_required
def organization_list(request):
    """Widok listy organizacji"""
    # Tylko admin może widzieć wszystkie organizacje
    if request.user.profile.role == 'admin':
        organizations = Organization.objects.all()
    else:
        # Agent i klient widzą tylko swoje organizacje
        organizations = request.user.profile.organizations.all()
    
    return render(request, 'crm/organizations/organization_list.html', {'organizations': organizations})


@login_required
def organization_detail(request, pk):
    """Widok szczegółów organizacji"""
    organization = get_object_or_404(Organization, pk=pk)
    
    # Sprawdzenie uprawnień
    if (request.user.profile.role not in ['admin', 'agent'] and 
        organization not in request.user.profile.organizations.all()):
        return HttpResponseForbidden("Brak dostępu")
    
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
    # Tylko admin może tworzyć organizacje
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("Brak uprawnień")
    
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
    # Tylko admin może aktualizować organizacje
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("Brak uprawnień")
    
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organizacja została zaktualizowana!')
            return redirect('organization_detail', pk=organization.pk)
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'crm/organizations/organization_form.html', {'form': form, 'organization': organization})
