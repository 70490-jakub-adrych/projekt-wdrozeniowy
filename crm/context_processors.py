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
    Add device information to template context
    """
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Detect mobile device
    mobile_patterns = [
        r'Mobile',
        r'Android.*Mobile',
        r'iPhone',
        r'iPod',
        r'BlackBerry',
        r'Windows Phone',
        r'Opera Mini',
        r'IEMobile',
    ]
    
    is_mobile = bool(re.search('|'.join(mobile_patterns), user_agent, re.IGNORECASE))
    
    # Detect tablet
    is_tablet = bool(re.search(r'iPad|Tablet|Android(?!.*Mobile)', user_agent, re.IGNORECASE))
    
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
