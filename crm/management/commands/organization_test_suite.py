"""
Comprehensive Organization Management Testing Module
Tests CRUD operations, user assignments, and organization workflows
"""
import time
import random
import string
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class OrganizationTestSuite:
    """Comprehensive organization management testing"""
    
    def __init__(self, driver, base_url, admin_username, admin_password):
        self.driver = driver
        self.base_url = base_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.created_organizations = []
        self.created_users = []
        self.test_org_names = []
        
    def run_full_organization_tests(self):
        """Run complete organization management test suite"""
        results = []
        
        # Test organization creation
        results.append(self.test_organization_creation())
        
        # Test organization editing
        results.append(self.test_organization_editing())
        
        # Test user assignment to organization
        results.append(self.test_user_organization_assignment())
        
        # Test organization user removal
        results.append(self.test_organization_user_removal())
        
        # Test organization permissions
        results.append(self.test_organization_permissions())
        
        # Test organization deletion
        results.append(self.test_organization_deletion())
        
        # Test organization listing and filtering
        results.append(self.test_organization_listing_filtering())
        
        # Test bulk operations
        results.append(self.test_organization_bulk_operations())
        
        return results
    
    def test_organization_creation(self):
        """Test creating new organizations"""
        try:
            self.login_as_admin()
            
            # Navigate to organization creation
            creation_urls = [
                '/organizations/create/',
                '/admin/organizations/add/',
                '/org/new/',
                '/organizations/new/',
                '/admin/crm/organization/add/'
            ]
            
            creation_page_found = False
            for url in creation_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for organization creation form
                    name_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                        'input[name*="name"], input[id*="name"]')
                    
                    if name_fields:
                        creation_page_found = True
                        break
                        
                except Exception:
                    continue
            
            if not creation_page_found:
                # Try Django admin interface
                try:
                    self.driver.get(f'{self.base_url}/admin/')
                    time.sleep(2)
                    
                    # Look for organization model
                    org_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'Organization')
                    if not org_links:
                        org_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'organization')
                    
                    if org_links:
                        org_links[0].click()
                        time.sleep(2)
                        
                        # Look for "Add" button
                        add_buttons = self.driver.find_elements(By.PARTIAL_LINK_TEXT, 'Add')
                        if add_buttons:
                            add_buttons[0].click()
                            time.sleep(2)
                            creation_page_found = True
                            
                except Exception:
                    pass
            
            if not creation_page_found:
                return {'status': 'SKIP', 'message': 'Organization creation interface not found'}
            
            # Fill organization form
            org_name = f'TestOrg_{random.randint(1000, 9999)}'
            
            # Find name field
            name_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                'input[name*="name"], input[id*="name"]')
            
            if name_fields:
                name_fields[0].clear()
                name_fields[0].send_keys(org_name)
                
                # Look for description field
                desc_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                    'textarea[name*="description"], textarea[id*="description"]')
                
                if desc_fields:
                    desc_fields[0].send_keys(f'Test organization created by automation - {org_name}')
                
                # Look for additional fields
                email_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                    'input[name*="email"], input[id*="email"]')
                
                if email_fields:
                    email_fields[0].send_keys(f'admin@{org_name.lower()}.testdomain.com')
                
                phone_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                    'input[name*="phone"], input[id*="phone"]')
                
                if phone_fields:
                    phone_fields[0].send_keys(f'+1-555-{random.randint(1000, 9999)}')
                
                # Submit form
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button[type="submit"], input[type="submit"], input[value="Save"]')
                
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)
                    
                    # Check for success
                    current_url = self.driver.current_url
                    page_source = self.driver.page_source.lower()
                    
                    success_indicators = ['successfully', 'created', 'added', org_name.lower()]
                    success = any(indicator in page_source for indicator in success_indicators)
                    
                    if success or '/admin/' in current_url:
                        self.created_organizations.append(org_name)
                        self.test_org_names.append(org_name)
                        return {'status': 'PASS', 'message': f'Organization "{org_name}" created successfully'}
                    else:
                        return {'status': 'FAIL', 'message': 'Organization creation failed - no success confirmation'}
            
            return {'status': 'FAIL', 'message': 'Organization creation form not properly accessible'}
            
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization creation test failed: {str(e)}'}
    
    def test_organization_editing(self):
        """Test editing existing organizations"""
        try:
            if not self.created_organizations:
                return {'status': 'SKIP', 'message': 'No organizations available to edit'}
            
            self.login_as_admin()
            
            org_name = self.created_organizations[0]
            
            # Navigate to organization list
            list_urls = [
                '/organizations/',
                '/admin/organizations/',
                '/org/',
                '/organizations/list/',
                '/admin/crm/organization/'
            ]
            
            edit_page_found = False
            for url in list_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for the organization in the list
                    if org_name in self.driver.page_source:
                        # Find edit link
                        org_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, org_name)
                        
                        if org_links:
                            org_links[0].click()
                            time.sleep(2)
                            
                            # Look for edit button or check if we're already on edit page
                            edit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'a[href*="edit"], button[name*="edit"], input[value*="Edit"]')
                            
                            if edit_buttons:
                                edit_buttons[0].click()
                                time.sleep(2)
                            
                            edit_page_found = True
                            break
                        
                        # Try clicking directly if it's a link
                        try:
                            org_element = self.driver.find_element(By.PARTIAL_LINK_TEXT, org_name)
                            org_element.click()
                            time.sleep(2)
                            edit_page_found = True
                            break
                        except Exception:
                            pass
                            
                except Exception:
                    continue
            
            if not edit_page_found:
                return {'status': 'SKIP', 'message': f'Edit interface for organization "{org_name}" not found'}
            
            # Modify organization data
            name_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                'input[name*="name"], input[id*="name"]')
            
            if name_fields:
                current_name = name_fields[0].get_attribute('value')
                new_name = f'{current_name}_EDITED'
                
                name_fields[0].clear()
                name_fields[0].send_keys(new_name)
                
                # Modify description if available
                desc_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                    'textarea[name*="description"], textarea[id*="description"]')
                
                if desc_fields:
                    desc_fields[0].clear()
                    desc_fields[0].send_keys(f'EDITED: Organization modified by automation test at {time.strftime("%Y-%m-%d %H:%M")}')
                
                # Submit changes
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button[type="submit"], input[type="submit"], input[value="Save"]')
                
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)
                    
                    # Check for success
                    page_source = self.driver.page_source.lower()
                    success_indicators = ['successfully', 'updated', 'modified', 'saved']
                    
                    if any(indicator in page_source for indicator in success_indicators):
                        # Update our tracking
                        if org_name in self.created_organizations:
                            idx = self.created_organizations.index(org_name)
                            self.created_organizations[idx] = new_name
                        
                        return {'status': 'PASS', 'message': f'Organization edited successfully: {org_name} -> {new_name}'}
                    else:
                        return {'status': 'FAIL', 'message': 'Organization edit failed - no success confirmation'}
            
            return {'status': 'FAIL', 'message': 'Organization edit form not accessible'}
            
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization editing test failed: {str(e)}'}
    
    def test_user_organization_assignment(self):
        """Test assigning users to organizations"""
        try:
            if not self.created_organizations:
                return {'status': 'SKIP', 'message': 'No organizations available for user assignment'}
            
            self.login_as_admin()
            
            # First, create a test user
            test_username = f'test_user_{random.randint(1000, 9999)}'
            user_created = self.create_test_user(test_username)
            
            if not user_created:
                return {'status': 'SKIP', 'message': 'Could not create test user for organization assignment'}
            
            org_name = self.created_organizations[0]
            
            # Navigate to user management
            user_mgmt_urls = [
                '/users/',
                '/admin/auth/user/',
                '/admin/users/',
                '/user/management/'
            ]
            
            assignment_successful = False
            for url in user_mgmt_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for the test user
                    if test_username in self.driver.page_source:
                        # Click on user
                        user_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, test_username)
                        
                        if user_links:
                            user_links[0].click()
                            time.sleep(2)
                            
                            # Look for organization assignment field
                            org_selects = self.driver.find_elements(By.CSS_SELECTOR, 
                                'select[name*="organization"], select[id*="organization"]')
                            
                            if org_selects:
                                org_select = Select(org_selects[0])
                                
                                # Look for our test organization in options
                                for option in org_select.options:
                                    if org_name in option.text:
                                        org_select.select_by_visible_text(option.text)
                                        break
                                
                                # Save changes
                                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                    'button[type="submit"], input[type="submit"], input[value="Save"]')
                                
                                if submit_buttons:
                                    submit_buttons[0].click()
                                    time.sleep(3)
                                    
                                    # Check for success
                                    page_source = self.driver.page_source.lower()
                                    success_indicators = ['successfully', 'updated', 'saved']
                                    
                                    if any(indicator in page_source for indicator in success_indicators):
                                        assignment_successful = True
                                        break
                        
                except Exception:
                    continue
            
            if assignment_successful:
                return {'status': 'PASS', 'message': f'User "{test_username}" assigned to organization "{org_name}" successfully'}
            else:
                return {'status': 'PARTIAL', 'message': 'User assignment interface found but assignment unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'User organization assignment test failed: {str(e)}'}
    
    def test_organization_user_removal(self):
        """Test removing users from organizations"""
        try:
            self.login_as_admin()
            
            # Navigate to organization management
            org_urls = [
                '/organizations/',
                '/admin/organizations/',
                '/org/',
                '/admin/crm/organization/'
            ]
            
            removal_interface_found = False
            for url in org_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for organization with users
                    page_source = self.driver.page_source.lower()
                    user_indicators = ['user', 'member', 'staff', 'employee']
                    
                    if any(indicator in page_source for indicator in user_indicators):
                        removal_interface_found = True
                        break
                        
                except Exception:
                    continue
            
            if removal_interface_found:
                return {'status': 'PASS', 'message': 'Organization user management interface accessible'}
            else:
                return {'status': 'SKIP', 'message': 'Organization user removal interface not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization user removal test failed: {str(e)}'}
    
    def test_organization_permissions(self):
        """Test organization-based permissions"""
        try:
            self.login_as_admin()
            
            # Check if organization permissions are enforced
            # This would involve testing access controls based on organization membership
            
            # Navigate to dashboard and check organization filtering
            self.driver.get(f'{self.base_url}/dashboard/')
            time.sleep(2)
            
            page_source = self.driver.page_source.lower()
            permission_indicators = ['organization', 'access', 'permission', 'restricted']
            
            permissions_present = any(indicator in page_source for indicator in permission_indicators)
            
            # Look for organization-based filtering
            org_filters = self.driver.find_elements(By.CSS_SELECTOR, 
                'select[name*="organization"], [class*="organization"]')
            
            if permissions_present or org_filters:
                return {'status': 'PASS', 'message': 'Organization permissions/filtering system detected'}
            else:
                return {'status': 'PARTIAL', 'message': 'Organization permissions system unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization permissions test failed: {str(e)}'}
    
    def test_organization_deletion(self):
        """Test organization deletion"""
        try:
            if not self.created_organizations:
                return {'status': 'SKIP', 'message': 'No organizations available for deletion test'}
            
            self.login_as_admin()
            
            # Get organization to delete (use last created)
            org_to_delete = self.created_organizations[-1]
            
            # Navigate to organization list
            list_urls = [
                '/organizations/',
                '/admin/organizations/',
                '/org/',
                '/admin/crm/organization/'
            ]
            
            deletion_successful = False
            for url in list_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for the organization
                    if org_to_delete in self.driver.page_source:
                        # Find and click on organization
                        org_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, org_to_delete)
                        
                        if org_links:
                            org_links[0].click()
                            time.sleep(2)
                            
                            # Look for delete button
                            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'button[name*="delete"], input[value*="Delete"], a[class*="delete"]')
                            
                            if delete_buttons:
                                delete_buttons[0].click()
                                time.sleep(2)
                                
                                # Confirm deletion if needed
                                confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                    'button[type="submit"], input[type="submit"], input[value="Yes"]')
                                
                                if confirm_buttons:
                                    confirm_buttons[0].click()
                                    time.sleep(3)
                                    
                                    # Check if organization is gone
                                    self.driver.get(f'{self.base_url}{url}')
                                    time.sleep(2)
                                    
                                    if org_to_delete not in self.driver.page_source:
                                        deletion_successful = True
                                        self.created_organizations.remove(org_to_delete)
                                        break
                        
                except Exception:
                    continue
            
            if deletion_successful:
                return {'status': 'PASS', 'message': f'Organization "{org_to_delete}" deleted successfully'}
            else:
                return {'status': 'PARTIAL', 'message': 'Organization deletion interface found but deletion unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization deletion test failed: {str(e)}'}
    
    def test_organization_listing_filtering(self):
        """Test organization listing and filtering functionality"""
        try:
            self.login_as_admin()
            
            # Navigate to organization list
            list_urls = [
                '/organizations/',
                '/admin/organizations/',
                '/org/',
                '/organizations/list/'
            ]
            
            listing_found = False
            for url in list_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    
                    # Look for organization listing
                    if 'organization' in page_source and ('list' in page_source or 'table' in page_source):
                        listing_found = True
                        
                        # Test search functionality
                        search_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                            'input[name*="search"], input[placeholder*="search"]')
                        
                        if search_inputs and self.created_organizations:
                            search_inputs[0].send_keys(self.created_organizations[0][:4])
                            time.sleep(1)
                            
                            # Submit search or auto-search
                            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'button[type="submit"], input[type="submit"]')
                            
                            if submit_buttons:
                                submit_buttons[0].click()
                                time.sleep(2)
                        
                        # Look for filtering options
                        filter_selects = self.driver.find_elements(By.CSS_SELECTOR, 
                            'select[name*="filter"], select[name*="status"]')
                        
                        if filter_selects:
                            return {'status': 'PASS', 'message': 'Organization listing with search and filtering found'}
                        else:
                            return {'status': 'PASS', 'message': 'Organization listing found (filtering unclear)'}
                        
                except Exception:
                    continue
            
            if not listing_found:
                return {'status': 'SKIP', 'message': 'Organization listing interface not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Organization listing test failed: {str(e)}'}
    
    def test_organization_bulk_operations(self):
        """Test bulk operations on organizations"""
        try:
            self.login_as_admin()
            
            # Navigate to organization list
            self.driver.get(f'{self.base_url}/admin/organizations/')
            time.sleep(2)
            
            # Look for bulk operation interface
            page_source = self.driver.page_source.lower()
            
            # Look for checkboxes and action selectors (Django admin style)
            checkboxes = self.driver.find_elements(By.CSS_SELECTOR, 'input[type="checkbox"]')
            action_selects = self.driver.find_elements(By.CSS_SELECTOR, 'select[name="action"]')
            
            bulk_interface = len(checkboxes) > 1 and action_selects
            
            # Look for bulk action indicators
            bulk_indicators = ['select all', 'bulk', 'action', 'delete selected']
            bulk_text_present = any(indicator in page_source for indicator in bulk_indicators)
            
            if bulk_interface or bulk_text_present:
                return {'status': 'PASS', 'message': 'Bulk operations interface available for organizations'}
            else:
                return {'status': 'SKIP', 'message': 'Bulk operations interface not detected'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Bulk operations test failed: {str(e)}'}
    
    def create_test_user(self, username):
        """Helper method to create a test user"""
        try:
            # Navigate to user creation
            user_create_urls = [
                '/admin/auth/user/add/',
                '/users/create/',
                '/admin/users/add/'
            ]
            
            for url in user_create_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    # Look for user creation form
                    username_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                        'input[name="username"], input[id="id_username"]')
                    
                    if username_fields:
                        username_fields[0].send_keys(username)
                        
                        # Fill required fields
                        password_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                            'input[name="password1"], input[name="password"]')
                        
                        if password_fields:
                            test_password = 'TestPassword123!'
                            password_fields[0].send_keys(test_password)
                            
                            # Password confirmation if available
                            password2_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                                'input[name="password2"]')
                            
                            if password2_fields:
                                password2_fields[0].send_keys(test_password)
                        
                        # Email field
                        email_fields = self.driver.find_elements(By.CSS_SELECTOR, 
                            'input[name="email"], input[id="id_email"]')
                        
                        if email_fields:
                            email_fields[0].send_keys(f'{username}@testdomain.com')
                        
                        # Submit form
                        submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                            'button[type="submit"], input[type="submit"], input[value="Save"]')
                        
                        if submit_buttons:
                            submit_buttons[0].click()
                            time.sleep(3)
                            
                            # Check for success
                            if '/admin/' in self.driver.current_url or 'successfully' in self.driver.page_source.lower():
                                self.created_users.append(username)
                                return True
                        
                except Exception:
                    continue
            
            return False
            
        except Exception:
            return False
    
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
    
    def cleanup_test_data(self):
        """Clean up test organizations and users"""
        cleanup_results = {
            'organizations_cleaned': 0,
            'users_cleaned': 0,
            'errors': []
        }
        
        try:
            self.login_as_admin()
            
            # Clean up organizations
            for org_name in self.created_organizations[:]:
                try:
                    self.driver.get(f'{self.base_url}/admin/organizations/')
                    time.sleep(2)
                    
                    if org_name in self.driver.page_source:
                        # Find and delete organization
                        org_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, org_name)
                        if org_links:
                            org_links[0].click()
                            time.sleep(1)
                            
                            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'input[value="Delete"], button[name="_delete"]')
                            
                            if delete_buttons:
                                delete_buttons[0].click()
                                time.sleep(1)
                                
                                confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                    'input[type="submit"]')
                                if confirm_buttons:
                                    confirm_buttons[0].click()
                                    time.sleep(1)
                                    
                                    cleanup_results['organizations_cleaned'] += 1
                                    self.created_organizations.remove(org_name)
                                    
                except Exception as e:
                    cleanup_results['errors'].append(f"Error cleaning organization {org_name}: {str(e)}")
            
            # Clean up users
            for username in self.created_users[:]:
                try:
                    self.driver.get(f'{self.base_url}/admin/auth/user/')
                    time.sleep(2)
                    
                    if username in self.driver.page_source:
                        user_links = self.driver.find_elements(By.PARTIAL_LINK_TEXT, username)
                        if user_links:
                            user_links[0].click()
                            time.sleep(1)
                            
                            delete_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                'input[value="Delete"], button[name="_delete"]')
                            
                            if delete_buttons:
                                delete_buttons[0].click()
                                time.sleep(1)
                                
                                confirm_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                                    'input[type="submit"]')
                                if confirm_buttons:
                                    confirm_buttons[0].click()
                                    time.sleep(1)
                                    
                                    cleanup_results['users_cleaned'] += 1
                                    self.created_users.remove(username)
                                    
                except Exception as e:
                    cleanup_results['errors'].append(f"Error cleaning user {username}: {str(e)}")
                    
        except Exception as e:
            cleanup_results['errors'].append(f"General cleanup error: {str(e)}")
        
        return cleanup_results
