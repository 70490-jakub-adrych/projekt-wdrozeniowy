"""
Calendar assignment views for tickets.
Handles assigning tickets to calendar dates for agent planning.
"""

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib.auth.models import User
from crm.models import Ticket, TicketCalendarAssignment
from crm.decorators import role_required
import logging

logger = logging.getLogger(__name__)


@login_required
@require_POST
@role_required(['admin', 'superagent', 'agent'])
def assign_ticket_to_calendar(request, ticket_id):
    """
    Assign a ticket to a calendar date.
    
    Agents can assign to their own calendar.
    Superagents and admins can assign to other agents' calendars.
    """
    try:
        ticket = get_object_or_404(Ticket, pk=ticket_id)
        user_role = request.user.profile.role
        
        # Get form data
        assigned_date_str = request.POST.get('assigned_date')
        notes = request.POST.get('notes', '').strip()
        assigned_to_agent_id = request.POST.get('assigned_to_agent')
        
        # Validate date is provided
        if not assigned_date_str:
            return JsonResponse({
                'success': False,
                'error': 'Data przypisania jest wymagana.'
            }, status=400)
        
        # Parse date
        try:
            assigned_date = timezone.datetime.strptime(assigned_date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format daty.'
            }, status=400)
        
        # Validate date is not in the past
        today = timezone.now().date()
        if assigned_date < today:
            return JsonResponse({
                'success': False,
                'error': 'Nie można przypisać zgłoszenia na przeszłą datę.'
            }, status=400)
        
        # Validate date is not a weekend
        if assigned_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return JsonResponse({
                'success': False,
                'error': 'Nie można przypisać zgłoszenia na weekend. Wybierz dzień roboczy.'
            }, status=400)
        
        # Determine who to assign to
        if assigned_to_agent_id and user_role in ['superagent', 'admin']:
            # Superagent/admin assigning to another agent
            try:
                assigned_to = User.objects.get(
                    pk=assigned_to_agent_id,
                    profile__role__in=['agent', 'superagent', 'admin'],
                    is_active=True
                )
            except User.DoesNotExist:
                return JsonResponse({
                    'success': False,
                    'error': 'Wybrany agent nie istnieje lub nie ma odpowiednich uprawnień.'
                }, status=400)
        else:
            # Regular agent or no agent specified - assign to self
            assigned_to = request.user
        
        # Check if this ticket already has an assignment for this user
        existing = TicketCalendarAssignment.objects.filter(
            ticket=ticket,
            assigned_to=assigned_to
        ).first()
        
        # If exists, update it (move to new date)
        if existing:
            old_date = existing.assigned_date
            existing.assigned_date = assigned_date
            existing.assigned_by = request.user
            existing.notes = notes
            existing.save()
            
            logger.info(
                f"Calendar assignment updated: Ticket #{ticket.id} moved from {old_date} to {assigned_date} "
                f"for {assigned_to.username} by {request.user.username}"
            )
            
            return JsonResponse({
                'success': True,
                'message': f'Zgłoszenie zostało przeniesione z {old_date.strftime("%d.%m.%Y")} na {assigned_date.strftime("%d.%m.%Y")}.',
                'assignment_id': existing.id,
                'assigned_date': assigned_date.strftime('%Y-%m-%d'),
                'assigned_to': assigned_to.get_full_name() or assigned_to.username,
                'was_updated': True
            })
        
        # Create new assignment
        assignment = TicketCalendarAssignment.objects.create(
            ticket=ticket,
            assigned_to=assigned_to,
            assigned_date=assigned_date,
            assigned_by=request.user,
            notes=notes
        )
        
        logger.info(
            f"Calendar assignment created: Ticket #{ticket.id} assigned to {assigned_to.username} "
            f"for {assigned_date} by {request.user.username}"
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Zgłoszenie zostało pomyślnie przypisane do kalendarza.',
            'assignment_id': assignment.id,
            'assigned_date': assigned_date.strftime('%Y-%m-%d'),
            'assigned_to': assigned_to.get_full_name() or assigned_to.username
        })
        
    except Exception as e:
        logger.error(f"Error creating calendar assignment: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Wystąpił błąd podczas przypisywania zgłoszenia do kalendarza.'
        }, status=500)


@login_required
@role_required(['admin', 'superagent', 'agent'])
def get_calendar_assignments(request):
    """
    Get calendar assignments for the current user and month.
    Used by the dashboard calendar widget.
    """
    try:
        # Get year and month from query params (default to current month)
        year = request.GET.get('year')
        month = request.GET.get('month')
        
        if year and month:
            try:
                year = int(year)
                month = int(month)
            except ValueError:
                return JsonResponse({
                    'success': False,
                    'error': 'Nieprawidłowy rok lub miesiąc.'
                }, status=400)
        else:
            now = timezone.now()
            year = now.year
            month = now.month
        
        # Everyone sees only their own assignments
        # If admin wants to check someone else's calendar, they can use admin panel
        assignments = TicketCalendarAssignment.objects.filter(
            assigned_to=request.user,
            assigned_date__year=year,
            assigned_date__month=month
        ).select_related('ticket', 'assigned_by')
        
        # Group by date
        assignments_by_date = {}
        for assignment in assignments:
            date_str = assignment.assigned_date.strftime('%Y-%m-%d')
            if date_str not in assignments_by_date:
                assignments_by_date[date_str] = []
            
            assignments_by_date[date_str].append({
                'id': assignment.id,
                'ticket_id': assignment.ticket.id,
                'ticket_title': assignment.ticket.title,
                'ticket_priority': assignment.ticket.priority,
                'assigned_to': assignment.assigned_to.get_full_name() or assignment.assigned_to.username,
                'assigned_by': assignment.assigned_by.get_full_name() if assignment.assigned_by else None,
                'notes': assignment.notes,
                'created_at': assignment.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'year': year,
            'month': month,
            'assignments': assignments_by_date
        })
        
    except Exception as e:
        logger.error(f"Error fetching calendar assignments: {str(e)}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': 'Wystąpił błąd podczas pobierania przypisań z kalendarza.'
        }, status=500)
