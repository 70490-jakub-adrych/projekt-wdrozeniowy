"""
Test configuration and runner script for the CRM system.
Run this script to execute all tests with proper configuration.
"""
import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

# Add the project directory to Python path
project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_dir)

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')
django.setup()

def run_tests():
    """Run all tests with proper configuration"""
    from django.test.runner import DiscoverRunner
    
    # Configure test settings
    test_settings = {
        'DATABASES': {
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',  # Use in-memory database for speed
            }
        },
        'EMAIL_BACKEND': 'django.core.mail.backends.locmem.EmailBackend',
        'PASSWORD_HASHERS': [
            'django.contrib.auth.hashers.MD5PasswordHasher',  # Fast hashing for tests
        ],
        'DEBUG': False,
        'LOGGING_CONFIG': None,  # Disable logging during tests
    }
    
    # Override settings for testing
    for key, value in test_settings.items():
        setattr(settings, key, value)
    
    # Create test runner
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    
    # Run tests
    failures = test_runner.run_tests(['tests'])
    
    if failures:
        print(f"\n❌ {failures} test(s) failed!")
        sys.exit(1)
    else:
        print("\n✅ All tests passed!")
        sys.exit(0)

def run_specific_test_suite(suite_name):
    """Run a specific test suite"""
    from django.test.runner import DiscoverRunner
    
    suite_mapping = {
        'auth': 'tests.test_authentication',
        'tickets': 'tests.test_tickets',
        'models': 'tests.test_models',
        'integrations': 'tests.test_integrations',
        'selenium': 'tests.test_selenium',
    }
    
    if suite_name not in suite_mapping:
        print(f"Unknown test suite: {suite_name}")
        print(f"Available suites: {', '.join(suite_mapping.keys())}")
        sys.exit(1)
    
    test_runner = DiscoverRunner(verbosity=2, interactive=False, keepdb=False)
    failures = test_runner.run_tests([suite_mapping[suite_name]])
    
    if failures:
        sys.exit(1)
    else:
        sys.exit(0)

def run_coverage_report():
    """Run tests with coverage report"""
    try:
        import coverage
    except ImportError:
        print("Coverage.py not installed. Install with: pip install coverage")
        sys.exit(1)
    
    # Start coverage
    cov = coverage.Coverage()
    cov.start()
    
    # Run tests
    run_tests()
    
    # Stop coverage and generate report
    cov.stop()
    cov.save()
    
    print("\n" + "="*50)
    print("COVERAGE REPORT")
    print("="*50)
    
    cov.report(show_missing=True)
    
    # Generate HTML report
    cov.html_report(directory='htmlcov')
    print(f"\nHTML coverage report generated in 'htmlcov' directory")

if __name__ == '__main__':
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == 'coverage':
            run_coverage_report()
        elif command in ['auth', 'tickets', 'models', 'integrations', 'selenium']:
            run_specific_test_suite(command)
        else:
            print(f"Unknown command: {command}")
            print("Available commands:")
            print("  python run_tests.py              - Run all tests")
            print("  python run_tests.py coverage     - Run tests with coverage")
            print("  python run_tests.py auth         - Run authentication tests")
            print("  python run_tests.py tickets      - Run ticket tests")
            print("  python run_tests.py models       - Run model tests")
            print("  python run_tests.py integrations - Run integration tests")
            print("  python run_tests.py selenium     - Run Selenium tests")
            sys.exit(1)
    else:
        run_tests()
