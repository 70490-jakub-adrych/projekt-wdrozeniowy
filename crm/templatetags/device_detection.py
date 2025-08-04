"""
Mobile device detection template tags with comprehensive detection patterns
"""
from django import template
import re

register = template.Library()

def _get_device_info(user_agent):
    """
    Core device detection logic - shared between template tags
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

@register.simple_tag(takes_context=True)
def is_mobile_device(context):
    """
    Detect if the user is on a mobile device based on User-Agent
    Returns True if mobile device, False otherwise
    """
    request = context.get('request')
    if not request:
        return False
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_info = _get_device_info(user_agent)
    return device_info['is_mobile']

@register.simple_tag(takes_context=True)
def device_type(context):
    """
    Return device type: 'mobile', 'tablet', or 'desktop'
    """
    request = context.get('request')
    if not request:
        return 'desktop'
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    device_info = _get_device_info(user_agent)
    return device_info['device_type']

@register.simple_tag(takes_context=True)
def screen_size_class(context):
    """
    Return Bootstrap screen size class based on device type
    """
    device = device_type(context)
    if device == 'mobile':
        return 'mobile-view'
    elif device == 'tablet':
        return 'tablet-view'
    else:
        return 'desktop-view'
