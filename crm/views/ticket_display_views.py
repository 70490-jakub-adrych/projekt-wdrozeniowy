from django.shortcuts import render
from ..models import Ticket
from ..decorators import viewer_required

@viewer_required
def ticket_display_view(request):
    """Widok wyświetlający listę zgłoszeń dla roli viewer"""
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'crm/ticket_display.html', {
        'tickets': tickets,
    }) 