#!/usr/bin/env python3
"""
Test script for the improved device detection functionality.
This script tests various User-Agent strings to ensure proper mobile/tablet/desktop detection.
"""

import os
import sys
import re

# Add the project path to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def get_device_info(user_agent):
    """
    Core device detection logic - identical to the one in context_processors.py
    """
    # Desktop patterns (check first to exclude false positives)
    desktop_patterns = [
        r'Windows NT.*WOW64',      # Windows 64-bit
        r'Windows NT.*Win64',      # Windows 64-bit
        r'Macintosh.*Intel',       # Intel Mac
        r'X11.*Linux.*x86_64',     # Linux 64-bit
        r'X11.*Linux.*i686',       # Linux 32-bit
    ]
    
    # Tablet specific patterns (check before mobile as tablets may contain "Mobile")
    tablet_patterns = [
        r'iPad',                           # iPad
        r'Android(?!.*Mobile).*Tablet',    # Android tablets explicitly
        r'Android.*SM-T\d+',              # Samsung Galaxy Tab series (SM-T...)
        r'Android.*SM-P\d+',              # Samsung Galaxy Note Tab series (SM-P...)
        r'Kindle',                         # Kindle tablets
        r'Silk',                          # Amazon Silk browser
        r'PlayBook',                      # BlackBerry PlayBook
        r'Windows.*Touch.*Tablet',        # Windows tablets
        # Large screen Android devices that are likely tablets (exclude phones and Opera Mini)
        r'Android(?!.*Mobile)(?!.*Opera Mini).*; (?!SM-)',  # Android tablets (non-phone form factor, excluding Opera Mini)
    ]
    
    # Mobile device patterns - comprehensive list for all major browsers
    mobile_patterns = [
        # iPhone/iOS devices
        r'iPhone',
        r'iPod',
        
        # Android mobile devices (must contain "Mobile")
        r'Android.*Mobile',
        r'Android.*SM-[AEGJN]',    # Samsung Galaxy phones (A, E, G, J, N series)
        r'Android.*GT-[IPN]',      # Samsung Galaxy phones (older series)
        r'Android.*SAMSUNG-SM-',   # Samsung phones
        
        # Mobile browsers specifically
        r'Mobile.*Safari',         # Mobile Safari
        r'Mobile.*Chrome',         # Chrome Mobile
        r'Mobile.*Firefox',        # Firefox Mobile
        r'Mobile.*Opera',          # Opera Mobile
        r'Mobile.*Edge',           # Edge Mobile
        r'Mobile.*SamsungBrowser', # Samsung Internet
        
        # Other mobile indicators
        r'Mobile(?!.*Tablet)',     # Generic mobile (not tablet)
        r'Phone',                  # Generic phone indicator
        r'BlackBerry',             # BlackBerry devices
        r'BB10',                   # BlackBerry 10
        r'Windows Phone',          # Windows Phone
        r'Windows.*Mobile',        # Windows Mobile
        r'IEMobile',              # Internet Explorer Mobile
        r'Opera Mini',            # Opera Mini (always mobile)
        r'Opera Mobi',            # Opera Mobile
        r'webOS',                 # webOS devices
        r'Palm',                  # Palm devices
        r'Symbian',               # Symbian OS
        
        # Additional mobile browser patterns
        r'CriOS',                 # Chrome on iOS
        r'FxiOS',                 # Firefox on iOS
        r'OPiOS',                 # Opera on iOS
        r'EdgiOS',                # Edge on iOS
        r'YaBrowser.*Mobile',     # Yandex Mobile
        r'UCBrowser.*Mobile',     # UC Browser Mobile
        r'SamsungBrowser.*Mobile', # Samsung Internet Mobile
        
        # Feature phones and older devices
        r'MIDP',                  # Mobile Information Device Profile
        r'WML',                   # Wireless Markup Language
        r'NetFront',              # NetFront browser
        r'UP\.Browser',           # UP.Browser
        r'UP\.Link',              # UP.Link
        r'Mmp',                   # Mobile Multimedia Platform
        r'PocketPC',              # Pocket PC
        r'Smartphone',            # Generic smartphone
        r'Cellphone',             # Generic cellphone
    ]
    
    # Check for desktop first (most restrictive)
    is_desktop_explicit = bool(re.search('|'.join(desktop_patterns), user_agent, re.IGNORECASE))
    
    # If explicitly desktop, skip mobile/tablet detection
    if is_desktop_explicit:
        is_mobile = False
        is_tablet = False
    else:
        # Check for tablet
        is_tablet = bool(re.search('|'.join(tablet_patterns), user_agent, re.IGNORECASE))
        
        # Check for mobile (only if not tablet)
        if not is_tablet:
            is_mobile = bool(re.search('|'.join(mobile_patterns), user_agent, re.IGNORECASE))
        else:
            is_mobile = False
    
    # Determine device type
    if is_mobile:
        device_type = 'mobile'
    elif is_tablet:
        device_type = 'tablet'
    else:
        device_type = 'desktop'
    
    return {
        'is_mobile': is_mobile,
        'is_tablet': is_tablet,
        'is_desktop': not (is_mobile or is_tablet),
        'device_type': device_type
    }

def test_device_detection():
    """
    Test the device detection with various User-Agent strings
    """
    test_cases = [
        # Desktop browsers
        ("Chrome Desktop Windows", 
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36", 
         "desktop"),
        
        ("Firefox Desktop Windows", 
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0", 
         "desktop"),
        
        ("Safari Desktop macOS", 
         "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Version/14.1.1 Safari/537.36", 
         "desktop"),
        
        ("Edge Desktop Windows", 
         "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36 Edg/91.0.864.59", 
         "desktop"),
        
        # Mobile browsers (the ones you specifically mentioned)
        ("Chrome Mobile Android", 
         "Mozilla/5.0 (Linux; Android 11; SM-A515F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36", 
         "mobile"),
        
        ("Firefox Mobile Android", 
         "Mozilla/5.0 (Mobile; rv:68.0) Gecko/68.0 Firefox/88.0", 
         "mobile"),
        
        ("Brave Mobile Android", 
         "Mozilla/5.0 (Linux; Android 10; SM-G973F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36", 
         "mobile"),
        
        ("Safari Mobile iPhone", 
         "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1", 
         "mobile"),
        
        ("Chrome Mobile iPhone", 
         "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/91.0.4472.80 Mobile/15E148 Safari/604.1", 
         "mobile"),
        
        ("Edge Mobile Android", 
         "Mozilla/5.0 (Linux; Android 10; SM-A505FN) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36 EdgA/46.04.4.5157", 
         "mobile"),
        
        ("Samsung Internet Mobile", 
         "Mozilla/5.0 (Linux; Android 11; SAMSUNG SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/14.2 Chrome/87.0.4280.141 Mobile Safari/537.36", 
         "mobile"),
        
        ("Mi Browser (example)", 
         "Mozilla/5.0 (Linux; U; Android 10; en-us; Mi 9T Pro Build/QKQ1.190825.002) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/89.0.4389.116 Mobile Safari/537.36 XiaoMi/MiuiBrowser/13.5.40", 
         "mobile"),
        
        # Tablets
        ("iPad Safari", 
         "Mozilla/5.0 (iPad; CPU OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1", 
         "tablet"),
        
        ("Android Tablet Chrome", 
         "Mozilla/5.0 (Linux; Android 11; SM-T870) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Safari/537.36", 
         "tablet"),
        
        # Edge cases and older browsers
        ("Opera Mini", 
         "Opera/9.80 (Android; Opera Mini/36.2.2254/119.132; U; id) Presto/2.12.423 Version/12.16", 
         "mobile"),
        
        ("UC Browser Mobile", 
         "Mozilla/5.0 (Linux; U; Android 10; en-US; SM-G975F Build/QP1A.190711.020) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 UCBrowser/13.4.0.1306 Mobile Safari/537.36", 
         "mobile"),
    ]
    
    print("🧪 Testing Device Detection")
    print("=" * 60)
    
    all_passed = True
    
    for name, user_agent, expected_device_type in test_cases:
        result = get_device_info(user_agent)
        actual_device_type = result['device_type']
        
        status = "✅ PASS" if actual_device_type == expected_device_type else "❌ FAIL"
        if actual_device_type != expected_device_type:
            all_passed = False
        
        print(f"{status} {name}")
        print(f"    Expected: {expected_device_type}")
        print(f"    Actual:   {actual_device_type}")
        if actual_device_type != expected_device_type:
            print(f"    User-Agent: {user_agent}")
        print()
    
    print("=" * 60)
    if all_passed:
        print("🎉 All tests passed! Device detection is working correctly.")
    else:
        print("⚠️  Some tests failed. Please review the device detection logic.")
    
    return all_passed

if __name__ == "__main__":
    test_device_detection()
