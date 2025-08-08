// Add this to your existing base.html JavaScript section

const SPANavigator = {
    init: function() {
        this.bindNavigation();
        this.setupPopState();
    },
    
    bindNavigation: function() {
        // Intercept navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[data-spa-nav]');
            if (link && link.getAttribute('href')) {
                e.preventDefault();
                this.navigateTo(link.getAttribute('href'));
            }
        });
    },
    
    setupPopState: function() {
        // Handle browser back/forward buttons
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.url) {
                this.loadContent(e.state.url, false);
            }
        });
    },
    
    navigateTo: function(url) {
        // Update browser history
        history.pushState({ url: url }, '', url);
        this.loadContent(url, true);
    },
    
    loadContent: function(url, updateHistory = true) {
        // Show loading indicator
        this.showLoading();
        
        // Fetch new content
        fetch(url + '?spa=1', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            }
        })
        .then(response => response.text())
        .then(html => {
            // Update content area
            document.getElementById('spa-content').innerHTML = html;
            
            // Update active nav states
            this.updateActiveNav(url);
            
            // Hide loading
            this.hideLoading();
            
            // Scroll to top
            window.scrollTo(0, 0);
        })
        .catch(error => {
            console.error('Navigation error:', error);
            this.hideLoading();
        });
    },
    
    updateActiveNav: function(url) {
        document.querySelectorAll('.nav-link').forEach(link => {
            link.classList.remove('active');
            if (link.getAttribute('href') === url) {
                link.classList.add('active');
            }
        });
    },
    
    showLoading: function() {
        document.querySelector('.loading-indicator').style.transform = 'scaleX(1)';
    },
    
    hideLoading: function() {
        document.querySelector('.loading-indicator').style.transform = 'scaleX(0)';
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    SPANavigator.init();
});
