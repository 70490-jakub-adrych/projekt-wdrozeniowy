# Add this to your middleware.py or create a new file
from django.utils.deprecation import MiddlewareMixin

class SPAMiddleware(MiddlewareMixin):
    """
    Middleware to detect SPA requests and modify context accordingly.
    This is optional but helps with better SPA experience.
    """
    
    def process_request(self, request):
        # Detect if this is an SPA/AJAX request
        request.is_spa_request = (
            request.headers.get('X-SPA-Request') == 'true' or
            request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        )
        return None

# Alternative: Simple decorator approach
def spa_friendly(view_func):
    """
    Decorator to make views SPA-friendly.
    You can apply this to views that need special SPA handling.
    """
    def wrapper(request, *args, **kwargs):
        response = view_func(request, *args, **kwargs)
        
        # Add SPA-friendly headers
        if hasattr(request, 'is_spa_request') and request.is_spa_request:
            if hasattr(response, 'headers'):
                response.headers['X-SPA-Response'] = 'true'
        
        return response
    return wrapper

# Example usage in your views.py:
# from .spa_utils import spa_friendly
# 
# @spa_friendly
# def dashboard_view(request):
#     # Your existing view code
#     return render(request, 'crm/dashboard.html', context)
