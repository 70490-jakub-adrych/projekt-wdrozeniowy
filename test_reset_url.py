#!/usr/bin/env python
"""Test script to simulate password reset confirmation URL"""

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
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.urls import reverse
from django.test import RequestFactory, Client
from django.contrib.sessions.middleware import SessionMiddleware

User = get_user_model()

def test_password_reset_url():
    print("=== TESTING PASSWORD RESET URL ===")
    
    # Get a test user
    user = User.objects.filter(is_active=True).first()
    if not user:
        print("No active users found!")
        return
        
    print(f"Testing with user: {user.username} (ID: {user.pk})")
    
    # Generate token and uidb64
    uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)
    
    print(f"uidb64: {uidb64}")
    print(f"token: {token}")
    
    # Generate the URL
    reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token})
    print(f"Generated URL: {reset_url}")
    
    # Test the URL with Django test client
    client = Client()
    response = client.get(reset_url)
    
    print(f"Response status: {response.status_code}")
    print(f"Response context keys: {list(response.context.keys()) if response.context else 'No context'}")
    
    if response.context:
        validlink = response.context.get('validlink')
        print(f"validlink in context: {validlink}")
        
        if not validlink:
            print("URL validation failed in view!")
            # Check if there are any additional context variables
            form = response.context.get('form')
            if form:
                print(f"Form class: {form.__class__.__name__}")
                print(f"Form errors: {form.errors}")
    
    # Also test with a fresh token after a delay to see if timing matters
    import time
    print("\n--- Testing after 1 second delay ---")
    time.sleep(1)
    
    # Generate new token
    token2 = default_token_generator.make_token(user)
    print(f"New token: {token2}")
    
    reset_url2 = reverse('password_reset_confirm', kwargs={'uidb64': uidb64, 'token': token2})
    response2 = client.get(reset_url2)
    
    print(f"Response status: {response2.status_code}")
    if response2.context:
        validlink2 = response2.context.get('validlink')
        print(f"validlink in context: {validlink2}")

if __name__ == "__main__":
    test_password_reset_url()
