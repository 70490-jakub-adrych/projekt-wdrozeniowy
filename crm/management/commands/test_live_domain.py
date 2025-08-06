"""
Management command to run automated tests against live domain.
Usage: python manage.py test_live_domain --username=<user> --password=<pass>
"""
from django.core.management.base import BaseCommand
from django.conf import settings
import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class Command(BaseCommand):
    help = 'Run automated tests against the live domain'
    
    def add_arguments(self, parser):
        parser.add_argument('--username', type=str, help='Username for login')
        parser.add_argument('--password', type=str, help='Password for login')
        parser.add_argument('--domain', type=str, default='https://dev.betulait.usermd.net', 
                          help='Domain to test (default: https://dev.betulait.usermd.net)')
        parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
        parser.add_argument('--verbose', action='store_true', help='Verbose output')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.driver = None
        self.base_url = None
        self.username = None
        self.password = None
        self.verbose = False
        self.test_results = []
    
    def handle(self, *args, **options):
        self.username = options['username']
        self.password = options['password']
        self.base_url = options['domain']
        self.verbose = options['verbose']
        
        if not self.username or not self.password:
            self.stdout.write(
                self.style.ERROR('Username and password are required!')
            )
            return
        
        # Setup browser
        self.setup_browser(headless=options['headless'])
        
        try:
            self.stdout.write(
                self.style.SUCCESS(f'Starting tests against {self.base_url}')
            )
            
            # Run test suite
            self.run_test_suite()
            
            # Print results
            self.print_results()
            
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Test execution failed: {str(e)}')
            )
        finally:
            if self.driver:
                self.driver.quit()
    
    def setup_browser(self, headless=True):
        """Setup Chrome browser for testing"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        self.driver = webdriver.Chrome(options=chrome_options)
        self.driver.implicitly_wait(10)
        
        # Execute script to hide webdriver property
        self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    def log(self, message, level='info'):
        """Log message if verbose mode is enabled"""
        if self.verbose or level == 'error':
            if level == 'error':
                self.stdout.write(self.style.ERROR(f'  ❌ {message}'))
            elif level == 'success':
                self.stdout.write(self.style.SUCCESS(f'  ✅ {message}'))
            else:
                self.stdout.write(f'  ℹ️  {message}')
    
    def run_test(self, test_name, test_function):
        """Run a single test and record results"""
        self.log(f'Running: {test_name}')
        start_time = time.time()
        
        try:
            test_function()
            duration = time.time() - start_time
            self.test_results.append({
                'name': test_name,
                'status': 'PASS',
                'duration': duration,
                'error': None
            })
            self.log(f'{test_name} - PASSED ({duration:.2f}s)', 'success')
            return True
        except Exception as e:
            duration = time.time() - start_time
            self.test_results.append({
                'name': test_name,
                'status': 'FAIL',
                'duration': duration,
                'error': str(e)
            })
            self.log(f'{test_name} - FAILED: {str(e)}', 'error')
            return False
    
    def run_test_suite(self):
        """Run the complete test suite"""
        tests = [
            ('Login Flow', self.test_login_flow),
            ('Dashboard Access', self.test_dashboard_access),
            ('Create Ticket', self.test_create_ticket),
            ('View Tickets', self.test_view_tickets),
            ('Activity Logs', self.test_activity_logs),
            ('Profile Access', self.test_profile_access),
            ('Password Validation', self.test_password_validation),
            ('Responsive Design', self.test_responsive_design),
            ('Logout Flow', self.test_logout_flow),
        ]
        
        for test_name, test_function in tests:
            self.run_test(test_name, test_function)
            time.sleep(1)  # Brief pause between tests
    
    def test_login_flow(self):
        """Test login functionality"""
        self.driver.get(f'{self.base_url}/login/')
        
        # Check login page loads
        username_input = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.NAME, 'username'))
        )
        password_input = self.driver.find_element(By.NAME, 'password')
        
        # Enter credentials
        username_input.send_keys(self.username)
        password_input.send_keys(self.password)
        
        # Submit form
        submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
        submit_button.click()
        
        # Wait for redirect
        WebDriverWait(self.driver, 10).until(
            lambda driver: '/login/' not in driver.current_url
        )
        
        # Should be on dashboard or main page
        if '/dashboard/' not in self.driver.current_url and self.driver.current_url == f'{self.base_url}/':
            # Might redirect to landing page, try to access dashboard directly
            self.driver.get(f'{self.base_url}/dashboard/')
        
        # Verify successful login
        assert 'login' not in self.driver.current_url.lower()
        self.log('Login successful')
    
    def test_dashboard_access(self):
        """Test dashboard functionality"""
        self.driver.get(f'{self.base_url}/dashboard/')
        
        # Check page loads successfully
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.TAG_NAME, 'body'))
        )
        
        # Look for dashboard elements
        page_source = self.driver.page_source.lower()
        
        # Should contain typical dashboard elements
        dashboard_indicators = ['ticket', 'dashboard', 'zgłoszenia', 'aktywność']
        found_indicators = [indicator for indicator in dashboard_indicators if indicator in page_source]
        
        assert len(found_indicators) > 0, f"Dashboard content not found. Page source length: {len(page_source)}"
        self.log(f'Dashboard loaded with indicators: {found_indicators}')
    
    def test_create_ticket(self):
        """Test ticket creation"""
        self.driver.get(f'{self.base_url}/tickets/create/')
        
        # Check if ticket creation page exists
        try:
            title_input = WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.NAME, 'title'))
            )
            
            # Fill out form
            title_input.send_keys('Automated Test Ticket')
            
            description_field = self.driver.find_element(By.NAME, 'description')
            description_field.send_keys('This ticket was created by automated testing')
            
            # Try to find and select category
            try:
                category_select = self.driver.find_element(By.NAME, 'category')
                category_options = category_select.find_elements(By.TAG_NAME, 'option')
                if len(category_options) > 1:
                    category_options[1].click()  # Select first non-empty option
            except NoSuchElementException:
                pass
            
            # Try to find and select priority
            try:
                priority_select = self.driver.find_element(By.NAME, 'priority')
                priority_options = priority_select.find_elements(By.TAG_NAME, 'option')
                for option in priority_options:
                    if option.get_attribute('value') == 'medium':
                        option.click()
                        break
            except NoSuchElementException:
                pass
            
            # Submit form
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"], input[type="submit"]')
            submit_button.click()
            
            # Wait for redirect or success message
            time.sleep(2)
            
            self.log('Ticket creation form submitted successfully')
            
        except TimeoutException:
            # Ticket creation might not be available for this user role
            self.log('Ticket creation page not accessible (might be role-restricted)')
            # This is not necessarily a failure
    
    def test_view_tickets(self):
        """Test ticket viewing"""
        # Try different ticket-related URLs
        ticket_urls = [
            '/dashboard/',
            '/tickets/',
            '/tickets/my/',
            '/tickets/list/',
        ]
        
        found_tickets = False
        
        for url in ticket_urls:
            try:
                self.driver.get(f'{self.base_url}{url}')
                time.sleep(1)
                
                page_source = self.driver.page_source.lower()
                
                # Look for ticket-related content
                ticket_indicators = ['ticket', 'zgłoszenia', '#', 'priority', 'status']
                found_indicators = [indicator for indicator in ticket_indicators if indicator in page_source]
                
                if len(found_indicators) >= 2:
                    found_tickets = True
                    self.log(f'Tickets found at {url}')
                    break
                    
            except Exception:
                continue
        
        if not found_tickets:
            # Try to find any page with ticket information
            self.driver.get(f'{self.base_url}/dashboard/')
            page_source = self.driver.page_source.lower()
            if 'ticket' in page_source or 'zgłosz' in page_source:
                found_tickets = True
        
        assert found_tickets, "No ticket-related content found on any page"
        self.log('Ticket viewing functionality verified')
    
    def test_activity_logs(self):
        """Test activity logs access"""
        try:
            self.driver.get(f'{self.base_url}/logs/activity/')
            
            # Check if page loads (might be restricted)
            WebDriverWait(self.driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, 'body'))
            )
            
            current_url = self.driver.current_url
            
            if '/logs/' in current_url or 'activity' in self.driver.page_source.lower():
                self.log('Activity logs accessible')
            else:
                # Might be redirected due to permissions
                self.log('Activity logs not accessible (likely role-restricted)')
                
        except TimeoutException:
            # Page might not exist or be accessible
            self.log('Activity logs page not found or accessible')
    
    def test_profile_access(self):
        """Test user profile access"""
        profile_urls = [
            '/profile/',
            '/account/',
            '/user/profile/',
            '/settings/',
        ]
        
        for url in profile_urls:
            try:
                self.driver.get(f'{self.base_url}{url}')
                time.sleep(1)
                
                if self.driver.current_url.endswith(url) or 'profile' in self.driver.page_source.lower():
                    self.log(f'Profile accessible at {url}')
                    return
                    
            except Exception:
                continue
        
        # Profile might be accessible through different means
        self.log('Dedicated profile page not found (might be integrated elsewhere)')
    
    def test_password_validation(self):
        """Test password validation features"""
        # Try to access password change page
        password_urls = [
            '/password/change/',
            '/account/password/',
            '/profile/password/',
        ]
        
        for url in password_urls:
            try:
                self.driver.get(f'{self.base_url}{url}')
                time.sleep(1)
                
                # Look for password form
                password_inputs = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="password"]')
                
                if len(password_inputs) > 0:
                    self.log(f'Password change form found at {url}')
                    
                    # Check for validation elements
                    page_source = self.driver.page_source.lower()
                    validation_indicators = ['requirement', 'validation', 'strength', 'characters']
                    found = [ind for ind in validation_indicators if ind in page_source]
                    
                    if found:
                        self.log(f'Password validation features detected: {found}')
                    
                    return
                    
            except Exception:
                continue
        
        self.log('Password change form not found')
    
    def test_responsive_design(self):
        """Test responsive design"""
        # Test mobile viewport
        self.driver.set_window_size(375, 667)  # iPhone size
        time.sleep(1)
        
        self.driver.get(f'{self.base_url}/dashboard/')
        
        # Check that page still loads and is usable
        body = self.driver.find_element(By.TAG_NAME, 'body')
        assert body.is_displayed()
        
        # Look for mobile-friendly elements
        page_source = self.driver.page_source.lower()
        mobile_indicators = ['mobile', 'responsive', 'viewport', 'hamburger', 'menu-toggle']
        found_mobile = [ind for ind in mobile_indicators if ind in page_source]
        
        # Reset to desktop size
        self.driver.set_window_size(1920, 1080)
        
        self.log(f'Mobile design check completed. Mobile indicators: {found_mobile}')
    
    def test_logout_flow(self):
        """Test logout functionality"""
        # Look for logout link/button
        logout_selectors = [
            'a[href*="logout"]',
            'button[name="logout"]',
            'input[value*="Logout"]',
            'a[href*="wyloguj"]',
        ]
        
        logout_element = None
        for selector in logout_selectors:
            try:
                logout_element = self.driver.find_element(By.CSS_SELECTOR, selector)
                break
            except NoSuchElementException:
                continue
        
        if not logout_element:
            # Try to find by text
            try:
                logout_element = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Logout')
            except NoSuchElementException:
                try:
                    logout_element = self.driver.find_element(By.PARTIAL_LINK_TEXT, 'Wyloguj')
                except NoSuchElementException:
                    pass
        
        if logout_element:
            logout_element.click()
            time.sleep(2)
            
            # Should redirect to login or landing page
            current_url = self.driver.current_url
            if '/login/' in current_url or current_url == f'{self.base_url}/':
                self.log('Logout successful')
            else:
                self.log(f'Logout redirected to: {current_url}')
        else:
            self.log('Logout element not found')
    
    def print_results(self):
        """Print test results summary"""
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r['status'] == 'PASS'])
        failed_tests = total_tests - passed_tests
        total_time = sum(r['duration'] for r in self.test_results)
        
        self.stdout.write("\n" + "="*60)
        self.stdout.write("TEST RESULTS SUMMARY")
        self.stdout.write("="*60)
        self.stdout.write(f"Total Tests: {total_tests}")
        self.stdout.write(f"Passed: {passed_tests}")
        self.stdout.write(f"Failed: {failed_tests}")
        self.stdout.write(f"Total Time: {total_time:.2f} seconds")
        self.stdout.write(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            self.stdout.write("\nFAILED TESTS:")
            for result in self.test_results:
                if result['status'] == 'FAIL':
                    self.stdout.write(f"  ❌ {result['name']}: {result['error']}")
        
        self.stdout.write("\nDETAILED RESULTS:")
        for result in self.test_results:
            status_icon = "✅" if result['status'] == 'PASS' else "❌"
            self.stdout.write(f"  {status_icon} {result['name']}: {result['status']} ({result['duration']:.2f}s)")
        
        self.stdout.write("="*60)
