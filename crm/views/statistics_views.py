from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden, JsonResponse
from django.db.models import Count, Avg, F, ExpressionWrapper, fields, Q, Sum
from django.db.models.functions import TruncDay, TruncWeek, TruncMonth, TruncYear
from django.utils import timezone
import datetime
from datetime import timedelta
import json

from ..models import (
    Ticket, ActivityLog, UserProfile, 
    Organization, TicketStatistics, AgentWorkLog, WorkHours
)
from ..views.error_views import forbidden_access

@login_required
def statistics_dashboard(request):
    """Main statistics dashboard view"""
    user = request.user
    role = user.profile.role
    
    # Check if the user has access to statistics
    if role not in ['admin', 'superagent']:
        # Check if the user's group has explicit permission
        if not (user.groups.exists() and user.groups.first().settings.show_statistics):
            return forbidden_access(request, "statystyk")
    
    # Time period filter
    period = request.GET.get('period', 'month')  # Default to month
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Get current date for default periods
    today = timezone.now().date()
    
    # Set default date range based on period if not specified
    if not date_from or not date_to:
        if period == 'day':
            date_from = today
            date_to = today
        elif period == 'week':
            date_from = today - timedelta(days=today.weekday())
            date_to = date_from + timedelta(days=6)
        elif period == 'month':
            date_from = today.replace(day=1)
            next_month = today.month + 1 if today.month < 12 else 1
            next_month_year = today.year if today.month < 12 else today.year + 1
            date_to = datetime.date(next_month_year, next_month, 1) - timedelta(days=1)
        elif period == 'year':
            date_from = today.replace(month=1, day=1)
            date_to = today.replace(month=12, day=31)
    else:
        try:
            date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            # If date parsing fails, use default for selected period
            if period == 'day':
                date_from = today
                date_to = today
            elif period == 'week':
                date_from = today - timedelta(days=today.weekday())
                date_to = date_from + timedelta(days=6)
            elif period == 'month':
                date_from = today.replace(day=1)
                next_month = today.month + 1 if today.month < 12 else 1
                next_month_year = today.year if today.month < 12 else today.year + 1
                date_to = datetime.date(next_month_year, next_month, 1) - timedelta(days=1)
            elif period == 'year':
                date_from = today.replace(month=1, day=1)
                date_to = today.replace(month=12, day=31)
    
    # Filter tickets based on user role and date range
    if role == 'admin':
        # Admin sees all tickets
        tickets = Ticket.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to
        )
    elif role == 'superagent':
        # Filter for superagent - depends on what they have access to
        user_orgs = user.profile.organizations.all()
        tickets = Ticket.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
            organization__in=user_orgs
        )
    else:
        # Fallback for other roles with explicit permission
        user_orgs = user.profile.organizations.all()
        tickets = Ticket.objects.filter(
            created_at__date__gte=date_from,
            created_at__date__lte=date_to,
            organization__in=user_orgs
        )
    
    # Organization filter
    org_filter = request.GET.get('organization', '')
    if org_filter:
        tickets = tickets.filter(organization_id=org_filter)
    
    # Agent filter
    agent_filter = request.GET.get('agent', '')
    if agent_filter:
        tickets = tickets.filter(assigned_to_id=agent_filter)
    
    # Calculate general statistics
    total_tickets = tickets.count()
    new_tickets = tickets.filter(status='new').count()
    in_progress_tickets = tickets.filter(status='in_progress').count()
    waiting_tickets = tickets.filter(status='waiting').count()
    resolved_tickets = tickets.filter(status='resolved').count()
    closed_tickets = tickets.filter(status='closed').count()
    
    # Calculate ticket resolution metrics
    avg_resolution_time = tickets.exclude(
        resolved_at__isnull=True
    ).aggregate(
        avg_time=Avg(
            ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        )
    )['avg_time']
    
    if avg_resolution_time:
        avg_resolution_hours = avg_resolution_time.total_seconds() / 3600
    else:
        avg_resolution_hours = 0
    
    # Get priority distribution
    priority_distribution = tickets.values('priority').annotate(
        count=Count('id')
    ).order_by('priority')
    
    # Get category distribution
    category_distribution = tickets.values('category').annotate(
        count=Count('id')
    ).order_by('category')
    
    # Get tickets by creation date
    if period == 'day':
        tickets_by_date = tickets.annotate(
            date=TruncDay('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
    elif period == 'week':
        tickets_by_date = tickets.annotate(
            date=TruncWeek('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
    elif period == 'month':
        tickets_by_date = tickets.annotate(
            date=TruncMonth('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
    else:  # year
        tickets_by_date = tickets.annotate(
            date=TruncYear('created_at')
        ).values('date').annotate(
            count=Count('id')
        ).order_by('date')
    
    # Get agent performance metrics - for agents with assigned tickets
    agent_performance = []
    
    if role in ['admin', 'superagent']:
        agents_with_tickets = tickets.values(
            'assigned_to'
        ).exclude(
            assigned_to__isnull=True
        ).annotate(
            ticket_count=Count('id')
        ).order_by('-ticket_count')
        
        for agent_data in agents_with_tickets:
            agent_id = agent_data['assigned_to']
            if agent_id:
                try:
                    agent_user = UserProfile.objects.get(user_id=agent_id).user
                    agent_tickets = tickets.filter(assigned_to_id=agent_id)
                    
                    agent_resolved = agent_tickets.filter(status__in=['resolved', 'closed']).count()
                    agent_total = agent_tickets.count()
                    
                    if agent_total > 0:
                        resolution_rate = (agent_resolved / agent_total) * 100
                    else:
                        resolution_rate = 0
                    
                    # Calculate average resolution time for this agent
                    agent_avg_time = agent_tickets.exclude(
                        resolved_at__isnull=True
                    ).aggregate(
                        avg_time=Avg(
                            ExpressionWrapper(
                                F('resolved_at') - F('created_at'),
                                output_field=fields.DurationField()
                            )
                        )
                    )['avg_time']
                    
                    if agent_avg_time:
                        agent_avg_hours = agent_avg_time.total_seconds() / 3600
                    else:
                        agent_avg_hours = 0
                    
                    agent_performance.append({
                        'agent_id': agent_id,  # Add this line
                        'agent_name': f"{agent_user.first_name} {agent_user.last_name}" if agent_user.first_name else agent_user.username,
                        'ticket_count': agent_total,
                        'resolved_count': agent_resolved,
                        'resolution_rate': resolution_rate,
                        'avg_resolution_time': agent_avg_hours
                    })
                except UserProfile.DoesNotExist:
                    # Skip if agent profile doesn't exist
                    pass
    
    # Get organizations for filter dropdown
    organizations = []
    if role == 'admin':
        organizations = Organization.objects.all()
    else:
        organizations = user.profile.organizations.all()
    
    # Get agents for filter dropdown (either all agents for admin or agents in user's organizations)
    if role == 'admin':
        agents = UserProfile.objects.filter(role='agent').select_related('user')
    else:
        # For superagent, only show agents in their organizations
        user_orgs = user.profile.organizations.all()
        agents = UserProfile.objects.filter(
            role='agent',
            organizations__in=user_orgs
        ).distinct().select_related('user')
    
    # Calculate the estimated agent work time if we have agent work logs
    agent_work_time_stats = {}
    if AgentWorkLog.objects.exists():
        # Calculate average work time per ticket for each agent
        agent_logs = AgentWorkLog.objects.filter(
            ticket__in=tickets,
            start_time__date__gte=date_from,
            start_time__date__lte=date_to
        )
        
        agent_work_summary = agent_logs.values('agent').annotate(
            total_time=Sum('work_time_minutes'),
            ticket_count=Count('ticket', distinct=True)
        )
        
        for summary in agent_work_summary:
            agent_id = summary['agent']
            try:
                agent_user = UserProfile.objects.get(user_id=agent_id).user
                agent_name = f"{agent_user.first_name} {agent_user.last_name}" if agent_user.first_name else agent_user.username
                
                total_minutes = summary['total_time'] or 0
                ticket_count = summary['ticket_count']
                
                if ticket_count > 0:
                    avg_minutes_per_ticket = total_minutes / ticket_count
                else:
                    avg_minutes_per_ticket = 0
                
                agent_work_time_stats[agent_id] = {
                    'agent_name': agent_name,
                    'total_minutes': total_minutes,
                    'avg_minutes_per_ticket': avg_minutes_per_ticket,
                    'ticket_count': ticket_count
                }
            except UserProfile.DoesNotExist:
                pass
    
    # In your statistics_dashboard view, before returning the context:
    agent_work_time_processed = []
    for ap in agent_performance:
        agent_id = ap.get('agent_id')
        if agent_id in agent_work_time_stats:
            ap['work_time_stats'] = agent_work_time_stats[agent_id]
        else:
            ap['work_time_stats'] = None
        agent_work_time_processed.append(ap)

    # Replace agent_performance in your context with the processed version
    context = {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'total_tickets': total_tickets,
        'new_tickets': new_tickets,
        'in_progress_tickets': in_progress_tickets,
        'waiting_tickets': waiting_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'avg_resolution_hours': avg_resolution_hours,
        'priority_distribution': list(priority_distribution),
        'category_distribution': list(category_distribution),
        'tickets_by_date': list(tickets_by_date),
        'agent_performance': agent_performance,
        'organizations': organizations,
        'agents': agents,
        'org_filter': org_filter,
        'agent_filter': agent_filter,
        'agent_work_time_stats': agent_work_time_stats,
    }
    
    # Format data for JSON serialization in charts
    priority_data = list(priority_distribution)
    category_data = list(category_distribution)
    
    # Format tickets_by_date for JSON serialization
    tickets_by_date_data = []
    for entry in tickets_by_date:
        tickets_by_date_data.append({
            'date': entry['date'].isoformat() if hasattr(entry['date'], 'isoformat') else str(entry['date']),
            'count': entry['count']
        })
    
    # Process agent performance data with work time stats
    for ap in agent_performance:
        agent_id = ap.get('agent_id')
        if agent_id and agent_id in agent_work_time_stats:
            ap['work_time_stats'] = agent_work_time_stats[agent_id]
        else:
            ap['work_time_stats'] = None
    
    context = {
        'period': period,
        'date_from': date_from,
        'date_to': date_to,
        'total_tickets': total_tickets,
        'new_tickets': new_tickets,
        'in_progress_tickets': in_progress_tickets,
        'waiting_tickets': waiting_tickets,
        'resolved_tickets': resolved_tickets,
        'closed_tickets': closed_tickets,
        'avg_resolution_hours': avg_resolution_hours,
        'priority_distribution': priority_data,
        'category_distribution': category_data,
        'tickets_by_date': tickets_by_date_data,
        'agent_performance': agent_work_time_processed,
        'organizations': organizations,
        'agents': agents,
        'org_filter': org_filter,
        'agent_filter': agent_filter,
        'agent_work_time_stats': agent_work_time_stats,
    }
    
    return render(request, 'crm/statistics/statistics_dashboard.html', context)

@login_required
def update_agent_work_log(request):
    """API endpoint to record agent work time on tickets"""
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Method not allowed'}, status=405)
    
    user = request.user
    if user.profile.role not in ['agent', 'admin', 'superagent']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    ticket_id = request.POST.get('ticket_id')
    action = request.POST.get('action')  # 'start' or 'stop'
    notes = request.POST.get('notes', '')
    
    try:
        ticket = Ticket.objects.get(id=ticket_id)
    except Ticket.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Ticket not found'}, status=404)
    
    # Only assigned agent, admin or superagent can log work time
    if user.profile.role not in ['admin', 'superagent'] and ticket.assigned_to != user:
        return JsonResponse({'status': 'error', 'message': 'You are not assigned to this ticket'}, status=403)
    
    now = timezone.now()
    
    if action == 'start':
        # Check if there's already an open work log
        open_log = AgentWorkLog.objects.filter(
            agent=user,
            ticket=ticket,
            end_time__isnull=True
        ).first()
        
        if open_log:
            return JsonResponse({
                'status': 'error',
                'message': 'You already have an open work log for this ticket'
            }, status=400)
        
        # Start new work log
        work_log = AgentWorkLog.objects.create(
            agent=user,
            ticket=ticket,
            start_time=now,
            notes=notes
        )
        
        return JsonResponse({
            'status': 'success',
            'message': 'Work log started',
            'work_log_id': work_log.id
        })
        
    elif action == 'stop':
        # Find open work log
        open_log = AgentWorkLog.objects.filter(
            agent=user,
            ticket=ticket,
            end_time__isnull=True
        ).first()
        
        if not open_log:
            return JsonResponse({
                'status': 'error',
                'message': 'No open work log found for this ticket'
            }, status=400)
        
        # Update end time and calculate work time
        open_log.end_time = now
        
        # Calculate work time considering only work hours
        work_minutes = calculate_work_minutes(open_log.start_time, now)
        open_log.work_time_minutes = work_minutes
        
        if notes:
            open_log.notes = notes
            
        open_log.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Work log completed',
            'work_minutes': work_minutes
        })
    
    return JsonResponse({'status': 'error', 'message': 'Invalid action'}, status=400)

def calculate_work_minutes(start_time, end_time):
    """Calculate working minutes between two timestamps, considering only work hours"""
    # Get work hours configuration
    work_hours = WorkHours.objects.all()
    
    # If no work hours defined, use 8:00-16:00 Mon-Fri as default
    if not work_hours.exists():
        default_work_hours = {}
        for day in range(5):  # Monday to Friday
            default_work_hours[day] = [(datetime.time(8, 0), datetime.time(16, 0))]
    else:
        # Organize work hours by day
        default_work_hours = {}
        for wh in work_hours:
            if wh.is_working_day:
                if wh.day_of_week not in default_work_hours:
                    default_work_hours[wh.day_of_week] = []
                default_work_hours[wh.day_of_week].append((wh.start_time, wh.end_time))
    
    # If start and end are on the same day, calculate directly
    if start_time.date() == end_time.date():
        day_of_week = start_time.weekday()
        if day_of_week in default_work_hours:
            # Check each work period in this day
            total_minutes = 0
            for start_hour, end_hour in default_work_hours[day_of_week]:
                period_start = datetime.datetime.combine(
                    start_time.date(), 
                    start_hour,
                    tzinfo=start_time.tzinfo
                )
                period_end = datetime.datetime.combine(
                    start_time.date(), 
                    end_hour,
                    tzinfo=start_time.tzinfo
                )
                
                # Find overlap between work period and log period
                overlap_start = max(period_start, start_time)
                overlap_end = min(period_end, end_time)
                
                if overlap_end > overlap_start:
                    overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                    total_minutes += overlap_minutes
            
            return total_minutes
        else:
            # Not a working day
            return 0
    else:
        # If spanning multiple days, calculate day by day
        current_date = start_time.date()
        end_date = end_time.date()
        total_minutes = 0
        
        while current_date <= end_date:
            if current_date == start_time.date():
                # First day - from start_time to end of work day
                day_start = start_time
                day_end = datetime.datetime.combine(
                    current_date,
                    datetime.time(23, 59, 59),
                    tzinfo=start_time.tzinfo
                )
            elif current_date == end_date:
                # Last day - from start of work day to end_time
                day_start = datetime.datetime.combine(
                    current_date,
                    datetime.time(0, 0),
                    tzinfo=start_time.tzinfo
                )
                day_end = end_time
            else:
                # Middle days - full day
                day_start = datetime.datetime.combine(
                    current_date,
                    datetime.time(0, 0),
                    tzinfo=start_time.tzinfo
                )
                day_end = datetime.datetime.combine(
                    current_date,
                    datetime.time(23, 59, 59),
                    tzinfo=start_time.tzinfo
                )
            
            # Calculate minutes for this day
            day_of_week = current_date.weekday()
            if day_of_week in default_work_hours:
                for start_hour, end_hour in default_work_hours[day_of_week]:
                    period_start = datetime.datetime.combine(
                        current_date, 
                        start_hour,
                        tzinfo=start_time.tzinfo
                    )
                    period_end = datetime.datetime.combine(
                        current_date, 
                        end_hour,
                        tzinfo=start_time.tzinfo
                    )
                    
                    overlap_start = max(period_start, day_start)
                    overlap_end = min(period_end, day_end)
                    
                    if overlap_end > overlap_start:
                        overlap_minutes = (overlap_end - overlap_start).total_seconds() / 60
                        total_minutes += overlap_minutes
            
            current_date += timedelta(days=1)
        
        return total_minutes

@login_required
def generate_statistics_report(request):
    """Generate and store statistics for analysis"""
    user = request.user
    
    # Only admin and superagent can generate reports
    if user.profile.role not in ['admin', 'superagent']:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=403)
    
    period_type = request.POST.get('period_type', 'month')
    period_start = request.POST.get('period_start')
    period_end = request.POST.get('period_end')
    organization_id = request.POST.get('organization')
    agent_id = request.POST.get('agent')
    
    try:
        period_start_date = datetime.datetime.strptime(period_start, '%Y-%m-%d').date()
        period_end_date = datetime.datetime.strptime(period_end, '%Y-%m-%d').date()
    except (ValueError, TypeError):
        return JsonResponse({'status': 'error', 'message': 'Invalid date format'}, status=400)
    
    # Filter tickets
    tickets_query = Ticket.objects.filter(
        created_at__date__gte=period_start_date,
        created_at__date__lte=period_end_date
    )
    
    # Apply organization filter if specified
    organization = None
    if organization_id:
        try:
            organization = Organization.objects.get(id=organization_id)
            tickets_query = tickets_query.filter(organization=organization)
        except Organization.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Organization not found'}, status=400)
    
    # Apply agent filter if specified
    agent = None
    if agent_id:
        try:
            agent = UserProfile.objects.get(user_id=agent_id).user
            tickets_query = tickets_query.filter(assigned_to=agent)
        except UserProfile.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Agent not found'}, status=400)
    
    # Calculate statistics
    tickets_opened = tickets_query.count()
    tickets_closed = tickets_query.filter(status='closed').count()
    tickets_resolved = tickets_query.filter(status='resolved').count()
    
    # Calculate average resolution time
    resolution_time_data = tickets_query.exclude(
        resolved_at__isnull=True
    ).aggregate(
        avg_time=Avg(
            ExpressionWrapper(
                F('resolved_at') - F('created_at'),
                output_field=fields.DurationField()
            )
        )
    )
    avg_resolution_time = 0
    if resolution_time_data['avg_time']:
        avg_resolution_time = resolution_time_data['avg_time'].total_seconds() / 60
    
    # Calculate priority distribution
    priority_counts = tickets_query.values('priority').annotate(count=Count('id'))
    priority_distribution = {item['priority']: item['count'] for item in priority_counts}
    
    # Calculate category distribution
    category_counts = tickets_query.values('category').annotate(count=Count('id'))
    category_distribution = {item['category']: item['count'] for item in category_counts}
    
    # Calculate average agent work time if agent work logs exist
    avg_agent_work_time = 0
    if AgentWorkLog.objects.filter(ticket__in=tickets_query).exists():
        agent_work_data = AgentWorkLog.objects.filter(
            ticket__in=tickets_query
        ).aggregate(
            avg_time=Avg('work_time_minutes')
        )
        avg_agent_work_time = agent_work_data['avg_time'] or 0
    
    # Calculate average first response time (if we track that data)
    avg_first_response_time = 0
    
    # Create or update statistics record
    stats, created = TicketStatistics.objects.update_or_create(
        period_type=period_type,
        period_start=period_start_date,
        period_end=period_end_date,
        organization=organization,
        agent=agent,
        defaults={
            'tickets_opened': tickets_opened,
            'tickets_closed': tickets_closed,
            'tickets_resolved': tickets_resolved,
            'avg_resolution_time': avg_resolution_time,
            'avg_first_response_time': avg_first_response_time,
            'avg_agent_work_time': avg_agent_work_time,
            'priority_distribution': priority_distribution,
            'category_distribution': category_distribution,
        }
    )
    
    return JsonResponse({
        'status': 'success',
        'message': 'Statistics report generated successfully',
        'report_id': stats.id
    })
