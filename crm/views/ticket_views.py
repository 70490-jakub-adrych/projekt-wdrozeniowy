from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponseForbidden
import os

from ..models import Organization, Ticket, TicketComment, TicketAttachment
from ..forms import (
    TicketForm, ModeratorTicketForm, TicketCommentForm, TicketAttachmentForm
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
    sort_by = request.GET.get('sort_by', '-created_at')
    
    # Określenie widocznych zgłoszeń na podstawie roli
    if role == 'admin':
        tickets = Ticket.objects.all()
    elif role == 'agent':
        # Agent sees tickets from organizations they belong to
        user_orgs = user.profile.organizations.all()
        tickets = Ticket.objects.filter(organization__in=user_orgs)
    else:  # client
        # Client sees tickets from their organizations
        user_orgs = user.profile.organizations.all()
        tickets = Ticket.objects.filter(Q(organization__in=user_orgs) | Q(created_by=user))
    
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
        user_orgs = user.profile.organizations.all()
        if ticket.organization not in user_orgs and user != ticket.created_by:
            return HttpResponseForbidden("Brak dostępu do tego zgłoszenia")
    
    comments = ticket.comments.all().order_by('created_at')
    attachments = ticket.attachments.all()
    
    # Sprawdzanie uprawnień do dodawania komentarzy i załączników
    can_comment = role in ['admin', 'agent'] or user == ticket.created_by
    can_attach = role in ['admin', 'agent'] or user == ticket.created_by
    
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
                attachment.save()
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
        'can_edit': role in ['admin', 'agent'] or user == ticket.created_by,
        'can_close': role in ['admin', 'agent'] or user == ticket.created_by,
        'can_reopen': role in ['admin', 'agent'],
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
            
            # Get the organization for the current user or from form
            if 'organization' in request.POST and request.POST['organization'] and user.profile.role in ['admin', 'agent']:
                # Admin/agent can select organization
                org_id = request.POST.get('organization')
                try:
                    ticket.organization = Organization.objects.get(id=org_id)
                except Organization.DoesNotExist:
                    messages.error(request, "Selected organization does not exist.")
                    return redirect('ticket_create')
            else:
                # Regular users use their first organization
                user_orgs = user.profile.organizations.all()
                if user_orgs.exists():
                    ticket.organization = user_orgs.first()
                else:
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
    if role == 'client' and ticket.created_by != user:
        return HttpResponseForbidden("Nie możesz edytować tego zgłoszenia")
    elif role == 'agent' and ticket.assigned_to and ticket.assigned_to != user:
        # Agent może edytować tylko przypisane do niego zgłoszenia lub nieprzypisane
        if ticket.assigned_to is not None:
            return HttpResponseForbidden("Nie możesz edytować zgłoszenia przypisanego do innego agenta")
    
    if request.method == 'POST':
        # Inny formularz w zależności od roli
        if role in ['admin', 'agent']:
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
        if role in ['admin', 'agent']:
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
    
    # Tylko admin i agent mogą ponownie otwierać zgłoszenia
    if user.profile.role not in ['admin', 'agent']:
        return HttpResponseForbidden("Nie możesz ponownie otworzyć zgłoszenia")
    
    if request.method == 'POST':
        ticket.status = 'new'
        ticket.closed_at = None
        ticket.save()
        
        log_activity(request, 'ticket_reopened', ticket, f"Ponownie otwarto zgłoszenie '{ticket.title}'")
        messages.success(request, 'Zgłoszenie zostało ponownie otwarte!')
        return redirect('ticket_detail', pk=ticket.pk)
    
    return render(request, 'crm/tickets/ticket_confirm_reopen.html', {'ticket': ticket})
