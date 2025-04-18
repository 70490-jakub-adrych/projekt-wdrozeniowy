from django.shortcuts import redirect, render
from django.contrib import messages
from .helpers import log_activity, log_error

def ticket_not_found(request, ticket_id):
    """Handle ticket not found errors"""
    log_error(request, '404_error', description=f"Attempted to access non-existent ticket: {ticket_id}")
    return render(request, 'crm/errors/404.html', {
        'item_type': 'zgłoszenia',
        'item_id': ticket_id,
        'message': f"Nie znaleziono zgłoszenia o ID: {ticket_id}"
    }, status=404)

def handle_custom_404(request, exception=None):
    """Generic 404 handler"""
    log_error(request, '404_error')
    return render(request, 'crm/errors/404.html', status=404)

def handle_custom_403(request, exception=None):
    """Generic 403 error handler with logging"""
    # Log the 403 error
    log_error(request, '403_error')
    return render(request, 'crm/errors/403.html', status=403)

def log_not_found(request, log_id):
    """Handle log not found errors"""
    log_error(request, '404_error', description=f"Attempted to access non-existent log: {log_id}")
    return render(request, 'crm/errors/404.html', {
        'item_type': 'logu',
        'item_id': log_id,
        'message': f"Nie ma logu o takim ID: {log_id}"
    }, status=404)

def forbidden_access(request, resource_type=None, resource_id=None):
    """Handle forbidden access to resources"""
    description = f"Attempted to access restricted {resource_type or 'resource'}"
    if resource_id:
        description += f" with ID: {resource_id}"
    
    log_error(request, '403_error', description=description)
    
    context = {
        'resource_type': resource_type,
        'resource_id': resource_id,
        'message': f"Brak dostępu do tego {resource_type or 'zasobu'}"
    }
    
    return render(request, 'crm/errors/403.html', context, status=403)

def attachment_not_found(request, attachment_id):
    """Handle attachment not found errors"""
    log_error(request, '404_error', description=f"Attempted to access non-existent attachment: {attachment_id}")
    return render(request, 'crm/errors/404.html', {
        'item_type': 'załącznika',
        'item_id': attachment_id,
        'message': f"Nie znaleziono załącznika o ID: {attachment_id}"
    }, status=404)

def organization_not_found(request, organization_id):
    """Handle organization not found errors"""
    log_error(request, '404_error', description=f"Attempted to access non-existent organization: {organization_id}")
    return render(request, 'crm/errors/404.html', {
        'item_type': 'organizacji',
        'item_id': organization_id,
        'message': f"Nie znaleziono organizacji o ID: {organization_id}"
    }, status=404)

# Add a function to test the 404 page even when DEBUG=True
def test_404_page(request):
    """Force display of the 404 page for testing"""
    return render(request, 'crm/errors/404.html', status=404)

# Add a function to test the 403 page
def test_403_page(request):
    """Force display of the 403 page for testing"""
    return render(request, 'crm/errors/403.html', status=403)
