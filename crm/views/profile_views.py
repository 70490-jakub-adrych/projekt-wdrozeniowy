from ..decorators import two_factor_required, sensitive_view

@login_required
@sensitive_view  # Always require 2FA for profile changes
def user_profile_edit(request):
    # Sensitive profile editing functionality
    # ...
    pass

@login_required
@two_factor_required  # Require 2FA but honor trusted devices
def user_profile_view(request):
    # Profile viewing functionality
    # ...
    pass
