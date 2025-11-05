"""
API views for AJAX requests
"""
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.views.decorators.http import require_http_methods


@login_required
@require_http_methods(["GET"])
def user_contact_info(request, user_id):
    """
    API endpoint to get user contact information for popup display
    Only accessible to non-client users
    """
    try:
        # Check if user has permission to view contact information
        if request.user.profile.role == 'client':
            return JsonResponse({
                'success': False,
                'error': 'Brak uprawnień do przeglądania informacji kontaktowych'
            }, status=403)
        
        user = get_object_or_404(User, id=user_id)
        
        # Build full name
        full_name = ""
        if user.first_name or user.last_name:
            full_name = f"{user.first_name} {user.last_name}".strip()
        
        # Get role display name
        role_display = ""
        if hasattr(user, 'profile') and user.profile:
            role_choices = dict(user.profile.USER_ROLES)
            role_display = role_choices.get(user.profile.role, user.profile.role)
        
        # Get organizations
        organizations = []
        if hasattr(user, 'profile') and user.profile:
            organizations = [org.name for org in user.profile.organizations.all()]
        
        # Get contact information
        email = user.email if user.email else ""
        phone = ""
        if hasattr(user, 'profile') and user.profile and user.profile.phone:
            phone = user.profile.phone
        
        return JsonResponse({
            'success': True,
            'username': user.username,
            'full_name': full_name,
            'email': email,
            'phone': phone,
            'role': role_display,
            'organizations': organizations
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def agent_tickets(request, agent_id):
    """
    API endpoint to get tickets assigned to a specific agent
    Only accessible to admin and superagent roles
    """
    try:
        # Check if user has permission to view agent tickets
        if request.user.profile.role not in ['admin', 'superagent']:
            return JsonResponse({
                'success': False,
                'error': 'Brak uprawnień do przeglądania szczegółów ticketów agentów'
            }, status=403)
        
        # Import here to avoid circular imports
        from ..models import Ticket
        import datetime
        
        # Get date range from query parameters
        date_from = request.GET.get('date_from', '')
        date_to = request.GET.get('date_to', '')
        
        # Parse dates
        try:
            if date_from:
                date_from = datetime.datetime.strptime(date_from, '%Y-%m-%d').date()
            if date_to:
                date_to = datetime.datetime.strptime(date_to, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format daty'
            }, status=400)
        
        # Get agent's tickets
        tickets = Ticket.objects.filter(assigned_to_id=agent_id)
        
        # Apply date filter if provided
        if date_from:
            tickets = tickets.filter(created_at__date__gte=date_from)
        if date_to:
            tickets = tickets.filter(created_at__date__lte=date_to)
        
        # Build ticket list
        ticket_list = []
        for ticket in tickets.order_by('-created_at'):
            ticket_list.append({
                'id': ticket.id,
                'title': ticket.title,
                'status': ticket.get_status_display(),
                'status_raw': ticket.status,
                'priority': ticket.get_priority_display(),
                'priority_raw': ticket.priority,
                'category': ticket.category,
                'created_at': ticket.created_at.strftime('%Y-%m-%d %H:%M'),
                'resolved_at': ticket.resolved_at.strftime('%Y-%m-%d %H:%M') if ticket.resolved_at else None,
                'closed_at': ticket.closed_at.strftime('%Y-%m-%d %H:%M') if ticket.closed_at else None,
                'url': f'/tickets/{ticket.id}/'
            })
        
        return JsonResponse({
            'success': True,
            'tickets': ticket_list,
            'count': len(ticket_list)
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@require_http_methods(["POST"])
def toggle_theme(request):
    """
    API endpoint to toggle user theme preference
    """
    try:
        theme = request.POST.get('theme', 'light')
        
        # Validate theme value
        if theme not in ['light', 'dark']:
            theme = 'light'
        
        # Create response and set cookie
        response = JsonResponse({
            'success': True,
            'theme': theme
        })
        
        # Set theme cookie with 1 year expiration
        response.set_cookie(
            'theme', 
            theme, 
            max_age=31536000,  # 1 year
            samesite='Lax'
        )
        
        return response
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def calendar_notes_api(request):
    """
    API endpoint to get user's calendar notes for a specific date range
    """
    try:
        from ..models import CalendarNote
        from datetime import datetime
        
        # Get date range from query parameters
        start_date = request.GET.get('start')
        end_date = request.GET.get('end')
        
        if not start_date or not end_date:
            return JsonResponse({
                'success': False,
                'error': 'Brak wymaganych parametrów daty'
            }, status=400)
        
        # Parse dates
        try:
            start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format daty'
            }, status=400)
        
        # Get user's notes in date range
        notes = CalendarNote.objects.filter(
            user=request.user,
            date__gte=start_date,
            date__lte=end_date
        ).order_by('date')
        
        # Build notes list
        notes_list = []
        for note in notes:
            notes_list.append({
                'id': note.id,
                'date': note.date.strftime('%Y-%m-%d'),
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
            })
        
        return JsonResponse({
            'success': True,
            'notes': notes_list
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["POST"])
def calendar_note_create(request):
    """
    API endpoint to create a new calendar note
    """
    try:
        from ..models import CalendarNote
        from datetime import datetime
        import json
        
        data = json.loads(request.body)
        date_str = data.get('date')
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        # Validate required fields
        if not date_str or not title:
            return JsonResponse({
                'success': False,
                'error': 'Data i tytuł są wymagane'
            }, status=400)
        
        # Parse date
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({
                'success': False,
                'error': 'Nieprawidłowy format daty'
            }, status=400)
        
        # Create note
        note = CalendarNote.objects.create(
            user=request.user,
            date=date,
            title=title,
            content=content
        )
        
        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'date': note.date.strftime('%Y-%m-%d'),
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Nieprawidłowy format danych'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["PUT", "PATCH"])
def calendar_note_update(request, note_id):
    """
    API endpoint to update an existing calendar note
    """
    try:
        from ..models import CalendarNote
        import json
        
        # Get note and verify ownership
        note = get_object_or_404(CalendarNote, id=note_id, user=request.user)
        
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        content = data.get('content', '').strip()
        
        # Validate title
        if not title:
            return JsonResponse({
                'success': False,
                'error': 'Tytuł jest wymagany'
            }, status=400)
        
        # Update note
        note.title = title
        note.content = content
        note.save()
        
        return JsonResponse({
            'success': True,
            'note': {
                'id': note.id,
                'date': note.date.strftime('%Y-%m-%d'),
                'title': note.title,
                'content': note.content,
                'created_at': note.created_at.strftime('%Y-%m-%d %H:%M'),
                'updated_at': note.updated_at.strftime('%Y-%m-%d %H:%M')
            }
        })
        
    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Nieprawidłowy format danych'
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["DELETE"])
def calendar_note_delete(request, note_id):
    """
    API endpoint to delete a calendar note
    """
    try:
        from ..models import CalendarNote
        
        # Get note and verify ownership
        note = get_object_or_404(CalendarNote, id=note_id, user=request.user)
        
        # Delete note
        note.delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Notatka została usunięta'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
