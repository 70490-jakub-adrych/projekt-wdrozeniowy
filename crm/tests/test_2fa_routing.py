from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from crm.models import UserProfile

class TwoFactorRoutingTests(TestCase):
    """Test cases for 2FA URL routing and middleware interactions"""
    
    def setUp(self):
        # Create test user with 2FA enabled
        self.user = User.objects.create_user(
            username='testuser', 
            email='test@example.com',
            password='password123'
        )
        self.profile = UserProfile.objects.create(
            user=self.user,
            is_approved=True,
            email_verified=True,
            ga_enabled=True,
            ga_secret_key='TESTKEY123456'
        )
        self.client = Client()
        
        # Important URLs
        self.verify_url = reverse('verify_2fa')
        self.dashboard_url = reverse('dashboard')
        self.debug_url = reverse('debug_2fa')
        
    def test_2fa_verify_access(self):
        """Test that the verify_2fa view can be accessed directly without redirect loops"""
        # Login to start a session
        self.client.login(username='testuser', password='password123')
        
        # Try to access the verification page directly
        response = self.client.get(self.verify_url)
        
        # Verify we get the page and not a redirect
        self.assertEqual(response.status_code, 200)
        self.assertIn('form', response.context)
        self.assertIn('verification_code', response.context['form'].fields)
        
    def test_debug_page_access(self):
        """Test that the debug page can be accessed with the debug parameter"""
        # Login to start a session
        self.client.login(username='testuser', password='password123')
        
        # Try to access using the debug parameter
        response = self.client.get(f"{self.dashboard_url}?2fa_debug=1")
        
        # Should redirect to debug page
        self.assertRedirects(response, self.debug_url)
