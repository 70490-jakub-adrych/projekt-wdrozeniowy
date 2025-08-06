# CRM System Automated Testing Suite

This directory contains a comprehensive automated testing suite for the CRM system. The tests cover authentication, permissions, ticket management, email functionality, and more.

## Test Structure

```
tests/
├── __init__.py                 # Test package initialization
├── base.py                    # Base test classes and utilities
├── test_authentication.py    # Authentication and permission tests
├── test_tickets.py           # Ticket functionality tests
├── test_models.py            # Model and form tests
├── test_integrations.py      # Email, API, and integration tests
├── test_selenium.py          # End-to-end browser tests
└── README.md                 # This file
```

## Setup Instructions

### 1. Install Testing Dependencies

```bash
# Install required packages for testing
pip install -r test-requirements.txt
```

### 2. Install Chrome WebDriver

For Selenium tests, you need Chrome and ChromeDriver:

**Windows:**
```bash
# Download ChromeDriver from https://chromedriver.chromium.org/
# Or use chocolatey:
choco install chromedriver
```

**Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install chromium-chromedriver

# Or download manually and add to PATH
```

**macOS:**
```bash
# Using Homebrew
brew install chromedriver
```

### 3. Configure Test Settings

The tests use in-memory SQLite database by default for speed. No additional configuration needed.

## Running Tests

### Run All Tests
```bash
# Using Django's test runner
python manage.py test tests

# Using the custom test runner
python run_tests.py
```

### Run Specific Test Suites
```bash
# Authentication tests only
python run_tests.py auth

# Ticket functionality tests
python run_tests.py tickets

# Model tests
python run_tests.py models

# Integration tests
python run_tests.py integrations

# Selenium browser tests
python run_tests.py selenium
```

### Run Tests with Coverage Report
```bash
# Generate coverage report
python run_tests.py coverage

# View HTML coverage report
# Open htmlcov/index.html in browser
```

### Run Tests Against Live Domain
```bash
# Test against dev.betulait.usermd.net
python manage.py test_live_domain --username=your_username --password=your_password

# Run in visible browser (not headless)
python manage.py test_live_domain --username=your_username --password=your_password --domain=https://dev.betulait.usermd.net

# Verbose output
python manage.py test_live_domain --username=your_username --password=your_password --verbose
```

## Test Categories

### 1. Authentication Tests (`test_authentication.py`)
- ✅ Valid/invalid login credentials
- ✅ Login with email address
- ✅ Email verification process
- ✅ User registration validation
- ✅ Password strength validation
- ✅ Failed login attempt tracking
- ✅ Account lockout after 5 failed attempts
- ✅ Role-based access control
- ✅ Permission checks for different user roles
- ✅ Activity logging for auth events
- ✅ No duplicate login logs

### 2. Ticket Management Tests (`test_tickets.py`)
- ✅ Ticket creation by clients/agents
- ✅ Ticket creation with attachments
- ✅ Form validation
- ✅ Ticket viewing permissions
- ✅ Ticket assignment to agents
- ✅ Status changes
- ✅ Comment functionality
- ✅ Attachment uploads
- ✅ Search and filtering
- ✅ Ticket workflow (open → in_progress → resolved → closed)

### 3. Model and Form Tests (`test_models.py`)
- ✅ Model validation and constraints
- ✅ Model relationships
- ✅ String representations
- ✅ Business logic methods
- ✅ Form validation
- ✅ Field widgets and choices
- ✅ Custom model managers
- ✅ Signal handling

### 4. Integration Tests (`test_integrations.py`)
- ✅ Email notification system
- ✅ API endpoints and AJAX functionality
- ✅ Complete user workflows
- ✅ Cross-component integration
- ✅ Performance with large datasets
- ✅ Security features (XSS, CSRF, SQL injection protection)

### 5. Browser Tests (`test_selenium.py`)
- ✅ Complete login/logout flows
- ✅ Real-time password validation feedback
- ✅ Ticket creation through browser
- ✅ User registration process
- ✅ Role-based UI restrictions
- ✅ Responsive design testing
- ✅ Activity logging verification

## Test Data

Tests create their own isolated test data:
- Test users with different roles (admin, agent, client, viewer)
- Test tickets with various statuses and priorities
- Test categories and comments
- Mock email backends for email testing

## Environment Variables

Optional environment variables for testing:

```bash
# Show browser during Selenium tests (default: headless)
export SHOW_BROWSER=1

# Test against live domain
export TEST_USERNAME=your_username
export TEST_PASSWORD=your_password
```

## Test Results Interpretation

### Pass/Fail Status
- ✅ **PASS**: Test completed successfully
- ❌ **FAIL**: Test failed with error

### Common Test Failures and Solutions

**1. Selenium Tests Failing**
```
WebDriverException: 'chromedriver' executable needs to be in PATH
```
**Solution**: Install ChromeDriver and add to PATH

**2. Database Errors**
```
django.db.utils.OperationalError: no such table
```
**Solution**: Tests use in-memory database, this shouldn't happen. Check Django settings.

**3. Import Errors**
```
ImportError: No module named 'selenium'
```
**Solution**: Install test dependencies: `pip install -r test-requirements.txt`

**4. Permission Errors**
```
AssertionError: Expected 403, got 200
```
**Solution**: Check permission decorators and middleware are working correctly.

## Performance Benchmarks

The test suite includes performance tests that verify:
- Dashboard loads in <5 seconds with 100+ tickets
- Search completes in <3 seconds with 50+ tickets
- Login process completes in <2 seconds

## Security Tests

Automated security tests check for:
- SQL injection protection
- XSS (Cross-Site Scripting) protection
- CSRF (Cross-Site Request Forgery) protection
- Unauthorized access prevention
- Session security

## Adding New Tests

### Creating a New Test

1. **Unit Tests**: Add to existing test files or create new ones
```python
class NewFeatureTestCase(BaseTestCase):
    def test_new_functionality(self):
        # Test implementation
        pass
```

2. **Selenium Tests**: Add to `test_selenium.py`
```python
def test_new_browser_feature(self):
    self.login_user('test_user', 'password')
    # Browser interaction code
```

3. **Integration Tests**: Add to `test_integrations.py`
```python
def test_new_integration(self):
    # Test component interaction
    pass
```

### Test Naming Conventions
- Test files: `test_*.py`
- Test classes: `*TestCase`
- Test methods: `test_*`
- Use descriptive names: `test_client_can_create_ticket_with_attachment`

### Test Data Best Practices
- Use `BaseTestCase.setUpTestData()` for data shared across test methods
- Use `setUp()` for data needed fresh for each test
- Clean up test data when necessary
- Use factories for complex test data generation

## Continuous Integration

The test suite is designed to run in CI/CD environments:

```yaml
# Example GitHub Actions workflow
name: Run Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -r test-requirements.txt
      - name: Run tests
        run: python run_tests.py
```

## Coverage Goals

Target coverage percentages:
- **Overall**: >90%
- **Models**: >95%
- **Views**: >85%
- **Forms**: >90%
- **Utilities**: >80%

## Troubleshooting

### Common Issues

1. **Tests Running Slowly**
   - Use `--keepdb` flag: `python manage.py test --keepdb`
   - Check for unnecessary database queries
   - Use `setUpTestData()` instead of `setUp()` where possible

2. **Selenium Tests Flaky**
   - Add explicit waits instead of `time.sleep()`
   - Use `WebDriverWait` with expected conditions
   - Increase timeout values if needed

3. **Email Tests Not Working**
   - Check `EMAIL_BACKEND` is set to `locmem` for tests
   - Clear `mail.outbox` between tests

4. **Permission Tests Failing**
   - Verify middleware order in settings
   - Check permission decorators are applied correctly
   - Ensure test users have correct roles

### Getting Help

- Check test output for detailed error messages
- Run tests with `--verbose` flag for more information
- Use `--keepdb` to inspect test database state
- Add `import pdb; pdb.set_trace()` for debugging

### Live Domain Testing

When testing against the live domain (dev.betulait.usermd.net):
- Ensure you have valid credentials
- Test user should have appropriate permissions
- Some tests may fail due to role restrictions (this is expected)
- Use `--verbose` flag to see detailed test progress

## Test Maintenance

Regular maintenance tasks:
- Update test data when models change
- Add tests for new features
- Remove tests for deprecated functionality
- Update Selenium selectors when UI changes
- Review and update performance benchmarks
- Keep test dependencies up to date
