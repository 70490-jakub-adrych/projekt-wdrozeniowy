from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Count, Q
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from ..models import UserProfile, Organization, Ticket
from ..forms import OrganizationForm
from .error_views import organization_not_found, organization_access_forbidden, forbidden_access


@login_required
def organization_list(request):
    """Widok listy organizacji"""
    # Use effective user for impersonation support
    from .impersonation_views import get_effective_user, get_effective_organizations
    
    effective_user = get_effective_user(request)
    if not effective_user:
        effective_user = request.user
    
    effective_organizations = get_effective_organizations(request)
    
    # Clients should not access the organizations list page at all
    if effective_user.profile.role == 'client':
        return forbidden_access(request, "listy organizacji")
    
    # Only admin and superagent can see all organizations
    if effective_user.profile.role in ['admin', 'superagent']:
        organizations = Organization.objects.all()
    else:
        # Agent can only see their organizations (use effective organizations)
        organizations = effective_organizations
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        organizations = organizations.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Annotate organizations with ticket counts
    organizations = organizations.annotate(ticket_count=Count('ticket'))
    
    # Sorting
    sort_by = request.GET.get('sort_by', 'name')
    if sort_by not in ['name', '-name', 'created_at', '-created_at', 'ticket_count', '-ticket_count']:
        sort_by = 'name'
    organizations = organizations.order_by(sort_by)
    
    # Pagination
    per_page = request.GET.get('per_page', '20')
    
    # Detect mobile devices and limit to 10 per page
    user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
    is_mobile = any(mobile in user_agent for mobile in ['mobile', 'android', 'iphone', 'ipad', 'tablet'])
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 30, 50, 100]:
            per_page = 20
        # Force mobile to max 10 entries per page
        if is_mobile and per_page > 10:
            per_page = 10
    except (ValueError, TypeError):
        per_page = 10 if is_mobile else 20
    
    paginator = Paginator(organizations, per_page)
    page = request.GET.get('page', 1)
    
    try:
        organizations_page = paginator.page(page)
    except PageNotAnInteger:
        organizations_page = paginator.page(1)
    except EmptyPage:
        organizations_page = paginator.page(paginator.num_pages)
    
    # Prepare URL parameters for pagination
    url_params = {}
    if search_query:
        url_params['search'] = search_query
    if sort_by != 'name':
        url_params['sort_by'] = sort_by
    if per_page != 20:
        url_params['per_page'] = per_page
    
    # Sort options for dropdown
    sort_options = [
        ('name', 'Nazwa (A-Z)'),
        ('-name', 'Nazwa (Z-A)'),
        ('created_at', 'Data utworzenia (najstarsze)'),
        ('-created_at', 'Data utworzenia (najnowsze)'),
        ('ticket_count', 'Liczba zgłoszeń (rosnąco)'),
        ('-ticket_count', 'Liczba zgłoszeń (malejąco)'),
    ]
    
    context = {
        'organizations': organizations_page,
        'organizations_page': organizations_page,  # For pagination controls
        'search_query': search_query,
        'sort_by': sort_by,
        'sort_options': sort_options,
        'per_page': per_page,
        'url_params': url_params,
        'total_organizations': paginator.count,
    }
    
    return render(request, 'crm/organizations/organization_list.html', context)


@login_required
def organization_detail(request, pk):
    """Widok szczegółów organizacji"""
    # Use effective user for impersonation support
    from .impersonation_views import get_effective_user, get_effective_organizations
    
    effective_user = get_effective_user(request)
    if not effective_user:
        effective_user = request.user
    
    effective_organizations = get_effective_organizations(request)
    
    try:
        organization = get_object_or_404(Organization, pk=pk)
    except Http404:
        return organization_not_found(request, pk)
    
    # Sprawdzenie uprawnień (use effective user)
    if effective_user.profile.role in ['admin', 'superagent']:
        # Admin i superagent ma dostęp do wszystkich organizacji
        pass
    elif effective_user.profile.role == 'agent':
        # Agent ma dostęp tylko do swoich organizacji (use effective organizations)
        if organization not in effective_organizations:
            return organization_access_forbidden(request, pk)
    elif organization not in effective_organizations:
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
