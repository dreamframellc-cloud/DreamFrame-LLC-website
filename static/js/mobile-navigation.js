// Mobile Navigation Toggle Functionality
document.addEventListener('DOMContentLoaded', function() {
    const mobileNavToggle = document.getElementById('mobileNavToggle');
    const navTabs = document.getElementById('navTabs');
    
    if (mobileNavToggle && navTabs) {
        // Toggle navigation menu
        mobileNavToggle.addEventListener('click', function() {
            navTabs.classList.toggle('mobile-open');
            
            // Update button icon and text
            const icon = this.querySelector('i');
            const text = this.querySelector('.toggle-text');
            
            if (navTabs.classList.contains('mobile-open')) {
                icon.className = 'fas fa-times';
                text.textContent = 'Close Navigation';
                this.setAttribute('aria-expanded', 'true');
            } else {
                icon.className = 'fas fa-bars';
                text.textContent = 'Service Navigation';
                this.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Close menu when clicking on a nav link
        const navLinks = navTabs.querySelectorAll('.nav-tab');
        navLinks.forEach(link => {
            link.addEventListener('click', function() {
                navTabs.classList.remove('mobile-open');
                const icon = mobileNavToggle.querySelector('i');
                const text = mobileNavToggle.querySelector('.toggle-text');
                icon.className = 'fas fa-bars';
                text.textContent = 'Service Navigation';
                mobileNavToggle.setAttribute('aria-expanded', 'false');
            });
        });
        
        // Close menu when clicking outside (for mobile)
        document.addEventListener('click', function(e) {
            if (!mobileNavToggle.contains(e.target) && !navTabs.contains(e.target)) {
                navTabs.classList.remove('mobile-open');
                const icon = mobileNavToggle.querySelector('i');
                const text = mobileNavToggle.querySelector('.toggle-text');
                icon.className = 'fas fa-bars';
                text.textContent = 'Service Navigation';
                mobileNavToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Close menu on escape key
        document.addEventListener('keydown', function(e) {
            if (e.key === 'Escape' && navTabs.classList.contains('mobile-open')) {
                navTabs.classList.remove('mobile-open');
                const icon = mobileNavToggle.querySelector('i');
                const text = mobileNavToggle.querySelector('.toggle-text');
                icon.className = 'fas fa-bars';
                text.textContent = 'Service Navigation';
                mobileNavToggle.setAttribute('aria-expanded', 'false');
            }
        });
        
        // Set initial ARIA attributes
        mobileNavToggle.setAttribute('aria-expanded', 'false');
        mobileNavToggle.setAttribute('aria-controls', 'navTabs');
        navTabs.setAttribute('role', 'menu');
    }
});