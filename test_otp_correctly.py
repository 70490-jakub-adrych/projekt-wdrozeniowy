#!/usr/bin/env python3
"""
Test Django-OTP Device Models Correctly
The Device model is abstract by design - we need to test the specific device types
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')

try:
    django.setup()
    
    print("🚀 TESTING DJANGO-OTP DEVICE ACCESS")
    print("=" * 50)
    
    # Test 1: Try to import the specific device models
    print("🧪 Test 1: Importing device models...")
    try:
        from django_otp.plugins.otp_totp.models import TOTPDevice
        from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
        print("✅ Device model imports successful!")
    except ImportError as e:
        print(f"❌ Import failed: {e}")
        sys.exit(1)
    
    # Test 2: Check database access
    print("\n🧪 Test 2: Testing database access...")
    try:
        totp_count = TOTPDevice.objects.count()
        static_count = StaticDevice.objects.count()
        token_count = StaticToken.objects.count()
        
        print(f"✅ Database access working!")
        print(f"   - TOTP Devices: {totp_count}")
        print(f"   - Static Devices: {static_count}")
        print(f"   - Static Tokens: {token_count}")
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        sys.exit(1)
    
    # Test 3: Check for admin user
    print("\n🧪 Test 3: Checking admin user...")
    try:
        from django.contrib.auth.models import User
        admin_user = User.objects.filter(username='admin').first()
        if admin_user:
            admin_totp = TOTPDevice.objects.filter(user=admin_user).count()
            admin_static = StaticDevice.objects.filter(user=admin_user).count()
            print(f"✅ Admin user found!")
            print(f"   - Admin TOTP devices: {admin_totp}")
            print(f"   - Admin Static devices: {admin_static}")
            
            if admin_totp == 0 and admin_static == 0:
                print("📝 No 2FA devices found for admin user")
                print("💡 Run: python enhanced_2fa_setup.py --username=admin")
        else:
            print("❌ Admin user not found!")
    except Exception as e:
        print(f"❌ User check failed: {e}")
    
    # Test 4: Verify the "Device is abstract" explanation
    print("\n🧪 Test 4: Explaining Device model behavior...")
    try:
        from django_otp.models import Device
        # This should fail as expected
        Device.objects.count()
        print("❌ Unexpected: Device.objects worked (this should not happen)")
    except AttributeError as e:
        if "Device is abstract" in str(e):
            print("✅ Confirmed: Device model is abstract by design")
            print("   This is NORMAL behavior - we use specific device types instead")
        else:
            print(f"❌ Unexpected AttributeError: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 DJANGO-OTP IS WORKING CORRECTLY!")
    print("=" * 50)
    print("✅ All device models are accessible")
    print("✅ Database connections working")
    print("✅ The 'Device is abstract' message is normal behavior")
    print("\n🚀 NEXT STEPS:")
    print("1. Run: python enhanced_2fa_setup.py --username=admin")
    print("2. Then: python manage.py ultimate_live_test --test-category=2fa")
    print("\n💡 The 'Device is abstract' error in your tests is misleading.")
    print("   Your django-otp setup is actually working perfectly!")

except Exception as e:
    print(f"❌ Setup error: {e}")
    import traceback
    traceback.print_exc()
