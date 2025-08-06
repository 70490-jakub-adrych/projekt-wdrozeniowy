#!/usr/bin/env python3
"""
Quick Setup and Runner for Comprehensive Live Domain Testing
This script helps you quickly set up and run tests without manual configuration
"""

import os
import sys
import subprocess
import getpass
import argparse
from pathlib import Path


def install_dependencies():
    """Install required testing dependencies"""
    print("📦 Installing testing dependencies...")
    
    dependencies = [
        'selenium==4.15.0',
        'pytest==7.4.3',
        'pytest-django==4.7.0',
        'webdriver-manager==4.0.1',
        'pyotp==2.9.0',
        'Pillow',
        'qrcode'
    ]
    
    for dep in dependencies:
        try:
            print(f"Installing {dep}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', dep])
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}: {e}")
            return False
    
    print("✅ All dependencies installed successfully!")
    return True


def check_django_project():
    """Check if we're in a Django project directory"""
    if not Path('manage.py').exists():
        print("❌ Error: manage.py not found!")
        print("Please run this script from your Django project root directory.")
        return False
    
    print("✅ Django project detected")
    return True


def check_chrome_installation():
    """Check if Chrome is installed"""
    try:
        # Try to run chrome --version
        result = subprocess.run(['google-chrome', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Chrome found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    try:
        # Try alternative chrome command
        result = subprocess.run(['chrome', '--version'], 
                              capture_output=True, text=True, timeout=5)
        if result.returncode == 0:
            print(f"✅ Chrome found: {result.stdout.strip()}")
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    
    print("⚠️  Chrome not found. Tests will use webdriver-manager to handle ChromeDriver.")
    return True  # webdriver-manager can handle this


def get_user_inputs():
    """Get user inputs for testing"""
    print("\n🔐 Please provide testing credentials:")
    
    username = input("Admin Username: ").strip()
    password = getpass.getpass("Admin Password: ")
    email = input("Test Email Address: ").strip()
    domain = input("Domain URL (default: https://dev.betulait.usermd.net): ").strip()
    
    if not domain:
        domain = "https://dev.betulait.usermd.net"
    
    if not username or not password or not email:
        print("❌ All fields are required!")
        return None
    
    return {
        'username': username,
        'password': password,
        'email': email,
        'domain': domain
    }


def run_tests(credentials, headless=True, cleanup=True, test_category='all'):
    """Run the ultimate comprehensive tests"""
    print(f"\n🚀 Running ULTIMATE comprehensive tests against {credentials['domain']}")
    
    cmd = [
        sys.executable, 'manage.py', 'ultimate_live_test',
        f'--username={credentials["username"]}',
        f'--password={credentials["password"]}',
        f'--domain={credentials["domain"]}',
        f'--test-category={test_category}'
    ]
    
    if headless:
        cmd.append('--headless')
    
    if not cleanup:
        cmd.append('--skip-cleanup')
    
    try:
        # Set environment variable for email
        env = os.environ.copy()
        env['TEST_EMAIL'] = credentials['email']
        
        result = subprocess.run(cmd, env=env)
        
        if result.returncode == 0:
            print("\n✅ Tests completed successfully!")
            return True
        else:
            print(f"\n❌ Tests failed with exit code {result.returncode}")
            if result.returncode == 1:
                print("💡 This might be due to DEBUG=False protection.")
                print("Set DEBUG=True in settings.py for live domain testing.")
            return False
            
    except KeyboardInterrupt:
        print("\n⚠️  Tests interrupted by user")
        return False
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        return False


def cleanup_only(credentials):
    """Run cleanup only"""
    print(f"\n🧹 Running cleanup against {credentials['domain']}")
    
    cmd = [
        sys.executable, 'manage.py', 'ultimate_live_test',
        f'--username={credentials["username"]}',
        f'--password={credentials["password"]}',
        f'--domain={credentials["domain"]}',
        '--cleanup-only',
        '--headless'
    ]
    
    try:
        result = subprocess.run(cmd)
        
        if result.returncode == 0:
            print("\n✅ Cleanup completed successfully!")
            return True
        else:
            print(f"\n❌ Cleanup failed with exit code {result.returncode}")
            if result.returncode == 1:
                print("💡 This might be due to DEBUG=False protection.")
            return False
            
    except Exception as e:
        print(f"\n❌ Error running cleanup: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Quick setup and runner for ULTIMATE comprehensive live domain testing')
    parser.add_argument('--install-deps', action='store_true', help='Install testing dependencies')
    parser.add_argument('--cleanup-only', action='store_true', help='Run cleanup only')
    parser.add_argument('--no-headless', action='store_true', help='Run browser in visible mode')
    parser.add_argument('--skip-cleanup', action='store_true', help='Skip cleanup after tests')
    parser.add_argument('--test-category', choices=[
        'auth', 'security', '2fa', 'organizations', 'tickets', 'email', 'mobile', 'ui', 'all'
    ], default='all', help='Run specific test category')
    parser.add_argument('--username', help='Admin username')
    parser.add_argument('--password', help='Admin password')
    parser.add_argument('--email', help='Test email address')
    parser.add_argument('--domain', default='https://dev.betulait.usermd.net', help='Domain to test')
    
    args = parser.parse_args()
    
    print("🌐 ULTIMATE Comprehensive Live Domain Testing Setup")
    print("=" * 55)
    print("⚠️  INCLUDES DEBUG=False PROTECTION FOR PRODUCTION SAFETY")
    print("=" * 55)
    
    # Check if we're in a Django project
    if not check_django_project():
        sys.exit(1)
    
    # Install dependencies if requested
    if args.install_deps:
        if not install_dependencies():
            sys.exit(1)
        print()
    
    # Check Chrome installation
    check_chrome_installation()
    
    # Get credentials
    if args.username and args.password and args.email:
        credentials = {
            'username': args.username,
            'password': args.password,
            'email': args.email,
            'domain': args.domain
        }
    else:
        credentials = get_user_inputs()
        if not credentials:
            sys.exit(1)
    
    # Run tests or cleanup
    if args.cleanup_only:
        success = cleanup_only(credentials)
    else:
        headless = not args.no_headless
        cleanup = not args.skip_cleanup
        success = run_tests(credentials, headless=headless, cleanup=cleanup, 
                          test_category=args.test_category)
    
    if success:
        print("\n🎉 Operation completed successfully!")
        if not args.cleanup_only:
            print("\nNext steps:")
            print("1. Review the comprehensive test results above")
            print("2. Check your domain for any remaining test data")
            print("3. Verify activity logs for test operations")
            print("4. Remember to set DEBUG=False in production!")
    else:
        print("\n💡 Troubleshooting tips:")
        print("1. Ensure DEBUG=True in settings.py for live testing")
        print("2. Ensure Chrome is installed and up to date")
        print("3. Check your internet connection")
        print("4. Verify admin credentials are correct")
        print("5. Make sure the domain is accessible")
        sys.exit(1)


if __name__ == "__main__":
    main()
