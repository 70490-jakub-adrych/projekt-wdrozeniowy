from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseForbidden, HttpResponse
import os
from datetime import datetime, timedelta
import logging
import json

# Configure logger
logger = logging.getLogger(__name__)

from ..models import Organization, Ticket, TicketComment, TicketAttachment, UserProfile
from ..forms import (
    TicketForm, ModeratorTicketForm, TicketCommentForm, TicketAttachmentForm,
    ClientTicketForm
)
from .helpers import log_activity


@login_required
def ticket_list(request):
    """Widok listy zgłoszeń"""
    user = request.user
    role = user.profile.role
    
    # Filtrowanie i sortowanie
    status_filter = request.GET.get('status', '')
    priority_filter = request.GET.get('priority', '')
    category_filter = request.GET.get('category', '')
    assigned_filter = request.GET.get('assigned', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    ticket_id = request.GET.get('ticket_id', '')
    sort_by = request.GET.get('sort_by', '-created_at')
    
    # Get user organizations and log their IDs for debugging
    user_orgs = user.profile.organizations.all()
    org_ids = list(user_orgs.values_list('id', flat=True))
    logger.debug(f"User {user.username} belongs to organizations: {org_ids}")
    
    # Określenie widocznych zgłoszeń na podstawie roli
    if role == 'admin':
        # Admin widzi wszystkie zgłoszenia
        tickets = Ticket.objects.all()
        logger.debug(f"Admin user {user.username} - showing all tickets")
    elif role == 'agent':
        # Agent widzi wszystkie zgłoszenia z organizacji, do których należy,
        # niezależnie od tego, do kogo są przypisane
        if not org_ids:
            tickets = Ticket.objects.none()
            logger.warning(f"Agent {user.username} has no organizations")
        else:
            # Force an explicit IN clause in SQL for clearer debugging and to avoid any optimization issues
            tickets = Ticket.objects.filter(organization_id__in=org_ids)
            # Log which organizations the user belongs to
            logger.debug(f"Agent {user.username} - showing tickets where organization_id IN {org_ids}")
            logger.debug(f"SQL Query: {str(tickets.query)}")
            
            # Debug: Log all ticket IDs from these organizations 
            ticket_ids = list(tickets.values_list('id', flat=True))
            logger.debug(f"Found {len(ticket_ids)} tickets: {ticket_ids}")
            
            # Debug: Log assigned tickets info
            assigned_tickets = tickets.filter(assigned_to__isnull=False)
            assigned_data = [(t.id, t.assigned_to.username) for t in assigned_tickets]
            logger.debug(f"Assigned tickets: {assigned_data}")
    else:  # client
        # Klient widzi zgłoszenia ze swoich organizacji i swoje własne
        tickets = Ticket.objects.filter(Q(organization__in=user_orgs) | Q(created_by=user))
        logger.debug(f"Client {user.username} - showing tickets from orgs and created by user")
    
    # Debug: Count results before filtering
    initial_count = tickets.count()
    logger.debug(f"Initial ticket count before filters: {initial_count}")
    
    # Zastosowanie filtrów
    if status_filter:
        tickets = tickets.filter(status=status_filter)
    if priority_filter:
        tickets = tickets.filter(priority=priority_filter)
    if category_filter:
        tickets = tickets.filter(category=category_filter)
    
    # Filtrowanie po przypisaniu
    if assigned_filter == 'me':
        tickets = tickets.filter(assigned_to=user)
    elif assigned_filter == 'unassigned':
        tickets = tickets.filter(assigned_to__isnull=True)
    # 'all' nie wymaga filtrowania - pokazuje wszystkie zgłoszenia z organizacji agenta
    
    # Filtrowanie po ID zgłoszenia
    if ticket_id:
        try:
            ticket_id = int(ticket_id)
            tickets = tickets.filter(id=ticket_id)
        except ValueError:
            # Jeśli podano nieprawidłowy ID, nie filtruj
            pass
    
    # Filtrowanie po zakresie dat
    if date_from:
        try:
            date_from_obj = datetime.strptime(date_from, '%Y-%m-%d')
            tickets = tickets.filter(created_at__gte=date_from_obj)
        except ValueError:
            # Nieprawidłowy format daty, ignorujemy
            pass
    
    if date_to:
        try:
            date_to_obj = datetime.strptime(date_to, '%Y-%m-%d')
            # Dodajemy jeden dzień, aby uwzględnić całą datę "do"
            date_to_obj = date_to_obj + timedelta(days=1)
            tickets = tickets.filter(created_at__lt=date_to_obj)
        except ValueError:
            # Nieprawidłowy format daty, ignorujemy
            pass
    
    # Dodaj logging do diagnostyki
    logger.debug(f"User {user.username} role {role} - final query: {str(tickets.query)}")
    final_count = tickets.count()
    logger.debug(f"Final ticket count after filters: {final_count}")
    
    # Zastosowanie sortowania
    tickets = tickets.order_by(sort_by)
    
    # Lista dostępnych opcji sortowania dla wyboru w interfejsie
    sort_options = [
        ('-created_at', 'Data utworzenia (najnowsze)'),
        ('created_at', 'Data utworzenia (najstarsze)'),
        ('title', 'Tytuł (A-Z)'),
        ('-title', 'Tytuł (Z-A)'),
        ('priority', 'Priorytet (rosnąco)'),
        ('-priority', 'Priorytet (malejąco)'),
        ('status', 'Status (rosnąco)'),
        ('-status', 'Status (malejąco)'),
        ('category', 'Kategoria (A-Z)'),
        ('-category', 'Kategoria (Z-A)'),
        ('organization__name', 'Organizacja (A-Z)'),
        ('-organization__name', 'Organizacja (Z-A)'),
    ]
    
    context = {
        'tickets': tickets,
        'status_filter': status_filter,
        'priority_filter': priority_filter,
        'category_filter': category_filter,
        'assigned_filter': assigned_filter,
        'date_from': date_from,
        'date_to': date_to,
        'ticket_id': ticket_id,
        'sort_by': sort_by,
        'sort_options': sort_options,
        'user_organizations': user_orgs,  # Add user's organizations for debugging in template
    }
    
    return render(request, 'crm/tickets/ticket_list.html', context)


@login_required
def debug_tickets(request):
    """Debug view to check access permissions"""
    if not request.user.is_staff:
        return HttpResponseForbidden("Only staff can access this debugging view")
    
    user = request.user
    result = {
        "username": user.username,
        "role": user.profile.role,
        "organizations": [],
        "tickets_visible": [],
    }
    
    # Get user's organizations
    user_orgs = user.profile.organizations.all()
    for org in user_orgs:
        org_data = {
            "id": org.id,
            "name": org.name,
            "tickets": []
        }
        
        # Get all tickets from this organization
        org_tickets = Ticket.objects.filter(organization=org)
        for ticket in org_tickets:
            org_data["tickets"].append({
                "id": ticket.id,
                "title": ticket.title,
                "assigned_to": ticket.assigned_to.username if ticket.assigned_to else "Unassigned",
                "status": ticket.status
            })
        
        result["organizations"].append(org_data)
    
    # Test the query that should show tickets
    if user.profile.role == 'agent':
        visible_tickets = Ticket.objects.filter(organization__in=user_orgs)
        for ticket in visible_tickets:
            result["tickets_visible"].append({
                "id": ticket.id,
                "title": ticket.title,
                "organization": ticket.organization.name,
                "assigned_to": ticket.assigned_to.username if ticket.assigned_to else "Unassigned"
            })
    
    return HttpResponse(
        json.dumps(result, indent=2), 
        content_type="application/json"
    )


@login_required
def ticket_detail(request, pk):
    """Widok szczegółów zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    user_orgs = user.profile.organizations.all()
    
    # Sprawdzenie uprawnień dostępu do zgłoszenia
    if role == 'client':
        # Klient może widzieć tylko zgłoszenia ze swoich organizacji lub utworzone przez siebie
        if ticket.organization not in user_orgs and user != ticket.created_by:
            logger.warning(f"Access denied: Client {user.username} tried to access ticket #{ticket.id}")
            return HttpResponseForbidden("Brak dostępu do tego zgłoszenia")
    elif role == 'agent':
        # Agent może widzieć wszystkie zgłoszenia z organizacji, do których należy
        if ticket.organization not in user_orgs:
            logger.warning(f"Access denied: Agent {user.username} tried to access ticket #{ticket.id} from org {ticket.organization.name}")
            return HttpResponseForbidden("Brak dostępu do tego zgłoszenia")
    
    comments = ticket.comments.all().order_by('created_at')
    attachments = ticket.attachments.all()
    
    # Wszyscy mogą komentować
    can_comment = True
    
    # Sprawdzanie uprawnień do dodawania załączników
    if role == 'client':
        can_attach = user == ticket.created_by
    else:
        can_attach = True  # Admin i agent mogą dodawać załączniki
    
    # Sprawdzanie uprawnień do edycji
    if role == 'admin':
        can_edit = True
    elif role == 'agent':
        # Agent może edytować tylko nieprzypisane zgłoszenia lub przypisane do niego
        can_edit = not ticket.assigned_to or ticket.assigned_to == user
    else:  # client
        can_edit = user == ticket.created_by
    
    # Sprawdzanie uprawnień do zamykania
    if role == 'admin':
        can_close = True
    elif role == 'agent':
        # Agent może zamykać tylko nieprzypisane zgłoszenia lub przypisane do niego
        can_close = not ticket.assigned_to or ticket.assigned_to == user
    else:  # client
        can_close = user == ticket.created_by
    
    # Tylko admin i przypisany agent mogą ponownie otwierać
    can_reopen = role == 'admin' or (role == 'agent' and ticket.assigned_to == user)
    
    # Możliwość przypisania do siebie (tylko dla agentów, gdy zgłoszenie nieprzypisane)
    can_assign_to_self = role == 'agent' and not ticket.assigned_to
    
    # Formularz komentarza
    if request.method == 'POST':
        if 'submit_comment' in request.POST and can_comment:
            comment_form = TicketCommentForm(request.POST)
            attachment_form = TicketAttachmentForm()
            
            if comment_form.is_valid():
                comment = comment_form.save(commit=False)
                comment.ticket = ticket
                comment.author = request.user
                comment.save()
                log_activity(request, 'ticket_commented', ticket, f"Dodano komentarz do zgłoszenia '{ticket.title}'")
                messages.success(request, 'Komentarz został dodany!')
                return redirect('ticket_detail', pk=ticket.pk)
        elif 'submit_attachment' in request.POST and can_attach:
            comment_form = TicketCommentForm()
            attachment_form = TicketAttachmentForm(request.POST, request.FILES)
            
            if attachment_form.is_valid():
                attachment = attachment_form.save(commit=False)
                attachment.ticket = ticket
                attachment.uploaded_by = request.user
                attachment.filename = os.path.basename(attachment.file.name)
                attachment.accepted_policy = attachment_form.cleaned_data['accepted_policy']
                attachment.save()
                log_activity(request, 'ticket_attachment_added', ticket=ticket, 
                            description=f"Added attachment: {attachment.filename}")
                messages.success(request, 'Załącznik został dodany!')
                return redirect('ticket_detail', pk=ticket.pk)
        else:
            # Nieautoryzowana próba dodania komentarza lub załącznika
            return HttpResponseForbidden("Brak uprawnień do wykonania tej akcji")
    else:
        comment_form = TicketCommentForm()
        attachment_form = TicketAttachmentForm()
    
    context = {
        'ticket': ticket,
        'comments': comments,
        'attachments': attachments,
        'comment_form': comment_form,
        'attachment_form': attachment_form,
        'can_comment': can_comment,
        'can_attach': can_attach,
        'can_edit': can_edit,
        'can_close': can_close,
        'can_reopen': can_reopen,
        'can_assign_to_self': can_assign_to_self,
    }
    
    return render(request, 'crm/tickets/ticket_detail.html', context)


@login_required
def ticket_create(request):
    """Widok tworzenia nowego zgłoszenia"""
    user = request.user
    
    if request.method == 'POST':
        # Use different form based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm(request.POST)
        else:
            form = ClientTicketForm(request.POST)
            
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = user
            
            # Set default priority for clients
            if user.profile.role == 'client':
                ticket.priority = 'medium'  # Default priority for client tickets
            
            # Get the organization for the current user or from form
            if 'organization' in request.POST and request.POST['organization'] and user.profile.role in ['admin', 'agent']:
                # Admin/agent can select organization
                org_id = request.POST.get('organization')
                try:
                    organization = Organization.objects.get(id=org_id)
                    
                    # Check if agent is part of the selected organization
                    if user.profile.role == 'agent' and organization not in user.profile.organizations.all():
                        messages.error(request, "Nie możesz utworzyć zgłoszenia w organizacji, do której nie jesteś przypisany.")
                        return redirect('ticket_create')
                    
                    ticket.organization = organization
                except Organization.DoesNotExist:
                    messages.error(request, "Wybrana organizacja nie istnieje.")
                    return redirect('ticket_create')
            else:
                # Regular users use their first organization
                user_orgs = user.profile.organizations.all()
                if user_orgs.exists():
                    ticket.organization = user_orgs.first()
                else:
                    messages.error(request, "Nie można utworzyć zgłoszenia: Brak organizacji przypisanej do Twojego konta.")
                    return redirect('dashboard')
                
            ticket.save()
            log_activity(request, 'ticket_created', ticket, f"Utworzono zgłoszenie: '{ticket.title}'")
            messages.success(request, 'Zgłoszenie zostało utworzone!')
            return redirect('ticket_detail', pk=ticket.pk)
    else:
        # Also use different form for GET requests based on user role
        if user.profile.role in ['admin', 'agent']:
            form = TicketForm()
        else:
            form = ClientTicketForm()
    
    # Dodanie pola wyboru organizacji dla admina i agenta
    organizations = []
    if user.profile.role == 'admin':
        # Admin sees all organizations
        organizations = Organization.objects.all()
    elif user.profile.role == 'agent':
        # Agent sees only organizations they belong to
        organizations = user.profile.organizations.all()
    
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
    elif role == 'agent':
        # Agent może edytować tylko nieprzypisane zgłoszenia lub przypisane do niego
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz edytować zgłoszenia przypisanego do innego agenta")
    
    if request.method == 'POST':
        # Inny formularz w zależności od roli
        if role == 'admin':
            form = ModeratorTicketForm(request.POST, instance=ticket)
        elif role == 'agent':
            form = ModeratorTicketForm(request.POST, instance=ticket)
            
            # Jeśli zgłoszenie nie jest przypisane, a agent je edytuje, przypisz do niego automatycznie
            if not ticket.assigned_to:
                old_form = form.save(commit=False)
                old_form.assigned_to = user
                form = ModeratorTicketForm(instance=old_form)
        else:
            # Klient używa ograniczonego formularza
            form = ClientTicketForm(request.POST, instance=ticket)
            
        if form.is_valid():
            old_status = ticket.status
            
            # Przypisanie zgłoszenia do agenta, jeśli nie jest przypisane
            updated_ticket = form.save(commit=False)
            if role == 'agent' and not ticket.assigned_to:
                updated_ticket.assigned_to = user
                messages.info(request, "Zgłoszenie zostało automatycznie przypisane do Ciebie.")
            
            updated_ticket.save()
            
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
        if role == 'admin' or role == 'agent':
            form = ModeratorTicketForm(instance=ticket)
        else:
            # Klient widzi ograniczony formularz
            form = ClientTicketForm(instance=ticket)
    
    context = {
        'form': form,
        'ticket': ticket,
    }
    
    return render(request, 'crm/tickets/ticket_form.html', context)


@login_required
def ticket_close(request, pk):
    """Widok zamykania zgłoszenia"""
    user = request.user
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdzenie uprawnień
    if role == 'client':
        if ticket.created_by != user:
            return HttpResponseForbidden("Nie możesz zamknąć tego zgłoszenia")
    elif role == 'agent':
        # Agent może zamykać tylko nieprzypisane zgłoszenia lub przypisane do niego
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz zamknąć zgłoszenia przypisanego do innego agenta")
    
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
    role = user.profile.role
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Tylko admin i przypisany agent mogą ponownie otworzyć zgłoszenie
    if role == 'admin':
        pass  # Admin może wszystko
    elif role == 'agent':
        if ticket.assigned_to and ticket.assigned_to != user:
            return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia przypisanego do innego agenta")
    else:
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
def ticket_assign_to_me(request, pk):
    """Widok przypisywania zgłoszenia do siebie (tylko dla agentów)"""
    user = request.user
    
    if user.profile.role != 'agent':
        return HttpResponseForbidden("Tylko agenci mogą przypisywać zgłoszenia do siebie")
    
    ticket = get_object_or_404(Ticket, pk=pk)
    
    # Sprawdź czy zgłoszenie jest już przypisane do kogoś innego
    if ticket.assigned_to and ticket.assigned_to != user:
        return HttpResponseForbidden("To zgłoszenie jest już przypisane do innego agenta")
    
    if request.method == 'POST':
        # Przypisz zgłoszenie do aktualnego użytkownika
        ticket.assigned_to = user
        ticket.save()
        
        log_activity(
            request,
            'ticket_updated',
            ticket,
            f"Przypisano zgłoszenie '{ticket.title}' do {user.username}"
        )
        
        messages.success(request, 'Zgłoszenie zostało przypisane do Ciebie!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_assign.html', {'ticket': ticket})
