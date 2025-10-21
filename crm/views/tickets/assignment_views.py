from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, Http404
from django.contrib.auth.models import User

from ...models import Ticket
from ..helpers import log_activity
from ..error_views import ticket_not_found
from ...services.email_service import EmailNotificationService

@login_required
def ticket_assign_to_me(request, pk):
    """Widok przypisywania zgłoszenia do siebie (dla agentów i superagentów)"""
    user = request.user
    
    # Update the role check to include admin role
    if user.profile.role not in ['admin', 'agent', 'superagent']:
        return HttpResponseForbidden("Tylko administratorzy, agenci i superagenci mogą przypisywać zgłoszenia do siebie")
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Prevent assigning closed tickets
    if ticket.status == 'closed':
        messages.error(request, "Nie można przypisać zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Sprawdź czy zgłoszenie jest już przypisane do kogoś innego
    if ticket.assigned_to and ticket.assigned_to != user:
        if user.profile.role == 'admin':
            # Admin can override assignments
            pass
        else:
            return HttpResponseForbidden("To zgłoszenie jest już przypisane do innego agenta")
    
    if request.method == 'POST':
        # Get the priority from the form
        priority = request.POST.get('priority')
        if priority and priority in [p[0] for p in Ticket.PRIORITY_CHOICES]:
            old_priority = ticket.priority
            # Update priority if it has changed
            if old_priority != priority:
                ticket.priority = priority
        
        # Przypisz zgłoszenie do aktualnego użytkownika
        old_status = ticket.status
        ticket.assigned_to = user
        
        # Change status to 'in_progress' when ticket is assigned
        if ticket.status == 'new':
            ticket.status = 'in_progress'
        
        ticket.save()
        
        # Create activity log with status and priority change information
        log_description = f"Przypisano zgłoszenie '{ticket.title}' do {user.username}"
        
        if old_status != ticket.status:
            log_description += f" i zmieniono status z '{old_status}' na '{ticket.status}'"
            
        if old_priority != ticket.priority:
            log_description += f". Priorytet zmieniony z '{old_priority}' na '{ticket.priority}'"
        
        log_activity(
            request,
            'ticket_updated',
            ticket,
            log_description
        )
        
        # Send email notification about the assignment
        EmailNotificationService.notify_ticket_stakeholders('assigned', ticket, triggered_by=user)
        
        messages.success(request, 'Zgłoszenie zostało przypisane do Ciebie!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_assign.html', {'ticket': ticket})

@login_required
def ticket_assign_to_other(request, pk):
    """View for superagents to assign tickets to other agents"""
    user = request.user
    
    # Check if user has permission to assign tickets to others
    user_groups = user.groups.all()
    if user_groups.exists():
        group = user_groups.first()
        if not hasattr(group, 'settings') or not group.settings.can_assign_tickets_to_others:
            return HttpResponseForbidden("Nie masz uprawnień do przydzielania zgłoszeń innym użytkownikom.")
    else:
        return HttpResponseForbidden("Nie masz uprawnień do przydzielania zgłoszeń innym użytkownikom.")
    
    try:
        ticket = get_object_or_404(Ticket, pk=pk)
    except Http404:
        return ticket_not_found(request, pk)
    
    # Prevent assigning closed tickets
    if ticket.status == 'closed':
        messages.error(request, "Nie można przypisać zamkniętego zgłoszenia. Najpierw otwórz je ponownie.")
        return redirect('ticket_detail', pk=ticket.pk)
    
    # Get list of possible agents to assign the ticket to
    # Include admins, superagents, and agents who can handle tickets
    possible_agents = []
    
    # Get all users with agent, superagent, or admin roles
    for potential_agent in User.objects.filter(
        profile__role__in=['admin', 'superagent', 'agent']
    ).select_related('profile').distinct():
        # Admins can be assigned to any ticket
        if potential_agent.profile.role == 'admin':
            possible_agents.append(potential_agent)
        # Superagents and agents must belong to the ticket's organization
        elif ticket.organization in potential_agent.profile.organizations.all():
            possible_agents.append(potential_agent)
    
    # Sort by role (admin first, then superagent, then agent) and username
    role_priority = {'admin': 0, 'superagent': 1, 'agent': 2}
    possible_agents.sort(key=lambda u: (role_priority.get(u.profile.role, 3), u.username))
    
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        
        # Get the priority from the form
        priority = request.POST.get('priority')
        
        if agent_id:
            try:
                agent = User.objects.get(id=agent_id)
                
                # Check if agent is eligible to handle this ticket
                # Admins can be assigned to any ticket
                if agent.profile.role != 'admin':
                    # Superagents and agents must belong to the ticket's organization
                    if ticket.organization not in agent.profile.organizations.all():
                        messages.error(request, "Wybrany użytkownik nie należy do organizacji tego zgłoszenia.")
                        return redirect('ticket_detail', pk=ticket.pk)
                
                # Update ticket assignment
                old_status = ticket.status
                old_assigned = ticket.assigned_to
                old_priority = ticket.priority
                
                # Update priority if provided and valid
                if priority and priority in [p[0] for p in Ticket.PRIORITY_CHOICES]:
                    ticket.priority = priority
                
                ticket.assigned_to = agent
                
                # Change status to 'in_progress' when ticket is assigned
                if ticket.status == 'new':
                    ticket.status = 'in_progress'
                
                ticket.save()
                
                # Log the assignment
                if old_assigned:
                    action_desc = f"Zmieniono przypisanie zgłoszenia '{ticket.title}' z {old_assigned.username} na {agent.username}"
                else:
                    action_desc = f"Przypisano zgłoszenie '{ticket.title}' do {agent.username}"
                
                if old_status != ticket.status:
                    action_desc += f" i zmieniono status z '{old_status}' na '{ticket.status}'"
                
                if old_priority != ticket.priority:
                    action_desc += f". Priorytet zmieniony z '{old_priority}' na '{ticket.priority}'"
                
                log_activity(
                    request,
                    'ticket_updated',
                    ticket,
                    action_desc
                )
                
                # Send email notification
                EmailNotificationService.notify_ticket_stakeholders(
                    'assigned', 
                    ticket, 
                    triggered_by=user
                )
                
                messages.success(request, f"Zgłoszenie zostało przypisane do {agent.username}!")
                return redirect('ticket_detail', pk=ticket.pk)
                
            except User.DoesNotExist:
                messages.error(request, "Wybrany agent nie istnieje.")
        else:
            messages.error(request, "Nie wybrano agenta.")
    
    return render(request, 'crm/tickets/ticket_assign_to_other.html', {
        'ticket': ticket,
        'possible_agents': possible_agents
    })
