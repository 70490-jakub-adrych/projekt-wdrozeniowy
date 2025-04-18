# This file now imports all views from the 'views' package
from crm.views import *

def ticket_list(request):
    """View for listing tickets with filtering options"""
    
    # Get or create user preferences
    if request.user.is_authenticated:
        user_prefs, created = UserPreference.objects.get_or_create(user=request.user)
    else:
        user_prefs = None
    
    # Process filter form submission
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    assigned_filter = request.GET.get('assigned', '')
    ticket_id = request.GET.get('ticket_id', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    # Get exclude_closed from form submission or use user preference if not in request
    exclude_closed = request.GET.get('exclude_closed')
    
    # If form submitted, update user preference based on exclude_closed checkbox
    if 'status' in request.GET and request.user.is_authenticated:
        # Update the preference - checkbox checked means exclude closed
        show_closed = exclude_closed != 'true'
        user_prefs.show_closed_tickets = show_closed
        user_prefs.save()
        
        # Log the preference change
        ActivityLog.objects.create(
            user=request.user,
            action_type='preferences_updated',
            description=f"Updated ticket filter preferences: show_closed_tickets={show_closed}"
        )
    else:
        # Use saved preference
        exclude_closed = 'true' if user_prefs and not user_prefs.show_closed_tickets else None
    
    # Apply filters to the queryset
    tickets = Ticket.objects.all()
    
    # ...existing filter code...
    
    # Apply closed ticket filter based on user preference
    if exclude_closed:
        tickets = tickets.exclude(status='closed')
    
    # ...rest of your view code...
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'ticket_id': ticket_id,
        'date_from': date_from,
        'date_to': date_to,
        'sort_by': sort_by,
        'exclude_closed': exclude_closed,  # Make sure this is passed to the template
        'sort_options': sort_options,
        # ...other context variables...
    }
    
    return render(request, 'crm/tickets/ticket_list.html', context)
