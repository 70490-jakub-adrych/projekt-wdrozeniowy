from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth.models import Group
from django.http import HttpResponseForbidden
import os

from .forms import (
    UserRegisterForm, UserProfileForm, OrganizationForm,
    TicketForm, ModeratorTicketForm, TicketCommentForm, TicketAttachmentForm
)
from .models import (
    UserProfile, Organization, Ticket, TicketComment,
    TicketAttachment, ActivityLog
)


def get_client_ip(request):
    """Funkcja pomocnicza do pobrania adresu IP klienta"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def log_activity(request, action_type, ticket=None, description=""):
    """Funkcja pomocnicza do logowania aktywności"""
    if request.user.is_authenticated:
        ActivityLog.objects.create(
            user=request.user,
            action_type=action_type,
            ticket=ticket,
            description=description,
            ip_address=get_client_ip(request)
        )


def landing_page(request):
    """Widok strony głównej przed zalogowaniem"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'crm/landing_page.html')


def register(request):
    """Widok rejestracji nowego użytkownika"""
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        profile_form = UserProfileForm(request.POST)
        
        if form.is_valid() and profile_form.is_valid():
            user = form.save()
            
            # Przypisanie do odpowiedniej grupy na podstawie roli
            if user.is_superuser:
                group, _ = Group.objects.get_or_create(name='Admin')
                role = 'admin'
            else:
                group, _ = Group.objects.get_or_create(name='Klient')
                role = 'client'
            
            user.groups.add(group)
            
            # Uzupełnienie profilu
            profile = user.profile
            profile.role = role
            profile.phone = profile_form.cleaned_data.get('phone')
            profile.organization = profile_form.cleaned_data.get('organization')
            profile.save()
            
            login(request, user)
            log_activity(request, 'login')
            messages.success(request, 'Konto zostało utworzone!')
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
        profile_form = UserProfileForm()
    
    return render(request, 'crm/register.html', {'form': form, 'profile_form': profile_form})


def custom_login_view(request):
    """Niestandardowy widok logowania z zapisywaniem logów"""
    if request.user.is_authenticated:
        log_activity(request, 'login')
    return redirect('dashboard')


def custom_logout_view(request):
    """Niestandardowy widok wylogowania z zapisywaniem logów"""
    if request.user.is_authenticated:
        log_activity(request, 'logout')
    logout(request)
    return redirect('landing_page')


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
        from crm.models import UserProfile
        from django.contrib.auth.models import Group
        
        # Determine appropriate role based on superuser status
        if user.is_superuser:
            role = 'admin'
            group_name = 'Admin'
            message = 'Twój profil administratora został utworzony.'
        else:
            role = 'client'
            group_name = 'Klient'
            message = 'Twój profil został utworzony. Skontaktuj się z administratorem, aby uzyskać odpowiednie uprawnienia.'
        
        # Create profile with appropriate role
        user_profile = UserProfile.objects.create(
            user=user,
            role=role
        )
        
        # Add user to appropriate group
        user_group, created = Group.objects.get_or_create(name=group_name)
        user.groups.add(user_group)
        
        messages.info(request, message)
    
    # Statystyki dla wszystkich użytkowników
    if user.profile.role == 'admin' or user.profile.role == 'moderator':
        # Statystyki dla administratorów i moderatorów
        new_tickets = Ticket.objects.filter(status='new').count()
        in_progress_tickets = Ticket.objects.filter(status='in_progress').count()
        waiting_tickets = Ticket.objects.filter(status='waiting').count()
        resolved_tickets = Ticket.objects.filter(status='resolved').count()
        closed_tickets = Ticket.objects.filter(status='closed').count()
        
        # Jeśli moderator, pokaż tylko swoje przypisane zgłoszenia
        if user.profile.role == 'moderator':
            assigned_tickets = Ticket.objects.filter(assigned_to=user)
            unassigned_tickets = Ticket.objects.filter(assigned_to=None)
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


# Widoki organizacji
@login_required
def organization_list(request):
    """Widok listy organizacji"""
    # Tylko admin i moderator mogą widzieć wszystkie organizacje
    if request.user.profile.role in ['admin', 'moderator']:
        organizations = Organization.objects.all()
    else:
        # Klient widzi tylko swoją organizację
        if request.user.profile.organization:
            organizations = [request.user.profile.organization]
        else:
            organizations = []
    
    return render(request, 'crm/organizations/organization_list.html', {'organizations': organizations})


@login_required
def organization_detail(request, pk):
    """Widok szczegółów organizacji"""
    organization = get_object_or_404(Organization, pk=pk)
    
    # Sprawdzenie uprawnień
    if (request.user.profile.role not in ['admin', 'moderator'] and 
        request.user.profile.organization != organization):
        return HttpResponseForbidden("Brak dostępu")
    
    members = UserProfile.objects.filter(organization=organization)
    tickets = Ticket.objects.filter(organization=organization)
    
    context = {
        'organization': organization,
        'members': members,
        'tickets': tickets,
    }
    
    return render(request, 'crm/organizations/organization_detail.html', context)


@login_required
def organization_create(request):
    """Widok tworzenia organizacji"""
    # Tylko admin może tworzyć organizacje
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("Brak uprawnień")
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST)
        if form.is_valid():
            organization = form.save()
            messages.success(request, 'Organizacja została utworzona!')
            return redirect('organization_detail', pk=organization.pk)
    else:
        form = OrganizationForm()
    
    return render(request, 'crm/organizations/organization_form.html', {'form': form})


@login_required
def organization_update(request, pk):
    """Widok aktualizacji organizacji"""
    # Tylko admin może aktualizować organizacje
    if request.user.profile.role != 'admin':
        return HttpResponseForbidden("Brak uprawnień")
    
    organization = get_object_or_404(Organization, pk=pk)
    
    if request.method == 'POST':
        form = OrganizationForm(request.POST, instance=organization)
        if form.is_valid():
            form.save()
            messages.success(request, 'Organizacja została zaktualizowana!')
            return redirect('organization_detail', pk=organization.pk)
    else:
        form = OrganizationForm(instance=organization)
    
    return render(request, 'crm/organizations/organization_form.html', {'form': form, 'organization': organization})


# Widoki zgłoszeń
@login_required
def ticket_list(request):
    """Widok listy zgłoszeń"""
    user = request.user
    role = user.profile.role
    
    # Filtrowanie i sortowanie
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    # Określenie widocznych zgłoszeń na podstawie roli
    if role == 'admin':
        tickets = Ticket.objects.all()
    elif role == 'moderator':
        tickets = Ticket.objects.filter(
            Q(assigned_to=user) | Q(assigned_to=None)
        )
    else:  # klient
        if user.profile.organization:
            tickets = Ticket.objects.filter(organization=user.profile.organization)
        else:
            tickets = Ticket.objects.filter(created_by=user)
    
    # Zastosowanie filtrów
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    # Zastosowanie sortowania
    tickets = tickets.order_by(sort_by)
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'sort_by': sort_by,
    }
    
    return render(request, 'crm/tickets/ticket_list.html', context)


@login_required
def ticket_detail(request, pk):
    """Widok szczegółów zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdzenie uprawnień dostępu do zgłoszenia
    if role == 'client':
        if user.profile.organization != ticket.organization and user != ticket.created_by:
            return HttpResponseForbidden("Brak dostępu do tego zgłoszenia")
    
    comments = ticket.comments.all().order_by('created_at')
    attachments = ticket.attachments.all()
    
    # Formularz komentarza
    if request.method == 'POST':
        comment_form = TicketCommentForm(request.POST)
        attachment_form = TicketAttachmentForm(request.POST, request.FILES)
        
        if 'submit_comment' in request.POST and comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.ticket = ticket
            comment.author = request.user
            comment.save()
            log_activity(request, 'ticket_commented', ticket, f"Dodano komentarz do zgłoszenia '{ticket.title}'")
            messages.success(request, 'Komentarz został dodany!')
            return redirect('ticket_detail', pk=ticket.pk)
            
        if 'submit_attachment' in request.POST and attachment_form.is_valid():
            attachment = attachment_form.save(commit=False)
            attachment.ticket = ticket
            attachment.uploaded_by = request.user
            attachment.filename = os.path.basename(attachment.file.name)
            attachment.save()
            messages.success(request, 'Załącznik został dodany!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        comment_form = TicketCommentForm()
        attachment_form = TicketAttachmentForm()
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
    }
    
    return render(request, 'crm/tickets/ticket_detail.html', context)


@login_required
def ticket_create(request):
    """Widok tworzenia nowego zgłoszenia"""
    user = request.user
    
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = user
            
            # Get the organization for the current user
            # This assumes the user has a profile with an organization
            if hasattr(request.user, 'profile') and request.user.profile.organization:
                ticket.organization = request.user.profile.organization
            # Alternative approach if user is directly related to organization
            elif hasattr(request.user, 'organization'):
                ticket.organization = request.user.organization
            else:
                # If no organization found and it's required, redirect with error
                messages.error(request, "Cannot create ticket: No organization associated with your account.")
                return redirect('dashboard')
                
            ticket.save()
            log_activity(request, 'ticket_created', ticket, f"Utworzono zgłoszenie: '{ticket.title}'")
            messages.success(request, 'Zgłoszenie zostało utworzone!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        form = TicketForm()
    
    # Dodanie pola wyboru organizacji dla admina i moderatora
    organizations = []
    if user.profile.role in ['admin', 'moderator']:
        organizations = Organization.objects.all()
    
    context = {
        'form': form,
        'organizations': organizations,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)


@login_required
def ticket_update(request, pk):
    """Widok aktualizacji zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdzenie uprawnień do edycji
    if role == 'client':
        # Klient może edytować tylko swoje zgłoszenia
        if ticket.created_by != user:
            return HttpResponseForbidden("Nie możesz edytować tego zgłoszenia")
    
    if request.method == 'POST':
        # Inny formularz w zależności od roli
        if role in ['admin', 'moderator']:
            form = ModeratorTicketForm(request.POST, instance=ticket)
        else:
            form = TicketForm(request.POST, instance=ticket)
            
        if form.is_valid():
            old_status = ticket.status
            updated_ticket = form.save()
            
            # Logowanie zmiany statusu
            if old_status != updated_ticket.status:
                log_activity(
                    request, 
                    'ticket_updated', 
                    ticket, 
                    f"Zmieniono status zgłoszenia '{ticket.title}' z '{old_status}' na '{updated_ticket.status}'"
                )
            else:
                log_activity(request, 'ticket_updated', ticket, f"Zaktualizowano zgłoszenie '{ticket.title}'")
            
            messages.success(request, 'Zgłoszenie zostało zaktualizowane!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        if role in ['admin', 'moderator']:
            form = ModeratorTicketForm(instance=ticket)
        else:
            form = TicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)


@login_required
def ticket_close(request, pk):
    """Widok zamykania zgłoszenia"""
    user = request.user
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdzenie uprawnień
    if user.profile.role == 'client' and ticket.created_by != user:
        return HttpResponseForbidden("Nie możesz zamknąć tego zgłoszenia")
    
    if request.method == 'POST':
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        
        log_activity(request, 'ticket_closed', ticket, f"Zamknięto zgłoszenie '{ticket.title}'")
        messages.success(request, 'Zgłoszenie zostało zamknięte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_close.html', {'ticket': ticket})


@login_required
def ticket_reopen(request, pk):
    """Widok ponownego otwierania zamkniętego zgłoszenia"""
    user = request.user
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Tylko admin i moderator mogą ponownie otwierać zgłoszenia
    if user.profile.role == 'client':
        return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia")
    
    if request.method == 'POST':
        ticket.status = 'new'
        ticket.closed_at = None
        ticket.save()
        
        log_activity(request, 'ticket_reopened', ticket, f"Ponownie otwarto zgłoszenie '{ticket.title}'")
        messages.success(request, 'Zgłoszenie zostało ponownie otwarte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_reopen.html', {'ticket': ticket})


@login_required
def activity_logs(request):
    """Widok logów aktywności"""
    user = request.user
    role = user.profile.role
    
    # Tylko admin może oglądać wszystkie logi
    if role != 'admin':
        return HttpResponseForbidden("Brak dostępu do logów")
    
    logs = ActivityLog.objects.all().order_by('-created_at')
    
    # Filtrowanie
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    
    if action_filter:
        logs = logs.filter(action_type=action_filter)
    if user_filter:
        logs = logs.filter(user__username__icontains=user_filter)
    
    context = {
        'logs': logs[:100],  # Ograniczenie do 100 ostatnich wpisów
        'action_filter': action_filter,
        'user_filter': user_filter,
    }
    
    return render(request, 'crm/logs/activity_logs.html', context)
