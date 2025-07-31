from django.test import TestCase, Client
from django.urls import reverse, NoReverseMatch
from django.contrib.auth.models import User
from crm.models import UserProfile

class TwoFactorURLTests(TestCase):
    """Test URL routing related to 2FA functionality"""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user('testuser', 'test@example.com', 'password123')
        self.profile = UserProfile.objects.create(user=self.user)
        self.client.login(username='testuser', password='password123')
        
    def test_2fa_view_urls(self):
        """Test that all 2FA URLs can be reversed without exceptions"""
        # Test that all these URL names are valid
        url_names = [
            'verify_2fa',
            'setup_2fa',
            'setup_2fa_success', 
            'recovery_code',
            'debug_2fa',
            'dashboard',  # This should be used instead of 'profile'
        ]
        
        for url_name in url_names:
            try:
                url = reverse(url_name)
                self.assertIsNotNone(url)
            except NoReverseMatch:
                self.fail(f"The URL name '{url_name}' could not be reversed")
