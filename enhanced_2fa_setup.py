#!/usr/bin/env python3
"""
Enhanced 2FA Testing Script with Device Management
This script will help you set up OTP devices and test 2FA functionality properly
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
    from django_otp.models import Device
    import pyotp
    import qrcode
    from io import BytesIO
    import base64
    
    class Enhanced2FASetup:
        def __init__(self, username):
            self.username = username
            try:
                self.user = User.objects.get(username=username)
                print(f"✅ Found user: {username}")
            except User.DoesNotExist:
                print(f"❌ User {username} not found!")
                sys.exit(1)
        
        def setup_totp_device(self):
            """Set up TOTP device for the user"""
            print("\n🔧 Setting up TOTP device...")
            
            # Remove existing TOTP devices
            TOTPDevice.objects.filter(user=self.user).delete()
            
            # Create new TOTP device
            totp_device = TOTPDevice.objects.create(
                user=self.user,
                name=f'TOTP Device for {self.user.username}',
                confirmed=True  # Auto-confirm for testing
            )
            
            # Generate secret and QR code
            secret = pyotp.random_base32()
            totp_device.key = secret
            totp_device.save()
            
            # Create provisioning URI for QR code
            totp = pyotp.TOTP(secret)
            provisioning_uri = totp.provisioning_uri(
                name=self.user.username,
                issuer_name="CRM System"
            )
            
            print(f"✅ TOTP device created successfully!")
            print(f"📱 Secret key: {secret}")
            print(f"🔗 Provisioning URI: {provisioning_uri}")
            
            # Generate current TOTP code for testing
            current_token = totp.now()
            print(f"🔢 Current TOTP code: {current_token}")
            
            return totp_device, secret, current_token
        
        def setup_static_device(self):
            """Set up static backup codes"""
            print("\n🔧 Setting up static backup codes...")
            
            # Remove existing static devices
            StaticDevice.objects.filter(user=self.user).delete()
            
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
        
        def test_2fa_functionality(self):
            """Test 2FA functionality comprehensively"""
            print("\n🧪 Testing 2FA functionality...")
            
            tests_passed = 0
            total_tests = 0
            
            # Test 1: Check device creation
            total_tests += 1
            totp_devices = TOTPDevice.objects.filter(user=self.user)
            static_devices = StaticDevice.objects.filter(user=self.user)
            
            if totp_devices.exists() and static_devices.exists():
                print("✅ Test 1: TOTP and Static devices exist")
                tests_passed += 1
            else:
                print("❌ Test 1: Missing devices")
            
            # Test 2: Test TOTP verification
            total_tests += 1
            if totp_devices.exists():
                totp_device = totp_devices.first()
                totp = pyotp.TOTP(totp_device.key)
                current_token = totp.now()
                
                # Verify the token
                if totp_device.verify_token(current_token):
                    print(f"✅ Test 2: TOTP verification works (code: {current_token})")
                    tests_passed += 1
                else:
                    print(f"❌ Test 2: TOTP verification failed (code: {current_token})")
            else:
                print("❌ Test 2: No TOTP device to test")
            
            # Test 3: Test static token verification
            total_tests += 1
            if static_devices.exists():
                static_device = static_devices.first()
                static_tokens = static_device.token_set.all()
                
                if static_tokens.exists():
                    test_token = static_tokens.first().token
                    if static_device.verify_token(test_token):
                        print(f"✅ Test 3: Static token verification works")
                        tests_passed += 1
                    else:
                        print(f"❌ Test 3: Static token verification failed")
                else:
                    print("❌ Test 3: No static tokens to test")
            else:
                print("❌ Test 3: No static device to test")
            
            # Test 4: Check if user is_verified
            total_tests += 1
            from django_otp import user_has_device
            if user_has_device(self.user):
                print("✅ Test 4: User has verified 2FA devices")
                tests_passed += 1
            else:
                print("❌ Test 4: User does not have verified devices")
            
            # Test 5: Test device listing
            total_tests += 1
            all_devices = Device.objects.devices_for_user(self.user)
            if len(list(all_devices)) >= 2:  # Should have TOTP + Static
                print(f"✅ Test 5: Multiple device types configured ({len(list(all_devices))} devices)")
                tests_passed += 1
            else:
                print(f"❌ Test 5: Insufficient devices configured ({len(list(all_devices))} devices)")
            
            print(f"\n📊 2FA Test Results: {tests_passed}/{total_tests} tests passed ({(tests_passed/total_tests)*100:.1f}%)")
            
            return tests_passed, total_tests
        
        def generate_admin_instructions(self):
            """Generate instructions for Django admin"""
            print("\n📋 DJANGO ADMIN PANEL INSTRUCTIONS")
            print("=" * 50)
            print("1. Log into Django admin panel")
            print("2. Navigate to 'DJANGO_OTP' section")
            print("3. You should see:")
            print("   - TOTP devices")
            print("   - Static devices") 
            print("   - Static tokens")
            print("\n4. For your user, you should now see:")
            
            totp_count = TOTPDevice.objects.filter(user=self.user).count()
            static_count = StaticDevice.objects.filter(user=self.user).count()
            token_count = StaticToken.objects.filter(device__user=self.user).count()
            
            print(f"   - TOTP devices: {totp_count}")
            print(f"   - Static devices: {static_count}")
            print(f"   - Static tokens: {token_count}")
            
            print("\n✅ All devices should be marked as 'confirmed: True'")
            print("✅ You can manually add/remove devices from admin panel")
            
        def run_complete_setup(self):
            """Run complete 2FA setup and testing"""
            print("🚀 ENHANCED 2FA SETUP AND TESTING")
            print("=" * 50)
            print(f"👤 User: {self.user.username}")
            print("🔧 Setting up comprehensive 2FA testing...")
            
            # Setup devices
            totp_device, secret, current_token = self.setup_totp_device()
            static_device, backup_codes = self.setup_static_device()
            
            # Test functionality
            passed, total = self.test_2fa_functionality()
            
            # Generate admin instructions
            self.generate_admin_instructions()
            
            print("\n🎉 2FA SETUP COMPLETE!")
            print("=" * 50)
            print(f"📱 Your current TOTP code: {current_token}")
            print(f"🔐 Backup codes generated: {len(backup_codes)}")
            print(f"✅ Tests passed: {passed}/{total}")
            
            if passed == total:
                print("🎊 ALL 2FA TESTS PASSED! Your system is fully configured!")
            else:
                print("⚠️  Some tests failed. Check the output above for details.")
            
            return passed == total

    if __name__ == "__main__":
        import argparse
        
        parser = argparse.ArgumentParser(description="Enhanced 2FA Setup and Testing")
        parser.add_argument('--username', required=True, help='Username to set up 2FA for')
        
        args = parser.parse_args()
        
        # Run enhanced 2FA setup
        setup = Enhanced2FASetup(args.username)
        success = setup.run_complete_setup()
        
        if success:
            print("\n🚀 Now run your ultimate_live_test again to see improved 2FA results!")
            print("The 2FA tests should now show much better coverage!")
        else:
            print("\n🔧 Some issues detected. Check the setup and try again.")

except ImportError as e:
    print(f"❌ Import error: {e}")
    print("💡 Make sure django-otp is installed: pip install django-otp")
    print("💡 Also install: pip install pyotp qrcode")
except Exception as e:
    print(f"❌ Error: {e}")
    print("💡 Make sure you're running this from your Django project directory")
