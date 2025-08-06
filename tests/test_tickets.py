"""
Tests for ticket functionality including creation, updates, comments,
status changes, assignments, and access control.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core.files.uploadedfile import SimpleUploadedFile
import tempfile
import os

from .base import BaseTestCase
from crm.models import (
    Ticket, TicketComment, TicketAttachment, Category, 
    ActivityLog, UserProfile
)


class TicketCreationTestCase(BaseTestCase):
    """Test ticket creation functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test categories
        self.category = Category.objects.create(
            name='Technical Issue',
            description='Technical problems'
        )
        self.category2 = Category.objects.create(
            name='Account Issue',
            description='Account related problems'
        )
    
    def test_client_can_create_ticket(self):
        """Test that client can create a ticket"""
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Test Ticket',
            'description': 'This is a test ticket description',
            'category': self.category.id,
            'priority': 'medium'
        })
        
        # Should redirect after creation
        self.assertEqual(response.status_code, 302)
        
        # Check that ticket was created
        ticket = Ticket.objects.get(title='Test Ticket')
        self.assertEqual(ticket.created_by, self.client_user)
        self.assertEqual(ticket.category, self.category)
        self.assertEqual(ticket.priority, 'medium')
        self.assertEqual(ticket.status, 'open')
        
        # Check activity log
        self.assert_activity_log_created(self.client_user, 'ticket_created')
    
    def test_agent_can_create_ticket(self):
        """Test that agent can create a ticket"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Agent Test Ticket',
            'description': 'Agent created ticket',
            'category': self.category.id,
            'priority': 'high',
            'assigned_to': self.agent_user.id
        })
        
        self.assertEqual(response.status_code, 302)
        
        ticket = Ticket.objects.get(title='Agent Test Ticket')
        self.assertEqual(ticket.assigned_to, self.agent_user)
        self.assertEqual(ticket.priority, 'high')
    
    def test_ticket_creation_with_attachment(self):
        """Test ticket creation with file attachment"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Create a temporary file
        test_file = SimpleUploadedFile(
            "test.txt", 
            b"This is test file content", 
            content_type="text/plain"
        )
        
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Ticket with Attachment',
            'description': 'Ticket with file',
            'category': self.category.id,
            'priority': 'low',
            'attachment': test_file
        })
        
        self.assertEqual(response.status_code, 302)
        
        ticket = Ticket.objects.get(title='Ticket with Attachment')
        
        # Check that attachment was created
        attachments = TicketAttachment.objects.filter(ticket=ticket)
        self.assertEqual(attachments.count(), 1)
        
        attachment = attachments.first()
        self.assertTrue(attachment.file.name.endswith('test.txt'))
    
    def test_ticket_creation_validation(self):
        """Test ticket creation form validation"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Test missing required fields
        response = self.client.post(reverse('ticket_create'), {
            'title': '',  # Missing title
            'description': 'Test description',
            'category': self.category.id,
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
        
        # Test invalid category
        response = self.client.post(reverse('ticket_create'), {
            'title': 'Test Ticket',
            'description': 'Test description',
            'category': 99999,  # Non-existent category
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Select a valid choice')
    
    def test_viewer_cannot_create_ticket(self):
        """Test that viewer cannot access ticket creation"""
        self.client.login(username='test_viewer', password='TestPass123!')
        
        response = self.client.get(reverse('ticket_create'))
        
        # Should redirect to ticket display (viewer restriction)
        self.assertRedirects(response, reverse('ticket_display'))


class TicketViewTestCase(BaseTestCase):
    """Test ticket viewing and listing functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        
        # Create test tickets
        self.client_ticket = Ticket.objects.create(
            title='Client Ticket',
            description='Client ticket description',
            created_by=self.client_user,
            category=self.category,
            status='open'
        )
        
        self.agent_ticket = Ticket.objects.create(
            title='Agent Ticket',
            description='Agent ticket description',
            created_by=self.agent_user,
            assigned_to=self.agent_user,
            category=self.category,
            status='in_progress'
        )
        
        self.closed_ticket = Ticket.objects.create(
            title='Closed Ticket',
            description='Closed ticket description',
            created_by=self.client_user,
            category=self.category,
            status='closed'
        )
    
    def test_client_can_view_own_tickets(self):
        """Test that client can view their own tickets"""
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Should see own tickets
        self.assertContains(response, 'Client Ticket')
        self.assertContains(response, 'Closed Ticket')
        
        # Should not see other user's tickets
        self.assertNotContains(response, 'Agent Ticket')
    
    def test_agent_can_view_assigned_tickets(self):
        """Test that agent can view assigned tickets"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Should see assigned tickets
        self.assertContains(response, 'Agent Ticket')
    
    def test_admin_can_view_all_tickets(self):
        """Test that admin can view all tickets"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Should see all tickets
        self.assertContains(response, 'Client Ticket')
        self.assertContains(response, 'Agent Ticket')
        self.assertContains(response, 'Closed Ticket')
    
    def test_ticket_detail_view(self):
        """Test ticket detail view access"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Can view own ticket
        response = self.client.get(reverse('ticket_detail', args=[self.client_ticket.id]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Client Ticket')
        
        # Cannot view other's ticket
        response = self.client.get(reverse('ticket_detail', args=[self.agent_ticket.id]))
        self.assertIn(response.status_code, [403, 404])
    
    def test_ticket_filtering(self):
        """Test ticket filtering functionality"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        # Filter by status
        response = self.client.get(reverse('dashboard'), {'status': 'open'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Client Ticket')
        self.assertNotContains(response, 'Closed Ticket')
        
        # Filter by category
        response = self.client.get(reverse('dashboard'), {'category': self.category.id})
        self.assertEqual(response.status_code, 200)


class TicketUpdateTestCase(BaseTestCase):
    """Test ticket updating functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category,
            status='open'
        )
    
    def test_client_can_update_own_ticket(self):
        """Test that client can update their own ticket"""
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_update', args=[self.ticket.id]), {
            'title': 'Updated Ticket Title',
            'description': 'Updated description',
            'category': self.category.id,
            'priority': 'high'
        })
        
        # Should redirect after update
        self.assertEqual(response.status_code, 302)
        
        # Check that ticket was updated
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.title, 'Updated Ticket Title')
        self.assertEqual(self.ticket.priority, 'high')
        
        # Check activity log
        self.assert_activity_log_created(self.client_user, 'ticket_updated')
    
    def test_agent_can_assign_ticket(self):
        """Test that agent can assign ticket to themselves"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_assign_to_me', args=[self.ticket.id]))
        
        self.assertEqual(response.status_code, 302)
        
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.assigned_to, self.agent_user)
        
        # Check activity log
        self.assert_activity_log_created(self.agent_user, 'ticket_updated')
    
    def test_agent_can_change_ticket_status(self):
        """Test that agent can change ticket status"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        # Assign ticket first
        self.ticket.assigned_to = self.agent_user
        self.ticket.save()
        
        response = self.client.post(reverse('ticket_update', args=[self.ticket.id]), {
            'title': self.ticket.title,
            'description': self.ticket.description,
            'category': self.category.id,
            'status': 'in_progress'
        })
        
        self.assertEqual(response.status_code, 302)
        
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'in_progress')
    
    def test_client_cannot_change_assignment(self):
        """Test that client cannot change ticket assignment"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Try to assign ticket (if assignment field is in form)
        response = self.client.post(reverse('ticket_update', args=[self.ticket.id]), {
            'title': 'Updated Title',
            'description': 'Updated description',
            'category': self.category.id,
            'assigned_to': self.agent_user.id  # Client shouldn't be able to set this
        })
        
        self.ticket.refresh_from_db()
        # Assignment should not have changed (should still be None)
        self.assertIsNone(self.ticket.assigned_to)
    
    def test_ticket_resolution(self):
        """Test ticket resolution process"""
        self.client.login(username='test_agent', password='TestPass123!')
        
        # Assign and resolve ticket
        self.ticket.assigned_to = self.agent_user
        self.ticket.save()
        
        response = self.client.post(reverse('ticket_resolve', args=[self.ticket.id]), {
            'resolution': 'Problem fixed by restarting the service'
        })
        
        self.assertEqual(response.status_code, 302)
        
        self.ticket.refresh_from_db()
        self.assertEqual(self.ticket.status, 'resolved')
        
        # Check activity log
        self.assert_activity_log_created(self.agent_user, 'ticket_resolved')


class TicketCommentTestCase(BaseTestCase):
    """Test ticket commenting functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
    
    def test_client_can_comment_on_own_ticket(self):
        """Test that client can comment on their own ticket"""
        self.client.login(username='test_client', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_comment', args=[self.ticket.id]), {
            'comment': 'This is a test comment from client'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check that comment was created
        comment = TicketComment.objects.get(ticket=self.ticket)
        self.assertEqual(comment.created_by, self.client_user)
        self.assertEqual(comment.comment, 'This is a test comment from client')
        
        # Check activity log
        self.assert_activity_log_created(self.client_user, 'ticket_commented')
    
    def test_agent_can_comment_on_assigned_ticket(self):
        """Test that agent can comment on assigned ticket"""
        self.ticket.assigned_to = self.agent_user
        self.ticket.save()
        
        self.client.login(username='test_agent', password='TestPass123!')
        
        response = self.client.post(reverse('ticket_comment', args=[self.ticket.id]), {
            'comment': 'Agent response to the issue'
        })
        
        self.assertEqual(response.status_code, 302)
        
        comment = TicketComment.objects.get(ticket=self.ticket, created_by=self.agent_user)
        self.assertEqual(comment.comment, 'Agent response to the issue')
    
    def test_comment_validation(self):
        """Test comment form validation"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Test empty comment
        response = self.client.post(reverse('ticket_comment', args=[self.ticket.id]), {
            'comment': ''
        })
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'This field is required')
    
    def test_comment_visibility(self):
        """Test comment visibility in ticket detail"""
        # Create comments from different users
        TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.client_user,
            comment='Client comment'
        )
        
        self.ticket.assigned_to = self.agent_user
        self.ticket.save()
        
        TicketComment.objects.create(
            ticket=self.ticket,
            created_by=self.agent_user,
            comment='Agent response'
        )
        
        self.client.login(username='test_client', password='TestPass123!')
        response = self.client.get(reverse('ticket_detail', args=[self.ticket.id]))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Client comment')
        self.assertContains(response, 'Agent response')


class TicketAttachmentTestCase(BaseTestCase):
    """Test ticket attachment functionality"""
    
    def setUp(self):
        super().setUp()
        self.category = Category.objects.create(name='Test Category')
        
        self.ticket = Ticket.objects.create(
            title='Test Ticket',
            description='Test description',
            created_by=self.client_user,
            category=self.category
        )
    
    def test_add_attachment_to_ticket(self):
        """Test adding attachment to existing ticket"""
        self.client.login(username='test_client', password='TestPass123!')
        
        test_file = SimpleUploadedFile(
            "document.pdf", 
            b"PDF content here", 
            content_type="application/pdf"
        )
        
        response = self.client.post(reverse('ticket_add_attachment', args=[self.ticket.id]), {
            'file': test_file,
            'description': 'Additional documentation'
        })
        
        self.assertEqual(response.status_code, 302)
        
        # Check that attachment was created
        attachment = TicketAttachment.objects.get(ticket=self.ticket)
        self.assertTrue(attachment.file.name.endswith('document.pdf'))
        self.assertEqual(attachment.description, 'Additional documentation')
        
        # Check activity log
        self.assert_activity_log_created(self.client_user, 'ticket_attachment_added')
    
    def test_attachment_file_type_validation(self):
        """Test file type validation for attachments"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Test potentially dangerous file type (if validation exists)
        dangerous_file = SimpleUploadedFile(
            "malware.exe", 
            b"Executable content", 
            content_type="application/x-executable"
        )
        
        response = self.client.post(reverse('ticket_add_attachment', args=[self.ticket.id]), {
            'file': dangerous_file,
            'description': 'Suspicious file'
        })
        
        # Should either reject the file or handle it safely
        # This depends on your file validation implementation
        # You might want to check for specific error messages
    
    def test_attachment_size_limit(self):
        """Test file size limit for attachments"""
        self.client.login(username='test_client', password='TestPass123!')
        
        # Create a large file (if size limits exist)
        large_content = b"x" * (10 * 1024 * 1024)  # 10MB
        large_file = SimpleUploadedFile(
            "large_file.txt", 
            large_content, 
            content_type="text/plain"
        )
        
        response = self.client.post(reverse('ticket_add_attachment', args=[self.ticket.id]), {
            'file': large_file,
            'description': 'Large file'
        })
        
        # Should handle according to your size limit policy
        # Check for appropriate error message if size limit exists


class TicketSearchTestCase(BaseTestCase):
    """Test ticket search and filtering functionality"""
    
    def setUp(self):
        super().setUp()
        self.category1 = Category.objects.create(name='Technical')
        self.category2 = Category.objects.create(name='Account')
        
        # Create various tickets for search testing
        self.tickets = [
            Ticket.objects.create(
                title='Database Connection Issue',
                description='Cannot connect to database server',
                created_by=self.client_user,
                category=self.category1,
                priority='high',
                status='open'
            ),
            Ticket.objects.create(
                title='Password Reset Request',
                description='User forgot password and needs reset',
                created_by=self.client_user,
                category=self.category2,
                priority='medium',
                status='in_progress'
            ),
            Ticket.objects.create(
                title='Server Performance Problem',
                description='Server running slowly, database queries timeout',
                created_by=self.agent_user,
                category=self.category1,
                priority='high',
                status='resolved'
            )
        ]
    
    def test_search_by_title(self):
        """Test searching tickets by title"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'), {'search': 'Database'})
        self.assertEqual(response.status_code, 200)
        
        # Should find tickets with "Database" in title or description
        self.assertContains(response, 'Database Connection Issue')
        self.assertContains(response, 'Server Performance Problem')  # Contains "database" in description
        self.assertNotContains(response, 'Password Reset Request')
    
    def test_filter_by_status(self):
        """Test filtering tickets by status"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'), {'status': 'resolved'})
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Server Performance Problem')
        self.assertNotContains(response, 'Database Connection Issue')
        self.assertNotContains(response, 'Password Reset Request')
    
    def test_filter_by_priority(self):
        """Test filtering tickets by priority"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'), {'priority': 'high'})
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Database Connection Issue')
        self.assertContains(response, 'Server Performance Problem')
        self.assertNotContains(response, 'Password Reset Request')
    
    def test_filter_by_category(self):
        """Test filtering tickets by category"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'), {'category': self.category2.id})
        self.assertEqual(response.status_code, 200)
        
        self.assertContains(response, 'Password Reset Request')
        self.assertNotContains(response, 'Database Connection Issue')
        self.assertNotContains(response, 'Server Performance Problem')
    
    def test_combined_filters(self):
        """Test using multiple filters together"""
        self.client.login(username='test_admin', password='TestPass123!')
        
        response = self.client.get(reverse('dashboard'), {
            'category': self.category1.id,
            'priority': 'high',
            'status': 'open'
        })
        self.assertEqual(response.status_code, 200)
        
        # Should only show tickets matching all criteria
        self.assertContains(response, 'Database Connection Issue')
        self.assertNotContains(response, 'Server Performance Problem')  # resolved, not open
        self.assertNotContains(response, 'Password Reset Request')  # different category
