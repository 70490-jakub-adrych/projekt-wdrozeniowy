/**
 * Cookie Consent Handler
 * Manages the cookie consent banner and user preferences
 */
document.addEventListener('DOMContentLoaded', function() {
    const COOKIE_NAME = 'helpdesk_cookie_consent';
    const COOKIE_DURATION = 180; // days
    
    // Debug logging - check if script is loaded
    console.log('Cookie consent script loaded');
    
    /**
     * Check if user has already provided cookie consent
     */
    function hasConsent() {
        const hasExistingConsent = document.cookie.split(';').some(function(cookie) {
            return cookie.trim().startsWith(COOKIE_NAME + '=true');
        });
        console.log('Has existing consent:', hasExistingConsent);
        return hasExistingConsent;
    }
    
    /**
     * Set the consent cookie
     */
    function setConsentCookie() {
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + COOKIE_DURATION);
        document.cookie = COOKIE_NAME + '=true; expires=' + expiryDate.toUTCString() + '; path=/; SameSite=Lax';
        console.log('Consent cookie set, expires:', expiryDate.toUTCString());
    }
    
    /**
     * Hide the cookie consent banner
     */
    function hideBanner() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner) {
            banner.style.display = 'none';
            // Optional: add animation class for smooth exit
            banner.classList.add('cookie-banner-hide');
            setTimeout(function() {
                banner.remove();
            }, 500); // Remove after animation completes
        }
    }
    
    /**
     * Show the cookie banner if consent isn't given yet
     */
    function showBannerIfNeeded() {
        if (!hasConsent()) {
            const banner = document.getElementById('cookie-consent-banner');
            if (banner) {
                console.log('Showing cookie consent banner');
                banner.style.display = 'block';
                banner.classList.add('cookie-banner-show');
            } else {
                console.error('Cookie banner element not found in the DOM');
            }
        } else {
            console.log('Consent already given, not showing banner');
        }
    }
    
    /**
     * Handle accept button click
     */
    function handleAccept() {
        console.log('Accept button clicked');
        setConsentCookie();
        hideBanner();
    }
    
    // Set up event listener for accept button
    const acceptButton = document.getElementById('cookie-consent-accept');
    if (acceptButton) {
        console.log('Accept button found, adding event listener');
        acceptButton.addEventListener('click', handleAccept);
    } else {
        console.error('Cookie consent accept button not found');
    }
    
    // Check and show banner if needed
    showBannerIfNeeded();
    
    // Failsafe - If the banner should be visible but isn't properly displayed by CSS
    setTimeout(function() {
        const banner = document.getElementById('cookie-consent-banner');
        if (banner && !hasConsent() && window.getComputedStyle(banner).display === 'none') {
            console.log('Failsafe: Force showing the cookie banner');
            banner.style.display = 'block';
        }
    }, 1000);
});
