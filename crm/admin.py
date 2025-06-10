from django.contrib import admin
from django.contrib.auth.models import User, Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.admin import GroupAdmin as BaseGroupAdmin
from django.contrib import messages  # Add this import
from django import forms
from .models import (
    UserProfile, Organization, Ticket, TicketComment,
    TicketAttachment, ActivityLog, GroupSettings, 
    ViewPermission, GroupViewPermission, UserViewPermission,
    WorkHours, TicketStatistics, AgentWorkLog  # Add the new models
)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    filter_horizontal = ('organizations',)
    
    def get_readonly_fields(self, request, obj=None):
        """Make role field read-only since it's synchronized with groups"""
        readonly_fields = list(self.readonly_fields)
        readonly_fields.append('role')
        return readonly_fields


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def save_model(self, request, obj, form, change):
        """Override save_model to enforce one group per user"""
        # Save the user instance first
        super().save_model(request, obj, form, change)
        
        # Check if the user belongs to multiple groups
        groups = obj.groups.all()
        if groups.count() > 1:
            # Remove all groups except the latest one
            latest_group = groups.last()
            obj.groups.clear()
            obj.groups.add(latest_group)
            messages.warning(request, 
                f"Użytkownik może należeć tylko do jednej grupy. Przypisano tylko do grupy {latest_group.name}.")
    
    def save_related(self, request, form, formsets, change):
        """Override save_related to enforce one organization based on group settings"""
        # Call the original save_related to save the inline forms
        super().save_related(request, form, formsets, change)
        
        # Get the user instance
        user = form.instance
        
        # Check if the user has a profile and belongs to a group
        if hasattr(user, 'profile') and user.groups.exists():
            # Get the user's group
            group = user.groups.first()
            
            # Check if the group has settings
            try:
                group_settings = group.settings
                allow_multiple = group_settings.allow_multiple_organizations
            except GroupSettings.DoesNotExist:
                # If settings don't exist, create them with default values
                allow_multiple = group.name in ['Admin', 'Superagent', 'Agent']
                group_settings = GroupSettings.objects.create(
                    group=group, 
                    allow_multiple_organizations=allow_multiple
                )
            
            # If multiple organizations are not allowed for this group
            if not allow_multiple:
                orgs = user.profile.organizations.all()
                if orgs.count() > 1:
                    # Keep only the first organization
                    first_org = orgs.first()
                    user.profile.organizations.clear()
                    user.profile.organizations.add(first_org)
                    messages.warning(request, 
                        f"Użytkownicy w grupie {group.name} mogą być przypisani tylko do jednej organizacji. Przypisano tylko do {first_org.name}.")


class GroupSettingsInline(admin.StackedInline):
    model = GroupSettings
    can_delete = False
    verbose_name_plural = 'Ustawienia'
    fieldsets = (
        (None, {
            'fields': ('allow_multiple_organizations', 'show_statistics')
        }),
        ('Ustawienia dostępu do załączników', {
            'fields': ('attachments_access_level',),
            'description': 'Określ poziom dostępu do załączników dla tej grupy użytkowników.'
        }),
    )

class GroupViewPermissionInline(admin.TabularInline):
    model = GroupViewPermission
    extra = 1

# Custom Group admin with role field
class GroupAdminForm(forms.ModelForm):
    ROLE_CHOICES = [
        ('admin', 'Administrator'),
        ('superagent', 'Super Agent'),
        ('agent', 'Agent'),
        ('client', 'Klient'),
        ('viewer', 'Przeglądający'),
    ]
    
    role = forms.ChoiceField(
        label="Rola użytkowników",
        choices=ROLE_CHOICES,
        required=True,
        help_text="Rola przypisywana użytkownikom w tej grupie."
    )
    
    class Meta:
        model = Group
        fields = '__all__'  # Include all fields, including permissions
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial role based on group name
        if self.instance.pk:
            if self.instance.name == 'Admin':
                self.fields['role'].initial = 'admin'
            elif self.instance.name == 'Superagent':
                self.fields['role'].initial = 'superagent'
            elif self.instance.name == 'Agent':
                self.fields['role'].initial = 'agent'
            elif self.instance.name == 'Klient':
                self.fields['role'].initial = 'client'
            elif self.instance.name == 'Viewer':
                self.fields['role'].initial = 'viewer'

class GroupAdmin(BaseGroupAdmin):
    form = GroupAdminForm
    inlines = [GroupSettingsInline, GroupViewPermissionInline]
    
    # Preserve the filter_horizontal for permissions from BaseGroupAdmin
    filter_horizontal = ('permissions',)
    
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        role = form.cleaned_data.get('role')
        
        # Update the role display name to match standard conventions
        standard_names = {
            'admin': 'Admin', 
            'superagent': 'Superagent',
            'agent': 'Agent', 
            'client': 'Klient',
            'viewer': 'Viewer'
        }
        
        if role in standard_names:
            target_name = standard_names[role]
            # Only update if the name is different and the target name doesn't exist
            if obj.name != target_name:
                # Check if target name already exists (excluding current object)
                existing_group = Group.objects.filter(name=target_name).exclude(pk=obj.pk).first()
                if not existing_group:
                    obj.name = target_name
                    obj.save(update_fields=['name'])
                else:
                    messages.warning(request, f'Grupa o nazwie "{target_name}" już istnieje. Nazwa nie została zmieniona.')

# Re-register User and Group with custom admins
admin.site.unregister(User)
admin.site.register(User, UserAdmin)

admin.site.unregister(Group)
admin.site.register(Group, GroupAdmin)


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
    
    def has_delete_permission(self, request, obj=None):
        return False  # Prevent deletion of logs from admin panel


@admin.register(ViewPermission)
class ViewPermissionAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_name_display', 'description')
    search_fields = ('name', 'description')


@admin.register(UserViewPermission)
class UserViewPermissionAdmin(admin.ModelAdmin):
    list_display = ('user', 'view', 'is_granted')
    list_filter = ('user', 'view', 'is_granted')
    search_fields = ('user__username', 'view__name')


@admin.register(WorkHours)
class WorkHoursAdmin(admin.ModelAdmin):
    list_display = ('get_day_of_week_display', 'start_time', 'end_time', 'is_working_day')
    list_filter = ('day_of_week', 'is_working_day')


@admin.register(TicketStatistics)
class TicketStatisticsAdmin(admin.ModelAdmin):
    list_display = ('period_type', 'period_start', 'period_end', 'organization', 'agent', 
                   'tickets_opened', 'tickets_closed', 'tickets_resolved', 'created_at')
    list_filter = ('period_type', 'organization', 'agent')
    search_fields = ('organization__name',)
    date_hierarchy = 'period_start'


@admin.register(AgentWorkLog)
class AgentWorkLogAdmin(admin.ModelAdmin):
    list_display = ('agent', 'ticket', 'start_time', 'end_time', 'work_time_minutes')
    list_filter = ('agent', 'start_time')
    search_fields = ('agent__username', 'ticket__title', 'notes')
    date_hierarchy = 'start_time'

    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of the admin user"""
        if obj is not None and obj.username == 'admin':
            return False
        return super().has_delete_permission(request, obj)
