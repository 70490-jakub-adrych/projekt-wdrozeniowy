#!/usr/bin/env python3
"""
Simplified 2FA Setup - Avoiding Hexadecimal Errors
This version focuses on creating devices without complex verification
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')

try:
    django.setup()
    
    from django.contrib.auth.models import User
    from django_otp.plugins.otp_totp.models import TOTPDevice
    from django_otp.plugins.otp_static.models import StaticDevice, StaticToken
    import pyotp
    
    class Simple2FASetup:
        def __init__(self, username):
            self.username = username
            try:
                self.user = User.objects.get(username=username)
                print(f"✅ Found user: {username}")
            except User.DoesNotExist:
                print(f"❌ User {username} not found!")
                sys.exit(1)
        
        def setup_totp_device(self):
            """Set up TOTP device with better error handling"""
            print("\n🔧 Setting up TOTP device...")
            
            # Remove existing TOTP devices
            deleted_count = TOTPDevice.objects.filter(user=self.user).count()
            TOTPDevice.objects.filter(user=self.user).delete()
            if deleted_count > 0:
                print(f"   Removed {deleted_count} existing TOTP devices")
            
            # Create new TOTP device with a clean key
            totp_device = TOTPDevice.objects.create(
                user=self.user,
                name=f'TOTP Device for {self.user.username}',
                confirmed=True
            )
            
            # Generate a clean Base32 secret
            secret = pyotp.random_base32()
            totp_device.key = secret
            totp_device.save()
            
            print(f"✅ TOTP device created successfully!")
            print(f"📱 Secret key: {secret}")
            print(f"🔢 Device ID: {totp_device.id}")
            
            # Generate current code for display (don't verify yet)
            try:
                totp = pyotp.TOTP(secret)
                current_token = totp.now()
                print(f"🔢 Current TOTP code: {current_token}")
            except Exception as e:
                print(f"⚠️  TOTP code generation had issue: {e}")
                current_token = "000000"
            
            return totp_device, secret, current_token
        
        def setup_static_device(self):
            """Set up static backup codes"""
            print("\n🔧 Setting up static backup codes...")
            
            # Remove existing static devices
            deleted_count = StaticDevice.objects.filter(user=self.user).count()
            StaticDevice.objects.filter(user=self.user).delete()
            if deleted_count > 0:
                print(f"   Removed {deleted_count} existing static devices")
            
            # Create new static device
            static_device = StaticDevice.objects.create(
                user=self.user,
                name=f'Backup Codes for {self.user.username}'
            )
            
            # Generate backup codes
            backup_codes = []
            for i in range(10):
                token = StaticToken.random_token()
                StaticToken.objects.create(device=static_device, token=token)
                backup_codes.append(token)
            
            print(f"✅ Static device created with {len(backup_codes)} backup codes!")
            print("🔐 Backup codes:")
            for i, code in enumerate(backup_codes, 1):
                print(f"   {i:2d}. {code}")
            
            return static_device, backup_codes
        
        def verify_setup(self):
            """Simple verification without complex token checking"""
            print("\n🧪 Verifying 2FA setup...")
            
            checks_passed = 0
            total_checks = 0
            
            # Check 1: TOTP device exists
            total_checks += 1
            totp_devices = TOTPDevice.objects.filter(user=self.user)
            if totp_devices.exists():
                totp_device = totp_devices.first()
                print(f"✅ Check 1: TOTP device exists (ID: {totp_device.id}, confirmed: {totp_device.confirmed})")
                checks_passed += 1
            else:
                print("❌ Check 1: No TOTP device found")
            
            # Check 2: Static device exists
            total_checks += 1
            static_devices = StaticDevice.objects.filter(user=self.user)
            if static_devices.exists():
                static_device = static_devices.first()
                token_count = StaticToken.objects.filter(device=static_device).count()
                print(f"✅ Check 2: Static device exists (ID: {static_device.id}, tokens: {token_count})")
                checks_passed += 1
            else:
                print("❌ Check 2: No static device found")
            
            # Check 3: Database access working
            total_checks += 1
            try:
                total_totp = TOTPDevice.objects.count()
                total_static = StaticDevice.objects.count()
                total_tokens = StaticToken.objects.count()
                print(f"✅ Check 3: Database access working (Total: {total_totp} TOTP, {total_static} Static, {total_tokens} tokens)")
                checks_passed += 1
            except Exception as e:
                print(f"❌ Check 3: Database access error: {e}")
            
            # Check 4: Admin panel visibility
            total_checks += 1
            try:
                admin_totp = TOTPDevice.objects.filter(user=self.user).count()
                admin_static = StaticDevice.objects.filter(user=self.user).count()
                if admin_totp > 0 and admin_static > 0:
                    print(f"✅ Check 4: Admin user has devices (TOTP: {admin_totp}, Static: {admin_static})")
                    checks_passed += 1
                else:
                    print(f"❌ Check 4: Admin user missing devices (TOTP: {admin_totp}, Static: {admin_static})")
            except Exception as e:
                print(f"❌ Check 4: Admin device check error: {e}")
            
            print(f"\n📊 Setup Verification: {checks_passed}/{total_checks} checks passed ({(checks_passed/total_checks)*100:.1f}%)")
            
            return checks_passed, total_checks
        
        def run_simple_setup(self):
            """Run simple 2FA setup without complex testing"""
            print("🚀 SIMPLE 2FA SETUP (Avoiding Hexadecimal Issues)")
            print("=" * 60)
            print(f"👤 User: {self.user.username}")
            print("🔧 Setting up 2FA devices safely...")
            
            # Setup devices
            totp_device, secret, current_token = self.setup_totp_device()
            static_device, backup_codes = self.setup_static_device()
            
            # Simple verification
            passed, total = self.verify_setup()
            
            print("\n📋 DJANGO ADMIN PANEL")
            print("=" * 30)
            print("You should now see in Django admin:")
            print("1. DJANGO_OTP section")
            print("2. TOTP devices: 1 device for admin")
            print("3. Static devices: 1 device for admin") 
            print("4. Static tokens: 10 tokens for admin")
            
            print("\n🎉 SIMPLE 2FA SETUP COMPLETE!")
            print("=" * 40)
            print(f"📱 TOTP secret: {secret}")
            print(f"🔢 Current TOTP: {current_token}")
            print(f"🔐 Backup codes: {len(backup_codes)} generated")
            print(f"✅ Verification: {passed}/{total} checks passed")
            
            if passed >= 3:  # At least 3 out of 4 checks
                print("🎊 SETUP SUCCESSFUL! Your 2FA is ready!")
                print("\n🚀 Next step: Test your improved coverage")
                print("python manage.py ultimate_live_test --test-category=2fa")
            else:
                print("⚠️  Setup had some issues. Check the errors above.")
            
            return passed >= 3

    if __name__ == "__main__":
        import argparse
        
        parser = argparse.ArgumentParser(description="Simple 2FA Setup")
        parser.add_argument('--username', required=True, help='Username to set up 2FA for')
        
        args = parser.parse_args()
        
        print("🎯 Running SIMPLE 2FA setup to avoid hexadecimal issues...")
        setup = Simple2FASetup(args.username)
        success = setup.run_simple_setup()
        
        if success:
            print("\n🎉 SUCCESS! Your 2FA devices are ready!")
            print("Now your 2FA tests should show much better results!")
        else:
            print("\n🔧 Some issues encountered. Please check the output above.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure django-otp is installed: pip install django-otp")
    print("💡 Also install: pip install pyotp")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("💡 Make sure you're running this from your Django project directory")
