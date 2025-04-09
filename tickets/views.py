from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from .models import Ticket, TicketAttachment, TicketHistory, CustomUser
from .forms import CustomUserRegistrationForm, TicketForm, TicketEditForm

def register(request):
    if request.method == 'POST':
        form = CustomUserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            # Optionally set as inactive until admin approval (here we set active immediately)
            user.is_active = True
            user.save()
            messages.success(request, "Rejestracja zakończona sukcesem. Możesz się teraz zalogować.")
            return redirect('login')
    else:
        form = CustomUserRegistrationForm()
    return render(request, 'tickets/register.html', {'form': form})

@login_required
def dashboard(request):
    # Staff sees all tickets; clients see only their own
    if request.user.is_staff:
        tickets = Ticket.objects.all()
    else:
        tickets = Ticket.objects.filter(created_by=request.user)
    # Split tickets by status
    open_tickets = tickets.filter(status__in=['open', 'in_progress', 'pending_closure'])
    closed_tickets = tickets.filter(status='closed')
    return render(request, 'tickets/dashboard.html', {
        'open_tickets': open_tickets,
        'closed_tickets': closed_tickets,
    })

@login_required
def ticket_detail(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    # Restrict access: clients see only their own tickets
    if not request.user.is_staff and ticket.created_by != request.user:
        messages.error(request, "Brak dostępu do tego zgłoszenia.")
        return redirect('dashboard')
    return render(request, 'tickets/ticket_detail.html', {'ticket': ticket})

@login_required
def ticket_create(request):
    if request.method == 'POST':
        form = TicketForm(request.POST, request.FILES)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.created_by = request.user
            ticket.save()
            # Save attachments if any
            for f in request.FILES.getlist('attachments'):
                TicketAttachment.objects.create(ticket=ticket, file=f)
            messages.success(request, "Zgłoszenie utworzone pomyślnie.")
            # Email notification for new ticket
            send_mail(
                'Nowe zgłoszenie',
                f'Zgłoszenie "{ticket.title}" zostało utworzone.',
                settings.DEFAULT_FROM_EMAIL,
                [ticket.created_by.email],
                fail_silently=True,
            )
            return redirect('dashboard')
    else:
        form = TicketForm()
    return render(request, 'tickets/ticket_create.html', {'form': form})

@login_required
def ticket_edit(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    # Only staff can edit tickets
    if not request.user.is_staff:
        messages.error(request, "Brak dostępu do edycji zgłoszenia.")
        return redirect('dashboard')
    if request.method == 'POST':
        form = TicketEditForm(request.POST, instance=ticket)
        if form.is_valid():
            old_ticket = Ticket.objects.get(id=ticket_id)
            form.save()
            # Record a history note
            change_note = f"Edycja zgłoszenia przez {request.user.username}. Zmiany: "
            if old_ticket.title != ticket.title:
                change_note += f"Tytuł: '{old_ticket.title}' -> '{ticket.title}'; "
            if old_ticket.problem_group != ticket.problem_group:
                change_note += f"Grupa problemu: '{old_ticket.problem_group}' -> '{ticket.problem_group}'; "
            if old_ticket.description != ticket.description:
                change_note += "Opis zmieniony; "
            if old_ticket.status != ticket.status:
                change_note += f"Status: '{old_ticket.status}' -> '{ticket.status}'; "
            if old_ticket.assigned_to != ticket.assigned_to:
                change_note += "Opiekun zmieniony; "
            TicketHistory.objects.create(ticket=ticket, changed_by=request.user, change_note=change_note)
            messages.success(request, "Zgłoszenie zaktualizowane.")
            # Send email notification for assignment change or status change
            if ticket.assigned_to:
                send_mail(
                    'Przypisano opiekuna do zgłoszenia',
                    f'Zgłoszenie "{ticket.title}" zostało przypisane do Ciebie.',
                    settings.DEFAULT_FROM_EMAIL,
                    [ticket.assigned_to.email],
                    fail_silently=True,
                )
            return redirect('ticket_detail', ticket_id=ticket.id)
    else:
        form = TicketEditForm(instance=ticket)
    return render(request, 'tickets/ticket_edit.html', {'form': form, 'ticket': ticket})

@login_required
def ticket_close(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    # Only the client who created the ticket can confirm closure
    if ticket.created_by != request.user:
        messages.error(request, "Nie masz uprawnień do zamknięcia tego zgłoszenia.")
        return redirect('dashboard')
    if request.method == 'POST':
        ticket.status = 'closed'
        ticket.closed_at = timezone.now()
        ticket.save()
        TicketHistory.objects.create(ticket=ticket, changed_by=request.user, change_note="Zgłoszenie zamknięte przez klienta.")
        messages.success(request, "Zgłoszenie zostało zamknięte.")
        send_mail(
            'Zgłoszenie zamknięte',
            f'Zgłoszenie "{ticket.title}" zostało zamknięte.',
            settings.DEFAULT_FROM_EMAIL,
            [ticket.created_by.email],
            fail_silently=True,
        )
        return redirect('ticket_detail', ticket_id=ticket.id)
    return render(request, 'tickets/ticket_close_confirm.html', {'ticket': ticket})
