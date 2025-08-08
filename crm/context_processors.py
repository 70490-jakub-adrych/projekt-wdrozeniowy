from .models import GroupViewPermission, UserViewPermission, ViewPermission
import re

def view_permissions(request):
    """
    Context processor that adds user view permissions to the template context
    """
    if not request.user.is_authenticated:
        return {'user_view_permissions': {}}
    
    # Start with a default set of denied permissions for all views
    permissions = {view[0]: False for view in ViewPermission.VIEW_CHOICES}
    
    # Get user's groups and their permissions
    if request.user.groups.exists():
        user_groups = request.user.groups.all()
        # Get all view permissions from user's groups
        group_permissions = GroupViewPermission.objects.filter(group__in=user_groups)
        
        for permission in group_permissions:
            permissions[permission.view.name] = True
    
    # Override with specific user permissions if any
    user_permissions = UserViewPermission.objects.filter(user=request.user)
    
    for permission in user_permissions:
        permissions[permission.view.name] = permission.is_granted
    
    # Special case for superusers - they get all permissions
    if request.user.is_superuser:
        for key in permissions:
            permissions[key] = True
    
    # Check if user's group has the statistics permission
    try:
        group = request.user.groups.first()
        if hasattr(group, 'settings') and group.settings.show_statistics:
            permissions['statistics'] = True
    except:
        # If group settings don't exist, default to no statistics access
        permissions['statistics'] = False
    
    return {'user_view_permissions': permissions}


def device_context(request):
    """
    Add device information to template context with comprehensive mobile detection
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Comprehensive mobile device detection patterns
    # These patterns are ordered by specificity - more specific patterns first
    
    # Desktop patterns (check first to exclude false positives)
    desktop_patterns = [
        r'Windows NT.*WOW64',      # Windows 64-bit
        r'Windows NT.*Win64',      # Windows 64-bit
        r'Macintosh.*Intel',       # Intel Mac
        r'X11.*Linux.*x86_64',     # Linux 64-bit
        r'X11.*Linux.*i686',       # Linux 32-bit
    ]
    
    # Tablet specific patterns (check before mobile as tablets may contain "Mobile")
    tablet_patterns = [
        r'iPad',                           # iPad
        r'Android(?!.*Mobile).*Tablet',    # Android tablets explicitly
        r'Android.*SM-T\d+',              # Samsung Galaxy Tab series (SM-T...)
        r'Android.*SM-P\d+',              # Samsung Galaxy Note Tab series (SM-P...)
        r'Kindle',                         # Kindle tablets
        r'Silk',                          # Amazon Silk browser
        r'PlayBook',                      # BlackBerry PlayBook
        r'Windows.*Touch.*Tablet',        # Windows tablets
        # Large screen Android devices that are likely tablets (exclude phones and Opera Mini)
        r'Android(?!.*Mobile)(?!.*Opera Mini).*; (?!SM-)',  # Android tablets (non-phone form factor, excluding Opera Mini)
    ]
    
    # Mobile device patterns - comprehensive list for all major browsers
    mobile_patterns = [
        # iPhone/iOS devices
        r'iPhone',
        r'iPod',
        
        # Android mobile devices (must contain "Mobile")
        r'Android.*Mobile',
        r'Android.*SM-[AEGJN]',    # Samsung Galaxy phones (A, E, G, J, N series)
        r'Android.*GT-[IPN]',      # Samsung Galaxy phones (older series)
        r'Android.*SAMSUNG-SM-',   # Samsung phones
        
        # Mobile browsers specifically
        r'Mobile.*Safari',         # Mobile Safari
        r'Mobile.*Chrome',         # Chrome Mobile
        r'Mobile.*Firefox',        # Firefox Mobile
        r'Mobile.*Opera',          # Opera Mobile
        r'Mobile.*Edge',           # Edge Mobile
        r'Mobile.*SamsungBrowser', # Samsung Internet
        
        # Other mobile indicators
        r'Mobile(?!.*Tablet)',     # Generic mobile (not tablet)
        r'Phone',                  # Generic phone indicator
        r'BlackBerry',             # BlackBerry devices
        r'BB10',                   # BlackBerry 10
        r'Windows Phone',          # Windows Phone
        r'Windows.*Mobile',        # Windows Mobile
        r'IEMobile',              # Internet Explorer Mobile
        r'Opera Mini',            # Opera Mini (always mobile)
        r'Opera Mobi',            # Opera Mobile
        r'webOS',                 # webOS devices
        r'Palm',                  # Palm devices
        r'Symbian',               # Symbian OS
        
        # Additional mobile browser patterns
        r'CriOS',                 # Chrome on iOS
        r'FxiOS',                 # Firefox on iOS
        r'OPiOS',                 # Opera on iOS
        r'EdgiOS',                # Edge on iOS
        r'YaBrowser.*Mobile',     # Yandex Mobile
        r'UCBrowser.*Mobile',     # UC Browser Mobile
        r'SamsungBrowser.*Mobile', # Samsung Internet Mobile
        
        # Feature phones and older devices
        r'MIDP',                  # Mobile Information Device Profile
        r'WML',                   # Wireless Markup Language
        r'NetFront',              # NetFront browser
        r'UP\.Browser',           # UP.Browser
        r'UP\.Link',              # UP.Link
        r'Mmp',                   # Mobile Multimedia Platform
        r'PocketPC',              # Pocket PC
        r'Smartphone',            # Generic smartphone
        r'Cellphone',             # Generic cellphone
    ]
    
    # Check for desktop first (most restrictive)
    is_desktop_explicit = bool(re.search('|'.join(desktop_patterns), user_agent, re.IGNORECASE))
    
    # If explicitly desktop, skip mobile/tablet detection
    if is_desktop_explicit:
        is_mobile = False
        is_tablet = False
    else:
        # Check for tablet
        is_tablet = bool(re.search('|'.join(tablet_patterns), user_agent, re.IGNORECASE))
        
        # Check for mobile (only if not tablet)
        if not is_tablet:
            is_mobile = bool(re.search('|'.join(mobile_patterns), user_agent, re.IGNORECASE))
        else:
            is_mobile = False
    
    # Determine device type
    if is_mobile:
        device_type = 'mobile'
    elif is_tablet:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    return {
        'is_mobile_device': is_mobile,
        'is_tablet_device': is_tablet,
        'is_desktop_device': not (is_mobile or is_tablet),
        'device_type': device_type,
        'user_agent': user_agent,
    }


def impersonation_context(request):
    """
    Context processor that adds impersonation status to templates
    """
    if not request.user.is_authenticated:
        return {'effective_user': None}
    
    # For non-admin users, effective_user is just the regular user
    if request.user.profile.role != 'admin':
        return {'effective_user': request.user}
    
    impersonated_user_id = request.session.get('impersonated_user_id')
    
    if impersonated_user_id:
        try:
            from .models import User, Organization
            impersonated_user = User.objects.get(id=impersonated_user_id)
            
            # Get simulated organizations
            impersonated_org_ids = request.session.get('impersonated_organizations', [])
            simulated_organizations = []
            if impersonated_org_ids:
                simulated_organizations = Organization.objects.filter(id__in=impersonated_org_ids)
            
            return {
                'is_impersonating': True,
                'impersonated_user': impersonated_user,
                'effective_user': impersonated_user,
                'simulated_organizations': simulated_organizations,
                'has_organization_simulation': impersonated_org_ids is not None,
            }
        except User.DoesNotExist:
            # Clean up invalid session
            keys_to_delete = ['impersonated_user_id', 'original_user_id', 'impersonated_organizations']
            for key in keys_to_delete:
                if key in request.session:
                    del request.session[key]
    
    return {
        'is_impersonating': False,
        'impersonated_user': None,
        'effective_user': request.user,
        'simulated_organizations': [],
        'has_organization_simulation': False,
    }
