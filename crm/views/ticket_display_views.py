from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from ..models import Ticket
from django.contrib.auth.decorators import login_required
from django.db.models import Q
import logging

logger = logging.getLogger(__name__)

@login_required
def ticket_display_view(request):
    """Widok wyświetlający listę zgłoszeń dla roli viewer"""
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'crm/ticket_display.html', {
        'tickets': tickets,
    })

@login_required
def get_tickets_update(request):
    """Endpoint do odświeżania listy zgłoszeń dla zalogowanych użytkowników"""
    logger.info("Otrzymano żądanie aktualizacji listy zgłoszeń")
    try:
        # Get filter parameters from request
        status_filter = request.GET.get('status', '')
        priority_filter = request.GET.get('priority', '')
        organization_filter = request.GET.get('organization', '')
        assigned_filter = request.GET.get('assigned', '')
        search_query = request.GET.get('search', '')
        
        # Base queryset
        tickets = Ticket.objects.all().order_by('-created_at')
        
        # Apply filters
        if status_filter:
            tickets = tickets.filter(status=status_filter)
        
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)
            
        if organization_filter:
            tickets = tickets.filter(organization_id=organization_filter)
            
        if assigned_filter == 'me':
            tickets = tickets.filter(assigned_to=request.user)
        elif assigned_filter == 'unassigned':
            tickets = tickets.filter(assigned_to__isnull=True)
            
        if search_query:
            tickets = tickets.filter(
                Q(title__icontains=search_query) | 
                Q(description__icontains=search_query) |
                Q(id__icontains=search_query)
            )
        
        # Filter based on user permissions
        user = request.user
        if user.profile.role == 'client':
            # Client can only see tickets from their organizations or created by them
            user_orgs = user.profile.organizations.all()
            tickets = tickets.filter(
                Q(organization__in=user_orgs) | Q(created_by=user)
            ).distinct()
        elif user.profile.role in ['agent', 'superagent']:
            # Agent and Superagent can see tickets from their organizations
            user_orgs = user.profile.organizations.all()
            tickets = tickets.filter(organization__in=user_orgs)
        
        logger.info(f"Znaleziono {tickets.count()} zgłoszeń spełniających kryteria")
        
        # Render the HTML partial
        html = render_to_string('crm/ticket_list_partial.html', {
            'tickets': tickets,
            'user': request.user
        })
        
        # Prepare additional data for enhanced UI feedback
        status_counts = {
            'new': tickets.filter(status='new').count(),
            'in_progress': tickets.filter(status='in_progress').count(),
            'unresolved': tickets.filter(status='unresolved').count(),
            'resolved': tickets.filter(status='resolved').count(),
            'closed': tickets.filter(status='closed').count(),
        }
        
        # Return JSON response with HTML and metadata
        response_data = {
            'html': html,
            'ticket_count': tickets.count(),
            'status_counts': status_counts,
            'filtered': bool(status_filter or priority_filter or organization_filter or assigned_filter or search_query)
        }
        
        logger.info("Wysyłanie odpowiedzi z aktualizacją")
        return JsonResponse(response_data)
    
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji listy: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)