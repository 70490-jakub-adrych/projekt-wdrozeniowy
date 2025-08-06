#!/usr/bin/env python3
"""
2FA Migration Fix Script
Run this on your SSH hosting environment to fix the 2FA models error
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')

try:
    django.setup()
    from django.core.management import execute_from_command_line
    
    print("🔧 Applying 2FA database migrations...")
    print("This will fix the '2FA models error: Manager isn't available; Device is abstract' issue")
    
    # Apply django-otp migrations
    execute_from_command_line(['manage.py', 'migrate', 'otp_static'])
    execute_from_command_line(['manage.py', 'migrate', 'otp_totp'])
    execute_from_command_line(['manage.py', 'migrate'])
    
    print("✅ 2FA migrations completed successfully!")
    print("📊 Your 2FA tests should now show better results")
    
except Exception as e:
    print(f"❌ Migration error: {e}")
    print("💡 Try running manually: python manage.py migrate")
