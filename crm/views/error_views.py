from django.shortcuts import redirect, render
from django.contrib import messages
from .helpers import log_error

def ticket_not_found(request, ticket_id):
    """Handle ticket not found errors by redirecting with message"""
    messages.error(request, f"Zgłoszenie o ID #{ticket_id} nie istnieje.")
    # Log the error
    log_error(request, '404_error', description=f"Próba dostępu do nieistniejącego zgłoszenia #{ticket_id}")
    return redirect('dashboard')

def handle_custom_404(request, exception=None):
    """Generic 404 error handler with logging"""
    # Log the 404 error
    log_error(request, '404_error')
    # For better UX, render the error page directly instead of redirecting
    return render(request, 'crm/errors/404.html', status=404)

def handle_custom_403(request, exception=None):
    """Generic 403 error handler with logging"""
    # Log the 403 error
    log_error(request, '403_error')
    return render(request, 'crm/errors/403.html', status=403)

# Add a function to test the 404 page even when DEBUG=True
def test_404_page(request):
    """Force display of the 404 page for testing"""
    return render(request, 'crm/errors/404.html', status=404)

# Add a function to test the 403 page
def test_403_page(request):
    """Force display of the 403 page for testing"""
    return render(request, 'crm/errors/403.html', status=403)
