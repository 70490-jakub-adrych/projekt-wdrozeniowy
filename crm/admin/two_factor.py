from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from ..models import TwoFactorAuth, TrustedDevice  # Update imports to use relative path
from ..utils.two_factor import get_recovery_url

class TwoFactorAuthInline(admin.StackedInline):
    model = TwoFactorAuth
    can_delete = False
    verbose_name_plural = 'Uwierzytelnianie dwuskładnikowe'
    readonly_fields = ['ga_enabled_on', 'ga_last_authenticated', 'regenerate_recovery_code']
    fields = ['ga_enabled', 'ga_enabled_on', 'ga_last_authenticated', 'regenerate_recovery_code']
    
    def regenerate_recovery_code(self, obj):
        if obj.pk and obj.ga_enabled:
            if obj.can_regenerate_recovery_code():
                return format_html(
                    '<a href="{}" class="button">Wygeneruj nowy kod odzyskiwania</a>',
                    get_recovery_url(obj.user.id)
                )
            else:
                return "Kod odzyskiwania został niedawno wygenerowany. Poczekaj 24h."
        return "Niedostępne"
    
    regenerate_recovery_code.short_description = 'Kod odzyskiwania'

class TrustedDeviceAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip_address', 'created_at', 'expires_at', 'is_valid')
    list_filter = ('user', 'created_at')
    search_fields = ('user__username', 'ip_address', 'device_identifier')
    readonly_fields = ('device_identifier',)
    
    def is_valid(self, obj):
        return obj.is_valid()
    
    is_valid.boolean = True
    is_valid.short_description = 'Ważne?'

# Register the trusted devices model
admin.site.register(TrustedDevice, TrustedDeviceAdmin)

# Extend the User admin 
class UserTwoFactorAdmin(BaseUserAdmin):
    inlines = [TwoFactorAuthInline]
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'has_2fa')
    actions = ['disable_2fa']
    
    def has_2fa(self, obj):
        try:
            return obj.two_factor.ga_enabled
        except TwoFactorAuth.DoesNotExist:
            return False
    
    has_2fa.boolean = True
    has_2fa.short_description = '2FA'
    
    def disable_2fa(self, request, queryset):
        count = 0
        for user in queryset:
            try:
                two_factor = TwoFactorAuth.objects.get(user=user)
                if two_factor.ga_enabled:
                    two_factor.ga_enabled = False
                    two_factor.ga_secret = None
                    two_factor.save()
                    
                    # Delete trusted devices
                    TrustedDevice.objects.filter(user=user).delete()
                    count += 1
            except TwoFactorAuth.DoesNotExist:
                continue
        
        self.message_user(request, f"Wyłączono uwierzytelnianie dwuskładnikowe dla {count} użytkowników.")
    
    disable_2fa.short_description = "Wyłącz uwierzytelnianie dwuskładnikowe"

# We'll use this class in the main admin.py file
