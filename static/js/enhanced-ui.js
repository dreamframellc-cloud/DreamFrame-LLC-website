/**
 * Enhanced UI Components and Interactions
 * Adds modern UX features like smooth scrolling, loading states, and animations
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
        this.setupProgressBars();
        this.setupMobileNavigation();
        this.setupKeyboardShortcuts();
    }

    // Smooth scrolling for anchor links
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

    // Loading states for buttons and forms
    setupLoadingStates() {
        document.querySelectorAll('button[type="submit"], .btn-primary, .btn-secondary').forEach(btn => {
            btn.addEventListener('click', (e) => {
                if (btn.type === 'submit' || btn.classList.contains('loading-enabled')) {
                    this.showButtonLoading(btn);
                }
            });
        });
    }

    showButtonLoading(button) {
        const originalText = button.textContent;
        button.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Loading...';
        button.disabled = true;
        
        // Reset after 3 seconds if no redirect occurs
        setTimeout(() => {
            button.textContent = originalText;
            button.disabled = false;
        }, 3000);
    }

    // Scroll animations for elements
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

        // Observe elements that should animate in
        document.querySelectorAll('.video-card, .pricing-card, .feature-card, .hero-content').forEach(el => {
            observer.observe(el);
        });
    }

    // Enhanced tooltips
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

    // Progress bars for video loading
    setupProgressBars() {
        document.querySelectorAll('video').forEach(video => {
            video.addEventListener('loadstart', () => {
                this.showVideoProgress(video);
            });
            
            video.addEventListener('progress', (e) => {
                this.updateVideoProgress(video, e);
            });
            
            video.addEventListener('canplaythrough', () => {
                this.hideVideoProgress(video);
            });
        });
    }

    showVideoProgress(video) {
        const progressBar = document.createElement('div');
        progressBar.className = 'video-progress-bar';
        progressBar.innerHTML = '<div class="progress-fill"></div>';
        video.parentNode.appendChild(progressBar);
    }

    updateVideoProgress(video, event) {
        const progressBar = video.parentNode.querySelector('.video-progress-bar');
        if (progressBar && event.lengthComputable) {
            const percentLoaded = (event.loaded / event.total) * 100;
            const progressFill = progressBar.querySelector('.progress-fill');
            progressFill.style.width = percentLoaded + '%';
        }
    }

    hideVideoProgress(video) {
        const progressBar = video.parentNode.querySelector('.video-progress-bar');
        if (progressBar) {
            progressBar.remove();
        }
    }

    // Mobile navigation improvements
    setupMobileNavigation() {
        // Create mobile menu toggle if it doesn't exist
        if (!document.querySelector('.mobile-menu-toggle')) {
            this.createMobileMenu();
        }

        // Handle swipe gestures
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
            
            // Swipe right to close modal
            if (distX > 100 && Math.abs(distY) < 100) {
                const modal = document.querySelector('.video-modal.show');
                if (modal) {
                    window.videoGallery?.closeModal();
                }
            }
            
            startX = null;
            startY = null;
        });
    }

    // Keyboard shortcuts
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Ctrl/Cmd + K for search
            if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
                e.preventDefault();
                const searchInput = document.querySelector('#tagSearch');
                if (searchInput) {
                    searchInput.focus();
                }
            }
            
            // Escape to close modal
            if (e.key === 'Escape') {
                const modal = document.querySelector('.video-modal.show');
                if (modal) {
                    window.videoGallery?.closeModal();
                }
            }
            
            // Arrow keys for video navigation
            if (e.key === 'ArrowLeft' || e.key === 'ArrowRight') {
                const modal = document.querySelector('.video-modal.show');
                if (modal) {
                    // Add previous/next video functionality
                    this.navigateVideos(e.key === 'ArrowRight' ? 'next' : 'prev');
                }
            }
        });
    }

    navigateVideos(direction) {
        // This would integrate with the existing video gallery
        console.log(`Navigate ${direction} video`);
    }
}

// Video interaction functions
function toggleFavorite(videoId) {
    const favoriteBtn = document.querySelector(`[data-video-id="${videoId}"] .favorite-btn`);
    const icon = favoriteBtn.querySelector('i');
    
    // Toggle favorite state
    const isFavorited = icon.classList.contains('fas');
    if (isFavorited) {
        icon.classList.remove('fas');
        icon.classList.add('far');
        favoriteBtn.style.color = 'white';
        window.enhancedUI.showNotification('Removed from favorites', 'info');
    } else {
        icon.classList.remove('far');
        icon.classList.add('fas');
        favoriteBtn.style.color = '#EF4444';
        window.enhancedUI.showNotification('Added to favorites', 'success');
    }
    
    // Store in localStorage
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
    const videoCard = document.querySelector(`[data-video-id="${videoId}"]`);
    const videoTitle = videoCard.querySelector('.video-title').textContent;
    const videoUrl = `${window.location.origin}/video/${videoId}`;
    
    if (navigator.share) {
        navigator.share({
            title: `DreamFrame - ${videoTitle}`,
            text: `Check out this video: ${videoTitle}`,
            url: videoUrl
        });
    } else {
        // Fallback to clipboard
        navigator.clipboard.writeText(videoUrl).then(() => {
            window.enhancedUI.showNotification('Link copied to clipboard', 'success');
        }).catch(() => {
            // Manual copy fallback
            const textArea = document.createElement('textarea');
            textArea.value = videoUrl;
            document.body.appendChild(textArea);
            textArea.select();
            document.execCommand('copy');
            document.body.removeChild(textArea);
            window.enhancedUI.showNotification('Link copied to clipboard', 'success');
        });
    }
}

function downloadVideo(videoId) {
    const videoCard = document.querySelector(`[data-video-id="${videoId}"]`);
    const videoTitle = videoCard.querySelector('.video-title').textContent;
    
    // Create download link
    const link = document.createElement('a');
    link.href = `/video/${videoId}`;
    link.download = `${videoTitle}.mp4`;
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    
    window.enhancedUI.showNotification('Download started', 'info');
}

// Initialize view tracking
function trackVideoView(videoId) {
    const viewElement = document.getElementById(`views-${videoId}`);
    if (viewElement) {
        let currentViews = parseInt(viewElement.textContent) || 0;
        viewElement.textContent = currentViews + 1;
        
        // Store in localStorage
        const views = JSON.parse(localStorage.getItem('videoViews') || '{}');
        views[videoId] = (views[videoId] || 0) + 1;
        localStorage.setItem('videoViews', JSON.stringify(views));
    }
}

// Load favorites on page load
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

// Load view counts on page load
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
    
    // Load saved data
    loadFavorites();
    loadViewCounts();
    
    // Integrate with existing video gallery
    if (window.videoGallery) {
        const originalOpenModal = window.videoGallery.openVideoModal;
        window.videoGallery.openVideoModal = function(videoId) {
            trackVideoView(videoId);
            return originalOpenModal.call(this, videoId);
        };
    }
});

// Utility function for notifications
function showNotification(message, type = 'info', duration = 3000) {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    
    // Create icon element safely
    const icon = document.createElement('i');
    icon.className = `fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info'}`;
    
    // Create message span safely using textContent to prevent XSS
    const messageSpan = document.createElement('span');
    messageSpan.textContent = message;
    
    // Create close button safely
    const closeBtn = document.createElement('button');
    closeBtn.className = 'notification-close';
    const closeIcon = document.createElement('i');
    closeIcon.className = 'fas fa-times';
    closeBtn.appendChild(closeIcon);
    
    // Append elements safely
    notification.appendChild(icon);
    notification.appendChild(messageSpan);
    notification.appendChild(closeBtn);
    
    document.body.appendChild(notification);
    
    setTimeout(() => notification.classList.add('show'), 10);
    
    // Add click event to the close button we created
    closeBtn.addEventListener('click', () => {
        hideNotification(notification);
    });
    
    setTimeout(() => {
        hideNotification(notification);
    }, duration);
}

function hideNotification(notification) {
    notification.classList.remove('show');
    setTimeout(() => notification.remove(), 300);
}

// Initialize enhanced UI when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.enhancedUI = new EnhancedUI();
    
    // Load saved data
    loadFavorites();
    loadViewCounts();
    
    // Integrate with existing video gallery
    if (window.videoGallery) {
        const originalOpenModal = window.videoGallery.openVideoModal;
        window.videoGallery.openVideoModal = function(videoId) {
            trackVideoView(videoId);
            return originalOpenModal.call(this, videoId);
        };
    }
});