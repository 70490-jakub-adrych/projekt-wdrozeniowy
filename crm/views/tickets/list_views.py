from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import HttpResponse, HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime, timedelta
import logging
import json

# Configure logger
logger = logging.getLogger(__name__)

from ...models import Organization, Ticket

@login_required
def ticket_list(request):
    """Widok listy zgłoszeń"""
    user = request.user
    role = user.profile.role
    
    # Filtrowanie i sortowanie
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    assigned_filter = request.GET.get('assigned', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    ticket_id = request.GET.get('ticket_id', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    # Check for explicit 'false' value, default to excluding closed tickets
    exclude_closed = request.GET.get('exclude_closed', 'true').lower() != 'false'
    
    # New filters for client view
    created_by_filter = request.GET.get('created_by', '')
    exclude_created_by = request.GET.get('exclude_created_by', '')
    
    # Add organization filter
    organization_filter = request.GET.get('organization', '')
    
    # Get user organizations and log their IDs for debugging
    user_orgs = user.profile.organizations.all()
    org_ids = list(user_orgs.values_list('id', flat=True))
    logger.debug(f"User {user.username} belongs to organizations: {org_ids}")
    
    # For admin users, get all organizations for the filter dropdown
    # For agent users, get only organizations they belong to
    all_organizations = None
    if role == 'admin':
        all_organizations = Organization.objects.all().order_by('name')
    elif role in ['agent', 'superagent']:  # Include superagents here
        all_organizations = user_orgs.order_by('name')
    
    # Określenie widocznych zgłoszeń na podstawie roli
    if role == 'admin':
        # Admin widzi wszystkie zgłoszenia
        tickets = Ticket.objects.all()
        logger.debug(f"Admin user {user.username} - showing all tickets")
    elif role == 'superagent':
        # Superagent widzi wszystkie zgłoszenia z organizacji, do których należy
        if not org_ids:
            tickets = Ticket.objects.none()
            logger.warning(f"Superagent {user.username} has no organizations")
        else:
            tickets = Ticket.objects.filter(organization_id__in=org_ids)
            logger.debug(f"Superagent {user.username} - showing tickets where organization_id IN {org_ids}")
    elif role == 'agent':
        # Agent widzi wszystkie zgłoszenia z organizacji, do których należy
        if not org_ids:
            tickets = Ticket.objects.none()
            logger.warning(f"Agent {user.username} has no organizations")
        else:
            tickets = Ticket.objects.filter(organization_id__in=org_ids)
            logger.debug(f"Agent {user.username} - showing tickets where organization_id IN {org_ids}")
    else:  # client
        # Klient widzi zgłoszenia ze swoich organizacji i swoje własne
        tickets = Ticket.objects.filter(Q(organization__in=user_orgs) | Q(created_by=user))
        logger.debug(f"Client {user.username} - showing tickets from orgs and created by user")
    
    # Apply exclude_closed filter by default - but only if status filter isn't explicitly set to 'closed'
    if exclude_closed and status_filter != 'closed':
        tickets = tickets.exclude(status='closed')
        logger.debug(f"Excluding closed tickets")
    
    # Debug: Count results before filtering
    initial_count = tickets.count()
    logger.debug(f"Initial ticket count before filters: {initial_count}")
    
    # Zastosowanie filtrów
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    # Apply organization filter if provided
    if organization_filter:
        try:
            org_id = int(organization_filter)
            tickets = tickets.filter(organization_id=org_id)
            logger.debug(f"Filtering tickets by organization ID: {org_id}")
        except ValueError:
            # Invalid organization ID format, ignore this filter
            logger.warning(f"Invalid organization ID format: {organization_filter}")
    
    # Filtrowanie po przypisaniu
    if assigned_filter == 'me':
        tickets = tickets.filter(assigned_to=user)
    elif assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    # 'all' nie wymaga filtrowania - pokazuje wszystkie zgłoszenia z organizacji agenta
    
    # New filtering options for client dashboard
    if created_by_filter == 'me':
        tickets = tickets.filter(created_by=user)
    if exclude_created_by == 'me':
        tickets = tickets.exclude(created_by=user)
    
    # Filtrowanie po ID zgłoszenia
    if ticket_id:
        try:
            ticket_id = int(ticket_id)
            tickets = tickets.filter(id=ticket_id)
        except ValueError:
            # Jeśli podano nieprawidłowy ID, nie filtruj
            pass
    
    # Filtrowanie po zakresie dat
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            tickets = tickets.filter(created_at__gte=date_from_obj)
        except ValueError:
            # Nieprawidłowy format daty, ignorujemy
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Dodajemy jeden dzień, aby uwzględnić całą datę "do"
            date_to_obj = date_to_obj + timedelta(days=1)
            tickets = tickets.filter(created_at__lt=date_to_obj)
        except ValueError:
            # Nieprawidłowy format daty, ignorujemy
            pass
    
    # Dodaj logging do diagnostyki
    logger.debug(f"User {user.username} role {role} - final query: {str(tickets.query)}")
    final_count = tickets.count()
    logger.debug(f"Final ticket count after filters: {final_count}")
    
    # Zastosowanie sortowania
    tickets = tickets.order_by(sort_by)
    
    # Paginacja
    per_page = request.GET.get('per_page', '20')
    # Handle mobile per_page parameter
    if not per_page or per_page == '':
        per_page = request.GET.get('per_page_mobile', '20')
    
    try:
        per_page = int(per_page)
        if per_page not in [10, 20, 30, 50, 100]:
            per_page = 20
    except (ValueError, TypeError):
        per_page = 20
    
    paginator = Paginator(tickets, per_page)
    page = request.GET.get('page', 1)
    
    try:
        tickets_page = paginator.page(page)
    except PageNotAnInteger:
        tickets_page = paginator.page(1)
    except EmptyPage:
        tickets_page = paginator.page(paginator.num_pages)
    
    # Przygotuj parametry URL dla zachowania filtrów w paginacji
    url_params = {}
    if status_filter:
        url_params['status'] = status_filter
    if priority_filter:
        url_params['priority'] = priority_filter
    if category_filter:
        url_params['category'] = category_filter
    if assigned_filter:
        url_params['assigned'] = assigned_filter
    if date_from:
        url_params['date_from'] = date_from
    if date_to:
        url_params['date_to'] = date_to
    if ticket_id:
        url_params['ticket_id'] = ticket_id
    if sort_by != '-created_at':
        url_params['sort_by'] = sort_by
    if not exclude_closed:
        url_params['exclude_closed'] = 'false'
    if created_by_filter:
        url_params['created_by'] = created_by_filter
    if exclude_created_by:
        url_params['exclude_created_by'] = exclude_created_by
    if organization_filter:
        url_params['organization'] = organization_filter
    if per_page != 20:
        url_params['per_page'] = per_page
    
    # Lista dostępnych opcji sortowania dla wyboru w interfejsie
    sort_options = [
        ('-created_at', 'Data utworzenia (najnowsze)'),
        ('created_at', 'Data utworzenia (najstarsze)'),
        ('title', 'Tytuł (A-Z)'),
        ('-title', 'Tytuł (Z-A)'),
        ('priority', 'Priorytet (rosnąco)'),
        ('-priority', 'Priorytet (malejąco)'),
        ('status', 'Status (rosnąco)'),
        ('-status', 'Status (malejąco)'),
        ('category', 'Kategoria (A-Z)'),
        ('-category', 'Kategoria (Z-A)'),
        ('organization__name', 'Organizacja (A-Z)'),
        ('-organization__name', 'Organizacja (Z-A)'),
    ]
    
    context = {
        'tickets': tickets_page,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'date_from': date_from,
        'date_to': date_to,
        'ticket_id': ticket_id,
        'sort_by': sort_by,
        'sort_options': sort_options,
        'user_organizations': user_orgs,  # Add user's organizations for debugging in template
        'exclude_closed': exclude_closed,  # Add the exclude_closed filter to context
        'created_by_filter': created_by_filter,  # Add new filters to context
        'exclude_created_by': exclude_created_by,
        'organization_filter': organization_filter,  # Add to context
        'all_organizations': all_organizations,  # Add all organizations for admin filter
        'per_page': per_page,
        'url_params': url_params,
        'total_tickets': paginator.count,
    }
    
    return render(request, 'crm/tickets/ticket_list.html', context)


@login_required
def debug_tickets(request):
    """Debug view to check access permissions"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can access this debugging view")
    
    user = request.user
    result = {
        "username": user.username,
        "role": user.profile.role,
        "organizations": [],
        "tickets_visible": [],
    }
    
    # Get user's organizations
    user_orgs = user.profile.organizations.all()
    for org in user_orgs:
        org_data = {
            "id": org.id,
            "name": org.name,
            "tickets": []
        }
        
        # Get all tickets from this organization
        org_tickets = Ticket.objects.filter(organization=org)
        for ticket in org_tickets:
            org_data["tickets"].append({
                "id": ticket.id,
                "title": ticket.title,
                "assigned_to": ticket.assigned_to.username if ticket.assigned_to else "Unassigned",
                "status": ticket.status
            })
        
        result["organizations"].append(org_data)
    
    # Test the query that should show tickets
    if user.profile.role == 'agent':
        visible_tickets = Ticket.objects.filter(organization__in=user_orgs)
        for ticket in visible_tickets:
            result["tickets_visible"].append({
                "id": ticket.id,
                "title": ticket.title,
                "organization": ticket.organization.name,
                "assigned_to": ticket.assigned_to.username if ticket.assigned_to else "Unassigned"
            })
    
    return HttpResponse(
        json.dumps(result, indent=2), 
        content_type="application/json"
    )
