from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _


class CrmAdminSite(AdminSite):
    site_title = _('BetulaIT Helpdesk Admin')
    site_header = _('BetulaIT Helpdesk Administration')
    index_title = _('Panel Administracyjny')
    
    def each_context(self, request):
        context = super().each_context(request)
        context['extra_css'] = [
            'admin/css/custom_admin.css',
        ]
        return context

    def get_app_list(self, request):
        # Get the default app list
        app_list = super().get_app_list(request)
        # Sort the app list by name
        app_list.sort(key=lambda x: x['name'])
        return app_list
