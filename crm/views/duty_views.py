from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import datetime, timedelta
from ..models import CalendarDuty
from ..decorators import role_required


@login_required
@role_required(['admin', 'superagent'])
def generate_duties(request):
    """Widok generowania dyżurów (tylko dla admin/superagent)"""
    
    # Get all agents, superagents and admins
    available_users = User.objects.filter(
        profile__role__in=['agent', 'superagent', 'admin']
    ).select_related('profile').order_by('username')
    
    if request.method == 'POST':
        # Get selected users
        selected_user_ids = request.POST.getlist('selected_users')
        num_weeks = request.POST.get('num_weeks', '52')
        
        try:
            num_weeks = int(num_weeks)
            if num_weeks < 1 or num_weeks > 104:  # Max 2 years
                messages.error(request, 'Liczba tygodni musi być między 1 a 104!')
                return redirect('generate_duties')
        except ValueError:
            messages.error(request, 'Nieprawidłowa liczba tygodni!')
            return redirect('generate_duties')
        
        if not selected_user_ids:
            messages.error(request, 'Musisz wybrać przynajmniej jedną osobę do dyżurów!')
            return redirect('generate_duties')
        
        # Get selected users
        selected_users = User.objects.filter(id__in=selected_user_ids)
        
        if not selected_users.exists():
            messages.error(request, 'Nie wybrano poprawnych użytkowników!')
            return redirect('generate_duties')
        
        # Get today and calculate end date
        today = timezone.now().date()
        # Start from next Monday if not Monday
        start_date = today
        if today.weekday() != 0:  # If not Monday
            start_date = today + timedelta(days=(7 - today.weekday()))
        
        # Calculate end date (num_weeks * 7 days)
        end_date = start_date + timedelta(weeks=num_weeks) - timedelta(days=1)
        
        # Check if overwrite is selected - if yes, delete ALL duties and don't continue rotation
        overwrite_existing = request.POST.get('overwrite_existing') == 'yes'
        
        if overwrite_existing:
            # Delete ALL duties from the entire calendar
            deleted_count = CalendarDuty.objects.all().delete()[0]
            if deleted_count > 0:
                messages.warning(request, f'Usunięto wszystkie {deleted_count} dyżurów z kalendarza.')
            # Start fresh - no continuation
            user_index = 0
            should_continue = False
            users_list = list(selected_users)
        else:
            # Normal mode - check if we should continue existing rotation
            user_index = 0
            should_continue = False
            users_list = list(selected_users)
            
            # Get last duty before start_date to continue rotation
            last_duty = CalendarDuty.objects.filter(
                duty_date__lt=start_date
            ).select_related('assigned_to').order_by('-duty_date').first()
            
            if last_duty and request.POST.get('continue_rotation') == 'yes':
                # Check if last duty person is in selected users
                try:
                    # Find where the last person was in the rotation
                    last_index = users_list.index(last_duty.assigned_to)
                    # Start with next person
                    user_index = (last_index + 1) % len(users_list)
                    should_continue = True
                except ValueError:
                    # Last person not in current selection, start from beginning
                    user_index = 0
        
        # Generate duties
        created_count = 0
        skipped_count = 0
        current_date = start_date
        
        while current_date <= end_date:
            # Change person every Monday (start of week)
            if current_date.weekday() == 0 and current_date != start_date:
                user_index = (user_index + 1) % len(users_list)
            
            # Skip if duty already exists (unless overwrite is selected)
            if overwrite_existing or not CalendarDuty.objects.filter(duty_date=current_date).exists():
                # Assign duty to current user in rotation
                CalendarDuty.objects.create(
                    duty_date=current_date,
                    assigned_to=users_list[user_index],
                    created_by=request.user,
                    notes=f"{'Kontynuacja rotacji - ' if should_continue else ''}Wygenerowano automatycznie (tydzień {current_date.isocalendar()[1]})"
                )
                created_count += 1
            else:
                skipped_count += 1
            
            # Move to next day
            current_date += timedelta(days=1)
        
        # Prepare success message
        if overwrite_existing:
            success_msg = f'Kalendarz wyczyszczony! Wygenerowano {created_count} nowych dyżurów na {num_weeks} tygodni (od {start_date} do {end_date}).'
        else:
            success_msg = f'Wygenerowano {created_count} dyżurów na {num_weeks} tygodni (od {start_date} do {end_date})!'
            if skipped_count > 0:
                success_msg += f' Pominięto {skipped_count} już istniejących.'
            if should_continue:
                success_msg += f' Kontynuowano rotację od: {users_list[user_index].username}'
        
        messages.success(request, success_msg)
        return redirect('dashboard')
    
    # GET request - show form
    # Get existing duties to show preview and detect continuation
    today = timezone.now().date()
    
    # Get last duty to show who was last
    last_duty = CalendarDuty.objects.filter(
        duty_date__lt=today
    ).select_related('assigned_to').order_by('-duty_date').first()
    
    # Get existing future duties
    existing_duties = CalendarDuty.objects.filter(
        duty_date__gte=today
    ).select_related('assigned_to').order_by('duty_date')[:30]  # Show next 30 days
    
    # Calculate next Monday if not Monday
    next_monday = today
    if today.weekday() != 0:
        next_monday = today + timedelta(days=(7 - today.weekday()))
    
    context = {
        'available_users': available_users,
        'existing_duties': existing_duties,
        'current_year': timezone.now().year,
        'last_duty': last_duty,
        'next_monday': next_monday,
        'today': today,
    }
    
    return render(request, 'crm/duties/generate_duties.html', context)


@login_required
@role_required(['admin', 'superagent'])
def change_duty(request):
    """AJAX endpoint do zmiany dyżuru dla konkretnego dnia"""
    
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Metoda nie dozwolona'}, status=405)
    
    duty_date_str = request.POST.get('duty_date')
    new_user_id = request.POST.get('user_id')
    notes = request.POST.get('notes', '')
    
    if not duty_date_str or not new_user_id:
        return JsonResponse({'success': False, 'error': 'Brak wymaganych danych'}, status=400)
    
    try:
        # Parse date
        duty_date = datetime.strptime(duty_date_str, '%Y-%m-%d').date()
        
        # Get user
        new_user = User.objects.get(id=new_user_id)
        
        # Check if user has proper role
        if new_user.profile.role not in ['agent', 'superagent', 'admin']:
            return JsonResponse({
                'success': False,
                'error': 'Wybrany użytkownik nie może pełnić dyżuru'
            }, status=400)
        
        # Prepare notes
        if not notes:
            notes = f"Zmieniony przez {request.user.username}"
        else:
            notes = f"{notes} (zmienił: {request.user.username})"
        
        # Update or create duty
        duty, created = CalendarDuty.objects.update_or_create(
            duty_date=duty_date,
            defaults={
                'assigned_to': new_user,
                'created_by': request.user,
                'notes': notes
            }
        )
        
        action = 'utworzony' if created else 'zmieniony'
        return JsonResponse({
            'success': True,
            'message': f'Dyżur na {duty_date} został {action} - przypisany do {new_user.username}',
            'duty': {
                'date': duty_date.strftime('%Y-%m-%d'),
                'user_id': new_user.id,
                'username': new_user.username,
                'full_name': new_user.get_full_name() or new_user.username,
                'notes': notes
            }
        })
        
    except ValueError:
        return JsonResponse({'success': False, 'error': 'Nieprawidłowy format daty'}, status=400)
    except User.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Użytkownik nie istnieje'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
