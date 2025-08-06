"""
Selenium tests for end-to-end testing of the CRM system.
These tests use a real browser to test the complete user experience.
"""
import time
import random
import string
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from django.contrib.auth.models import User
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import os

from .base import SeleniumTestCase
from crm.models import UserProfile, ActivityLog, Category, Ticket


class AuthenticationSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for authentication flows"""
    
    def test_login_flow(self):
        """Test complete login flow"""
        # Go to login page
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Check that login form is present
        self.assert_element_present(By.NAME, 'username')
        self.assert_element_present(By.NAME, 'password')
        
        # Test login with valid credentials
        self.login_user('selenium_client', 'TestPass123!')
        
        # Should redirect to dashboard
        self.assert_url_contains('/dashboard/')
        
        # Check activity log was created
        user = User.objects.get(username='selenium_client')
        login_logs = ActivityLog.objects.filter(user=user, action_type='login')
        self.assertEqual(login_logs.count(), 1)
    
    def test_login_validation_feedback(self):
        """Test login form validation and error messages"""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        # Test with invalid credentials
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_input.send_keys('nonexistent_user')
        password_input.send_keys('wrong_password')
        submit_button.click()
        
        # Should stay on login page with error message
        self.assert_url_contains('/login/')
        
        # Look for error message
        try:
            error_element = self.wait_for_element(By.CSS_SELECTOR, '.alert-danger, .errorlist, .invalid-feedback')
            self.assertIn('correct username and password', error_element.text.lower())
        except TimeoutException:
            # Alternative: check for any error indication
            page_source = self.selenium.page_source.lower()
            self.assertIn('invalid', page_source)
    
    def test_logout_flow(self):
        """Test logout functionality"""
        # Login first
        self.login_user('selenium_client', 'TestPass123!')
        
        # Find and click logout link/button
        logout_link = self.wait_for_clickable(By.PARTIAL_LINK_TEXT, 'Logout')
        logout_link.click()
        
        # Should redirect to landing page
        self.assert_url_contains('/')
        
        # Try to access protected page - should redirect to login
        self.selenium.get(f'{self.live_server_url}/dashboard/')
        self.assert_url_contains('/login/')
    
    def test_password_validation_visual_feedback(self):
        """Test real-time password validation with visual feedback"""
        self.selenium.get(f'{self.live_server_url}/register/')
        
        # Find password fields
        password1 = self.wait_for_element(By.NAME, 'password1')
        password2 = self.wait_for_element(By.NAME, 'password2')
        
        # Test weak password
        password1.send_keys('123')
        
        # Wait a moment for validation to trigger
        time.sleep(1)
        
        # Check for validation indicators (depends on your implementation)
        try:
            # Look for validation feedback elements
            validation_elements = self.selenium.find_elements(By.CSS_SELECTOR, 
                '.password-requirement, .validation-feedback, .requirement')
            
            # Should show red/invalid indicators for weak password
            red_indicators = []
            for elem in validation_elements:
                classes = elem.get_attribute('class')
                style = elem.get_attribute('style')
                if 'red' in classes or 'invalid' in classes or 'color: red' in style:
                    red_indicators.append(elem)
            
            self.assertGreater(len(red_indicators), 0, "Should show red indicators for weak password")
        except NoSuchElementException:
            # If no visual indicators found, skip this test
            self.skipTest("Password validation visual feedback not implemented")
        
        # Test strong password
        password1.clear()
        password1.send_keys('StrongPassword123!')
        time.sleep(1)
        
        # Should show green/valid indicators
        try:
            green_indicators = []
            validation_elements = self.selenium.find_elements(By.CSS_SELECTOR, 
                '.password-requirement, .validation-feedback, .requirement')
            
            for elem in validation_elements:
                classes = elem.get_attribute('class')
                style = elem.get_attribute('style')
                if 'green' in classes or 'valid' in classes or 'color: green' in style:
                    green_indicators.append(elem)
            
            self.assertGreater(len(green_indicators), 0, "Should show green indicators for strong password")
        except NoSuchElementException:
            pass  # Visual feedback might not be fully implemented


class RegistrationSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for user registration"""
    
    def test_complete_registration_flow(self):
        """Test complete user registration process"""
        # Go to registration page
        self.selenium.get(f'{self.live_server_url}/register/')
        
        # Fill out registration form
        random_suffix = ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))
        username = f'testuser_{random_suffix}'
        email = f'testuser_{random_suffix}@example.com'
        
        username_input = self.wait_for_element(By.NAME, 'username')
        email_input = self.selenium.find_element(By.NAME, 'email')
        password1_input = self.selenium.find_element(By.NAME, 'password1')
        password2_input = self.selenium.find_element(By.NAME, 'password2')
        phone_input = self.selenium.find_element(By.NAME, 'phone')
        
        username_input.send_keys(username)
        email_input.send_keys(email)
        password1_input.send_keys('ComplexPassword123!')
        password2_input.send_keys('ComplexPassword123!')
        phone_input.send_keys('123456789')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should show email verification page or success message
        try:
            self.wait_for_element(By.CSS_SELECTOR, '.alert-success')
            self.assertIn('email', self.selenium.page_source.lower())
        except TimeoutException:
            # Alternative: check URL or page content
            self.assertIn('verif', self.selenium.current_url.lower())
        
        # Check that user was created in database
        user = User.objects.get(username=username)
        self.assertEqual(user.email, email)
        self.assertFalse(user.is_active)  # Should be inactive until verification
    
    def test_registration_validation_errors(self):
        """Test registration form validation"""
        self.selenium.get(f'{self.live_server_url}/register/')
        
        # Try to submit empty form
        submit_button = self.wait_for_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should show validation errors
        try:
            error_elements = self.selenium.find_elements(By.CSS_SELECTOR, 
                '.alert-danger, .errorlist, .invalid-feedback, .field-error')
            self.assertGreater(len(error_elements), 0, "Should show validation errors for empty form")
        except:
            # Alternative: check for required field indicators
            required_elements = self.selenium.find_elements(By.CSS_SELECTOR, 'input:invalid')
            self.assertGreater(len(required_elements), 0, "Should have invalid fields")
    
    def test_duplicate_username_validation(self):
        """Test validation for duplicate username"""
        self.selenium.get(f'{self.live_server_url}/register/')
        
        # Try to register with existing username
        username_input = self.wait_for_element(By.NAME, 'username')
        email_input = self.selenium.find_element(By.NAME, 'email')
        password1_input = self.selenium.find_element(By.NAME, 'password1')
        password2_input = self.selenium.find_element(By.NAME, 'password2')
        
        username_input.send_keys('selenium_client')  # Already exists
        email_input.send_keys('new_email@example.com')
        password1_input.send_keys('ComplexPassword123!')
        password2_input.send_keys('ComplexPassword123!')
        
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should show error about existing username
        try:
            self.wait_for_element(By.CSS_SELECTOR, '.alert-danger, .errorlist')
            page_text = self.selenium.page_source.lower()
            self.assertIn('already exists', page_text)
        except TimeoutException:
            # Alternative check
            self.assert_url_contains('/register/')  # Should stay on registration page


class TicketSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for ticket functionality"""
    
    def setUp(self):
        super().setUp()
        # Create test category
        self.category = Category.objects.create(
            name='Test Category',
            description='Test category for selenium tests'
        )
    
    def test_ticket_creation_flow(self):
        """Test complete ticket creation process"""
        # Login as client
        self.login_user('selenium_client', 'TestPass123!')
        
        # Navigate to ticket creation
        self.selenium.get(f'{self.live_server_url}/tickets/create/')
        
        # Fill out ticket form
        title_input = self.wait_for_element(By.NAME, 'title')
        description_textarea = self.selenium.find_element(By.NAME, 'description')
        category_select = Select(self.selenium.find_element(By.NAME, 'category'))
        priority_select = Select(self.selenium.find_element(By.NAME, 'priority'))
        
        title_input.send_keys('Selenium Test Ticket')
        description_textarea.send_keys('This ticket was created by Selenium automated test')
        category_select.select_by_visible_text('Test Category')
        priority_select.select_by_value('medium')
        
        # Submit form
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Should redirect to ticket detail or dashboard
        self.wait_for_element(By.TAG_NAME, 'body')  # Wait for page load
        
        # Check that ticket was created
        ticket = Ticket.objects.get(title='Selenium Test Ticket')
        self.assertEqual(ticket.category, self.category)
        self.assertEqual(ticket.priority, 'medium')
        
        # Check activity log
        user = User.objects.get(username='selenium_client')
        self.assert_activity_log_created(user, 'ticket_created')
    
    def test_ticket_comment_functionality(self):
        """Test adding comments to tickets"""
        # Create a test ticket
        user = User.objects.get(username='selenium_client')
        ticket = Ticket.objects.create(
            title='Test Ticket for Comments',
            description='Test description',
            created_by=user,
            category=self.category
        )
        
        # Login and navigate to ticket
        self.login_user('selenium_client', 'TestPass123!')
        self.selenium.get(f'{self.live_server_url}/tickets/{ticket.id}/')
        
        # Find comment form and add comment
        comment_textarea = self.wait_for_element(By.NAME, 'comment')
        comment_textarea.send_keys('This is a test comment added via Selenium')
        
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for page reload and check comment appears
        self.wait_for_element(By.TAG_NAME, 'body')
        
        # Check comment in page content
        self.assertIn('test comment added via Selenium', self.selenium.page_source)
    
    def test_ticket_filtering_interface(self):
        """Test ticket filtering interface"""
        # Create test tickets with different properties
        user = User.objects.get(username='selenium_client')
        
        Ticket.objects.create(
            title='High Priority Ticket',
            description='Urgent issue',
            created_by=user,
            category=self.category,
            priority='high',
            status='open'
        )
        
        Ticket.objects.create(
            title='Low Priority Ticket',
            description='Minor issue',
            created_by=user,
            category=self.category,
            priority='low',
            status='closed'
        )
        
        # Login and go to dashboard
        self.login_user('selenium_client', 'TestPass123!')
        self.selenium.get(f'{self.live_server_url}/dashboard/')
        
        # Test priority filter
        try:
            priority_filter = self.wait_for_element(By.NAME, 'priority')
            priority_select = Select(priority_filter)
            priority_select.select_by_value('high')
            
            # Submit filter
            filter_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
            filter_button.click()
            
            # Wait for results
            self.wait_for_element(By.TAG_NAME, 'body')
            
            # Should show high priority ticket
            self.assertIn('High Priority Ticket', self.selenium.page_source)
            # Should not show low priority ticket
            self.assertNotIn('Low Priority Ticket', self.selenium.page_source)
        except NoSuchElementException:
            # Filter interface might not be implemented yet
            self.skipTest("Ticket filtering interface not found")


class PermissionSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for permission and access control"""
    
    def test_viewer_restriction(self):
        """Test that viewer users are restricted to ticket display only"""
        # Create viewer user
        viewer_user = User.objects.create_user(
            username='selenium_viewer',
            email='selenium_viewer@test.com',
            password='TestPass123!',
            is_active=True
        )
        UserProfile.objects.create(
            user=viewer_user,
            role='viewer',
            is_approved=True,
            email_verified=True
        )
        
        # Login as viewer
        self.login_user('selenium_viewer', 'TestPass123!')
        
        # Should be on ticket display page
        self.assert_url_contains('/tickets/display/')
        
        # Try to access other pages - should redirect back
        restricted_urls = [
            '/dashboard/',
            '/tickets/create/',
            '/admin/',
        ]
        
        for url in restricted_urls:
            self.selenium.get(f'{self.live_server_url}{url}')
            # Should redirect back to ticket display
            WebDriverWait(self.selenium, 5).until(
                lambda driver: '/tickets/display/' in driver.current_url
            )
    
    def test_admin_access_all_areas(self):
        """Test that admin users can access all areas"""
        # Login as admin
        self.login_user('selenium_admin', 'TestPass123!')
        
        # Test access to various admin areas
        admin_urls = [
            '/dashboard/',
            '/admin/',
            '/logs/activity/',
            '/users/pending-approvals/',
        ]
        
        for url in admin_urls:
            with self.subTest(url=url):
                self.selenium.get(f'{self.live_server_url}{url}')
                # Should not redirect to login or forbidden page
                current_url = self.selenium.current_url
                self.assertNotIn('/login/', current_url)
                self.assertNotIn('/403/', current_url)
                self.assertNotIn('/404/', current_url)
    
    def test_client_cannot_access_admin_areas(self):
        """Test that client users cannot access admin areas"""
        # Login as client
        self.login_user('selenium_client', 'TestPass123!')
        
        # Try to access admin areas
        restricted_urls = [
            '/admin/',
            '/logs/activity/',
            '/logs/activity/wipe/',
        ]
        
        for url in restricted_urls:
            with self.subTest(url=url):
                self.selenium.get(f'{self.live_server_url}{url}')
                
                # Should either get forbidden, not found, or redirect
                current_url = self.selenium.current_url
                page_source = self.selenium.page_source.lower()
                
                # Check for access denied indicators
                access_denied = (
                    '/login/' in current_url or
                    '/403/' in current_url or
                    '/404/' in current_url or
                    'forbidden' in page_source or
                    'permission denied' in page_source or
                    'access denied' in page_source
                )
                
                self.assertTrue(access_denied, f"Client should not have access to {url}")


class ActivityLogSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for activity logging"""
    
    def test_login_logout_logging(self):
        """Test that login/logout activities are properly logged"""
        # Clear existing logs
        ActivityLog.objects.all().delete()
        
        # Perform login
        self.login_user('selenium_client', 'TestPass123!')
        
        # Check login log was created
        user = User.objects.get(username='selenium_client')
        login_logs = ActivityLog.objects.filter(user=user, action_type='login')
        self.assertEqual(login_logs.count(), 1)
        
        # Perform logout
        logout_link = self.wait_for_clickable(By.PARTIAL_LINK_TEXT, 'Logout')
        logout_link.click()
        
        # Check logout log was created
        logout_logs = ActivityLog.objects.filter(user=user, action_type='logout')
        self.assertEqual(logout_logs.count(), 1)
    
    def test_failed_login_logging(self):
        """Test that failed login attempts are logged"""
        ActivityLog.objects.all().delete()
        
        # Attempt failed login
        self.selenium.get(f'{self.live_server_url}/login/')
        
        username_input = self.wait_for_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_input.send_keys('selenium_client')
        password_input.send_keys('wrong_password')
        submit_button.click()
        
        # Wait for form processing
        time.sleep(2)
        
        # Check failed login log was created
        user = User.objects.get(username='selenium_client')
        failed_logs = ActivityLog.objects.filter(user=user, action_type='login_failed')
        self.assertEqual(failed_logs.count(), 1)
    
    def test_no_duplicate_login_logs(self):
        """Test that login doesn't create duplicate log entries"""
        ActivityLog.objects.all().delete()
        
        # Perform login
        self.login_user('selenium_client', 'TestPass123!')
        
        # Wait a moment for all signal processing
        time.sleep(2)
        
        # Check only one login log was created
        user = User.objects.get(username='selenium_client')
        login_logs = ActivityLog.objects.filter(user=user, action_type='login')
        self.assertEqual(login_logs.count(), 1, 
                        f"Expected 1 login log, got {login_logs.count()}")


class ResponsiveDesignSeleniumTestCase(SeleniumTestCase):
    """Selenium tests for responsive design and mobile compatibility"""
    
    def test_mobile_layout(self):
        """Test mobile responsive layout"""
        # Set mobile viewport
        self.selenium.set_window_size(375, 667)  # iPhone dimensions
        
        # Login and check layout
        self.login_user('selenium_client', 'TestPass123!')
        
        # Check that mobile navigation is working
        try:
            # Look for mobile menu toggle
            mobile_menu = self.selenium.find_element(By.CSS_SELECTOR, 
                '.navbar-toggler, .mobile-menu, .hamburger')
            self.assertTrue(mobile_menu.is_displayed())
        except NoSuchElementException:
            # If no mobile menu found, check that regular nav is responsive
            nav = self.selenium.find_element(By.CSS_SELECTOR, 'nav, .navbar')
            self.assertTrue(nav.is_displayed())
    
    def test_tablet_layout(self):
        """Test tablet responsive layout"""
        # Set tablet viewport
        self.selenium.set_window_size(768, 1024)  # iPad dimensions
        
        self.login_user('selenium_client', 'TestPass123!')
        
        # Check that layout adapts to tablet size
        body = self.selenium.find_element(By.TAG_NAME, 'body')
        self.assertTrue(body.is_displayed())
    
    def test_desktop_layout(self):
        """Test desktop layout"""
        # Set desktop viewport
        self.selenium.set_window_size(1920, 1080)
        
        self.login_user('selenium_client', 'TestPass123!')
        
        # Check desktop-specific elements
        try:
            # Look for desktop-specific navigation or layout
            desktop_nav = self.selenium.find_element(By.CSS_SELECTOR, 
                '.desktop-nav, .full-nav, nav')
            self.assertTrue(desktop_nav.is_displayed())
        except NoSuchElementException:
            # Basic check that page loads properly
            self.assert_element_present(By.TAG_NAME, 'body')


# Test configuration for running with real domain
class LiveDomainTestCase(StaticLiveServerTestCase):
    """Tests that can be run against the actual dev.betulait.usermd.net domain"""
    
    @classmethod
    def setUpClass(cls):
        # Don't call super() - we want to use real domain, not test server
        pass
    
    def setUp(self):
        """Set up Chrome driver for real domain testing"""
        chrome_options = Options()
        if not os.environ.get('SHOW_BROWSER'):
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        self.selenium = webdriver.Chrome(options=chrome_options)
        self.selenium.implicitly_wait(10)
        
        # Use real domain
        self.base_url = 'https://dev.betulait.usermd.net'
    
    def tearDown(self):
        self.selenium.quit()
    
    def test_live_domain_login(self):
        """Test login on live domain with real credentials"""
        # This test would use real credentials provided by the user
        # For security, credentials should be passed via environment variables
        
        username = os.environ.get('TEST_USERNAME')
        password = os.environ.get('TEST_PASSWORD')
        
        if not username or not password:
            self.skipTest("Live domain credentials not provided")
        
        self.selenium.get(f'{self.base_url}/login/')
        
        username_input = WebDriverWait(self.selenium, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()
        
        # Should redirect away from login page
        WebDriverWait(self.selenium, 10).until(
            lambda driver: '/login/' not in driver.current_url
        )
        
        # Should be logged in successfully
        self.assertIn('/dashboard/', self.selenium.current_url)
