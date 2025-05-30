from .models import GroupViewPermission, UserViewPermission, ViewPermission

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
    
    return {'user_view_permissions': permissions}
