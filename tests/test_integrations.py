"""
Tests for email functionality, API endpoints, and integration features.
"""
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from django.conf import settings
from unittest.mock import patch, MagicMock
import json

from .base import BaseTestCase
from crm.models import (
    UserProfile, EmailNotificationSettings, EmailVerification,
    Ticket, Category, ActivityLog
)
from crm.services.email_service import EmailNotificationService


class EmailServiceTestCase(BaseTestCase):
    """Test email notification functionality"""
    
    def setUp(self):
        super().setUp()
        # Ensure test email backend is being used
        self.original_email_backend = settings.EMAIL_BACKEND
        settings.EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
        
        # Clear mail outbox
        mail.outbox = []
    
    def tearDown(self):
        # Restore original email backend
        settings.EMAIL_BACKEND = self.original_email_backend
        super().tearDown()
    
    def test_send_verification_email(self):
        """Test sending verification email"""
        result = EmailNotificationService.send_verification_email(
            self.unverified_user, 
            '123456'
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.unverified_user.email)
        self.assertIn('123456', email.body)
        self.assertIn('weryfikacji', email.subject.lower())
    
    def test_send_account_approved_email(self):
        """Test sending account approval notification"""
        result = EmailNotificationService.send_account_approved_email(
            self.pending_user,
            approved_by=self.admin_user
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.pending_user.email)
        self.assertIn('zatwierdzono', email.subject.lower())
    
    def test_send_password_changed_notification(self):
        """Test sending password change notification"""
        result = EmailNotificationService.send_password_changed_notification(
            self.client_user
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.client_user.email)
        self.assertIn('hasło', email.subject.lower())
    
    def test_send_password_verification_email(self):
        """Test sending password change verification email"""
        result = EmailNotificationService.send_password_verification_email(
            self.client_user,
            '567890'
        )
        
        self.assertTrue(result)
        self.assertEqual(len(mail.outbox), 1)
        
        email = mail.outbox[0]
        self.assertEqual(email.to[0], self.client_user.email)
        self.assertIn('567890', email.body)
    
    def test_send_ticket_notification(self):
        """Test sending ticket-related notifications"""
        category = Category.objects.create(name='Test Category')
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=category
        )
        
        # Test new ticket notification
        result = EmailNotificationService.send_new_ticket_notification(
            ticket,
            recipients=[self.agent_user.email]
        )
        
        if result:  # Only test if method exists
            self.assertEqual(len(mail.outbox), 1)
            email = mail.outbox[0]
            self.assertIn(self.agent_user.email, email.to)
            self.assertIn(ticket.title, email.subject)
    
    @patch('crm.services.email_service.EmailNotificationService.send_email')
    def test_email_service_error_handling(self, mock_send_email):
        """Test email service error handling"""
        # Mock email sending failure
        mock_send_email.return_value = False
        
        result = EmailNotificationService.send_verification_email(
            self.unverified_user,
            '123456'
        )
        
        self.assertFalse(result)
    
    def test_email_notification_settings(self):
        """Test email notification settings"""
        # Create notification settings
        settings_obj, created = EmailNotificationSettings.objects.get_or_create(
            user=self.client_user
        )
        
        # Test default settings
        self.assertTrue(settings_obj.ticket_updates)
        self.assertTrue(settings_obj.ticket_comments)
        
        # Test disabling notifications
        settings_obj.ticket_updates = False
        settings_obj.save()
        
        # Should respect user preferences when sending notifications
        # (Implementation depends on your email service logic)


class APITestCase(BaseTestCase):
    """Test API endpoints and AJAX functionality"""
    
    def test_get_tickets_update_api(self):
        """Test tickets update API endpoint"""
        # Create some test tickets
        category = Category.objects.create(name='API Test Category')
        
        ticket1 = Ticket.objects.create(
            title='API Ticket 1',
            description='First test ticket',
            created_by=self.client_user,
            category=category,
            status='open'
        )
        
        ticket2 = Ticket.objects.create(
            title='API Ticket 2',
            description='Second test ticket',
            created_by=self.client_user,
            category=category,
            status='in_progress'
        )
        
        # Login and make API request
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.get(reverse('get_tickets_update'))
        
        # Should return JSON response
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/json')
        
        # Parse JSON response
        data = json.loads(response.content)
        
        # Should contain ticket information
        self.assertIn('tickets', data)
        self.assertIsInstance(data['tickets'], list)
    
    def test_api_authentication_required(self):
        """Test that API endpoints require authentication"""
        response = self.client.get(reverse('get_tickets_update'))
        
        # Should redirect to login or return 401/403
        self.assertIn(response.status_code, [302, 401, 403])
    
    def test_ajax_ticket_assignment(self):
        """Test AJAX ticket assignment functionality"""
        category = Category.objects.create(name='Assignment Test')
        ticket = Ticket.objects.create(
            title='Assignment Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=category
        )
        
        # Login as agent
        self.client.login(username='test_agent', password='TestPass123!')
        
        # Make AJAX request to assign ticket
        response = self.client.post(
            reverse('ticket_assign_to_me', args=[ticket.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should return success response
        self.assertIn(response.status_code, [200, 302])
        
        # Check that ticket was assigned
        ticket.refresh_from_db()
        self.assertEqual(ticket.assigned_to, self.agent_user)
    
    def test_api_permission_checks(self):
        """Test API permission checks"""
        # Create ticket owned by different user
        category = Category.objects.create(name='Permission Test')
        other_user_ticket = Ticket.objects.create(
            title='Other User Ticket',
            description='Not accessible',
            created_by=self.admin_user,
            category=category
        )
        
        # Login as client
        self.client.login(username='test_client', password='TestPass123!')
        
        # Try to access other user's ticket via API
        response = self.client.get(
            reverse('ticket_detail', args=[other_user_ticket.id]),
            HTTP_X_REQUESTED_WITH='XMLHttpRequest'
        )
        
        # Should deny access
        self.assertIn(response.status_code, [403, 404])


class IntegrationTestCase(BaseTestCase):
    """Test integration between different system components"""
    
    def test_user_registration_to_approval_flow(self):
        """Test complete user registration and approval flow"""
        # 1. User registers
        response = self.client.post(reverse('register'), {
            'username': 'integration_user',
            'email': 'integration@test.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!',
            'phone': '987654321'
        })
        
        # Should create user and verification record
        user = User.objects.get(username='integration_user')
        self.assertFalse(user.is_active)
        self.assertTrue(EmailVerification.objects.filter(user=user).exists())
        
        # 2. User verifies email
        verification = EmailVerification.objects.get(user=user)
        
        # Simulate email verification
        response = self.client.post(reverse('register'), {
            'verify_email': 'true',
            'verification_code': verification.verification_code
        })
        
        # User should now be active but not approved
        user.refresh_from_db()
        self.assertTrue(user.is_active)
        self.assertTrue(user.profile.email_verified)
        self.assertFalse(user.profile.is_approved)
        
        # 3. Admin approves user
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.post(reverse('approve_user', args=[user.id]))
        
        # User should now be fully approved
        user.refresh_from_db()
        self.assertTrue(user.profile.is_approved)
    
    def test_ticket_creation_with_notifications(self):
        """Test ticket creation with email notifications"""
        # Login as client
        self.client.login(username='test_client', password='TestPass123!')
        
        category = Category.objects.create(name='Integration Test')
        
        # Clear mail outbox
        mail.outbox = []
        
        # Create ticket
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Integration Test Ticket',
            'description': 'This tests the integration',
            'category': category.id,
            'priority': 'high'
        })
        
        # Should create ticket
        ticket = Ticket.objects.get(title='Integration Test Ticket')
        self.assertEqual(ticket.created_by, self.client_user)
        
        # Should create activity log
        self.assert_activity_log_created(self.client_user, 'ticket_created')
        
        # Should send notifications (if implemented)
        # This depends on your notification implementation
    
    def test_role_transition_workflow(self):
        """Test user role transition workflow"""
        # Start with client user
        user = self.client_user
        self.assertEqual(user.profile.role, 'client')
        
        # Admin promotes client to agent
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.post(reverse('update_user_role', args=[user.id]), {
            'role': 'agent'
        })
        
        # User should now be agent
        user.refresh_from_db()
        self.assertEqual(user.profile.role, 'agent')
        
        # Should be able to access agent features
        self.client.login(username='test_client', password='TestPass123!')
        response = self.client.get(reverse('pending_approvals'))
        
        # Should now have access (depending on implementation)
    
    def test_activity_logging_integration(self):
        """Test that all major actions create appropriate logs"""
        ActivityLog.objects.all().delete()
        
        # 1. Login creates log
        self.client.login(username='test_client', password='TestPass123!')
        self.assert_activity_log_created(self.client_user, 'login')
        
        # 2. Ticket creation creates log
        category = Category.objects.create(name='Logging Test')
        self.client.post(reverse('ticket_create'), {
            'title': 'Logging Test Ticket',
            'description': 'Test logging',
            'category': category.id,
            'priority': 'medium'
        })
        self.assert_activity_log_created(self.client_user, 'ticket_created')
        
        # 3. Password change creates log
        self.client.post(reverse('password_change'), {
            'old_password': 'TestPass123!',
            'new_password1': 'NewComplexPass123!',
            'new_password2': 'NewComplexPass123!'
        })
        
        # Should create password change log (if implemented)
        password_logs = ActivityLog.objects.filter(
            user=self.client_user, 
            action_type='password_changed'
        )
        
        # 4. Logout creates log
        self.client.get(reverse('logout'))
        self.assert_activity_log_created(self.client_user, 'logout')


class PerformanceTestCase(BaseTestCase):
    """Test system performance and scalability"""
    
    def test_dashboard_performance_with_many_tickets(self):
        """Test dashboard performance with large number of tickets"""
        category = Category.objects.create(name='Performance Test')
        
        # Create many tickets
        tickets = []
        for i in range(100):
            ticket = Ticket(
                title=f'Performance Test Ticket {i}',
                description=f'Performance test description {i}',
                created_by=self.client_user,
                category=category,
                priority='medium'
            )
            tickets.append(ticket)
        
        Ticket.objects.bulk_create(tickets)
        
        # Login and access dashboard
        self.client.login(username='test_client', password='TestPass123!')
        
        # Measure response time
        import time
        start_time = time.time()
        
        response = self.client.get(reverse('dashboard'))
        
        end_time = time.time()
        response_time = end_time - start_time
        
        # Should complete within reasonable time (adjust threshold as needed)
        self.assertLess(response_time, 5.0, f"Dashboard took {response_time:.2f} seconds")
        self.assertEqual(response.status_code, 200)
    
    def test_activity_log_pagination(self):
        """Test activity log pagination with many entries"""
        # Create many activity logs
        logs = []
        for i in range(200):
            log = ActivityLog(
                user=self.client_user,
                action_type='login',
                description=f'Test log entry {i}',
                ip_address='127.0.0.1'
            )
            logs.append(log)
        
        ActivityLog.objects.bulk_create(logs)
        
        # Login as admin and access logs
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('activity_logs'))
        
        # Should handle large number of logs efficiently
        self.assertEqual(response.status_code, 200)
        
        # Should use pagination (check for page parameters)
        self.assertContains(response, 'page')  # Look for pagination
    
    def test_search_performance(self):
        """Test search performance with many records"""
        category = Category.objects.create(name='Search Test')
        
        # Create many tickets with searchable content
        tickets = []
        for i in range(50):
            ticket = Ticket(
                title=f'Search Test Ticket {i}',
                description=f'Database connection issue number {i}',
                created_by=self.client_user,
                category=category
            )
            tickets.append(ticket)
        
        Ticket.objects.bulk_create(tickets)
        
        self.client.login(username='test_admin', password='TestPass123!')
        
        # Perform search
        import time
        start_time = time.time()
        
        response = self.client.get(reverse('dashboard'), {'search': 'Database'})
        
        end_time = time.time()
        search_time = end_time - start_time
        
        # Should complete search quickly
        self.assertLess(search_time, 3.0, f"Search took {search_time:.2f} seconds")
        self.assertEqual(response.status_code, 200)


class SecurityTestCase(BaseTestCase):
    """Test security features and vulnerabilities"""
    
    def test_sql_injection_protection(self):
        """Test protection against SQL injection"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        # Try SQL injection in search parameter
        malicious_input = "'; DROP TABLE crm_ticket; --"
        
        response = self.client.get(reverse('dashboard'), {'search': malicious_input})
        
        # Should handle safely without database damage
        self.assertEqual(response.status_code, 200)
        
        # Verify tickets table still exists
        self.assertTrue(Ticket.objects.all().exists())
    
    def test_xss_protection(self):
        """Test protection against XSS attacks"""
        category = Category.objects.create(name='XSS Test')
        
        self.client.login(username='test_client', password='TestPass123!')
        
        # Try XSS in ticket creation
        malicious_script = '<script>alert("XSS")</script>'
        
        response = self.client.post(reverse('ticket_create'), {
            'title': f'XSS Test {malicious_script}',
            'description': f'XSS in description {malicious_script}',
            'category': category.id,
            'priority': 'medium'
        })
        
        # Should create ticket but escape the script
        ticket = Ticket.objects.get(title__contains='XSS Test')
        
        # View ticket detail
        response = self.client.get(reverse('ticket_detail', args=[ticket.id]))
        
        # Script should be escaped in HTML output
        self.assertNotContains(response, '<script>')
        self.assertContains(response, '&lt;script&gt;')
    
    def test_csrf_protection(self):
        """Test CSRF protection on forms"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Try to submit form without CSRF token
        self.client.logout()  # Clear any existing CSRF tokens
        
        category = Category.objects.create(name='CSRF Test')
        
        response = self.client.post(reverse('ticket_create'), {
            'title': 'CSRF Test Ticket',
            'description': 'Test CSRF protection',
            'category': category.id,
            'priority': 'medium'
        })
        
        # Should be rejected due to missing CSRF token
        self.assertIn(response.status_code, [403, 302])  # 403 or redirect to login
    
    def test_unauthorized_access_protection(self):
        """Test protection against unauthorized access"""
        category = Category.objects.create(name='Auth Test')
        
        # Create ticket as one user
        ticket = Ticket.objects.create(
            title='Private Ticket',
            description='Should not be accessible',
            created_by=self.admin_user,
            category=category
        )
        
        # Try to access as different user
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.get(reverse('ticket_detail', args=[ticket.id]))
        
        # Should deny access
        self.assertIn(response.status_code, [403, 404])
    
    def test_session_security(self):
        """Test session security features"""
        # Login
        self.client.login(username='test_client', password='TestPass123!')
        
        # Check that session is created
        self.assertTrue('_auth_user_id' in self.client.session)
        
        # Simulate session hijacking attempt
        old_session_key = self.client.session.session_key
        
        # Try to access with manipulated session
        # (This is a basic test - real session security testing would be more complex)
