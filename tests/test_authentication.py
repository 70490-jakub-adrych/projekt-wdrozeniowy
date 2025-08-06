"""
Tests for authentication functionality including login, logout, registration,
password validation, email verification, and role-based access control.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.core import mail
from django.conf import settings
from unittest.mock import patch
import re

from .base import BaseTestCase
from crm.models import UserProfile, ActivityLog, EmailVerification, EmailNotificationSettings
from crm.forms import CustomUserCreationForm, UserProfileForm, CustomAuthenticationForm


class AuthenticationTestCase(BaseTestCase):
    """Test authentication functionality"""
    
    def test_login_valid_credentials(self):
        """Test login with valid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'TestPass123!'
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check that user is logged in
        user = User.objects.get(username='test_client')
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Check activity log
        self.assert_activity_log_created(user, 'login')
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        response = self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'WrongPassword'
        })
        
        # Should stay on login page
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Please enter a correct username and password')
        
        # Check failed login activity log
        user = User.objects.get(username='test_client')
        self.assert_activity_log_created(user, 'login_failed')
    
    def test_login_with_email(self):
        """Test login using email address"""
        response = self.client.post(reverse('login'), {
            'username': 'client@test.com',
            'password': 'TestPass123!'
        })
        
        # Should redirect after successful login
        self.assertEqual(response.status_code, 302)
        
        # Check that user is logged in
        user = User.objects.get(email='client@test.com')
        self.assertTrue('_auth_user_id' in self.client.session)
    
    def test_login_unverified_user(self):
        """Test login with unverified email"""
        # Activate the unverified user but keep email unverified
        self.unverified_user.is_active = True
        self.unverified_user.save()
        
        response = self.client.post(reverse('login'), {
            'username': 'test_unverified',
            'password': 'TestPass123!'
        })
        
        # Should redirect to email verification
        self.assertRedirects(response, reverse('verify_email'))
    
    def test_login_pending_approval(self):
        """Test login with pending approval"""
        response = self.client.post(reverse('login'), {
            'username': 'test_pending',
            'password': 'TestPass123!'
        })
        
        # Should redirect to pending approval page
        self.assertRedirects(response, reverse('register_pending'))
    
    def test_logout(self):
        """Test logout functionality"""
        # Login first
        self.client.login(username='test_client', password='TestPass123!')
        
        # Logout
        response = self.client.get(reverse('logout'))
        
        # Should redirect to landing page
        self.assertRedirects(response, reverse('landing_page'))
        
        # Check that user is logged out
        self.assertFalse('_auth_user_id' in self.client.session)
        
        # Check logout activity log
        user = User.objects.get(username='test_client')
        self.assert_activity_log_created(user, 'logout')
    
    def test_failed_login_attempt_counting(self):
        """Test that failed login attempts are counted"""
        user = User.objects.get(username='test_client')
        profile = user.profile
        
        # Make multiple failed login attempts
        for i in range(3):
            self.client.post(reverse('login'), {
                'username': 'test_client',
                'password': 'WrongPassword'
            })
        
        # Refresh profile from database
        profile.refresh_from_db()
        
        # Check failed login count
        self.assertEqual(profile.failed_login_attempts, 3)
        
        # Check activity logs
        failed_logs = ActivityLog.objects.filter(user=user, action_type='login_failed')
        self.assertEqual(failed_logs.count(), 3)
    
    def test_account_lockout_after_failed_attempts(self):
        """Test account lockout after 5 failed attempts"""
        user = User.objects.get(username='test_client')
        
        # Make 5 failed login attempts
        for i in range(5):
            self.client.post(reverse('login'), {
                'username': 'test_client',
                'password': 'WrongPassword'
            })
        
        # Check that account is locked
        profile = user.profile
        profile.refresh_from_db()
        self.assertTrue(profile.is_locked)
        
        # Check account locked activity log
        self.assert_activity_log_created(user, 'account_locked')
        
        # Try to login with correct password - should fail
        response = self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'TestPass123!'
        })
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Account is locked')


class RegistrationTestCase(BaseTestCase):
    """Test user registration functionality"""
    
    def test_registration_valid_data(self):
        """Test registration with valid data"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'phone': '123456789'
        })
        
        # Should redirect to verification page or show success message
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Sprawdź swój email')
        
        # Check that user was created
        user = User.objects.get(username='newuser')
        self.assertFalse(user.is_active)  # Should be inactive until email verification
        
        # Check that profile was created
        self.assertTrue(hasattr(user, 'profile'))
        self.assertEqual(user.profile.phone, '123456789')
        self.assertFalse(user.profile.email_verified)
        self.assertFalse(user.profile.is_approved)
        
        # Check that verification record was created
        self.assertTrue(EmailVerification.objects.filter(user=user).exists())
    
    def test_registration_duplicate_username(self):
        """Test registration with duplicate username"""
        response = self.client.post(reverse('register'), {
            'username': 'test_client',  # Already exists
            'email': 'newemail@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'phone': '123456789'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'A user with that username already exists')
    
    def test_registration_duplicate_email(self):
        """Test registration with duplicate email"""
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'client@test.com',  # Already exists
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'phone': '123456789'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'już istnieje')  # "already exists" in Polish
    
    def test_registration_password_validation(self):
        """Test password validation during registration"""
        # Test weak password
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': '123',
            'password2': '123',
            'phone': '123456789'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'too short')
        
        # Test password mismatch
        response = self.client.post(reverse('register'), {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'DifferentPass123!',
            'phone': '123456789'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "didn't match")
    
    def test_email_verification_process(self):
        """Test email verification process"""
        # Register a new user
        self.client.post(reverse('register'), {
            'username': 'verifyuser',
            'email': 'verifyuser@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'phone': '123456789'
        })
        
        user = User.objects.get(username='verifyuser')
        verification = EmailVerification.objects.get(user=user)
        
        # Test verification with correct code
        self.client.post(reverse('register'), {
            'verify_email': 'true',
            'verification_code': verification.verification_code
        }, follow=True)
        
        # Check that user is now active and email verified
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.email_verified)
        
        # Check that verification is marked as verified
        verification.refresh_from_db()
        self.assertTrue(verification.is_verified)
    
    def test_email_verification_invalid_code(self):
        """Test email verification with invalid code"""
        # Register a new user
        self.client.post(reverse('register'), {
            'username': 'verifyuser2',
            'email': 'verifyuser2@test.com',
            'password1': 'ComplexPass123!',
            'password2': 'ComplexPass123!',
            'phone': '123456789'
        })
        
        # Test verification with wrong code
        response = self.client.post(reverse('register'), {
            'verify_email': 'true',
            'verification_code': '000000'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Nieprawidłowy kod')  # "Invalid code" in Polish


class PermissionTestCase(BaseTestCase):
    """Test role-based permissions and access control"""
    
    def setUp(self):
        super().setUp()
        self.admin_urls = [
            reverse('admin:index'),
            reverse('pending_approvals'),
            reverse('activity_logs'),
            reverse('activity_logs_wipe'),
        ]
        
        self.agent_urls = [
            reverse('dashboard'),
            reverse('pending_approvals'),
            reverse('activity_logs'),
        ]
        
        self.client_urls = [
            reverse('dashboard'),
            reverse('ticket_create'),
        ]
        
        self.viewer_only_urls = [
            reverse('ticket_display'),
        ]
    
    def test_admin_access(self):
        """Test admin user access to all areas"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        # Admin should access admin-only areas
        for url in self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 302])  # 302 for redirects
    
    def test_agent_access(self):
        """Test agent user access restrictions"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        # Agent should access agent areas
        for url in self.agent_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 302])
        
        # Agent should NOT access admin-only areas
        response = self.client.get(reverse('activity_logs_wipe'))
        self.assertIn(response.status_code, [403, 404, 302])
    
    def test_client_access(self):
        """Test client user access restrictions"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Client should access client areas
        for url in self.client_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, [200, 302])
        
        # Client should NOT access admin areas
        for url in self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, [403, 404, 302])
    
    def test_viewer_access(self):
        """Test viewer user access restrictions"""
        self.client.login(username='test_viewer', password='TestPass123!')
        
        # Viewer should only access ticket display
        response = self.client.get(reverse('ticket_display'))
        self.assertEqual(response.status_code, 200)
        
        # Viewer should be redirected from other areas
        for url in self.client_urls + self.admin_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                # Should redirect to ticket_display
                if response.status_code == 302:
                    self.assertTrue(response.url.endswith(reverse('ticket_display')))
    
    def test_unauthenticated_access(self):
        """Test unauthenticated user access"""
        # Should be redirected to login for protected areas
        protected_urls = self.admin_urls + self.agent_urls + self.client_urls
        
        for url in protected_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertIn(response.status_code, [302, 403])
                if response.status_code == 302:
                    self.assertIn('/login/', response.url)


class PasswordValidationTestCase(BaseTestCase):
    """Test password validation functionality"""
    
    def test_password_change_form_validation(self):
        """Test password change form validation"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Test with weak new password
        response = self.client.post(reverse('password_change'), {
            'old_password': 'TestPass123!',
            'new_password1': '123',
            'new_password2': '123'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'too short')
    
    def test_password_reset_validation(self):
        """Test password reset form validation"""
        # Request password reset
        response = self.client.post(reverse('password_reset'), {
            'email': 'client@test.com'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check that email was sent (if email backend is configured)
        if hasattr(mail, 'outbox'):
            self.assertEqual(len(mail.outbox), 1)
    
    def test_password_similarity_validation(self):
        """Test password similarity to user info validation"""
        response = self.client.post(reverse('register'), {
            'username': 'john',
            'email': 'john@test.com',
            'password1': 'john123',  # Too similar to username
            'password2': 'john123',
            'phone': '123456789'
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'too similar')


class ActivityLoggingTestCase(BaseTestCase):
    """Test activity logging functionality"""
    
    def test_login_logout_logging(self):
        """Test that login and logout activities are logged"""
        # Clear existing logs
        ActivityLog.objects.all().delete()
        
        # Login
        self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'TestPass123!'
        })
        
        user = User.objects.get(username='test_client')
        login_log = self.assert_activity_log_created(user, 'login')
        self.assertIn('logged in', login_log.description)
        self.assertIsNotNone(login_log.ip_address)
        
        # Logout
        self.client.get(reverse('logout'))
        logout_log = self.assert_activity_log_created(user, 'logout')
    
    def test_failed_login_logging(self):
        """Test that failed login attempts are logged"""
        ActivityLog.objects.all().delete()
        
        self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'WrongPassword'
        })
        
        user = User.objects.get(username='test_client')
        failed_log = self.assert_activity_log_created(user, 'login_failed')
        self.assertIn('Failed login attempt', failed_log.description)
    
    def test_account_lockout_logging(self):
        """Test that account lockout is logged"""
        ActivityLog.objects.all().delete()
        user = User.objects.get(username='test_client')
        
        # Make 5 failed attempts to trigger lockout
        for i in range(5):
            self.client.post(reverse('login'), {
                'username': 'test_client',
                'password': 'WrongPassword'
            })
        
        # Check that account locked log was created
        locked_log = self.assert_activity_log_created(user, 'account_locked')
        self.assertIn('locked after 5 failed', locked_log.description)
    
    def test_no_duplicate_login_logs(self):
        """Test that no duplicate login logs are created"""
        ActivityLog.objects.all().delete()
        
        # Login (this might trigger multiple login() calls internally)
        self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'TestPass123!'
        })
        
        user = User.objects.get(username='test_client')
        login_logs = ActivityLog.objects.filter(user=user, action_type='login')
        
        # Should only have ONE login log, not multiple
        self.assertEqual(login_logs.count(), 1, 
                        f"Expected 1 login log, got {login_logs.count()}")
    
    def test_ip_address_logging(self):
        """Test that IP addresses are properly logged"""
        ActivityLog.objects.all().delete()
        
        # Login with custom IP headers
        self.client.post(reverse('login'), {
            'username': 'test_client',
            'password': 'TestPass123!'
        }, HTTP_X_FORWARDED_FOR='192.168.1.100,10.0.0.1')
        
        user = User.objects.get(username='test_client')
        login_log = ActivityLog.objects.get(user=user, action_type='login')
        
        # Should log the first IP from X-Forwarded-For
        self.assertEqual(login_log.ip_address, '192.168.1.100')
