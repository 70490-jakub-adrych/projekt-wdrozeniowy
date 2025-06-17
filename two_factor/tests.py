from django.test import TestCase, Client, RequestFactory
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
import pyotp
from .models import TwoFactorAuth, TrustedDevice
from .utils import generate_totp_secret, verify_totp_code
from .middleware import TwoFactorMiddleware

class TwoFactorModelTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create 2FA record for user
        self.two_factor = TwoFactorAuth.objects.create(
            user=self.user,
            ga_secret=generate_totp_secret(),
            ga_enabled=True,
            ga_enabled_on=timezone.now(),
            ga_last_authenticated=timezone.now()
        )
    
    def test_recovery_code_generation(self):
        """Test recovery code generation and verification"""
        # Generate recovery code
        recovery_code = self.two_factor.generate_recovery_code()
        
        # Verify code is correct length
        self.assertEqual(len(recovery_code), 16)
        
        # Verify code correctly validates
        self.assertTrue(self.two_factor.verify_recovery_code(recovery_code))
        
        # Verify code can only be used once
        self.assertFalse(self.two_factor.verify_recovery_code(recovery_code))
        self.assertIsNone(self.two_factor.recovery_code_hash)
    
    def test_regeneration_throttling(self):
        """Test that recovery codes can't be regenerated too frequently"""
        # Generate first code
        first_code = self.two_factor.generate_recovery_code()
        self.assertIsNotNone(first_code)
        
        # Try to regenerate immediately
        second_code = self.two_factor.generate_recovery_code()
        self.assertIsNone(second_code)
        
        # Mock time passing
        self.two_factor.recovery_code_generated = timezone.now() - timezone.timedelta(hours=25)
        self.two_factor.save()
        
        # Should allow regeneration now
        third_code = self.two_factor.generate_recovery_code()
        self.assertIsNotNone(third_code)

class TwoFactorViewTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        self.client = Client()
        self.client.login(username='testuser', password='testpassword')
        
        # Create 2FA record but not enabled yet
        self.two_factor = TwoFactorAuth.objects.create(
            user=self.user,
            ga_secret=generate_totp_secret(),
            ga_enabled=False
        )
    
    def test_setup_view(self):
        """Test the 2FA setup view"""
        response = self.client.get(reverse('two_factor_setup'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Set Up Two-Factor Authentication")
    
    def test_successful_setup(self):
        """Test successful 2FA setup with valid code"""
        # Generate valid TOTP code
        totp = pyotp.TOTP(self.two_factor.ga_secret)
        valid_code = totp.now()
        
        response = self.client.post(reverse('two_factor_setup'), {
            'verification_code': valid_code
        })
        
        # Refresh from database
        self.two_factor.refresh_from_db()
        
        # Check that 2FA was enabled
        self.assertTrue(self.two_factor.ga_enabled)
        self.assertIsNotNone(self.two_factor.ga_enabled_on)
        
        # Check for success message and redirect to success page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Two-factor authentication has been enabled")
    
    def test_failed_setup(self):
        """Test failed 2FA setup with invalid code"""
        response = self.client.post(reverse('two_factor_setup'), {
            'verification_code': '000000'  # Invalid code
        })
        
        # Refresh from database
        self.two_factor.refresh_from_db()
        
        # Check that 2FA was not enabled
        self.assertFalse(self.two_factor.ga_enabled)
        
        # Check for error message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Invalid verification code")

class TrustedDeviceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Create 2FA for user
        self.two_factor = TwoFactorAuth.objects.create(
            user=self.user,
            ga_secret=generate_totp_secret(),
            ga_enabled=True,
            ga_enabled_on=timezone.now(),
            ga_last_authenticated=timezone.now()
        )
        
        # Create a request factory
        self.factory = RequestFactory()
    
    def test_device_fingerprint(self):
        """Test device fingerprinting"""
        # Create two different requests
        request1 = self.factory.get('/test/')
        request1.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        request1.META['REMOTE_ADDR'] = '192.168.1.1'
        
        request2 = self.factory.get('/test/')
        request2.META['HTTP_USER_AGENT'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)'
        request2.META['REMOTE_ADDR'] = '192.168.1.2'
        
        # Generate device fingerprints
        device_id1 = TrustedDevice.generate_device_id(request1)
        device_id2 = TrustedDevice.generate_device_id(request2)
        
        # Fingerprints should be different
        self.assertNotEqual(device_id1, device_id2)
        
        # Same request should produce same fingerprint
        device_id3 = TrustedDevice.generate_device_id(request1)
        self.assertEqual(device_id1, device_id3)
    
    def test_trusted_device_expiry(self):
        """Test that trusted devices expire properly"""
        request = self.factory.get('/test/')
        request.META['HTTP_USER_AGENT'] = 'Test User Agent'
        request.META['REMOTE_ADDR'] = '127.0.0.1'
        request.user = self.user
        
        # Create a trusted device that expires soon
        device = TrustedDevice.create(self.user, request)
        device.expires_at = timezone.now() + timezone.timedelta(minutes=5)
        device.save()
        
        # Should be valid now
        self.assertTrue(device.is_valid())
        
        # Expire the device
        device.expires_at = timezone.now() - timezone.timedelta(minutes=5)
        device.save()
        
        # Should be invalid now
        self.assertFalse(device.is_valid())

class TwoFactorMiddlewareTests(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpassword'
        )
        
        # Set up middleware
        self.middleware = TwoFactorMiddleware(lambda r: None)
        self.factory = RequestFactory()
    
    def test_exempt_paths(self):
        """Test that exempt paths are not redirected"""
        # Create a request for an exempt path
        request = self.factory.get('/static/css/style.css')
        request.user = self.user
        
        # Middleware should not redirect
        response = self.middleware(request)
        self.assertIsNone(response)
    
    def test_admin_ip_bypass(self):
        """Test that admins from known IPs bypass 2FA"""
        # Create a superuser
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass',
            is_staff=True
        )
        
        # Create a request
        request = self.factory.get('/dashboard/')
        request.user = admin
        request.META['REMOTE_ADDR'] = '192.168.1.100'
        request.session = {'admin_ips': ['192.168.1.100']}
        
        # Middleware should not redirect
        response = self.middleware(request)
        self.assertIsNone(response)
