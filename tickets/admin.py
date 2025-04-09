from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Ticket, CustomUser, TicketAttachment, TicketHistory

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'status', 'created_at')

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'company_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('company_name', 'phone_number')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('email', 'company_name', 'phone_number')}),
    )

admin.site.register(TicketAttachment)
admin.site.register(TicketHistory)