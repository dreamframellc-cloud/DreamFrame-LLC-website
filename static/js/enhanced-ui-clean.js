/**
 * Enhanced UI Components and Interactions
 * Clean version without syntax errors
 */

class EnhancedUI {
    constructor() {
        this.init();
    }

    init() {
        this.setupSmoothScrolling();
        this.setupLoadingStates();
        this.setupScrollAnimations();
        this.setupTooltips();
        this.setupMobileNavigation();
        this.setupKeyboardShortcuts();
        this.setupLanguageSelector();
    }

    setupSmoothScrolling() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', (e) => {
                e.preventDefault();
                const target = document.querySelector(anchor.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }

    setupLoadingStates() {
        document.querySelectorAll('button[type="submit"], .btn-primary, .btn-secondary').forEach(btn => {
            btn.addEventListener('click', (e) => {
                // Don't interfere with Pay Now buttons that have their own handling
                if (btn.classList.contains('pay-now-btn')) {
                    return; // Let the form submit normally
                }
                
                if (btn.type === 'submit' || btn.classList.contains('loading-enabled')) {
                    this.showButtonLoading(btn);
                }
            });
        });
    }

    showButtonLoading(button) {
        const originalContent = button.cloneNode(true).childNodes;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        button.disabled = true;
        
        setTimeout(() => {
            button.innerHTML = '';
            originalContent.forEach(node => button.appendChild(node.cloneNode(true)));
            button.disabled = false;
        }, 3000);
    }

    setupScrollAnimations() {
        const observerOptions = {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        };

        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, observerOptions);

        document.querySelectorAll('.video-card, .pricing-card, .feature-card, .hero-content').forEach(el => {
            observer.observe(el);
        });
    }

    setupTooltips() {
        document.querySelectorAll('[data-tooltip]').forEach(element => {
            element.addEventListener('mouseenter', (e) => {
                this.showTooltip(e.target, e.target.dataset.tooltip);
            });
            
            element.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'custom-tooltip';
        tooltip.textContent = text;
        document.body.appendChild(tooltip);

        const rect = element.getBoundingClientRect();
        tooltip.style.left = rect.left + (rect.width / 2) - (tooltip.offsetWidth / 2) + 'px';
        tooltip.style.top = rect.top - tooltip.offsetHeight - 10 + 'px';
        
        setTimeout(() => tooltip.classList.add('show'), 10);
    }

    hideTooltip() {
        const tooltip = document.querySelector('.custom-tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    setupMobileNavigation() {
        if (!document.querySelector('.mobile-menu-toggle')) {
            this.createMobileMenu();
        }
        this.setupSwipeGestures();
    }

    createMobileMenu() {
        const header = document.querySelector('.main-header');
        if (header) {
            const menuToggle = document.createElement('button');
            menuToggle.className = 'mobile-menu-toggle';
            menuToggle.innerHTML = '<i class="fas fa-bars"></i>';
            menuToggle.setAttribute('aria-label', 'Toggle menu');
            
            const nav = document.createElement('nav');
            nav.className = 'mobile-nav';
            nav.innerHTML = `
                <a href="/" class="nav-link"><i class="fas fa-home"></i> Home</a>
                <a href="/gallery" class="nav-link"><i class="fas fa-play"></i> Gallery</a>
                <a href="/pricing" class="nav-link"><i class="fas fa-dollar-sign"></i> Pricing</a>
                <a href="/upload" class="nav-link"><i class="fas fa-upload"></i> Upload</a>
                <a href="/invite" class="nav-link"><i class="fas fa-user-plus"></i> Invite</a>
            `;
            
            header.appendChild(menuToggle);
            header.appendChild(nav);
            
            menuToggle.addEventListener('click', () => {
                nav.classList.toggle('active');
                menuToggle.classList.toggle('active');
            });
        }
    }

    setupSwipeGestures() {
        let startX, startY, distX, distY;
        
        document.addEventListener('touchstart', (e) => {
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
        });
        
        document.addEventListener('touchend', (e) => {
            if (!startX || !startY) return;
            
            distX = e.changedTouches[0].clientX - startX;
            distY = e.changedTouches[0].clientY - startY;
            
            if (distX > 100 && Math.abs(distY) < 100) {
                const modal = document.querySelector('.video-modal.show');
                if (modal && window.videoGallery) {
                    window.videoGallery.closeModal();
                }
            }
            
            startX = null;
            startY = null;
        });
    }

    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('#tagSearch');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            if (e.key === 'Escape') {
                const modal = document.querySelector('.video-modal.show');
                if (modal && window.videoGallery) {
                    window.videoGallery.closeModal();
                }
            }
        });
    }

    showNotification(message, type = 'info', duration = 3000) {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        
        const icon = document.createElement('i');
        icon.className = `fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info'}`;
        
        const messageSpan = document.createElement('span');
        messageSpan.textContent = message;
        
        const closeBtn = document.createElement('button');
        closeBtn.className = 'notification-close';
        const closeIcon = document.createElement('i');
        closeIcon.className = 'fas fa-times';
        closeBtn.appendChild(closeIcon);
        
        notification.appendChild(icon);
        notification.appendChild(messageSpan);
        notification.appendChild(closeBtn);
        
        document.body.appendChild(notification);
        
        setTimeout(() => notification.classList.add('show'), 10);
        
        closeBtn.addEventListener('click', () => {
            this.hideNotification(notification);
        });
        
        setTimeout(() => {
            this.hideNotification(notification);
        }, duration);
    }

    hideNotification(notification) {
        notification.classList.remove('show');
        setTimeout(() => notification.remove(), 300);
    }

    setupLanguageSelector() {
        const langButton = document.querySelector('.df-lang-btn');
        const langMenu = document.querySelector('.df-lang-menu');
        const langList = document.querySelector('.df-lang-list');
        
        if (!langButton || !langMenu || !langList) {
            return; // Language selector not found
        }

        // Handle button click to toggle dropdown
        langButton.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            
            // Toggle the dropdown
            langMenu.classList.toggle('is-open');
            
            // Update aria attributes
            const isOpen = langMenu.classList.contains('is-open');
            langButton.setAttribute('aria-expanded', isOpen);
        });

        // Close dropdown when clicking outside
        document.addEventListener('click', (e) => {
            if (!langMenu.contains(e.target)) {
                langMenu.classList.remove('is-open');
                langButton.setAttribute('aria-expanded', 'false');
            }
        });

        // Close dropdown on escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && langMenu.classList.contains('is-open')) {
                langMenu.classList.remove('is-open');
                langButton.setAttribute('aria-expanded', 'false');
                langButton.focus();
            }
        });

        // Close dropdown after language selection
        langList.addEventListener('click', () => {
            langMenu.classList.remove('is-open');
            langButton.setAttribute('aria-expanded', 'false');
        });
    }
}

// Video interaction functions
function toggleFavorite(videoId) {
    const favoriteBtn = document.querySelector(`[data-video-id="${videoId}"] .favorite-btn`);
    if (!favoriteBtn) return;
    
    const icon = favoriteBtn.querySelector('i');
    const isFavorited = icon.classList.contains('fas');
    
    if (isFavorited) {
        icon.classList.remove('fas');
        icon.classList.add('far');
        favoriteBtn.style.color = 'white';
        if (window.enhancedUI) {
            window.enhancedUI.showNotification('Removed from favorites', 'info');
        }
    } else {
        icon.classList.remove('far');
        icon.classList.add('fas');
        favoriteBtn.style.color = '#EF4444';
        if (window.enhancedUI) {
            window.enhancedUI.showNotification('Added to favorites', 'success');
        }
    }
    
    const favorites = JSON.parse(localStorage.getItem('videoFavorites') || '[]');
    if (isFavorited) {
        const index = favorites.indexOf(videoId);
        if (index > -1) favorites.splice(index, 1);
    } else {
        favorites.push(videoId);
    }
    localStorage.setItem('videoFavorites', JSON.stringify(favorites));
}

function shareVideo(videoId) {
    // Legacy share function - new VideoGallery handles sharing internally
    console.log('Legacy shareVideo called, redirecting to new system');
}

function trackVideoView(videoId) {
    const viewElement = document.getElementById(`views-${videoId}`);
    if (viewElement) {
        let currentViews = parseInt(viewElement.textContent) || 0;
        viewElement.textContent = currentViews + 1;
        
        const views = JSON.parse(localStorage.getItem('videoViews') || '{}');
        views[videoId] = (views[videoId] || 0) + 1;
        localStorage.setItem('videoViews', JSON.stringify(views));
    }
}

function loadFavorites() {
    const favorites = JSON.parse(localStorage.getItem('videoFavorites') || '[]');
    favorites.forEach(videoId => {
        const favoriteBtn = document.querySelector(`[data-video-id="${videoId}"] .favorite-btn`);
        if (favoriteBtn) {
            const icon = favoriteBtn.querySelector('i');
            icon.classList.remove('far');
            icon.classList.add('fas');
            favoriteBtn.style.color = '#EF4444';
        }
    });
}

function loadViewCounts() {
    const views = JSON.parse(localStorage.getItem('videoViews') || '{}');
    Object.entries(views).forEach(([videoId, count]) => {
        const viewElement = document.getElementById(`views-${videoId}`);
        if (viewElement) {
            viewElement.textContent = count;
        }
    });
}

// Initialize enhanced UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedUI = new EnhancedUI();
    
    // Setup language selector
    if (window.enhancedUI && window.enhancedUI.setupLanguageSelector) {
        window.enhancedUI.setupLanguageSelector();
        console.log('Language selector setup complete');
    }
    
    // Load saved data
    loadFavorites();
    loadViewCounts();
    
    // Integrate with existing video gallery if it exists
    // VideoGallery integration removed - new system handles tracking internally
});