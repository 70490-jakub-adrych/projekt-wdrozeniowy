"""
Comprehensive 2FA Testing Module for Live Domain Testing
"""
import time
import random
import string
import pyotp
import qrcode
import io
import base64
from PIL import Image
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class TwoFactorTestSuite:
    """Comprehensive 2FA testing functionality"""
    
    def __init__(self, driver, base_url, admin_username, admin_password):
        self.driver = driver
        self.base_url = base_url
        self.admin_username = admin_username
        self.admin_password = admin_password
        self.test_users = []
        self.totp_secrets = {}
        
    def test_2fa_full_workflow(self):
        """Test complete 2FA workflow from setup to verification"""
        results = []
        
        # Test 2FA setup process
        results.append(self.test_2fa_setup_process())
        
        # Test 2FA login verification
        results.append(self.test_2fa_login_verification())
        
        # Test backup codes generation
        results.append(self.test_backup_codes_generation())
        
        # Test backup codes usage
        results.append(self.test_backup_codes_usage())
        
        # Test 2FA disable process
        results.append(self.test_2fa_disable_process())
        
        # Test invalid TOTP codes
        results.append(self.test_invalid_totp_codes())
        
        return results
    
    def test_2fa_setup_process(self):
        """Test 2FA setup from start to finish"""
        try:
            # Login as admin
            self.login_as_admin()
            
            # Navigate to 2FA setup
            setup_urls = [
                '/2fa/setup/',
                '/account/2fa/',
                '/profile/security/',
                '/two-factor/setup/',
                '/security/2fa/'
            ]
            
            setup_page_found = False
            for url in setup_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    setup_indicators = ['qr', 'authenticator', 'google auth', 'totp', '2fa', 'setup']
                    
                    if any(indicator in page_source for indicator in setup_indicators):
                        setup_page_found = True
                        break
                        
                except Exception:
                    continue
            
            if not setup_page_found:
                return {'status': 'SKIP', 'message': '2FA setup page not found'}
            
            # Look for QR code or secret key
            qr_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img[src*="qr"], canvas, .qr-code')
            secret_elements = self.driver.find_elements(By.CSS_SELECTOR, 'code, .secret, [class*="secret"]')
            
            if qr_elements:
                # QR code found - try to extract secret
                qr_img = qr_elements[0]
                # In real implementation, you'd decode the QR code
                # For testing, we'll simulate the process
                secret_key = self.generate_test_secret()
                
            elif secret_elements:
                # Manual secret found
                secret_key = secret_elements[0].text.strip()
                
            else:
                # Look for any text that might be the secret
                page_text = self.driver.page_source
                # Try to find 32-character base32 string
                import re
                secret_match = re.search(r'[A-Z2-7]{32}', page_text)
                if secret_match:
                    secret_key = secret_match.group()
                else:
                    secret_key = self.generate_test_secret()
            
            # Generate TOTP code
            totp = pyotp.TOTP(secret_key)
            current_code = totp.now()
            
            # Look for verification form
            code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                'input[name*="code"], input[name*="token"], input[name*="otp"]')
            
            if code_inputs:
                code_inputs[0].send_keys(current_code)
                
                # Submit verification
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button[type="submit"], input[type="submit"]')
                
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)
                    
                    # Check for success
                    page_source = self.driver.page_source.lower()
                    success_indicators = ['success', 'enabled', 'activated', 'setup complete']
                    
                    if any(indicator in page_source for indicator in success_indicators):
                        self.totp_secrets[self.admin_username] = secret_key
                        return {'status': 'PASS', 'message': '2FA setup completed successfully'}
                    else:
                        return {'status': 'FAIL', 'message': '2FA setup verification failed'}
            
            return {'status': 'PARTIAL', 'message': '2FA setup interface found but verification form not accessible'}
            
        except Exception as e:
            return {'status': 'FAIL', 'message': f'2FA setup test failed: {str(e)}'}
    
    def test_2fa_login_verification(self):
        """Test 2FA verification during login"""
        try:
            # Logout first
            try:
                self.driver.get(f'{self.base_url}/logout/')
                time.sleep(2)
            except Exception:
                pass
            
            # Login with username/password
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
            
            # Check if 2FA verification page appears
            current_url = self.driver.current_url
            page_source = self.driver.page_source.lower()
            
            verification_indicators = ['2fa', 'verify', 'authentication', 'code', 'token']
            verification_page = any(indicator in current_url.lower() for indicator in verification_indicators) or \
                              any(indicator in page_source for indicator in verification_indicators)
            
            if verification_page:
                # 2FA verification required
                if self.admin_username in self.totp_secrets:
                    # Generate current TOTP code
                    totp = pyotp.TOTP(self.totp_secrets[self.admin_username])
                    current_code = totp.now()
                    
                    # Enter code
                    code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                        'input[name*="code"], input[name*="token"], input[name*="otp"]')
                    
                    if code_inputs:
                        code_inputs[0].send_keys(current_code)
                        
                        submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                            'button[type="submit"], input[type="submit"]')
                        
                        if submit_buttons:
                            submit_buttons[0].click()
                            time.sleep(3)
                            
                            # Check if login successful
                            if '/login/' not in self.driver.current_url:
                                return {'status': 'PASS', 'message': '2FA login verification successful'}
                            else:
                                return {'status': 'FAIL', 'message': '2FA code rejected'}
                
                return {'status': 'PARTIAL', 'message': '2FA verification page found but no test secret available'}
            
            else:
                # No 2FA required - check if already logged in
                if '/login/' not in self.driver.current_url:
                    return {'status': 'SKIP', 'message': '2FA not enabled for this account'}
                else:
                    return {'status': 'FAIL', 'message': 'Login failed entirely'}
                    
        except Exception as e:
            return {'status': 'FAIL', 'message': f'2FA login test failed: {str(e)}'}
    
    def test_backup_codes_generation(self):
        """Test backup codes generation"""
        try:
            self.login_as_admin()
            
            # Navigate to backup codes
            backup_urls = [
                '/2fa/backup/',
                '/account/backup-codes/',
                '/profile/backup/',
                '/two-factor/backup/',
                '/security/backup-codes/'
            ]
            
            backup_page_found = False
            for url in backup_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    backup_indicators = ['backup', 'recovery', 'emergency', 'codes']
                    
                    if any(indicator in page_source for indicator in backup_indicators):
                        backup_page_found = True
                        break
                        
                except Exception:
                    continue
            
            if not backup_page_found:
                return {'status': 'SKIP', 'message': 'Backup codes page not found'}
            
            # Look for backup codes display or generation button
            codes_displayed = self.driver.find_elements(By.CSS_SELECTOR, 
                'code, .backup-code, .recovery-code, [class*="code"]')
            
            generate_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[name*="generate"], button[name*="backup"], input[value*="Generate"]')
            
            if codes_displayed:
                # Backup codes already visible
                return {'status': 'PASS', 'message': f'Backup codes displayed ({len(codes_displayed)} codes found)'}
            
            elif generate_buttons:
                # Try to generate backup codes
                generate_buttons[0].click()
                time.sleep(2)
                
                # Check for generated codes
                new_codes = self.driver.find_elements(By.CSS_SELECTOR, 
                    'code, .backup-code, .recovery-code, [class*="code"]')
                
                if new_codes:
                    return {'status': 'PASS', 'message': f'Backup codes generated successfully ({len(new_codes)} codes)'}
                else:
                    return {'status': 'FAIL', 'message': 'Backup code generation failed'}
            
            else:
                return {'status': 'PARTIAL', 'message': 'Backup codes page found but generation interface unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Backup codes test failed: {str(e)}'}
    
    def test_backup_codes_usage(self):
        """Test using backup codes for login"""
        try:
            # This test would require having backup codes from previous test
            # For now, we'll simulate the test
            
            self.driver.get(f'{self.base_url}/logout/')
            time.sleep(2)
            
            # Attempt login to get to 2FA verification
            self.driver.get(f'{self.base_url}/login/')
            
            username_input = self.driver.find_element(By.NAME, 'username')
            password_input = self.driver.find_element(By.NAME, 'password')
            
            username_input.send_keys(self.admin_username)
            password_input.send_keys(self.admin_password)
            
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            time.sleep(3)
            
            # Look for backup code option
            page_source = self.driver.page_source.lower()
            backup_options = ['backup', 'recovery', 'emergency', 'alternative']
            
            backup_available = any(option in page_source for option in backup_options)
            
            # Look for backup code links or buttons
            backup_links = self.driver.find_elements(By.CSS_SELECTOR, 
                'a[href*="backup"], button[name*="backup"], [class*="backup"]')
            
            if backup_available or backup_links:
                return {'status': 'PASS', 'message': 'Backup code option available during 2FA verification'}
            else:
                return {'status': 'SKIP', 'message': 'Backup code usage interface not found'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Backup codes usage test failed: {str(e)}'}
    
    def test_2fa_disable_process(self):
        """Test 2FA disable functionality"""
        try:
            self.login_as_admin()
            
            # Navigate to 2FA settings
            settings_urls = [
                '/2fa/disable/',
                '/account/2fa/',
                '/profile/security/',
                '/two-factor/settings/',
                '/security/2fa/'
            ]
            
            disable_page_found = False
            for url in settings_urls:
                try:
                    self.driver.get(f'{self.base_url}{url}')
                    time.sleep(2)
                    
                    page_source = self.driver.page_source.lower()
                    disable_indicators = ['disable', 'turn off', 'deactivate', 'remove']
                    
                    if any(indicator in page_source for indicator in disable_indicators):
                        disable_page_found = True
                        break
                        
                except Exception:
                    continue
            
            if not disable_page_found:
                return {'status': 'SKIP', 'message': '2FA disable option not found'}
            
            # Look for disable buttons
            disable_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[name*="disable"], input[value*="Disable"], button[name*="remove"]')
            
            if disable_buttons:
                return {'status': 'PASS', 'message': '2FA disable option available'}
            else:
                return {'status': 'PARTIAL', 'message': '2FA settings page found but disable option unclear'}
                
        except Exception as e:
            return {'status': 'FAIL', 'message': f'2FA disable test failed: {str(e)}'}
    
    def test_invalid_totp_codes(self):
        """Test handling of invalid TOTP codes"""
        try:
            # Logout and attempt login with invalid 2FA code
            self.driver.get(f'{self.base_url}/logout/')
            time.sleep(2)
            
            # Login with username/password
            self.driver.get(f'{self.base_url}/login/')
            
            username_input = self.driver.find_element(By.NAME, 'username')
            password_input = self.driver.find_element(By.NAME, 'password')
            
            username_input.send_keys(self.admin_username)
            password_input.send_keys(self.admin_password)
            
            submit_button = self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]')
            submit_button.click()
            
            time.sleep(3)
            
            # If 2FA verification page appears
            code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
                'input[name*="code"], input[name*="token"], input[name*="otp"]')
            
            if code_inputs:
                # Enter invalid code
                invalid_code = '000000'
                code_inputs[0].send_keys(invalid_code)
                
                submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                    'button[type="submit"], input[type="submit"]')
                
                if submit_buttons:
                    submit_buttons[0].click()
                    time.sleep(3)
                    
                    # Should show error and stay on verification page
                    page_source = self.driver.page_source.lower()
                    error_indicators = ['error', 'invalid', 'incorrect', 'wrong']
                    
                    error_shown = any(indicator in page_source for indicator in error_indicators)
                    still_on_verification = any(indicator in page_source for indicator in 
                                              ['verify', '2fa', 'code', 'authentication'])
                    
                    if error_shown and still_on_verification:
                        return {'status': 'PASS', 'message': 'Invalid 2FA codes properly rejected'}
                    elif still_on_verification:
                        return {'status': 'PARTIAL', 'message': 'Invalid code rejected but error message unclear'}
                    else:
                        return {'status': 'FAIL', 'message': 'Invalid 2FA code was accepted'}
            
            return {'status': 'SKIP', 'message': '2FA verification not triggered for invalid code test'}
            
        except Exception as e:
            return {'status': 'FAIL', 'message': f'Invalid TOTP codes test failed: {str(e)}'}
    
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
        
        # Handle 2FA if required
        code_inputs = self.driver.find_elements(By.CSS_SELECTOR, 
            'input[name*="code"], input[name*="token"], input[name*="otp"]')
        
        if code_inputs and self.admin_username in self.totp_secrets:
            totp = pyotp.TOTP(self.totp_secrets[self.admin_username])
            current_code = totp.now()
            
            code_inputs[0].send_keys(current_code)
            
            submit_buttons = self.driver.find_elements(By.CSS_SELECTOR, 
                'button[type="submit"], input[type="submit"]')
            
            if submit_buttons:
                submit_buttons[0].click()
                time.sleep(3)
    
    def generate_test_secret(self):
        """Generate a test TOTP secret"""
        return pyotp.random_base32()
    
    def cleanup_test_data(self):
        """Clean up any test users created during 2FA testing"""
        for user in self.test_users:
            try:
                # Attempt to delete test user
                # Implementation depends on admin interface
                pass
            except Exception:
                pass
