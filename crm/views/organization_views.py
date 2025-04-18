from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

from ..models import UserProfile, Organization, Ticket
from ..forms import OrganizationForm


@login_required
def organization_list(request):
    """Widok listy organizacji"""
    # Tylko admin i moderator mogą widzieć wszystkie organizacje
    if request.user.profile.role in ['admin', 'moderator']:
        organizations = Organization.objects.all()
    else:
        # Klient widzi tylko swoją organizację
        if request.user.profile.organization:
            organizations = [request.user.profile.organization]
        else:
            organizations = []
    
    return render(request, 'crm/organizations/organization_list.html', {'organizations': organizations})


@login_required
def organization_detail(request, pk):
    """Widok szczegółów organizacji"""
    organization = get_object_or_404(Organization, pk=pk)
    
    # Sprawdzenie uprawnień
    if (request.user.profile.role not in ['admin', 'moderator'] and 
        request.user.profile.organization != organization):
        return HttpResponseForbidden("Brak dostępu")
    
    members = UserProfile.objects.filter(organization=organization)
    tickets = Ticket.objects.filter(organization=organization)
    
    context = {
        'organization': organization,
        'members': members,
        'tickets': tickets,
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
