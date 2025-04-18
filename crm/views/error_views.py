from django.shortcuts import redirect
from django.contrib import messages

def ticket_not_found(request, ticket_id):
    """Handle ticket not found errors by redirecting with message"""
    messages.error(request, f"Zgłoszenie o ID #{ticket_id} nie istnieje.")
    return redirect('dashboard')

def handle_custom_404(request, exception=None):
    """Generic 404 error handler"""
    messages.error(request, "Strona, której szukasz, nie istnieje.")
    return redirect('dashboard')
