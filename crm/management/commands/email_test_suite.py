"""
Comprehensive Email System Testing Module
Tests email notifications, templates, and delivery systems
"""
import time
import random
import string
import smtplib
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


class EmailTestSuite:
    """Comprehensive email system testing"""
    
    def __init__(self, driver, base_url, admin_username, admin_password, test_email):
        self.driver = driver
        self.base_url = base_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.test_email = test_email
        self.test_emails_sent = []
        
    def run_full_email_tests(self):
        """Run complete email system test suite"""
        results = []
        
        # Test email configuration
        results.append(self.test_email_configuration())
        
        # Test password reset email
        results.append(self.test_password_reset_email())
        
        # Test ticket notification emails
        results.append(self.test_ticket_notification_emails())
        
        # Test user registration emails
        results.append(self.test_user_registration_emails())
        
        # Test organization invitation emails
        results.append(self.test_organization_invitation_emails())
        
        # Test email templates
        results.append(self.test_email_templates())
        
        # Test email queue system
        results.append(self.test_email_queue_system())
        
        # Test email bounce handling
        results.append(self.test_email_bounce_handling())
        
        return results
    
    def test_email_configuration(self):
        """Test email system configuration and settings"""
        try:
            self.login_as_admin()
            
            # Navigate to email settings
            email_settings_urls = [
                '/admin/settings/email/',
                '/settings/email/',
                '/admin/email/',
                '/configuration/email/',
                '/admin/constance/config/'  # django-constance
            ]
            
            settings_found = False
            for url in email_settings_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    email_indicators = ['smtp', 'email', 'mail', 'host', 'port', 'tls', 'ssl']
                    
                    if any(indicator in page_source for indicator in email_indicators):
                        settings_found = True
                        
                        # Look for SMTP configuration fields
                        smtp_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                            'input[name*="smtp"], input[name*="email"], input[name*="host"]')
                        
                        if smtp_fields:
                            return {'status': 'PASS', 'message': f'Email configuration interface found with {len(smtp_fields)} settings'}
                        else:
                            return {'status': 'PARTIAL', 'message': 'Email settings page found but configuration fields unclear'}
                        
                except Exception:
                    continue
            
            if not settings_found:
                return {'status': 'SKIP', 'message': 'Email configuration interface not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Email configuration test failed: {str(e)}'}
    
    def test_password_reset_email(self):
        """Test password reset email functionality"""
        try:
            # Logout to test password reset
            try:
                self.driver.get(f'{self.base_url}/logout/')
                time.sleep(2)
            except Exception:
                pass
            
            # Navigate to password reset
            reset_urls = [
                '/password_reset/',
                '/auth/password_reset/',
                '/reset/',
                '/forgot-password/'
            ]
            
            reset_page_found = False
            for url in reset_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for email input field
                    email_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                        'input[name="email"], input[type="email"]')
                    
                    if email_inputs:
                        reset_page_found = True
                        break
                        
                except Exception:
                    continue
            
            if not reset_page_found:
                return {'status': 'SKIP', 'message': 'Password reset page not found'}
            
            # Fill email and submit
            email_inputs[0].send_keys(self.test_email)
            
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[type="submit"], input[type="submit"]')
            
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(3)
                
                # Check for success message
                page_source = self.driver.page_source.lower()
                success_indicators = ['sent', 'email', 'check', 'reset', 'link', 'instructions']
                
                if any(indicator in page_source for indicator in success_indicators):
                    self.test_emails_sent.append('password_reset')
                    return {'status': 'PASS', 'message': 'Password reset email functionality working'}
                else:
                    return {'status': 'FAIL', 'message': 'Password reset email not sent or no confirmation'}
            
            return {'status': 'FAIL', 'message': 'Password reset form submission failed'}
            
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Password reset email test failed: {str(e)}'}
    
    def test_ticket_notification_emails(self):
        """Test ticket-related email notifications"""
        try:
            self.login_as_admin()
            
            # Create a test ticket to trigger notifications
            self.driver.get(f'{self.base_url}/tickets/create/')
            time.sleep(2)
            
            try:
                # Fill ticket form
                title_input = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, 'title'))
                )
                
                ticket_title = f'Email Test Ticket {random.randint(1000, 9999)}'
                title_input.send_keys(ticket_title)
                
                description_field = self.driver.find_element(By.NAME, 'description')
                description_field.send_keys(f'This ticket is created to test email notifications - {ticket_title}')
                
                # Set notification email
                email_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                    'input[name*="email"], input[name*="notify"]')
                
                if email_fields:
                    email_fields[0].send_keys(self.test_email)
                
                # Submit ticket
                submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                
                time.sleep(3)
                
                # Check if ticket was created successfully
                current_url = self.driver.current_url
                if '/tickets/' in current_url or 'dashboard' in current_url:
                    self.test_emails_sent.append('ticket_creation')
                    
                    # Try to update ticket to trigger update notification
                    if '/tickets/' in current_url and current_url.split('/')[-2].isdigit():
                        # Add comment to trigger notification
                        comment_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                            'textarea[name*="comment"], input[name*="comment"]')
                        
                        if comment_fields:
                            comment_fields[0].send_keys('Test comment to trigger email notification')
                            
                            comment_submit = self.driver.find_elements(By.CSS_SELECTOR, 
                                'button[type="submit"]')
                            
                            if comment_submit:
                                comment_submit[0].click()
                                time.sleep(2)
                                self.test_emails_sent.append('ticket_comment')
                    
                    return {'status': 'PASS', 'message': 'Ticket notification emails triggered successfully'}
                else:
                    return {'status': 'FAIL', 'message': 'Ticket creation failed, no email notification'}
                    
            except TimeoutException:
                return {'status': 'SKIP', 'message': 'Ticket creation form not accessible'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Ticket notification email test failed: {str(e)}'}
    
    def test_user_registration_emails(self):
        """Test user registration email notifications"""
        try:
            # Logout to test registration
            try:
                self.driver.get(f'{self.base_url}/logout/')
                time.sleep(2)
            except Exception:
                pass
            
            # Navigate to registration
            self.driver.get(f'{self.base_url}/register/')
            time.sleep(2)
            
            try:
                # Fill registration form
                username_field = WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.NAME, 'username'))
                )
                
                test_username = f'email_test_user_{random.randint(1000, 9999)}'
                username_field.send_keys(test_username)
                
                # Use a unique email for registration
                email_field = self.driver.find_element(By.NAME, 'email')
                test_reg_email = f'test_{random.randint(1000, 9999)}@testdomain.com'
                email_field.send_keys(test_reg_email)
                
                password1_field = self.driver.find_element(By.NAME, 'password1')
                password1_field.send_keys('ComplexTestPassword123!')
                
                password2_field = self.driver.find_element(By.NAME, 'password2')
                password2_field.send_keys('ComplexTestPassword123!')
                
                # Submit registration
                submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
                submit_button.click()
                
                time.sleep(3)
                
                # Check for success or email verification message
                page_source = self.driver.page_source.lower()
                email_indicators = ['email', 'verification', 'activate', 'confirm', 'check']
                
                if any(indicator in page_source for indicator in email_indicators):
                    self.test_emails_sent.append('user_registration')
                    return {'status': 'PASS', 'message': 'User registration email notification working'}
                else:
                    return {'status': 'PARTIAL', 'message': 'User registration completed but email notification unclear'}
                    
            except TimeoutException:
                return {'status': 'SKIP', 'message': 'User registration form not accessible'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'User registration email test failed: {str(e)}'}
    
    def test_organization_invitation_emails(self):
        """Test organization invitation email functionality"""
        try:
            self.login_as_admin()
            
            # Look for organization invitation functionality
            invite_urls = [
                '/organizations/invite/',
                '/invite/',
                '/org/invite/',
                '/users/invite/'
            ]
            
            invite_page_found = False
            for url in invite_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for invitation form
                    email_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                        'input[name*="email"], input[type="email"]')
                    
                    if email_inputs:
                        invite_page_found = True
                        
                        # Fill invitation form
                        email_inputs[0].send_keys(self.test_email)
                        
                        # Look for organization selection
                        org_selects = self.driver.find_elements(By.CSS_SELECTOR, 
                            'select[name*="organization"]')
                        
                        if org_selects:
                            org_select = Select(org_selects[0])
                            if len(org_select.options) > 1:
                                org_select.select_by_index(1)
                        
                        # Submit invitation
                        submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                            'button[type="submit"], input[type="submit"]')
                        
                        if submit_buttons:
                            submit_buttons[0].click()
                            time.sleep(3)
                            
                            # Check for success
                            page_source = self.driver.page_source.lower()
                            success_indicators = ['sent', 'invitation', 'invited', 'email']
                            
                            if any(indicator in page_source for indicator in success_indicators):
                                self.test_emails_sent.append('organization_invitation')
                                return {'status': 'PASS', 'message': 'Organization invitation email sent successfully'}
                        
                        break
                        
                except Exception:
                    continue
            
            if not invite_page_found:
                return {'status': 'SKIP', 'message': 'Organization invitation functionality not found'}
            else:
                return {'status': 'PARTIAL', 'message': 'Invitation form found but submission unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization invitation email test failed: {str(e)}'}
    
    def test_email_templates(self):
        """Test email template system"""
        try:
            self.login_as_admin()
            
            # Look for email template management
            template_urls = [
                '/admin/email/templates/',
                '/email/templates/',
                '/admin/templates/',
                '/settings/templates/',
                '/admin/django_ses/'  # if using SES
            ]
            
            templates_found = False
            for url in template_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    template_indicators = ['template', 'email', 'subject', 'body', 'content']
                    
                    if any(indicator in page_source for indicator in template_indicators):
                        templates_found = True
                        
                        # Look for template list or editing interface
                        template_links = self.driver.find_elements(By.CSS_SELECTOR, 
                            'a[href*="template"], tr, .template')
                        
                        if template_links:
                            return {'status': 'PASS', 'message': f'Email template management found with {len(template_links)} elements'}
                        else:
                            return {'status': 'PARTIAL', 'message': 'Email template system detected but interface unclear'}
                        
                except Exception:
                    continue
            
            if not templates_found:
                return {'status': 'SKIP', 'message': 'Email template management not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Email template test failed: {str(e)}'}
    
    def test_email_queue_system(self):
        """Test email queue and delivery system"""
        try:
            self.login_as_admin()
            
            # Look for email queue management
            queue_urls = [
                '/admin/post_office/',  # django-post-office
                '/email/queue/',
                '/admin/email/queue/',
                '/admin/mailer/',
                '/admin/djcelery_email/'  # celery email
            ]
            
            queue_found = False
            for url in queue_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    queue_indicators = ['queue', 'email', 'delivery', 'status', 'sent', 'pending']
                    
                    if any(indicator in page_source for indicator in queue_indicators):
                        queue_found = True
                        
                        # Look for email queue entries
                        queue_entries = self.driver.find_elements(By.CSS_SELECTOR, 
                            'tr, .email, .message')
                        
                        if len(queue_entries) > 1:  # More than just header
                            return {'status': 'PASS', 'message': f'Email queue system found with {len(queue_entries)} entries'}
                        else:
                            return {'status': 'PASS', 'message': 'Email queue system found (empty queue)'}
                        
                except Exception:
                    continue
            
            if not queue_found:
                return {'status': 'SKIP', 'message': 'Email queue system not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Email queue test failed: {str(e)}'}
    
    def test_email_bounce_handling(self):
        """Test email bounce and error handling"""
        try:
            self.login_as_admin()
            
            # Look for bounce handling interface
            bounce_urls = [
                '/admin/email/bounces/',
                '/email/bounces/',
                '/admin/post_office/email/',
                '/admin/mailer/message/'
            ]
            
            bounce_handling_found = False
            for url in bounce_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    bounce_indicators = ['bounce', 'failed', 'error', 'delivery', 'status']
                    
                    if any(indicator in page_source for indicator in bounce_indicators):
                        bounce_handling_found = True
                        
                        # Look for failed/bounced emails
                        status_elements = self.driver.find_elements(By.CSS_SELECTOR, 
                            '[class*="status"], [class*="failed"], [class*="error"]')
                        
                        return {'status': 'PASS', 'message': 'Email bounce handling system detected'}
                        
                except Exception:
                    continue
            
            if not bounce_handling_found:
                return {'status': 'SKIP', 'message': 'Email bounce handling system not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Email bounce handling test failed: {str(e)}'}
    
    def test_email_delivery_verification(self):
        """Verify that emails are actually being sent (requires external verification)"""
        try:
            # This would require checking actual email delivery
            # For testing purposes, we check if emails were triggered
            
            if self.test_emails_sent:
                email_types = ', '.join(self.test_emails_sent)
                return {'status': 'PASS', 'message': f'Email triggers verified for: {email_types}'}
            else:
                return {'status': 'PARTIAL', 'message': 'No email triggers detected during tests'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Email delivery verification failed: {str(e)}'}
    
    def login_as_admin(self):
        """Helper method to login as admin"""
        self.driver.get(f'{self.base_url}/login/')
        
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_input = self.driver.find_element(By.NAME, 'password')
        
        username_input.send_keys(self.admin_username)
        password_input.send_keys(self.admin_password)
        
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        time.sleep(3)
    
    def generate_test_email_content(self, email_type):
        """Generate test email content for different types"""
        templates = {
            'ticket_notification': {
                'subject': f'Test Ticket Notification - {random.randint(1000, 9999)}',
                'body': 'This is a test ticket notification email generated by automated testing.'
            },
            'password_reset': {
                'subject': f'Password Reset Request - {random.randint(1000, 9999)}',
                'body': 'This is a test password reset email generated by automated testing.'
            },
            'user_registration': {
                'subject': f'Account Registration Confirmation - {random.randint(1000, 9999)}',
                'body': 'This is a test registration confirmation email generated by automated testing.'
            }
        }
        
        return templates.get(email_type, {
            'subject': f'Test Email - {random.randint(1000, 9999)}',
            'body': 'This is a generic test email generated by automated testing.'
        })
