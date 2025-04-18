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
    context = {}
    
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
    
    # Statystyki dla wszystkich użytkowników
    if user.profile.role == 'admin' or user.profile.role == 'agent':
        # Statystyki dla administratorów i agentów
        new_tickets = Ticket.objects.filter(status='new').count()
        in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
        waiting_tickets = Ticket.objects.filter(status='waiting').count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()
        closed_tickets = Ticket.objects.filter(status='closed').count()
        
        # Get pending approvals count
        if user.profile.role == 'admin':
            pending_approvals = UserProfile.objects.filter(is_approved=False).count()
        else:
            org = user.profile.organization
            if org:
                pending_approvals = UserProfile.objects.filter(
                    is_approved=False, 
                    organization=org
                ).count()
            else:
                pending_approvals = 0
        
        # Jeśli agent, pokaż tylko swoje przypisane zgłoszenia
        if user.profile.role == 'agent':
            assigned_tickets = Ticket.objects.filter(assigned_to=user)
            unassigned_tickets = Ticket.objects.filter(
                assigned_to=None,
                organization=user.profile.organization
            )
        else:
            assigned_tickets = Ticket.objects.filter(assigned_to=user)
            unassigned_tickets = Ticket.objects.filter(assigned_to=None)
        
        # Ostatnie aktualizacje zgłoszeń
        recent_activities = ActivityLog.objects.filter(
            action_type__in=['ticket_created', 'ticket_updated', 'ticket_commented', 'ticket_resolved', 'ticket_closed']
        ).select_related('user', 'ticket')[:10]
        
        context.update({
            'new_tickets': new_tickets,
            'in_progress_tickets': in_progress_tickets,
            'waiting_tickets': waiting_tickets,
            'resolved_tickets': resolved_tickets,
            'closed_tickets': closed_tickets,
            'assigned_tickets': assigned_tickets[:5],
            'unassigned_tickets': unassigned_tickets[:5],
            'recent_activities': recent_activities,
            'pending_approvals': pending_approvals,
        })
    else:
        # Statystyki dla klientów
        user_org = user.profile.organization
        if user_org:
            org_tickets = Ticket.objects.filter(organization=user_org)
            new_tickets = org_tickets.filter(status='new').count()
            in_progress_tickets = org_tickets.filter(status='in_progress').count()
            waiting_tickets = org_tickets.filter(status='waiting').count()
            resolved_tickets = org_tickets.filter(status='resolved').count()
            closed_tickets = org_tickets.filter(status='closed').count()
            
            # Ostatnie zgłoszenia użytkownika
            user_tickets = Ticket.objects.filter(created_by=user).order_by('-created_at')[:5]
            
            # Ostatnie zgłoszenia organizacji
            org_recent_tickets = org_tickets.order_by('-created_at')[:5]
            
            context.update({
                'new_tickets': new_tickets,
                'in_progress_tickets': in_progress_tickets,
                'waiting_tickets': waiting_tickets,
                'resolved_tickets': resolved_tickets,
                'closed_tickets': closed_tickets,
                'user_tickets': user_tickets,
                'org_recent_tickets': org_recent_tickets,
            })
    
    return render(request, 'crm/dashboard.html', context)
