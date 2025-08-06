"""
Base test configuration and utilities for the CRM system tests.
"""
import os
from django.test import TestCase, TransactionTestCase, LiveServerTestCase
from django.contrib.auth.models import User
from django.conf import settings
from django.core.management import call_command
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import random
import string
from crm.models import UserProfile, ActivityLog, EmailVerification

class BaseTestCase(TestCase):
    """Base test case with common setup and utilities"""
    
    @classmethod
    def setUpTestData(cls):
        """Set up test data that will be used by multiple test methods"""
        # Create test users with different roles
        cls.admin_user = User.objects.create_user(
            username='test_admin',
            email='admin@test.com',
            password='TestPass123!',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        cls.admin_profile = UserProfile.objects.create(
            user=cls.admin_user,
            role='admin',
            is_approved=True,
            email_verified=True
        )
        
        cls.agent_user = User.objects.create_user(
            username='test_agent',
            email='agent@test.com',
            password='TestPass123!',
            is_active=True
        )
        cls.agent_profile = UserProfile.objects.create(
            user=cls.agent_user,
            role='agent',
            is_approved=True,
            email_verified=True
        )
        
        cls.client_user = User.objects.create_user(
            username='test_client',
            email='client@test.com',
            password='TestPass123!',
            is_active=True
        )
        cls.client_profile = UserProfile.objects.create(
            user=cls.client_user,
            role='client',
            is_approved=True,
            email_verified=True
        )
        
        cls.viewer_user = User.objects.create_user(
            username='test_viewer',
            email='viewer@test.com',
            password='TestPass123!',
            is_active=True
        )
        cls.viewer_profile = UserProfile.objects.create(
            user=cls.viewer_user,
            role='viewer',
            is_approved=True,
            email_verified=True
        )
        
        # Unverified user for email verification tests
        cls.unverified_user = User.objects.create_user(
            username='test_unverified',
            email='unverified@test.com',
            password='TestPass123!',
            is_active=False
        )
        cls.unverified_profile = UserProfile.objects.create(
            user=cls.unverified_user,
            role='client',
            is_approved=False,
            email_verified=False
        )
        
        # Pending approval user
        cls.pending_user = User.objects.create_user(
            username='test_pending',
            email='pending@test.com',
            password='TestPass123!',
            is_active=True
        )
        cls.pending_profile = UserProfile.objects.create(
            user=cls.pending_user,
            role='client',
            is_approved=False,
            email_verified=True
        )
    
    def setUp(self):
        """Set up for each test method"""
        # Clear activity logs before each test
        ActivityLog.objects.all().delete()
    
    def generate_random_string(self, length=8):
        """Generate random string for test data"""
        return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    
    def generate_random_email(self):
        """Generate random email for test data"""
        return f"test_{self.generate_random_string()}@example.com"
    
    def assert_activity_log_created(self, user, action_type, count=1):
        """Assert that activity log was created"""
        logs = ActivityLog.objects.filter(user=user, action_type=action_type)
        self.assertEqual(logs.count(), count, 
                        f"Expected {count} {action_type} log(s) for user {user.username}, got {logs.count()}")
        return logs.first() if count == 1 else logs
    
    def assert_no_activity_log(self, user, action_type):
        """Assert that no activity log was created"""
        logs = ActivityLog.objects.filter(user=user, action_type=action_type)
        self.assertEqual(logs.count(), 0, 
                        f"Expected no {action_type} logs for user {user.username}, got {logs.count()}")


class SeleniumTestCase(LiveServerTestCase):
    """Base test case for Selenium tests"""
    
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Set up Chrome driver
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # Run headless by default
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # You can set environment variable to run with visible browser
        if os.environ.get('SHOW_BROWSER'):
            chrome_options.headless = False
        
        cls.selenium = webdriver.Chrome(options=chrome_options)
        cls.selenium.implicitly_wait(10)
    
    @classmethod
    def tearDownClass(cls):
        cls.selenium.quit()
        super().tearDownClass()
    
    def setUp(self):
        """Set up for each Selenium test"""
        super().setUp()
        # Clear activity logs
        ActivityLog.objects.all().delete()
        
        # Create test users (same as BaseTestCase)
        self.admin_user = User.objects.create_user(
            username='selenium_admin',
            email='selenium_admin@test.com',
            password='TestPass123!',
            is_active=True,
            is_staff=True,
            is_superuser=True
        )
        UserProfile.objects.create(
            user=self.admin_user,
            role='admin',
            is_approved=True,
            email_verified=True
        )
        
        self.agent_user = User.objects.create_user(
            username='selenium_agent',
            email='selenium_agent@test.com',
            password='TestPass123!',
            is_active=True
        )
        UserProfile.objects.create(
            user=self.agent_user,
            role='agent',
            is_approved=True,
            email_verified=True
        )
        
        self.client_user = User.objects.create_user(
            username='selenium_client',
            email='selenium_client@test.com',
            password='TestPass123!',
            is_active=True
        )
        UserProfile.objects.create(
            user=self.client_user,
            role='client',
            is_approved=True,
            email_verified=True
        )
    
    def login_user(self, username, password):
        """Helper method to login a user via Selenium"""
        self.selenium.get(f'{self.live_server_url}/login/')
        
        username_input = self.selenium.find_element(By.NAME, 'username')
        password_input = self.selenium.find_element(By.NAME, 'password')
        submit_button = self.selenium.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        
        username_input.send_keys(username)
        password_input.send_keys(password)
        submit_button.click()
        
        # Wait for redirect after login
        WebDriverWait(self.selenium, 10).until(
            lambda driver: '/login/' not in driver.current_url
        )
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        return WebDriverWait(self.selenium, timeout).until(
            EC.presence_of_element_located((by, value))
        )
    
    def wait_for_clickable(self, by, value, timeout=10):
        """Wait for element to be clickable"""
        return WebDriverWait(self.selenium, timeout).until(
            EC.element_to_be_clickable((by, value))
        )
    
    def assert_url_contains(self, expected_part):
        """Assert that current URL contains expected part"""
        current_url = self.selenium.current_url
        self.assertIn(expected_part, current_url, 
                     f"Expected URL to contain '{expected_part}', got '{current_url}'")
    
    def assert_element_present(self, by, value):
        """Assert that element is present on the page"""
        try:
            self.selenium.find_element(by, value)
        except:
            self.fail(f"Element {by}='{value}' not found on page")
    
    def assert_element_not_present(self, by, value):
        """Assert that element is not present on the page"""
        try:
            self.selenium.find_element(by, value)
            self.fail(f"Element {by}='{value}' should not be present on page")
        except:
            pass  # Element not found, which is what we want
    
    def get_activity_log_count(self, user, action_type):
        """Get count of activity logs for user and action type"""
        return ActivityLog.objects.filter(user=user, action_type=action_type).count()
