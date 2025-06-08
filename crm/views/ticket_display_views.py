from django.shortcuts import render
from django.http import JsonResponse
from django.template.loader import render_to_string
from ..models import Ticket
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

@login_required
def ticket_display_view(request):
    """Widok wyświetlający listę zgłoszeń dla roli viewer"""
    tickets = Ticket.objects.all().order_by('-created_at')
    return render(request, 'crm/ticket_display.html', {
        'tickets': tickets,
    })

@login_required
def get_tickets_update(request):
    """Endpoint do odświeżania listy zgłoszeń dla zalogowanych użytkowników"""
    logger.info("Otrzymano żądanie aktualizacji listy zgłoszeń")
    try:
        tickets = Ticket.objects.all().order_by('-created_at')
        logger.info(f"Znaleziono {tickets.count()} zgłoszeń")
        
        html = render_to_string('crm/ticket_list_partial.html', {
            'tickets': tickets,
            'user': request.user
        })
        
        response_data = {
            'html': html,
            'ticket_count': tickets.count()
        }
        logger.info("Wysyłanie odpowiedzi z aktualizacją")
        return JsonResponse(response_data)
    except Exception as e:
        logger.error(f"Błąd podczas aktualizacji listy: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500) 