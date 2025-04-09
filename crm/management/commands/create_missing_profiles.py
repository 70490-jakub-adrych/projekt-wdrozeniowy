from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from crm.models import UserProfile

class Command(BaseCommand):
    help = 'Creates UserProfile objects for users that don\'t have them'

    def handle(self, *args, **kwargs):
        users_without_profile = []
        
        # Get all users
        for user in User.objects.all():
            try:
                # Skip if profile exists
                profile = user.profile
            except:
                # Create profile if it doesn't exist
                self.stdout.write(f"Creating profile for user: {user.username}")
                
                # Determine role based on superuser status
                if user.is_superuser:
                    role = 'admin'
                    group_name = 'Admin'
                else:
                    role = 'client'
                    group_name = 'Klient'
                
                # Create profile with appropriate role
                profile = UserProfile.objects.create(
                    user=user,
                    role=role
                )
                
                # Ensure group exists and add user to it
                user_group, created = Group.objects.get_or_create(name=group_name)
                user.groups.add(user_group)
                
                users_without_profile.append(f"{user.username} ({role})")
        
        if users_without_profile:
            self.stdout.write(self.style.SUCCESS(f'Created profiles for {len(users_without_profile)} users: {", ".join(users_without_profile)}'))
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
