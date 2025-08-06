#!/usr/bin/env python3
"""
Quick Django-OTP Migration Fix
This will create the necessary database tables for 2FA functionality
"""

import os
import sys
import subprocess

def run_command(command, description):
    """Run a command and show the result"""
    print(f"🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ {description} - SUCCESS")
            if result.stdout.strip():
                print(f"   Output: {result.stdout.strip()}")
        else:
            print(f"❌ {description} - FAILED")
            print(f"   Error: {result.stderr.strip()}")
        return result.returncode == 0
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def main():
    print("🚀 FIXING DJANGO-OTP DATABASE MIGRATIONS")
    print("=" * 50)
    
    # Check if we're in a Django project
    if not os.path.exists('manage.py'):
        print("❌ manage.py not found! Run this from your Django project directory")
        sys.exit(1)
    
    print("📂 Django project detected")
    
    # Step 1: Show current migration status
    print("\n📋 Checking current migration status...")
    run_command("python manage.py showmigrations django_otp", "Checking django_otp migrations")
    
    # Step 2: Make migrations for django-otp
    print("\n🔧 Creating django-otp migrations...")
    run_command("python manage.py makemigrations django_otp", "Making django_otp migrations")
    
    # Step 3: Apply django-otp migrations
    print("\n🔧 Applying django-otp migrations...")
    success1 = run_command("python manage.py migrate django_otp", "Applying django_otp core migrations")
    
    # Step 4: Apply otp_static migrations
    print("\n🔧 Applying otp_static migrations...")
    success2 = run_command("python manage.py migrate otp_static", "Applying otp_static migrations")
    
    # Step 5: Apply otp_totp migrations
    print("\n🔧 Applying otp_totp migrations...")
    success3 = run_command("python manage.py migrate otp_totp", "Applying otp_totp migrations")
    
    # Step 6: Apply all remaining migrations
    print("\n🔧 Applying all remaining migrations...")
    success4 = run_command("python manage.py migrate", "Applying all migrations")
    
    # Step 7: Verify the fix
    print("\n🧪 Testing the fix...")
    test_success = run_command("python -c \"import django; import os; os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings'); django.setup(); from django_otp.models import Device; print(f'Device model accessible! Total devices: {Device.objects.count()}')\"", "Testing Device model access")
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MIGRATION RESULTS")
    print("=" * 50)
    
    if success1 and success2 and success3 and success4 and test_success:
        print("🎉 ALL MIGRATIONS SUCCESSFUL!")
        print("✅ django-otp database tables created")
        print("✅ Device model is now accessible")
        print("✅ Your 2FA tests should now work much better!")
        
        print("\n🚀 NEXT STEPS:")
        print("1. Run: python enhanced_2fa_setup.py --username=admin")
        print("2. Then test: python manage.py ultimate_live_test --test-category=2fa")
        
    else:
        print("⚠️  Some migrations had issues")
        print("💡 Try running manually:")
        print("   python manage.py migrate")
        print("   python manage.py showmigrations")

if __name__ == "__main__":
    main()
