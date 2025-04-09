from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    UserProfile, Organization, Ticket, TicketComment,
    TicketAttachment, ActivityLog
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)


# Ponowna rejestracja modelu User z nowym adminem
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 0


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name', 'website')
    date_hierarchy = 'created_at'


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('title', 'organization', 'status', 'priority', 'category', 'created_by', 'assigned_to', 'created_at')
    list_filter = ('status', 'priority', 'category', 'organization')
    search_fields = ('title', 'description', 'created_by__username', 'assigned_to__username')
    date_hierarchy = 'created_at'
    inlines = [TicketCommentInline, TicketAttachmentInline]


@admin.register(TicketComment)
class TicketCommentAdmin(admin.ModelAdmin):
    list_display = ('ticket', 'author', 'created_at')
    list_filter = ('ticket__status', 'author')
    search_fields = ('content', 'ticket__title', 'author__username')
    date_hierarchy = 'created_at'


@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('filename', 'ticket', 'uploaded_by', 'uploaded_at')
    list_filter = ('ticket__status', 'uploaded_by')
    search_fields = ('filename', 'ticket__title', 'uploaded_by__username')
    date_hierarchy = 'uploaded_at'


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('action_type', 'user', 'ticket', 'ip_address', 'created_at')
    list_filter = ('action_type', 'user')
    search_fields = ('description', 'user__username', 'ip_address')
    date_hierarchy = 'created_at'
    readonly_fields = ('user', 'action_type', 'ticket', 'description', 'ip_address', 'created_at')
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
