/**
 * Accessibility Features for Veterans with Disabilities
 * Comprehensive accessibility enhancements for DreamFrame LLC
 */

class AccessibilityManager {
    constructor() {
        this.settings = {
            highContrast: false,
            largeText: false,
            reducedMotion: false,
            screenReader: false,
            keyboardNav: true,
            autoplay: true
        };
        
        this.init();
    }

    init() {
        this.loadSettings();
        this.createAccessibilityPanel();
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupMotionReduction();
        this.setupContrastMode();
        this.setupTextSizing();
        this.setupFocusManagement();
        this.announcePageLoad();
    }

    createAccessibilityPanel() {
        const panel = document.createElement('div');
        panel.id = 'accessibility-panel';
        panel.className = 'accessibility-panel';
        panel.setAttribute('role', 'region');
        panel.setAttribute('aria-label', 'Accessibility Controls');
        
        panel.innerHTML = `
            <button class="accessibility-toggle" aria-label="Open accessibility options" title="Accessibility Options">
                ♿
            </button>
            <div class="accessibility-content" role="dialog" aria-labelledby="accessibility-title">
                <div class="accessibility-header">
                    <h3 id="accessibility-title">Accessibility Options</h3>
                    <button class="accessibility-close" aria-label="Close accessibility options">&times;</button>
                </div>
                <div class="accessibility-options">
                    <div class="option-group">
                        <h4>Visual Accessibility</h4>
                        <label class="option-item">
                            <input type="checkbox" id="high-contrast" aria-describedby="contrast-desc">
                            <span>High Contrast Mode</span>
                            <small id="contrast-desc">Enhances text visibility for better reading</small>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" id="large-text" aria-describedby="text-desc">
                            <span>Large Text</span>
                            <small id="text-desc">Increases font size for easier reading</small>
                        </label>
                    </div>
                    
                    <div class="option-group">
                        <h4>Motion & Animation</h4>
                        <label class="option-item">
                            <input type="checkbox" id="reduced-motion" aria-describedby="motion-desc">
                            <span>Reduce Motion</span>
                            <small id="motion-desc">Minimizes animations and transitions</small>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" id="disable-autoplay" aria-describedby="autoplay-desc">
                            <span>Disable Video Autoplay</span>
                            <small id="autoplay-desc">Prevents videos from playing automatically</small>
                        </label>
                    </div>
                    
                    <div class="option-group">
                        <h4>Navigation</h4>
                        <label class="option-item">
                            <input type="checkbox" id="keyboard-nav" checked aria-describedby="keyboard-desc">
                            <span>Enhanced Keyboard Navigation</span>
                            <small id="keyboard-desc">Improved keyboard shortcuts and focus indicators</small>
                        </label>
                        <label class="option-item">
                            <input type="checkbox" id="skip-links" checked aria-describedby="skip-desc">
                            <span>Skip Navigation Links</span>
                            <small id="skip-desc">Quick links to main content areas</small>
                        </label>
                    </div>
                </div>
                
                <div class="accessibility-actions">
                    <button class="btn-reset" type="button">Reset to Defaults</button>
                    <button class="btn-save" type="button">Save Preferences</button>
                </div>
                
                <div class="accessibility-info">
                    <p><strong>Veteran Support:</strong> For additional assistance, contact us at support@dreamframellc.com</p>
                    <p><strong>Keyboard Shortcuts:</strong></p>
                    <ul>
                        <li>Alt + A: Open accessibility panel</li>
                        <li>Alt + S: Skip to main content</li>
                        <li>Alt + P: Pause/play videos</li>
                        <li>Escape: Close modal dialogs</li>
                    </ul>
                </div>
            </div>
        `;
        
        document.body.appendChild(panel);
        this.setupPanelEvents();
    }

    setupPanelEvents() {
        const toggle = document.querySelector('.accessibility-toggle');
        const close = document.querySelector('.accessibility-close');
        const content = document.querySelector('.accessibility-content');
        const resetBtn = document.querySelector('.btn-reset');
        const saveBtn = document.querySelector('.btn-save');

        toggle.addEventListener('click', () => {
            content.classList.toggle('open');
            const isOpen = content.classList.contains('open');
            toggle.setAttribute('aria-expanded', isOpen);
            if (isOpen) {
                content.focus();
            }
        });

        close.addEventListener('click', () => {
            content.classList.remove('open');
            toggle.setAttribute('aria-expanded', 'false');
            toggle.focus();
        });

        // Close with Escape key
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && content.classList.contains('open')) {
                content.classList.remove('open');
                toggle.setAttribute('aria-expanded', 'false');
                toggle.focus();
            }
        });

        // Option changes
        document.getElementById('high-contrast').addEventListener('change', (e) => {
            this.toggleHighContrast(e.target.checked);
        });

        document.getElementById('large-text').addEventListener('change', (e) => {
            this.toggleLargeText(e.target.checked);
        });

        document.getElementById('reduced-motion').addEventListener('change', (e) => {
            this.toggleReducedMotion(e.target.checked);
        });

        document.getElementById('disable-autoplay').addEventListener('change', (e) => {
            this.toggleAutoplay(!e.target.checked);
        });

        resetBtn.addEventListener('click', () => this.resetSettings());
        saveBtn.addEventListener('click', () => this.saveSettings());
    }

    setupKeyboardNavigation() {
        // Add skip links
        const skipLinks = document.createElement('div');
        skipLinks.className = 'skip-links';
        skipLinks.innerHTML = `
            <a href="#main-content" class="skip-link">Skip to main content</a>
            <a href="#navigation" class="skip-link">Skip to navigation</a>
            <a href="#accessibility-panel" class="skip-link">Accessibility options</a>
        `;
        document.body.insertBefore(skipLinks, document.body.firstChild);

        // Keyboard shortcuts
        document.addEventListener('keydown', (e) => {
            if (e.altKey) {
                switch (e.key.toLowerCase()) {
                    case 'a':
                        e.preventDefault();
                        document.querySelector('.accessibility-toggle').click();
                        break;
                    case 's':
                        e.preventDefault();
                        const mainContent = document.getElementById('main-content') || document.querySelector('main');
                        if (mainContent) mainContent.focus();
                        break;
                    case 'p':
                        e.preventDefault();
                        this.toggleAllVideos();
                        break;
                }
            }
        });

        // Enhanced focus indicators
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                document.body.classList.add('keyboard-navigation');
            }
        });

        document.addEventListener('mousedown', () => {
            document.body.classList.remove('keyboard-navigation');
        });
    }

    setupScreenReaderSupport() {
        // Add ARIA landmarks
        const main = document.querySelector('main') || document.querySelector('.container');
        if (main && !main.id) {
            main.id = 'main-content';
            main.setAttribute('role', 'main');
        }

        // Add live region for announcements
        const liveRegion = document.createElement('div');
        liveRegion.id = 'live-announcements';
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.style.position = 'absolute';
        liveRegion.style.left = '-10000px';
        liveRegion.style.width = '1px';
        liveRegion.style.height = '1px';
        liveRegion.style.overflow = 'hidden';
        document.body.appendChild(liveRegion);

        // Improve video accessibility
        const videos = document.querySelectorAll('video');
        videos.forEach((video, index) => {
            if (!video.getAttribute('aria-label')) {
                video.setAttribute('aria-label', `Video ${index + 1}: Professional video production showcase`);
            }
            video.setAttribute('role', 'img');
        });

        // Add alt text to images missing it
        const images = document.querySelectorAll('img:not([alt])');
        images.forEach(img => {
            img.setAttribute('alt', 'Decorative image');
        });
    }

    toggleHighContrast(enabled) {
        this.settings.highContrast = enabled;
        document.body.classList.toggle('high-contrast', enabled);
        this.announce(enabled ? 'High contrast mode enabled' : 'High contrast mode disabled');
    }

    toggleLargeText(enabled) {
        this.settings.largeText = enabled;
        document.body.classList.toggle('large-text', enabled);
        this.announce(enabled ? 'Large text enabled' : 'Large text disabled');
    }

    toggleReducedMotion(enabled) {
        this.settings.reducedMotion = enabled;
        document.body.classList.toggle('reduced-motion', enabled);
        this.announce(enabled ? 'Reduced motion enabled' : 'Reduced motion disabled');
    }

    toggleAutoplay(enabled) {
        this.settings.autoplay = enabled;
        const videos = document.querySelectorAll('video[autoplay]');
        videos.forEach(video => {
            if (enabled) {
                video.setAttribute('autoplay', '');
                video.play().catch(() => {});
            } else {
                video.removeAttribute('autoplay');
                video.pause();
            }
        });
        this.announce(enabled ? 'Video autoplay enabled' : 'Video autoplay disabled');
    }

    toggleAllVideos() {
        const videos = document.querySelectorAll('video');
        let playedCount = 0;
        let pausedCount = 0;

        videos.forEach(video => {
            if (video.paused) {
                video.play().catch(() => {});
                playedCount++;
            } else {
                video.pause();
                pausedCount++;
            }
        });

        if (playedCount > 0) {
            this.announce(`${playedCount} videos started playing`);
        } else if (pausedCount > 0) {
            this.announce(`${pausedCount} videos paused`);
        }
    }

    setupMotionReduction() {
        // Respect system preference
        const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)');
        if (prefersReducedMotion.matches) {
            this.toggleReducedMotion(true);
            document.getElementById('reduced-motion').checked = true;
        }

        prefersReducedMotion.addEventListener('change', (e) => {
            if (e.matches) {
                this.toggleReducedMotion(true);
                document.getElementById('reduced-motion').checked = true;
            }
        });
    }

    setupContrastMode() {
        // Respect system preference
        const prefersHighContrast = window.matchMedia('(prefers-contrast: high)');
        if (prefersHighContrast.matches) {
            this.toggleHighContrast(true);
            document.getElementById('high-contrast').checked = true;
        }
    }

    setupTextSizing() {
        // Add text size controls
        const textControls = document.createElement('div');
        textControls.className = 'text-size-controls';
        textControls.innerHTML = `
            <button class="text-size-btn" data-size="small" aria-label="Decrease text size">A-</button>
            <button class="text-size-btn" data-size="normal" aria-label="Normal text size">A</button>
            <button class="text-size-btn" data-size="large" aria-label="Increase text size">A+</button>
        `;
        
        document.querySelector('#accessibility-panel .accessibility-content').appendChild(textControls);

        textControls.addEventListener('click', (e) => {
            if (e.target.classList.contains('text-size-btn')) {
                const size = e.target.dataset.size;
                this.setTextSize(size);
            }
        });
    }

    setTextSize(size) {
        document.body.classList.remove('text-small', 'text-normal', 'text-large');
        document.body.classList.add(`text-${size}`);
        this.announce(`Text size set to ${size}`);
    }

    setupFocusManagement() {
        // Ensure modal focus management
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                const modal = document.querySelector('.accessibility-content.open');
                if (modal) {
                    const focusableElements = modal.querySelectorAll(
                        'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
                    );
                    
                    const firstElement = focusableElements[0];
                    const lastElement = focusableElements[focusableElements.length - 1];

                    if (e.shiftKey && document.activeElement === firstElement) {
                        e.preventDefault();
                        lastElement.focus();
                    } else if (!e.shiftKey && document.activeElement === lastElement) {
                        e.preventDefault();
                        firstElement.focus();
                    }
                }
            }
        });
    }

    announce(message) {
        const liveRegion = document.getElementById('live-announcements');
        if (liveRegion) {
            liveRegion.textContent = message;
        }
    }

    announcePageLoad() {
        setTimeout(() => {
            this.announce('DreamFrame LLC website loaded. Press Alt+A for accessibility options.');
        }, 1000);
    }

    saveSettings() {
        localStorage.setItem('dreamframe-accessibility', JSON.stringify(this.settings));
        this.announce('Accessibility preferences saved');
    }

    loadSettings() {
        const saved = localStorage.getItem('dreamframe-accessibility');
        if (saved) {
            this.settings = { ...this.settings, ...JSON.parse(saved) };
            this.applySettings();
        }
    }

    applySettings() {
        document.getElementById('high-contrast').checked = this.settings.highContrast;
        document.getElementById('large-text').checked = this.settings.largeText;
        document.getElementById('reduced-motion').checked = this.settings.reducedMotion;
        document.getElementById('disable-autoplay').checked = !this.settings.autoplay;

        if (this.settings.highContrast) this.toggleHighContrast(true);
        if (this.settings.largeText) this.toggleLargeText(true);
        if (this.settings.reducedMotion) this.toggleReducedMotion(true);
        if (!this.settings.autoplay) this.toggleAutoplay(false);
    }

    resetSettings() {
        this.settings = {
            highContrast: false,
            largeText: false,
            reducedMotion: false,
            screenReader: false,
            keyboardNav: true,
            autoplay: true
        };
        
        document.body.classList.remove('high-contrast', 'large-text', 'reduced-motion', 'text-small', 'text-large');
        document.body.classList.add('text-normal');
        
        document.getElementById('high-contrast').checked = false;
        document.getElementById('large-text').checked = false;
        document.getElementById('reduced-motion').checked = false;
        document.getElementById('disable-autoplay').checked = false;
        
        this.announce('Accessibility settings reset to defaults');
    }
}

// Initialize accessibility features when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    new AccessibilityManager();
});