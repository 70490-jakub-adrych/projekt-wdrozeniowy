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
