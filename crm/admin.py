from django.contrib import admin
from .models import Contact, Organization, Deal


class ContactAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'company', 'status', 'created_at')
    list_filter = ('status', 'lead_source', 'created_at')
    search_fields = ('first_name', 'last_name', 'email', 'company')
    date_hierarchy = 'created_at'


class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name', 'website')
    date_hierarchy = 'created_at'


class DealAdmin(admin.ModelAdmin):
    list_display = ('title', 'contact', 'organization', 'value', 'stage', 'expected_close_date')
    list_filter = ('stage', 'expected_close_date')
    search_fields = ('title', 'contact__first_name', 'contact__last_name', 'organization__name')
    date_hierarchy = 'created_at'


admin.site.register(Contact, ContactAdmin)
admin.site.register(Organization, OrganizationAdmin)
admin.site.register(Deal, DealAdmin)
