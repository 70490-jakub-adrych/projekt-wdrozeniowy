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
                profile = UserProfile.objects.create(
                    user=user,
                    role='client'  # Default role
                )
                
                # Ensure client group exists and add user to it
                client_group, created = Group.objects.get_or_create(name='Klient')
                user.groups.add(client_group)
                
                users_without_profile.append(user.username)
        
        if users_without_profile:
            self.stdout.write(self.style.SUCCESS(f'Created profiles for {len(users_without_profile)} users: {", ".join(users_without_profile)}'))
        else:
            self.stdout.write(self.style.SUCCESS('All users already have profiles'))
