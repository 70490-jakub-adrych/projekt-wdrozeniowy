# Comprehensive Live Domain Testing Suite

This enhanced testing suite provides comprehensive automated testing for your CRM system directly against your live domain. It includes advanced features for 2FA testing, organization management, mobile responsiveness, email system verification, and proper cleanup procedures.

## 🚀 Features

### Core Testing Areas
- **Authentication & Security**: Login flows, password validation, failed login protection, XSS/CSRF protection
- **2FA System**: Complete workflow testing from setup to verification, backup codes, invalid code handling
- **Organization Management**: CRUD operations, user assignments, permissions, bulk operations
- **Ticket Management**: Creation, assignment, status changes, comments, filtering, closing/reopening
- **Email System**: Notifications, templates, queue system, bounce handling, password reset emails
- **Mobile Responsiveness**: Multiple viewport sizes, touch interface, responsive layout verification
- **Toast Notifications**: User feedback system testing
- **Activity Logging**: Verification of logging system, duplicate prevention
- **Performance Testing**: Load times, search performance, system resource usage

### Advanced Capabilities
- **Live Domain Testing**: Run directly against your hosting environment via SSH
- **Comprehensive Cleanup**: Removes all test data while preserving activity logs
- **Secret Key Prompting**: Secure handling of sensitive operations
- **Multiple User Creation**: Tests registration without form limitations
- **Cross-Browser Support**: Chrome with mobile emulation
- **Detailed Reporting**: Comprehensive test results with categorization

## 📁 File Structure

```
crm/management/commands/
├── comprehensive_live_test.py     # Main test orchestrator
├── twofa_test_suite.py           # 2FA system testing
├── organization_test_suite.py    # Organization management testing
├── email_test_suite.py           # Email system testing
└── mobile_test_suite.py          # Mobile responsiveness testing

# Deployment Scripts
├── live_domain_test.sh           # Linux/Unix deployment script
├── live_domain_test.ps1          # Windows PowerShell script
└── requirements.txt              # Updated with testing dependencies
```

## 🛠️ Installation & Setup

### 1. Install Dependencies

```bash
# Install testing dependencies
pip install selenium==4.15.0 pytest==7.4.3 pytest-django==4.7.0 webdriver-manager==4.0.1 pyotp==2.9.0 Pillow qrcode
```

### 2. For Live Domain Testing (SSH)

#### Linux/Unix:
```bash
# Upload and run the deployment script
chmod +x live_domain_test.sh
./live_domain_test.sh
```

#### Windows (PowerShell):
```powershell
# Run the PowerShell script
.\live_domain_test.ps1
```

### 3. Manual Django Command

```bash
# Run comprehensive tests
python manage.py comprehensive_live_test --username=admin --password=yourpass --domain=https://yourdomain.com

# Cleanup only
python manage.py comprehensive_live_test --username=admin --password=yourpass --cleanup-only

# Skip cleanup
python manage.py comprehensive_live_test --username=admin --password=yourpass --skip-cleanup
```

## 🧪 Test Categories

### Authentication & Security Tests
- ✅ Admin login flow verification
- ✅ Password validation visual feedback
- ✅ Failed login protection mechanisms
- ✅ XSS protection verification
- ✅ CSRF token validation
- ✅ Session management

### 2FA System Tests
- ✅ 2FA setup process (QR code/manual secret)
- ✅ TOTP code generation and verification
- ✅ Login with 2FA verification
- ✅ Backup codes generation and usage
- ✅ Invalid code handling
- ✅ 2FA disable functionality

### Organization Management Tests
- ✅ Organization creation with full data
- ✅ Organization editing and updates
- ✅ User assignment to organizations
- ✅ User removal from organizations
- ✅ Organization permissions verification
- ✅ Organization deletion with confirmation
- ✅ Listing and filtering functionality
- ✅ Bulk operations support

### Ticket Management Tests
- ✅ Ticket creation with assignments
- ✅ Status changes and history tracking
- ✅ Comments and attachments
- ✅ Filtering and search functionality
- ✅ Ticket closing and reopening
- ✅ Assignment workflows
- ✅ Priority and category management

### Email System Tests
- ✅ Email configuration verification
- ✅ Password reset email delivery
- ✅ Ticket notification emails
- ✅ User registration emails
- ✅ Organization invitation emails
- ✅ Email template system
- ✅ Email queue management
- ✅ Bounce handling verification

### Mobile Responsiveness Tests
- ✅ Multiple viewport sizes (iPhone, Android, iPad)
- ✅ Touch interface compatibility
- ✅ Mobile navigation elements
- ✅ Responsive layout verification
- ✅ Form usability on mobile
- ✅ Performance on mobile viewports

### UI & System Tests
- ✅ Toast notification system
- ✅ Dashboard filters and search
- ✅ Activity logging verification
- ✅ No duplicate login logs
- ✅ Performance load testing
- ✅ Resource usage monitoring

## 🔧 Configuration Options

### Command Line Arguments
```bash
--username=ADMIN_USER      # Admin username for login
--password=ADMIN_PASS      # Admin password for login
--domain=DOMAIN_URL        # Domain to test (default: https://dev.betulait.usermd.net)
--headless                 # Run browser in headless mode
--cleanup-only             # Only run cleanup, no tests
--skip-cleanup             # Skip cleanup after tests
```

### Environment Variables
```bash
# Email for testing (prompted if not set)
TEST_EMAIL=admin@yourdomain.com

# Browser settings
BROWSER_HEADLESS=true
BROWSER_WIDTH=1920
BROWSER_HEIGHT=1080
```

## 🧹 Cleanup Procedures

The testing suite includes comprehensive cleanup to ensure your live system remains pristine:

### What Gets Cleaned Up:
- ✅ Test user accounts created during testing
- ✅ Test tickets and comments
- ✅ Test organizations
- ✅ Test email notifications (from queue)
- ✅ Test attachments and files

### What Gets Preserved:
- ✅ Activity logs (for verification)
- ✅ Existing user data
- ✅ Production tickets and organizations
- ✅ System configurations
- ✅ Email templates

### Secret Key Handling:
- Activity log operations require secret key input
- Prompted securely in terminal
- Never stored or logged
- Optional - can skip activity log wiping

## 📊 Test Results & Reporting

### Result Categories:
- **PASS**: Test completed successfully
- **FAIL**: Test failed with error details
- **SKIP**: Test skipped (feature not available)
- **PARTIAL**: Test partially completed

### Report Sections:
1. **Executive Summary**: Overall statistics and success rate
2. **Category Breakdown**: Results by test category
3. **Failed Test Details**: Specific error information
4. **Test Data Summary**: Created and cleaned up items
5. **Performance Metrics**: Timing and resource usage

### Sample Output:
```
🧪 COMPREHENSIVE TEST RESULTS
================================================================================
📊 Total Tests: 28
✅ Passed: 24
❌ Failed: 2
⏱️  Total Time: 145.67 seconds
📈 Success Rate: 85.7%

📋 TEST CATEGORIES:
  Authentication & Security: 5/6 passed
  2FA System: 4/4 passed
  Organization Management: 6/6 passed
  Ticket Management: 5/5 passed
  Email System: 4/4 passed
  UI & Responsiveness: 0/3 passed

🗂️  TEST DATA CREATED:
  Users: 3
  Tickets: 2
  Organizations: 1

🧹 Cleanup completed. Activity logs preserved for verification.
```

## 🔍 Troubleshooting

### Common Issues:

#### Chrome/ChromeDriver Issues:
```bash
# Install Chrome (Linux)
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | sudo apt-key add -
echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" | sudo tee /etc/apt/sources.list.d/google-chrome.list
sudo apt-get update && sudo apt-get install google-chrome-stable

# Update ChromeDriver
pip install --upgrade webdriver-manager
```

#### Permission Issues:
```bash
# Make scripts executable
chmod +x live_domain_test.sh

# Run with appropriate permissions
sudo ./live_domain_test.sh  # if needed
```

#### Python Dependencies:
```bash
# Reinstall testing dependencies
pip install --force-reinstall selenium pytest pytest-django webdriver-manager
```

#### Memory Issues:
```bash
# Monitor memory usage
htop
# or
./live_domain_test.sh  # Select option 6 for monitoring
```

### Test-Specific Issues:

#### 2FA Tests Failing:
- Ensure 2FA is properly configured in admin
- Check if QR code generation is working
- Verify TOTP library compatibility

#### Email Tests Failing:
- Verify SMTP configuration
- Check email queue system
- Ensure test email address is valid

#### Organization Tests Failing:
- Verify admin permissions
- Check organization model permissions
- Ensure Django admin is accessible

## 🚀 Advanced Usage

### Running Specific Test Suites:
```python
# Only run 2FA tests
from crm.management.commands.twofa_test_suite import TwoFactorTestSuite
suite = TwoFactorTestSuite(driver, base_url, username, password)
results = suite.test_2fa_full_workflow()

# Only run organization tests
from crm.management.commands.organization_test_suite import OrganizationTestSuite
suite = OrganizationTestSuite(driver, base_url, username, password)
results = suite.run_full_organization_tests()
```

### Custom Test Integration:
```python
# Add custom tests to the main suite
def test_custom_functionality(self):
    """Your custom test implementation"""
    try:
        # Test logic here
        return {'status': 'PASS', 'message': 'Custom test passed'}
    except Exception as e:
        return {'status': 'FAIL', 'message': f'Custom test failed: {str(e)}'}

# Add to comprehensive test suite
tests.append(('Custom Functionality Test', self.test_custom_functionality))
```

### Continuous Integration:
```yaml
# .github/workflows/live-testing.yml
name: Live Domain Tests
on:
  schedule:
    - cron: '0 2 * * *'  # Daily at 2 AM
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Run Live Domain Tests
      run: |
        python manage.py comprehensive_live_test \
          --username=${{ secrets.ADMIN_USER }} \
          --password=${{ secrets.ADMIN_PASS }} \
          --domain=${{ secrets.LIVE_DOMAIN }} \
          --headless
```

## 🛡️ Security Considerations

- **Credentials**: Never commit admin credentials to version control
- **Test Data**: All test data is automatically cleaned up
- **Live System**: Tests are designed to be non-destructive
- **Secret Keys**: Prompted securely, never stored
- **Network**: Tests run over HTTPS with proper security headers
- **Isolation**: Test data is clearly marked and isolated

## 📈 Performance Monitoring

The test suite includes built-in performance monitoring:

- **Load Times**: Dashboard, search, form submissions
- **Memory Usage**: Browser and system memory tracking
- **CPU Usage**: System resource monitoring during tests
- **Network**: Request/response times
- **Scalability**: Multi-user simulation capabilities

## 🤝 Contributing

To add new tests or enhance existing ones:

1. Follow the existing test pattern in test suites
2. Include proper error handling and cleanup
3. Add comprehensive documentation
4. Test against multiple environments
5. Ensure security best practices

## 📞 Support

For issues or questions:
1. Check the troubleshooting section
2. Review test output logs
3. Verify system requirements
4. Check domain accessibility
5. Validate admin credentials

---

This comprehensive testing suite ensures your CRM system is thoroughly validated across all critical functionality while maintaining the integrity of your live environment.
