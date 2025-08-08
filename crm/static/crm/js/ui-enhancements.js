/**
 * UI Enhancements for BetulaIT Helpdesk
 * Adds interactive features to Bootstrap 5 components
 */

// Initialization function that can be called multiple times
function initializeUIComponents() {
    // Initialize all tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]:not(.tooltip-initialized)'));
    tooltipTriggerList.map(function(tooltipTriggerEl) {
        tooltipTriggerEl.classList.add('tooltip-initialized');
        return new bootstrap.Tooltip(tooltipTriggerEl, {
            animation: true,
            delay: { show: 100, hide: 100 }
        });
    });

    // Initialize all popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]:not(.popover-initialized)'));
    popoverTriggerList.map(function(popoverTriggerEl) {
        popoverTriggerEl.classList.add('popover-initialized');
        return new bootstrap.Popover(popoverTriggerEl, {
            animation: true,
            trigger: 'hover focus'
        });
    });

    // Button ripple effect
    const rippleButtons = document.querySelectorAll('.btn-ripple:not(.ripple-initialized)');
    rippleButtons.forEach(button => {
        button.classList.add('ripple-initialized');
        button.addEventListener('click', function(e) {
            const rect = button.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const ripple = document.createElement('span');
            ripple.className = 'ripple';
            ripple.style.left = `${x}px`;
            ripple.style.top = `${y}px`;

            button.appendChild(ripple);

            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });

    // Enhanced dropdown animation
    const dropdownToggleList = document.querySelectorAll('.dropdown-toggle:not(.dropdown-initialized)');
    dropdownToggleList.forEach(dropdown => {
        dropdown.classList.add('dropdown-initialized');
        dropdown.addEventListener('click', function() {
            setTimeout(() => {
                const dropdownMenu = dropdown.nextElementSibling;
                if (dropdownMenu && dropdownMenu.classList.contains('show')) {
                    dropdownMenu.classList.add('animated-dropdown');
                }
            }, 10);
        });
    });

    // Auto-collapsing sidebar on mobile
    const sidebarToggles = document.querySelectorAll('.sidebar-toggle:not(.sidebar-initialized)');
    const sidebar = document.querySelector('.sidebar');
    if (sidebar && window.innerWidth < 992) {
        sidebarToggles.forEach(toggle => {
            toggle.classList.add('sidebar-initialized');
            toggle.addEventListener('click', function() {
                sidebar.classList.toggle('expanded');
            });
        });
    }

    // Interactive cards
    const interactiveCards = document.querySelectorAll('.card-interactive:not(.card-initialized)');
    interactiveCards.forEach(card => {
        card.classList.add('card-initialized');
        card.addEventListener('mouseenter', function() {
            this.classList.add('card-hover-effect');
        });
        
        card.addEventListener('mouseleave', function() {
            this.classList.remove('card-hover-effect');
        });
    });

    // Form validation on the fly
    const forms = document.querySelectorAll('.needs-live-validation:not(.validation-initialized)');
    forms.forEach(form => {
        form.classList.add('validation-initialized');
        const inputs = form.querySelectorAll('input, select, textarea');
        inputs.forEach(input => {
            input.addEventListener('blur', function() {
                if (this.checkValidity()) {
                    this.classList.remove('is-invalid');
                    this.classList.add('is-valid');
                } else {
                    this.classList.remove('is-valid');
                    this.classList.add('is-invalid');
                }
            });
        });
    });

    // Counter animation for statistics
    const animateCounter = (counterElement, endValue, duration = 1500) => {
        const startValue = 0;
        const startTime = performance.now();
        const updateCounter = (timestamp) => {
            const elapsedTime = timestamp - startTime;
            if (elapsedTime < duration) {
                const progress = elapsedTime / duration;
                const currentValue = Math.round(progress * (endValue - startValue) + startValue);
                counterElement.textContent = currentValue;
                requestAnimationFrame(updateCounter);
            } else {
                counterElement.textContent = endValue;
            }
        };
        requestAnimationFrame(updateCounter);
    };

    const counterElements = document.querySelectorAll('.animate-counter:not(.counter-initialized)');
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const counterObserver = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const target = entry.target;
                const endValue = parseInt(target.getAttribute('data-count'), 10);
                animateCounter(target, endValue);
                counterObserver.unobserve(target);
            }
        });
    }, observerOptions);

    counterElements.forEach(element => {
        element.classList.add('counter-initialized');
        counterObserver.observe(element);
    });

    // Smooth scroll for anchor links
    document.querySelectorAll('a[href^="#"]:not(.anchor-initialized)').forEach(anchor => {
        anchor.classList.add('anchor-initialized');
        anchor.addEventListener('click', function(e) {
            const targetId = this.getAttribute('href');
            if (targetId === '#') return;
            
            const targetElement = document.querySelector(targetId);
            if (targetElement) {
                e.preventDefault();
                window.scrollTo({
                    top: targetElement.offsetTop - 70,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Toast initialization with optional auto-hiding
    const toastElements = document.querySelectorAll('.toast:not(.toast-initialized)');
    toastElements.forEach(toastEl => {
        toastEl.classList.add('toast-initialized');
        const toast = new bootstrap.Toast(toastEl, {
            autohide: toastEl.getAttribute('data-autohide') !== 'false',
            delay: parseInt(toastEl.getAttribute('data-delay') || 5000, 10)
        });
        
        if (toastEl.classList.contains('show-on-load')) {
            toast.show();
        }
    });

    // Collapsible card bodies with animation
    const collapsibleCardHeaders = document.querySelectorAll('.card-header-collapsible:not(.collapsible-initialized)');
    collapsibleCardHeaders.forEach(header => {
        header.classList.add('collapsible-initialized');
        header.addEventListener('click', function() {
            const cardBody = this.parentElement.querySelector('.card-body');
            const icon = this.querySelector('.collapse-icon');
            
            if (cardBody) {
                cardBody.classList.toggle('d-none');
                if (icon) {
                    icon.classList.toggle('fa-chevron-down');
                    icon.classList.toggle('fa-chevron-up');
                }
            }
        });
    });
}

// Initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', initializeUIComponents);

// Re-initialize on SPA content loaded
window.addEventListener('spaContentLoaded', initializeUIComponents);

// Add global utilities
window.BetulaUI = {
    // Show toast message programmatically
    showToast: function(message, type = 'info', autohide = true, delay = 5000) {
        const toastContainer = document.querySelector('.toast-container');
        if (!toastContainer) {
            console.error('Toast container not found');
            return;
        }
        
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type} border-0`;
        toast.setAttribute('role', 'alert');
        toast.setAttribute('aria-live', 'assertive');
        toast.setAttribute('aria-atomic', 'true');
        
        const toastContent = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>
            </div>
        `;
        
        toast.innerHTML = toastContent;
        toastContainer.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast, {
            autohide: autohide,
            delay: delay
        });
        
        bsToast.show();
        
        if (autohide) {
            setTimeout(() => {
                toast.remove();
            }, delay + 500);
        }
    },
    
    // Add loading spinner to button
    buttonLoading: function(button, isLoading = true) {
        if (!button) return;
        
        const originalContent = button.getAttribute('data-original-content') || button.innerHTML;
        
        if (isLoading) {
            button.setAttribute('data-original-content', originalContent);
            button.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Ładowanie...';
            button.disabled = true;
        } else {
            button.innerHTML = originalContent;
            button.disabled = false;
        }
    },
    
    // Re-initialize all components (can be called manually)
    reinitialize: initializeUIComponents
};