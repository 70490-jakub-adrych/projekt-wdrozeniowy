#!/usr/bin/env python
"""Debug script for password reset token validation"""

import os
import sys
import django
from django.conf import settings

# Add the project directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'projekt_wdrozeniowy.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.urls import reverse

User = get_user_model()

def debug_password_reset():
    print("=== PASSWORD RESET DEBUG ===")
    print(f"SECRET_KEY (first 10 chars): {settings.SECRET_KEY[:10]}...")
    print(f"PASSWORD_RESET_TIMEOUT: {getattr(settings, 'PASSWORD_RESET_TIMEOUT', 'Not set')}")
    print()
    
    # Find a user to test with
    try:
        user = User.objects.filter(is_active=True).first()
        if not user:
            print("No active users found!")
            return
            
        print(f"Testing with user: {user.username} (ID: {user.pk})")
        print(f"User is active: {user.is_active}")
        print(f"User email: {user.email}")
        print()
        
        # Generate a fresh token
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)
        
        print(f"Generated uidb64: {uidb64}")
        print(f"Generated token: {token}")
        print()
        
        # Test decoding uidb64
        try:
            decoded_uid = force_str(urlsafe_base64_decode(uidb64))
            print(f"Decoded UID: {decoded_uid}")
            
            # Find user by decoded UID
            test_user = User.objects.get(pk=decoded_uid)
            print(f"Found user by UID: {test_user.username}")
            print()
            
            # Test token validation
            is_valid = default_token_generator.check_token(test_user, token)
            print(f"Token is valid: {is_valid}")
            
            if not is_valid:
                print("Token validation failed!")
                # Try to understand why
                
                # Check if user changed recently
                print(f"User last_login: {test_user.last_login}")
                print(f"User date_joined: {test_user.date_joined}")
                
        except Exception as e:
            print(f"Error decoding UID: {e}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    debug_password_reset()
