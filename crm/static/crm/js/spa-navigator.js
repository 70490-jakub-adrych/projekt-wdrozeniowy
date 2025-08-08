// Enhanced SPA Navigator with Bootstrap 5 support

const SPANavigator = {
    init: function() {
        this.bindNavigation();
        this.setupPopState();
        console.log('🚀 SPA Navigator initialized with Bootstrap support');
    },
    
    bindNavigation: function() {
        // Intercept navigation clicks
        document.addEventListener('click', (e) => {
            const link = e.target.closest('a[data-spa-nav]');
            if (link && link.getAttribute('href')) {
                e.preventDefault();
                console.log(`🔗 SPA Navigation to: ${link.getAttribute('href')}`);
                this.navigateTo(link.getAttribute('href'));
            }
        });
    },
    
    setupPopState: function() {
        // Handle browser back/forward buttons
        window.addEventListener('popstate', (e) => {
            if (e.state && e.state.url) {
                console.log(`⬅️ Browser back/forward to: ${e.state.url}`);
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
        
        // Dispose existing Bootstrap components before content replacement
        this.disposeBootstrapComponents();
        
        // Fetch new content
        fetch(url + '?spa=1', {
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
                'Accept': 'text/html'
            }
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            return response.text();
        })
        .then(html => {
            // Update content area
            const contentElement = document.getElementById('spa-content');
            if (contentElement) {
                contentElement.innerHTML = html;
                console.log(`✅ Content updated for: ${url}`);
                
                // Execute any inline scripts in the new content
                this.executeInlineScripts(contentElement);
                
                // Initialize Bootstrap components in new content
                this.initializeBootstrapComponents(contentElement);
                
                // Update active nav states
                this.updateActiveNav(url);
                
                // Hide loading
                this.hideLoading();
                
                // Scroll to top
                window.scrollTo(0, 0);
                
                console.log(`🎯 SPA Navigation completed successfully`);
            } else {
                throw new Error('SPA content container not found');
            }
        })
        .catch(error => {
            console.error('❌ SPA Navigation error:', error);
            this.hideLoading();
            // Fallback to regular navigation
            window.location.href = url;
        });
    },
    
    disposeBootstrapComponents: function() {
        const contentArea = document.getElementById('spa-content');
        if (!contentArea) return;
        
        console.log('🧹 Disposing existing Bootstrap components...');
        let disposedCount = 0;
        
        // Dispose tooltips
        contentArea.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            const tooltip = bootstrap.Tooltip.getInstance(el);
            if (tooltip) {
                tooltip.dispose();
                disposedCount++;
            }
        });
        
        // Dispose popovers
        contentArea.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
            const popover = bootstrap.Popover.getInstance(el);
            if (popover) {
                popover.dispose();
                disposedCount++;
            }
        });
        
        // Dispose dropdowns
        contentArea.querySelectorAll('.dropdown-toggle, [data-bs-toggle="dropdown"]').forEach(el => {
            const dropdown = bootstrap.Dropdown.getInstance(el);
            if (dropdown) {
                dropdown.dispose();
                disposedCount++;
            }
        });
        
        // Dispose modals
        contentArea.querySelectorAll('.modal').forEach(el => {
            const modal = bootstrap.Modal.getInstance(el);
            if (modal) {
                modal.dispose();
                disposedCount++;
            }
        });
        
        // Dispose collapses
        contentArea.querySelectorAll('[data-bs-toggle="collapse"]').forEach(el => {
            const collapse = bootstrap.Collapse.getInstance(el);
            if (collapse) {
                collapse.dispose();
                disposedCount++;
            }
        });
        
        // Dispose toasts
        contentArea.querySelectorAll('.toast').forEach(el => {
            const toast = bootstrap.Toast.getInstance(el);
            if (toast) {
                toast.dispose();
                disposedCount++;
            }
        });
        
        console.log(`🗑️ Disposed ${disposedCount} Bootstrap components`);
    },
    
    initializeBootstrapComponents: function(container) {
        if (!container) return;
        
        console.log('🚀 Initializing Bootstrap components in new content...');
        let initializedCount = 0;
        
        // Initialize tooltips
        container.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => {
            if (!bootstrap.Tooltip.getInstance(el)) {
                new bootstrap.Tooltip(el);
                initializedCount++;
            }
        });
        
        // Initialize popovers
        container.querySelectorAll('[data-bs-toggle="popover"]').forEach(el => {
            if (!bootstrap.Popover.getInstance(el)) {
                new bootstrap.Popover(el);
                initializedCount++;
            }
        });
        
        // Initialize dropdowns
        container.querySelectorAll('.dropdown-toggle, [data-bs-toggle="dropdown"]').forEach(el => {
            if (!bootstrap.Dropdown.getInstance(el)) {
                new bootstrap.Dropdown(el);
                initializedCount++;
            }
        });
        
        // Initialize modals
        container.querySelectorAll('.modal').forEach(el => {
            if (!bootstrap.Modal.getInstance(el)) {
                new bootstrap.Modal(el);
                initializedCount++;
            }
        });
        
        // Initialize collapses
        container.querySelectorAll('[data-bs-toggle="collapse"]').forEach(el => {
            if (!bootstrap.Collapse.getInstance(el)) {
                new bootstrap.Collapse(el);
                initializedCount++;
            }
        });
        
        // Initialize toasts
        container.querySelectorAll('.toast').forEach(el => {
            if (!bootstrap.Toast.getInstance(el)) {
                new bootstrap.Toast(el);
                initializedCount++;
            }
        });
        
        console.log(`✅ Initialized ${initializedCount} Bootstrap components`);
    },
    
    executeInlineScripts: function(container) {
        const scripts = container.querySelectorAll('script');
        console.log(`📜 Executing ${scripts.length} inline scripts...`);
        
        scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            if (oldScript.src) {
                newScript.src = oldScript.src;
            } else {
                newScript.textContent = oldScript.textContent;
            }
            
            // Append to head temporarily to execute, then remove
            document.head.appendChild(newScript);
            document.head.removeChild(newScript);
            oldScript.remove();
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
        const indicator = document.querySelector('.loading-indicator');
        if (indicator) {
            indicator.style.transform = 'scaleX(1)';
            indicator.style.opacity = '1';
        }
    },
    
    hideLoading: function() {
        const indicator = document.querySelector('.loading-indicator');
        if (indicator) {
            indicator.style.transform = 'scaleX(0)';
            indicator.style.opacity = '0';
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', function() {
    SPANavigator.init();
});

// Make available globally for debugging
window.SPANavigator = SPANavigator;