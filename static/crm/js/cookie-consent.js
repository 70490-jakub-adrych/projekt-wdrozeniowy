/**
 * Cookie Consent Handler
 * Manages the cookie consent banner and user preferences
 */
document.addEventListener('DOMContentLoaded', function() {
    const COOKIE_NAME = 'helpdesk_cookie_consent';
    const COOKIE_DURATION = 180; // days
    
    /**
     * Check if user has already provided cookie consent
     */
    function hasConsent() {
        return document.cookie.split(';').some(function(cookie) {
            return cookie.trim().startsWith(COOKIE_NAME + '=true');
        });
    }
    
    /**
     * Set the consent cookie
     */
    function setConsentCookie() {
        const expiryDate = new Date();
        expiryDate.setDate(expiryDate.getDate() + COOKIE_DURATION);
        document.cookie = COOKIE_NAME + '=true; expires=' + expiryDate.toUTCString() + '; path=/; SameSite=Lax';
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
                banner.style.display = 'block';
                banner.classList.add('cookie-banner-show');
            }
        }
    }
    
    /**
     * Handle accept button click
     */
    function handleAccept() {
        setConsentCookie();
        hideBanner();
    }
    
    // Set up event listener for accept button
    const acceptButton = document.getElementById('cookie-consent-accept');
    if (acceptButton) {
        acceptButton.addEventListener('click', handleAccept);
    }
    
    // Check and show banner if needed
    showBannerIfNeeded();
});
