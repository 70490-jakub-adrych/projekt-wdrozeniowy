from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from .models import TwoFactorAuth, TrustedDevice

class TwoFactorAuthInline(admin.StackedInline):
    model = TwoFactorAuth
    can_delete = False
    verbose_name_plural = 'Two-Factor Authentication'
    readonly_fields = ['ga_enabled_on', 'ga_last_authenticated', 'regenerate_recovery_code']
    fields = ['ga_enabled', 'ga_enabled_on', 'ga_last_authenticated', 'regenerate_recovery_code']
    
    def regenerate_recovery_code(self, obj):
        if obj.pk and obj.ga_enabled:
            if obj.can_regenerate_recovery_code():
                return format_html(
                    '<a href="{}?user_id={}" class="button">Regenerate Recovery Code</a>',
                    '/two-factor/regenerate-recovery-code/',
                    obj.user.id
                )
            else:
                return "Recovery code was recently generated. Wait 24h to regenerate."
        return "N/A"
    
    regenerate_recovery_code.short_description = 'Recovery Code'

class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('user', 'created_at', 'expires_at')
    search_fields = ('user__username', 'ip_address', 'device_identifier')
    readonly_fields = ('device_identifier', 'created_at', 'last_used')
    
    def is_valid(self, obj):
        return obj.is_valid()
    is_valid.boolean = True
    is_valid.short_description = 'Valid'

# Unregister the default UserAdmin
admin.site.unregister(User)

# Register our custom UserAdmin
class UserAdmin(BaseUserAdmin):
    inlines = (TwoFactorAuthInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_2fa_enabled')
    actions = ['disable_2fa']
    
    def is_2fa_enabled(self, obj):
        try:
            return obj.two_factor.ga_enabled
        except TwoFactorAuth.DoesNotExist:
            return False
    
    is_2fa_enabled.boolean = True
    is_2fa_enabled.short_description = '2FA Enabled'
    
    def disable_2fa(self, request, queryset):
        for user in queryset:
            try:
                two_factor = TwoFactorAuth.objects.get(user=user)
                two_factor.ga_enabled = False
                two_factor.ga_secret = None
                two_factor.save()
                
                # Delete trusted devices
                TrustedDevice.objects.filter(user=user).delete()
            except TwoFactorAuth.DoesNotExist:
                pass
        
        self.message_user(request, f"2FA disabled for {queryset.count()} user(s)")
    disable_2fa.short_description = "Disable 2FA for selected users"

# Register your models with admin site
admin.site.register(User, UserAdmin)
admin.site.register(TrustedDevice, TrustedDeviceAdmin)
