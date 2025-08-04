"""
Mobile device detection template tags
"""
from django import template
import re

register = template.Library()

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
    
    # Mobile device patterns
    mobile_patterns = [
        r'Mobile',
        r'Android',
        r'iPhone',
        r'iPad',
        r'iPod',
        r'BlackBerry',
        r'Windows Phone',
        r'Opera Mini',
        r'IEMobile',
        r'Mobile Safari',
    ]
    
    mobile_regex = '|'.join(mobile_patterns)
    return bool(re.search(mobile_regex, user_agent, re.IGNORECASE))

@register.simple_tag(takes_context=True)
def device_type(context):
    """
    Return device type: 'mobile', 'tablet', or 'desktop'
    """
    request = context.get('request')
    if not request:
        return 'desktop'
    
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Tablet patterns (checked first as they might also match mobile)
    if re.search(r'iPad|Tablet|Android(?!.*Mobile)', user_agent, re.IGNORECASE):
        return 'tablet'
    
    # Mobile patterns
    mobile_patterns = [
        r'Mobile',
        r'Android.*Mobile',
        r'iPhone',
        r'iPod',
        r'BlackBerry',
        r'Windows Phone',
        r'Opera Mini',
        r'IEMobile',
    ]
    
    mobile_regex = '|'.join(mobile_patterns)
    if re.search(mobile_regex, user_agent, re.IGNORECASE):
        return 'mobile'
    
    return 'desktop'

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
