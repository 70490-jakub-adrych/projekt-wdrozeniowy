from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count

from ..models import UserProfile, Organization, Ticket, ActivityLog
from django.contrib.auth.models import Group


@login_required
def dashboard(request):
    """Widok panelu głównego"""
    user = request.user
    role = user.profile.role
    
    # Check if user has a profile, create one if not
    try:
        user_profile = user.profile
    except:
        # Create a profile if missing
        # Note: UserProfile is already imported at the top
        
        # Determine appropriate role based on superuser status
        if user.is_superuser:
            role = 'admin'
            group_name = 'Admin'
            message = 'Twój profil administratora został utworzony.'
            is_approved = True
        else:
            role = 'client'
            group_name = 'Klient'
            message = 'Twój profil został utworzony. Skontaktuj się z administratorem, aby uzyskać odpowiednie uprawnienia.'
            is_approved = False
        
        # Create profile with appropriate role
        user_profile = UserProfile.objects.create(
            user=user,
            role=role,
            is_approved=is_approved
        )
        
        # Add user to appropriate group
        user_group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(user_group)
        
        messages.info(request, message)
    
    # Tickets by status count
    if role == 'admin':
        # Admin sees all tickets for statistics
        new_tickets = Ticket.objects.filter(status='new').count()
        in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()
        closed_tickets = Ticket.objects.filter(status='closed').count()
        
        # Show only tickets assigned to current admin user
        assigned_tickets = Ticket.objects.filter(assigned_to=user).exclude(status='closed').order_by('-updated_at')[:5]
        # All tickets with no assigned user
        unassigned_tickets = Ticket.objects.filter(assigned_to__isnull=True).exclude(status='closed').order_by('-created_at')[:5]
        # In-progress tickets list for the admin panel
        in_progress_tickets_list = Ticket.objects.filter(status='in_progress').order_by('-updated_at')[:5]
        
        # Add recently closed tickets section
        recently_closed_tickets = Ticket.objects.filter(status='closed').order_by('-closed_at')[:5]
        
        # Get recent activities
        recent_activities = ActivityLog.objects.all().order_by('-created_at')[:10]
        
        # Check for pending approvals
        pending_approvals = UserProfile.objects.filter(is_approved=False).count()
        
    elif role in ['superagent', 'agent']:  # Handle both superagent and agent in similar way
        # Get user organizations
        user_orgs = user.profile.organizations.all()
        org_tickets = Ticket.objects.filter(organization__in=user_orgs)
        
        new_tickets = org_tickets.filter(status='new').count()
        in_progress_tickets = org_tickets.filter(status='in_progress').count()
        resolved_tickets = org_tickets.filter(status='resolved').count()
        closed_tickets = org_tickets.filter(status='closed').count()
        
        # For both agent and superagent - show tickets assigned to them
        assigned_tickets = org_tickets.filter(assigned_to=user).exclude(status='closed').order_by('-updated_at')[:5]
        # Show unassigned tickets from their organizations
        unassigned_tickets = org_tickets.filter(assigned_to__isnull=True).exclude(status='closed').order_by('-created_at')[:5]
        
        # For superagent, add in-progress tickets list
        if role == 'superagent':
            in_progress_tickets_list = org_tickets.filter(status='in_progress').order_by('-updated_at')[:5]
        else:
            in_progress_tickets_list = None
        
        # Add recently closed tickets section
        recently_closed_tickets = org_tickets.filter(status='closed').order_by('-closed_at')[:5]
        
        # Get recent activities
        recent_activities = ActivityLog.objects.filter(
            Q(user=user) | Q(ticket__organization__in=user_orgs)
        ).distinct().order_by('-created_at')[:10]
        
        # Check for pending approvals in user's organizations
        pending_approvals = UserProfile.objects.filter(
            is_approved=False,
            organizations__in=user_orgs
        ).distinct().count()
    else:  # client
        # Client sees tickets from their organizations or created by them
        user_orgs = user.profile.organizations.all()
        if user_orgs.exists():
            org_tickets = Ticket.objects.filter(
                Q(organization__in=user_orgs) | Q(created_by=user)
            ).distinct()
        else:
            org_tickets = Ticket.objects.filter(created_by=user)
        
        new_tickets = org_tickets.filter(status='new').count()
        in_progress_tickets = org_tickets.filter(status='in_progress').count()
        resolved_tickets = org_tickets.filter(status='resolved').count()
        closed_tickets = org_tickets.filter(status='closed').count()
        
        # Client's own tickets - exclude closed
        user_tickets = Ticket.objects.filter(created_by=user).exclude(status='closed').order_by('-created_at')[:5]
        
        # Client sees other tickets from their organization - exclude closed and exclude own tickets
        if user_orgs.exists():
            org_recent_tickets = org_tickets.exclude(created_by=user).exclude(status='closed').order_by('-created_at')[:5]
        else:
            org_recent_tickets = []
        
        # Add recently closed tickets for client
        recently_closed_tickets = org_tickets.filter(status='closed').order_by('-closed_at')[:5]
            
        # Variables not needed for client view
        assigned_tickets = None
        unassigned_tickets = None
        recent_activities = None
        pending_approvals = None
        in_progress_tickets_list = None
    
    # Common context
    context = {
        'new_tickets': new_tickets,
        'in_progress_tickets': in_progress_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
    }
    
    # Add role specific context
    if role == 'client':
        context.update({
            'user_tickets': user_tickets,
            'org_recent_tickets': org_recent_tickets,
            'recently_closed_tickets': recently_closed_tickets,
        })
    else:
        # For all staff roles
        context.update({
            'assigned_tickets': assigned_tickets,
            'unassigned_tickets': unassigned_tickets,
            'recent_activities': recent_activities,
            'pending_approvals': pending_approvals,
            'recently_closed_tickets': recently_closed_tickets,
        })
        
        # Add in-progress tickets list for admins and superagents
        if role in ['admin', 'superagent']:
            context.update({
                'in_progress_tickets_list': in_progress_tickets_list,
            })
    
    return render(request, 'crm/dashboard.html', context)
