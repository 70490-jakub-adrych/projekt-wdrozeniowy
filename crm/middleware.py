from django.shortcuts import redirect
from django.urls import reverse

class ViewerRestrictMiddleware:
    """
    Blokuje użytkownikom z rolą 'viewer' dostęp do wszystkich stron poza ticket_display i logout.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'profile'):
            if request.user.profile.role == 'viewer':
                allowed_urls = [reverse('ticket_display'), reverse('logout')]
                if request.path not in allowed_urls:
                    return redirect('ticket_display')
        return self.get_response(request) 