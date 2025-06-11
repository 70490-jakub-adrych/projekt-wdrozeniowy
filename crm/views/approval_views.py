from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.utils import timezone
from django.db import transaction

from ..models import UserProfile, EmailVerification, EmailNotificationSettings
from .helpers import log_activity, check_permissions
from ..forms import GroupSelectionForm
import logging

# Configure logger
logger = logging.getLogger(__name__)


@login_required
def reject_user(request, user_id):
    """Reject a user and delete their account"""
    # Check permissions
    if not check_permissions(request.user, ['admin', 'superagent']):
        return forbidden_access(request)
    
    profile = get_object_or_404(UserProfile, user_id=user_id)
    user = profile.user
    
    if request.method == 'POST':
        try:
            with transaction.atomic():
                # Log this action before deletion
                log_activity(
                    user=request.user,
                    action_type='user_rejected',
                    description=f"Rejected account for user: {user.username} ({user.email})",
                    request=request
                )
                
                # Capture email for logging
                username = user.username
                email = user.email
                
                # First delete all related records EXCEPT the profile
                # Delete verification record if exists
                EmailVerification.objects.filter(user=user).delete()
                
                # Delete notification settings if exists
                EmailNotificationSettings.objects.filter(user=user).delete()
                
                # Important: Delete the profile BEFORE deleting the user
                # This prevents orphaned profile records
                profile_id = profile.id
                profile.delete()
                logger.info(f"Deleted UserProfile with ID {profile_id}")
                
                # Now delete the user account itself
                user.delete()
                
                logger.info(f"User {username} ({email}) rejected and deleted by {request.user.username}")
                messages.success(request, f'Konto użytkownika {username} zostało odrzucone i usunięte z systemu.')
            
            return redirect('pending_approvals')
        except Exception as e:
            logger.error(f"Error rejecting user {user_id}: {str(e)}")
            messages.error(request, f'Wystąpił błąd podczas odrzucania użytkownika: {str(e)}')
            return redirect('pending_approvals')
    
    # Display confirmation page
    return render(request, 'crm/approvals/reject_user.html', {'profile': profile})

@login_required
def approve_user(request, user_id):
    """View for approving a pending user."""
    # Check permissions
    if not check_permissions(request.user, ['admin', 'superagent']):
        return forbidden_access(request)
    
    profile = get_object_or_404(UserProfile, user_id=user_id)
    user = profile.user
    
    # Get available groups and organizations for selection
    available_groups = request.user.groups.all()
    available_organizations = request.user.userprofile.organizations.all()
    
    if request.method == 'POST':
        # Create form with organizations included
        form = GroupSelectionForm(request.POST, 
                                 available_groups=available_groups, 
                                 available_organizations=available_organizations)
        
        if form.is_valid():
            try:
                with transaction.atomic():
                    # Log this action
                    log_activity(
                        user=request.user,
                        action_type='user_approved',
                        description=f"Approved account for user: {user.username} ({user.email})",
                        request=request
                    )
                    
                    # Set approved flag and approver/timestamp
                    profile.approved_by = request.user
                    profile.approved_at = timezone.now()
                    profile.is_approved = True
                    
                    # Assign user to selected group
                    selected_group = form.cleaned_data['group']
                    user.groups.clear()
                    user.groups.add(selected_group)
                    
                    # Assign selected organizations
                    selected_organizations = form.cleaned_data['organizations']
                    profile.organizations.clear()
                    for org in selected_organizations:
                        profile.organizations.add(org)
                    
                    profile.save()
                    
                    logger.info(f"User {user.username} approved by {request.user.username}")
                    messages.success(request, f'Użytkownik {user.username} został pomyślnie zatwierdzony.')
                
                # Redirect to appropriate page
                return redirect('pending_approvals')
            except Exception as e:
                logger.error(f"Error approving user {user_id}: {str(e)}")
                messages.error(request, f'Wystąpił błąd podczas zatwierdzania użytkownika: {str(e)}')
                return redirect('pending_approvals')
        else:
            messages.error(request, 'Wystąpił błąd w przesłanym formularzu. Proszę spróbować ponownie.')
            return redirect('pending_approvals')
    else:
        # For GET requests, include organizations in the form
        form = GroupSelectionForm(
            available_groups=available_groups,
            available_organizations=available_organizations,
            initial_organizations=profile.organizations.all()
        )
    
    # Display approval confirmation page
    return render(request, 'crm/approvals/approve_user.html', {'profile': profile, 'form': form})