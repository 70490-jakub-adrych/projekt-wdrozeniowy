# Add this to your views.py or create a new file like spa_views.py

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import TemplateView

class SPAMixin:
    """Mixin to handle both traditional and HTMX/SPA requests"""
    
    def get_template_names(self):
        """Return different templates based on request type"""
        if self.request.headers.get('HX-Request'):
            # HTMX request - return content-only template
            return [self.spa_template_name] if hasattr(self, 'spa_template_name') else [self.template_name.replace('.html', '_content.html')]
        else:
            # Traditional request - return full page template
            return [self.template_name]
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_htmx'] = bool(self.request.headers.get('HX-Request'))
        return context

# Example of how to modify your existing views
class DashboardView(SPAMixin, TemplateView):
    template_name = 'crm/dashboard.html'
    spa_template_name = 'crm/dashboard_content.html'  # Optional: specify different content template
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your dashboard data here
        return context

class TicketListView(SPAMixin, TemplateView):
    template_name = 'crm/ticket_list.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add your ticket data here
        return context

# Alternative approach using a decorator
from functools import wraps

def spa_response(spa_template=None):
    """Decorator to handle SPA responses automatically"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            response = view_func(request, *args, **kwargs)
            
            # If it's an HTMX request and we got a rendered template response
            if hasattr(response, 'template_name') and request.headers.get('HX-Request'):
                if spa_template:
                    response.template_name = spa_template
                elif isinstance(response.template_name, str):
                    # Auto-generate content template name
                    response.template_name = response.template_name.replace('.html', '_content.html')
                elif isinstance(response.template_name, list):
                    response.template_name = [t.replace('.html', '_content.html') for t in response.template_name]
            
            return response
        return wrapper
    return decorator

# Example using the decorator
@spa_response('crm/dashboard_content.html')
def dashboard_view(request):
    context = {
        'tickets': get_user_tickets(request.user),
        'stats': get_dashboard_stats(request.user),
    }
    return render(request, 'crm/dashboard.html', context)
