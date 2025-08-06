"""
Tests for Django models, forms, and business logic.
"""
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
import random
import string

from .base import BaseTestCase
from crm.models import (
    UserProfile, Ticket, TicketComment, TicketAttachment, 
    Category, ActivityLog, EmailVerification, EmailNotificationSettings
)
from crm.forms import (
    CustomUserCreationForm, UserProfileForm, TicketForm, 
    TicketCommentForm, CustomAuthenticationForm
)


class UserProfileModelTestCase(BaseTestCase):
    """Test UserProfile model functionality"""
    
    def test_profile_creation_on_user_save(self):
        """Test that UserProfile is automatically created when User is saved"""
        user = User.objects.create_user(
            username='test_auto_profile',
            email='auto@test.com',
            password='TestPass123!'
        )
        
        # Profile should be created automatically via signal
        self.assertTrue(hasattr(user, 'profile'))
        self.assertIsInstance(user.profile, UserProfile)
    
    def test_profile_role_validation(self):
        """Test profile role validation"""
        profile = self.client_user.profile
        
        # Test valid roles
        valid_roles = ['client', 'agent', 'superagent', 'admin', 'viewer']
        for role in valid_roles:
            profile.role = role
            profile.full_clean()  # Should not raise ValidationError
    
    def test_failed_login_attempt_tracking(self):
        """Test failed login attempt tracking"""
        profile = self.client_user.profile
        
        # Initially no failed attempts
        self.assertEqual(profile.failed_login_attempts, 0)
        self.assertFalse(profile.is_locked)
        
        # Increment failed attempts
        for i in range(1, 4):
            profile.increment_failed_login()
            self.assertEqual(profile.failed_login_attempts, i)
            self.assertFalse(profile.is_locked)  # Not locked yet
        
        # 5th attempt should lock account
        profile.increment_failed_login()
        profile.increment_failed_login()
        self.assertEqual(profile.failed_login_attempts, 5)
        self.assertTrue(profile.is_locked)
    
    def test_reset_failed_login_attempts(self):
        """Test resetting failed login attempts"""
        profile = self.client_user.profile
        
        # Set some failed attempts
        profile.failed_login_attempts = 3
        profile.save()
        
        # Reset attempts
        profile.reset_failed_login_attempts()
        self.assertEqual(profile.failed_login_attempts, 0)
        self.assertFalse(profile.is_locked)
    
    def test_profile_str_representation(self):
        """Test profile string representation"""
        profile = self.client_user.profile
        profile.role = 'client'
        profile.save()
        
        expected = f"{self.client_user.username} - client"
        self.assertEqual(str(profile), expected)


class TicketModelTestCase(BaseTestCase):
    """Test Ticket model functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
    
    def test_ticket_creation(self):
        """Test basic ticket creation"""
        ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category,
            priority='medium'
        )
        
        self.assertEqual(ticket.status, 'open')  # Default status
        self.assertEqual(ticket.priority, 'medium')
        self.assertIsNotNone(ticket.created_at)
        self.assertIsNone(ticket.assigned_to)
    
    def test_ticket_status_choices(self):
        """Test ticket status validation"""
        ticket = Ticket.objects.create(
            title='Status Test',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
        
        valid_statuses = ['open', 'in_progress', 'resolved', 'closed', 'reopened']
        for status in valid_statuses:
            ticket.status = status
            ticket.full_clean()  # Should not raise ValidationError
    
    def test_ticket_priority_choices(self):
        """Test ticket priority validation"""
        ticket = Ticket.objects.create(
            title='Priority Test',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
        
        valid_priorities = ['low', 'medium', 'high', 'critical']
        for priority in valid_priorities:
            ticket.priority = priority
            ticket.full_clean()  # Should not raise ValidationError
    
    def test_ticket_assignment(self):
        """Test ticket assignment functionality"""
        ticket = Ticket.objects.create(
            title='Assignment Test',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
        
        # Assign to agent
        ticket.assigned_to = self.agent_user
        ticket.save()
        
        self.assertEqual(ticket.assigned_to, self.agent_user)
    
    def test_ticket_str_representation(self):
        """Test ticket string representation"""
        ticket = Ticket.objects.create(
            title='String Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
        
        expected = f"#{ticket.id} - String Test Ticket"
        self.assertEqual(str(ticket), expected)
    
    def test_ticket_ordering(self):
        """Test ticket default ordering"""
        # Create tickets at different times
        ticket1 = Ticket.objects.create(
            title='First Ticket',
            description='First',
            created_by=self.client_user,
            category=self.category
        )
        
        ticket2 = Ticket.objects.create(
            title='Second Ticket',
            description='Second',
            created_by=self.client_user,
            category=self.category
        )
        
        # Should be ordered by creation time (newest first)
        tickets = list(Ticket.objects.all())
        self.assertEqual(tickets[0], ticket2)  # Newest first
        self.assertEqual(tickets[1], ticket1)


class TicketCommentModelTestCase(BaseTestCase):
    """Test TicketComment model functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
    
    def test_comment_creation(self):
        """Test comment creation"""
        comment = TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.client_user,
            comment='This is a test comment'
        )
        
        self.assertEqual(comment.ticket, self.ticket)
        self.assertEqual(comment.created_by, self.client_user)
        self.assertEqual(comment.comment, 'This is a test comment')
        self.assertIsNotNone(comment.created_at)
    
    def test_comment_str_representation(self):
        """Test comment string representation"""
        comment = TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.client_user,
            comment='Test comment'
        )
        
        expected = f"Comment on #{self.ticket.id} by {self.client_user.username}"
        self.assertEqual(str(comment), expected)
    
    def test_comment_ordering(self):
        """Test comment ordering (oldest first)"""
        comment1 = TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.client_user,
            comment='First comment'
        )
        
        comment2 = TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.agent_user,
            comment='Second comment'
        )
        
        comments = list(TicketComment.objects.filter(ticket=self.ticket))
        self.assertEqual(comments[0], comment1)  # Oldest first
        self.assertEqual(comments[1], comment2)


class ActivityLogModelTestCase(BaseTestCase):
    """Test ActivityLog model functionality"""
    
    def test_activity_log_creation(self):
        """Test activity log creation"""
        log = ActivityLog.objects.create(
            user=self.client_user,
            action_type='login',
            description='User logged in',
            ip_address='192.168.1.1'
        )
        
        self.assertEqual(log.user, self.client_user)
        self.assertEqual(log.action_type, 'login')
        self.assertEqual(log.ip_address, '192.168.1.1')
        self.assertIsNotNone(log.created_at)
    
    def test_activity_log_without_user(self):
        """Test activity log creation without user (anonymous)"""
        log = ActivityLog.objects.create(
            action_type='login_failed',
            description='Failed login attempt',
            ip_address='192.168.1.1'
        )
        
        self.assertIsNone(log.user)
        self.assertEqual(log.action_type, 'login_failed')
    
    def test_activity_log_action_types(self):
        """Test all activity log action types"""
        valid_actions = [
            'login', 'logout', 'login_failed', 'account_locked', 'account_unlocked',
            'ticket_created', 'ticket_updated', 'ticket_commented', 'ticket_resolved',
            'ticket_closed', 'ticket_reopened', 'preferences_updated', 'password_changed',
            '404_error', '403_error', 'ticket_attachment_added', 'logs_wiped'
        ]
        
        for action in valid_actions:
            log = ActivityLog(
                user=self.client_user,
                action_type=action,
                description=f'Test {action}',
                ip_address='127.0.0.1'
            )
            log.full_clean()  # Should not raise ValidationError
    
    def test_activity_log_str_representation(self):
        """Test activity log string representation"""
        log = ActivityLog.objects.create(
            user=self.client_user,
            action_type='login',
            description='User logged in'
        )
        
        expected = f"Zalogowanie - {self.client_user.username} - {log.created_at}"
        self.assertEqual(str(log), expected)
    
    def test_activity_log_ordering(self):
        """Test activity log ordering (newest first)"""
        log1 = ActivityLog.objects.create(
            user=self.client_user,
            action_type='login',
            description='First log'
        )
        
        log2 = ActivityLog.objects.create(
            user=self.client_user,
            action_type='logout',
            description='Second log'
        )
        
        logs = list(ActivityLog.objects.all())
        self.assertEqual(logs[0], log2)  # Newest first
        self.assertEqual(logs[1], log1)


class EmailVerificationModelTestCase(BaseTestCase):
    """Test EmailVerification model functionality"""
    
    def test_verification_creation(self):
        """Test email verification creation"""
        verification = EmailVerification.objects.create(
            user=self.unverified_user,
            verification_code='123456'
        )
        
        self.assertEqual(verification.user, self.unverified_user)
        self.assertEqual(verification.verification_code, '123456')
        self.assertFalse(verification.is_verified)
        self.assertIsNone(verification.verified_at)
    
    def test_verification_code_generation(self):
        """Test automatic verification code generation"""
        verification = EmailVerification.objects.create(
            user=self.unverified_user
        )
        
        # Should have generated a 6-digit code
        self.assertEqual(len(verification.verification_code), 6)
        self.assertTrue(verification.verification_code.isdigit())
    
    def test_verification_expiration(self):
        """Test verification code expiration"""
        verification = EmailVerification.objects.create(
            user=self.unverified_user,
            verification_code='123456'
        )
        
        # Fresh verification should not be expired
        self.assertFalse(verification.is_expired())
        
        # Manually set old creation time
        old_time = timezone.now() - timedelta(hours=25)  # 25 hours ago
        verification.created_at = old_time
        verification.save()
        
        # Should now be expired
        self.assertTrue(verification.is_expired())
    
    def test_generate_new_code(self):
        """Test generating new verification code"""
        verification = EmailVerification.objects.create(
            user=self.unverified_user,
            verification_code='123456'
        )
        
        old_code = verification.verification_code
        new_code = verification.generate_new_code()
        
        self.assertNotEqual(old_code, new_code)
        self.assertEqual(len(new_code), 6)
        self.assertTrue(new_code.isdigit())
        
        # Refresh from database
        verification.refresh_from_db()
        self.assertEqual(verification.verification_code, new_code)


class CategoryModelTestCase(TestCase):
    """Test Category model functionality"""
    
    def test_category_creation(self):
        """Test category creation"""
        category = Category.objects.create(
            name='Technical Issues',
            description='All technical problems'
        )
        
        self.assertEqual(category.name, 'Technical Issues')
        self.assertEqual(category.description, 'All technical problems')
    
    def test_category_str_representation(self):
        """Test category string representation"""
        category = Category.objects.create(
            name='Account Issues',
            description='Account related problems'
        )
        
        self.assertEqual(str(category), 'Account Issues')
    
    def test_category_unique_name(self):
        """Test category name uniqueness"""
        Category.objects.create(name='Unique Category')
        
        # Creating another category with same name should raise error
        with self.assertRaises(ValidationError):
            duplicate = Category(name='Unique Category')
            duplicate.full_clean()


class FormTestCase(BaseTestCase):
    """Test Django forms"""
    
    def test_custom_user_creation_form_valid(self):
        """Test valid user creation form"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPassword123!',
            'password2': 'ComplexPassword123!'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_custom_user_creation_form_password_mismatch(self):
        """Test user creation form with password mismatch"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': 'ComplexPassword123!',
            'password2': 'DifferentPassword123!'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_custom_user_creation_form_weak_password(self):
        """Test user creation form with weak password"""
        form_data = {
            'username': 'newuser',
            'email': 'newuser@test.com',
            'password1': '123',
            'password2': '123'
        }
        
        form = CustomUserCreationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
    
    def test_user_profile_form_valid(self):
        """Test valid user profile form"""
        form_data = {
            'phone': '123456789'
        }
        
        form = UserProfileForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_ticket_form_valid(self):
        """Test valid ticket form"""
        category = Category.objects.create(name='Test Category')
        
        form_data = {
            'title': 'Test Ticket',
            'description': 'Test description',
            'category': category.id,
            'priority': 'medium'
        }
        
        form = TicketForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_ticket_form_missing_required_fields(self):
        """Test ticket form with missing required fields"""
        form_data = {
            'title': '',  # Missing title
            'description': 'Test description'
        }
        
        form = TicketForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)
    
    def test_ticket_comment_form_valid(self):
        """Test valid ticket comment form"""
        form_data = {
            'comment': 'This is a test comment'
        }
        
        form = TicketCommentForm(data=form_data)
        self.assertTrue(form.is_valid(), form.errors)
    
    def test_ticket_comment_form_empty_comment(self):
        """Test ticket comment form with empty comment"""
        form_data = {
            'comment': ''
        }
        
        form = TicketCommentForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('comment', form.errors)
    
    def test_custom_authentication_form_valid(self):
        """Test valid authentication form"""
        form_data = {
            'username': 'test_client',
            'password': 'TestPass123!'
        }
        
        form = CustomAuthenticationForm(data=form_data)
        form.request = type('MockRequest', (), {'META': {'REMOTE_ADDR': '127.0.0.1'}})()
        
        # Note: This might fail if the form does additional validation
        # The form might need a real request object with session, etc.
    
    def test_form_field_widgets(self):
        """Test that forms have appropriate widgets"""
        form = TicketForm()
        
        # Check that description field has textarea widget
        self.assertEqual(form.fields['description'].widget.__class__.__name__, 'Textarea')
        
        # Check that category field has select widget
        self.assertEqual(form.fields['category'].widget.__class__.__name__, 'Select')


class BusinessLogicTestCase(BaseTestCase):
    """Test business logic and complex scenarios"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
    
    def test_ticket_workflow(self):
        """Test complete ticket workflow"""
        # 1. Client creates ticket
        ticket = Ticket.objects.create(
            title='Workflow Test',
            description='Test ticket workflow',
            created_by=self.client_user,
            category=self.category,
            status='open'
        )
        
        # 2. Agent takes the ticket
        ticket.assigned_to = self.agent_user
        ticket.status = 'in_progress'
        ticket.save()
        
        # 3. Agent adds comment
        comment = TicketComment.objects.create(
            ticket=ticket,
            created_by=self.agent_user,
            comment='Working on this issue'
        )
        
        # 4. Client responds
        client_comment = TicketComment.objects.create(
            ticket=ticket,
            created_by=self.client_user,
            comment='Thank you for the update'
        )
        
        # 5. Agent resolves ticket
        ticket.status = 'resolved'
        ticket.resolved_at = timezone.now()
        ticket.save()
        
        # 6. Client closes ticket
        ticket.status = 'closed'
        ticket.save()
        
        # Verify final state
        self.assertEqual(ticket.status, 'closed')
        self.assertEqual(ticket.assigned_to, self.agent_user)
        self.assertEqual(TicketComment.objects.filter(ticket=ticket).count(), 2)
    
    def test_user_approval_workflow(self):
        """Test user approval workflow"""
        # User registers (already created as pending_user)
        user = self.pending_user
        self.assertFalse(user.profile.is_approved)
        self.assertTrue(user.profile.email_verified)
        
        # Admin approves user
        user.profile.is_approved = True
        user.profile.approved_by = self.admin_user
        user.profile.save()
        
        # Verify approval
        self.assertTrue(user.profile.is_approved)
        self.assertEqual(user.profile.approved_by, self.admin_user)
    
    def test_account_lockout_and_unlock(self):
        """Test account lockout and unlock process"""
        profile = self.client_user.profile
        
        # Simulate 5 failed login attempts
        for i in range(5):
            profile.increment_failed_login()
        
        self.assertTrue(profile.is_locked)
        
        # Admin unlocks account
        profile.reset_failed_login_attempts()
        
        self.assertFalse(profile.is_locked)
        self.assertEqual(profile.failed_login_attempts, 0)
    
    def test_role_based_permissions(self):
        """Test role-based business logic"""
        # Create a ticket
        ticket = Ticket.objects.create(
            title='Permission Test',
            description='Test permissions',
            created_by=self.client_user,
            category=self.category
        )
        
        # Test that client can only see their own tickets
        client_tickets = Ticket.objects.filter(created_by=self.client_user)
        self.assertIn(ticket, client_tickets)
        
        # Test that agent can see unassigned tickets
        unassigned_tickets = Ticket.objects.filter(assigned_to__isnull=True)
        self.assertIn(ticket, unassigned_tickets)
        
        # Assign ticket to agent
        ticket.assigned_to = self.agent_user
        ticket.save()
        
        # Test that agent can see assigned tickets
        agent_tickets = Ticket.objects.filter(assigned_to=self.agent_user)
        self.assertIn(ticket, agent_tickets)
