/**
 * Video Player and Modal Management
 * Handles video gallery interactions, modal display, and video playback
 */

class VideoGallery {
    constructor() {
        this.modal = document.getElementById('videoModal');
        this.modalVideo = document.getElementById('modalVideo');
        this.modalTitle = document.getElementById('modalTitle');
        this.modalDescription = document.getElementById('modalDescription');
        this.modalClose = document.getElementById('modalClose');
        this.modalBackdrop = document.getElementById('modalBackdrop');
        this.videoLoading = document.getElementById('videoLoading');
        this.videoError = document.getElementById('videoError');
        this.retryButton = document.getElementById('retryButton');
        this.downloadBtn = document.getElementById('downloadVideoBtn');
        
        // Debug modal elements
        console.log('Modal elements found:', {
            modal: !!this.modal,
            modalVideo: !!this.modalVideo,
            modalTitle: !!this.modalTitle,
            modalDescription: !!this.modalDescription,
            modalClose: !!this.modalClose,
            modalBackdrop: !!this.modalBackdrop,
            videoLoading: !!this.videoLoading,
            videoError: !!this.videoError
        });
        
        this.currentVideo = null;
        this.videos = [];
        
        this.init();
    }

    init() {
        this.loadVideoData();
        this.setupEventListeners();
        this.setupVideoGalleryListeners();
        this.setupShareModal();
    }

    async loadVideoData() {
        try {
            console.log('Loading video data from API...');
            const response = await fetch('/api/videos');
            if (response.ok) {
                const data = await response.json();
                this.videos = data.videos || data; // Handle both response formats
                console.log('Video data loaded:', this.videos);
            } else {
                console.error('Failed to load video data. Status:', response.status);
                this.videos = []; // Initialize as empty array
            }
        } catch (error) {
            console.error('Error loading video data:', error);
            this.videos = []; // Initialize as empty array
        }
    }

    setupEventListeners() {
        // Modal close events
        if (this.modalClose) {
            this.modalClose.addEventListener('click', () => this.closeModal());
        }
        
        if (this.modalBackdrop) {
            this.modalBackdrop.addEventListener('click', () => this.closeModal());
        }

        // Escape key to close modal
        document.addEventListener('keydown', (e) => {
            if (e.key === 'Escape' && this.isModalOpen()) {
                this.closeModal();
            }
        });

        // Retry button
        if (this.retryButton) {
            this.retryButton.addEventListener('click', () => this.retryVideoLoad());
        }

        // Download button
        if (this.downloadBtn) {
            this.downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                const videoId = this.downloadBtn.dataset.videoId;
                const videoTitle = this.downloadBtn.dataset.videoTitle;
                if (videoId && !this.downloadBtn.classList.contains('downloading')) {
                    this.downloadVideo(videoId, videoTitle);
                }
            });
        }

        // Video events
        if (this.modalVideo) {
            this.modalVideo.addEventListener('loadstart', () => this.showVideoLoading());
            this.modalVideo.addEventListener('loadeddata', () => this.hideVideoLoading());
            this.modalVideo.addEventListener('canplay', () => this.hideVideoLoading());
            this.modalVideo.addEventListener('error', () => this.showVideoError());
            this.modalVideo.addEventListener('ended', () => this.onVideoEnded());
        }
    }

    setupVideoGalleryListeners() {
        const videoCards = document.querySelectorAll('.video-card');
        console.log('Found video cards:', videoCards.length);
        
        videoCards.forEach(card => {
            // Add video preview container to each card
            this.addVideoPreviewToCard(card);

            card.addEventListener('click', (e) => {
                e.preventDefault();
                const videoId = card.dataset.videoId;
                console.log('Video card clicked:', videoId);
                console.log('Available videos:', this.videos);
                this.openVideoModal(videoId);
            });

            // Add keyboard support
            card.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const videoId = card.dataset.videoId;
                    this.openVideoModal(videoId);
                }
            });

            // Add hover preview functionality
            card.addEventListener('mouseenter', (e) => {
                this.startVideoPreview(card);
            });

            card.addEventListener('mouseleave', (e) => {
                this.stopVideoPreview(card);
            });

            // Make cards focusable
            card.setAttribute('tabindex', '0');
        });
    }

    openVideoModal(videoId) {
        console.log('Opening video modal for:', videoId);
        console.log('Available videos:', this.videos);
        
        const video = this.videos.find(v => v.id === videoId);
        
        if (!video) {
            console.error('Video not found:', videoId);
            console.error('Available video IDs:', this.videos.map(v => v.id));
            return;
        }

        this.currentVideo = video;
        
        // Update modal content
        if (this.modalTitle) {
            this.modalTitle.textContent = video.title;
        }
        
        if (this.modalDescription) {
            this.modalDescription.textContent = video.description;
        }

        // Update share preview
        this.updateSharePreview(video);

        // Update download button
        const downloadBtn = document.getElementById('downloadVideoBtn');
        if (downloadBtn) {
            downloadBtn.dataset.videoId = video.id;
            downloadBtn.dataset.videoTitle = video.title;
            downloadBtn.style.display = 'flex';
            
            // Reset button state
            downloadBtn.classList.remove('downloading', 'completed');
            const downloadIcon = document.getElementById('downloadIcon');
            const downloadText = document.getElementById('downloadText');
            const downloadProgress = document.getElementById('downloadProgress');
            if (downloadIcon) downloadIcon.className = 'fas fa-download';
            if (downloadText) downloadText.textContent = 'Download Video';
            if (downloadProgress) downloadProgress.style.display = 'none';
        }

        // Use original video file with fallback capability
        const videoUrl = `/video/${video.video}`;
        
        if (this.modalVideo) {
            console.log(`Loading video: ${video.title} from ${videoUrl}`);
            this.showVideoLoading();
            
            // Reset video completely
            this.modalVideo.pause();
            this.modalVideo.currentTime = 0;
            
            // Clear any existing event handlers
            this.modalVideo.onloadstart = null;
            this.modalVideo.onloadeddata = null;
            this.modalVideo.oncanplay = null;
            this.modalVideo.onerror = null;
            
            // Set video source and properties
            this.modalVideo.src = videoUrl;
            this.modalVideo.controls = true;
            this.modalVideo.preload = 'metadata';
            this.modalVideo.playsInline = true;
            
            // Add event handlers for video loading
            this.modalVideo.onloadstart = () => {
                console.log('Video loading started:', video.title);
                this.showVideoLoading();
            };
            
            this.modalVideo.onloadedmetadata = () => {
                console.log('Video metadata loaded:', video.title);
            };
            
            this.modalVideo.onloadeddata = () => {
                console.log('Video data loaded:', video.title);
                this.hideVideoLoading();
            };
            
            this.modalVideo.oncanplay = () => {
                console.log('Video can play:', video.title);
                this.hideVideoLoading();
            };
            
            this.modalVideo.oncanplaythrough = () => {
                console.log('Video ready to play:', video.title);
                this.hideVideoLoading();
            };
            
            this.modalVideo.onerror = (e) => {
                console.error('Video error for:', video.title);
                console.error('Video error details:', {
                    error: this.modalVideo.error,
                    code: this.modalVideo.error ? this.modalVideo.error.code : 'unknown',
                    message: this.modalVideo.error ? this.modalVideo.error.message : 'unknown',
                    src: this.modalVideo.currentSrc || this.modalVideo.src
                });
                this.showVideoError();
            };
            
            // Load the video
            this.modalVideo.load();
            
            // Ambient lighting events
            this.modalVideo.addEventListener('play', () => this.startAmbientMode());
            this.modalVideo.addEventListener('pause', () => this.stopAmbientMode());
            this.modalVideo.addEventListener('ended', () => this.stopAmbientMode());
            

            
            // Force video codec detection
            this.modalVideo.addEventListener('loadedmetadata', () => {
                if (this.modalVideo.videoWidth === 0 || this.modalVideo.videoHeight === 0) {
                    console.warn('Video has no visual track:', video.title);
                    // Show message for audio-only content
                    const container = this.modalVideo.parentElement;
                    const audioWarning = document.createElement('div');
                    audioWarning.className = 'audio-only-warning';
                    audioWarning.style.cssText = `
                        position: absolute;
                        top: 50%;
                        left: 50%;
                        transform: translate(-50%, -50%);
                        background: rgba(255, 193, 7, 0.9);
                        color: #000;
                        padding: 1rem;
                        border-radius: 8px;
                        text-align: center;
                        z-index: 10;
                        pointer-events: none;
                    `;
                    audioWarning.innerHTML = `
                        <i class="fas fa-volume-up" style="font-size: 2rem; margin-bottom: 0.5rem; display: block;"></i>
                        <strong>Audio Only</strong><br>
                        This video contains audio but no visual content
                    `;
                    container.style.position = 'relative';
                    container.appendChild(audioWarning);
                    
                    // Remove warning after 3 seconds
                    setTimeout(() => {
                        if (audioWarning.parentElement) {
                            audioWarning.remove();
                        }
                    }, 3000);
                }
            });
            
            this.modalVideo.load();
            
            console.log(`Video element configured for: ${video.title}`);
        }
        
        if (this.videoDownloadLink) {
            this.videoDownloadLink.href = videoUrl;
        }

        // Show modal
        console.log('About to show modal for:', video.title);
        this.showModal();
        
        // Track video opening
        this.trackVideoOpen(video);
    }

    closeModal() {
        if (this.modalVideo) {
            this.modalVideo.pause();
            this.modalVideo.currentTime = 0;
        }
        
        this.stopAmbientMode();
        this.hideModal();
        this.currentVideo = null;
        
        // Return focus to the video card that was clicked
        const videoCards = document.querySelectorAll('.video-card');
        if (videoCards.length > 0) {
            videoCards[0].focus();
        }
    }

    startAmbientMode() {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.classList.add('ambient-mode');
            console.log('Ambient lighting activated');
        }
    }

    stopAmbientMode() {
        const backdrop = document.querySelector('.modal-backdrop');
        if (backdrop) {
            backdrop.classList.remove('ambient-mode');
            console.log('Ambient lighting deactivated');
        }
    }

    updateSharePreview(video) {
        const sharePreviewThumbnail = document.getElementById('sharePreviewThumbnail');
        const sharePreviewTitle = document.getElementById('sharePreviewTitle');
        const sharePreviewDescription = document.getElementById('sharePreviewDescription');

        if (sharePreviewThumbnail) {
            sharePreviewThumbnail.src = `/thumbnails/${video.thumbnail}`;
            sharePreviewThumbnail.alt = video.title;
        }

        if (sharePreviewTitle) {
            sharePreviewTitle.textContent = video.title;
        }

        if (sharePreviewDescription) {
            sharePreviewDescription.textContent = video.description;
        }
    }

    setupShareModal() {
        const shareBtn = document.getElementById('shareVideoBtn');
        const shareModal = document.getElementById('shareModal');
        const shareCloseBtn = document.getElementById('shareCloseBtn');
        const shareCopyBtn = document.getElementById('shareCopy');
        const shareUrlInput = document.getElementById('shareUrlInput');

        if (shareBtn) {
            shareBtn.addEventListener('click', () => {
                this.openShareModal();
            });
        }

        if (shareCloseBtn) {
            shareCloseBtn.addEventListener('click', () => {
                this.closeShareModal();
            });
        }

        if (shareModal) {
            shareModal.addEventListener('click', (e) => {
                if (e.target === shareModal) {
                    this.closeShareModal();
                }
            });
        }

        if (shareCopyBtn) {
            shareCopyBtn.addEventListener('click', () => {
                this.copyShareUrl();
            });
        }

        // Setup social sharing buttons
        this.setupSocialSharing();
    }

    openShareModal() {
        const shareModal = document.getElementById('shareModal');
        const shareUrlInput = document.getElementById('shareUrlInput');
        
        if (this.currentVideo && shareModal) {
            const shareUrl = `${window.location.origin}${window.location.pathname}?video=${this.currentVideo.id}`;
            
            if (shareUrlInput) {
                shareUrlInput.value = shareUrl;
            }
            
            shareModal.style.display = 'block';
            this.updateSocialShareLinks(shareUrl);
        }
    }

    closeShareModal() {
        const shareModal = document.getElementById('shareModal');
        if (shareModal) {
            shareModal.style.display = 'none';
        }
    }

    copyShareUrl() {
        const shareUrlInput = document.getElementById('shareUrlInput');
        if (shareUrlInput) {
            shareUrlInput.select();
            shareUrlInput.setSelectionRange(0, 99999);
            
            try {
                document.execCommand('copy');
                this.showShareNotification('Link copied to clipboard!', 'success');
            } catch (err) {
                // Fallback for modern browsers
                navigator.clipboard.writeText(shareUrlInput.value).then(() => {
                    this.showShareNotification('Link copied to clipboard!', 'success');
                }).catch(() => {
                    this.showShareNotification('Failed to copy link', 'error');
                });
            }
        }
    }

    setupSocialSharing() {
        const facebookBtn = document.getElementById('shareFacebook');
        const twitterBtn = document.getElementById('shareTwitter');
        const whatsappBtn = document.getElementById('shareWhatsApp');
        const emailBtn = document.getElementById('shareEmail');

        if (facebookBtn) {
            facebookBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareToFacebook();
            });
        }

        if (twitterBtn) {
            twitterBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareToTwitter();
            });
        }

        if (whatsappBtn) {
            whatsappBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareToWhatsApp();
            });
        }

        if (emailBtn) {
            emailBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.shareToEmail();
            });
        }
    }

    updateSocialShareLinks(shareUrl) {
        if (!this.currentVideo) return;

        const title = encodeURIComponent(this.currentVideo.title + ' - DreamFrame LLC');
        const description = encodeURIComponent(this.currentVideo.description);
        const url = encodeURIComponent(shareUrl);

        this.shareData = {
            title,
            description,
            url,
            shareUrl
        };
    }

    shareToFacebook() {
        if (this.shareData) {
            const facebookUrl = `https://www.facebook.com/sharer/sharer.php?u=${this.shareData.url}&quote=${this.shareData.title}`;
            window.open(facebookUrl, '_blank', 'width=600,height=400');
        }
    }

    shareToTwitter() {
        if (this.shareData) {
            const twitterUrl = `https://twitter.com/intent/tweet?text=${this.shareData.title}&url=${this.shareData.url}`;
            window.open(twitterUrl, '_blank', 'width=600,height=400');
        }
    }

    shareToWhatsApp() {
        if (this.shareData) {
            const whatsappUrl = `https://wa.me/?text=${this.shareData.title}%20${this.shareData.url}`;
            window.open(whatsappUrl, '_blank');
        }
    }

    shareToEmail() {
        if (this.shareData && this.currentVideo) {
            const subject = encodeURIComponent(`Check out this video: ${this.currentVideo.title}`);
            const body = encodeURIComponent(`Hi,\n\nI wanted to share this amazing video with you:\n\n${this.currentVideo.title}\n${this.currentVideo.description}\n\nWatch it here: ${this.shareData.shareUrl}\n\nBest regards`);
            const mailtoUrl = `mailto:?subject=${subject}&body=${body}`;
            window.location.href = mailtoUrl;
        }
    }

    showShareNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `voice-notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check' : type === 'error' ? 'exclamation-triangle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;
        
        document.body.appendChild(notification);
        
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showModal() {
        if (this.modal) {
            this.modal.style.display = 'flex';
            this.modal.style.zIndex = '9999';
            this.modal.style.position = 'fixed';
            this.modal.style.top = '0';
            this.modal.style.left = '0';
            this.modal.style.width = '100%';
            this.modal.style.height = '100%';
            document.body.style.overflow = 'hidden';
            
            // Focus management
            this.modalClose?.focus();
        }
    }

    hideModal() {
        if (this.modal) {
            this.modal.style.display = 'none';
            document.body.style.overflow = '';
        }
    }

    isModalOpen() {
        return this.modal && this.modal.style.display === 'flex';
    }

    showVideoLoading() {
        if (this.videoLoading) {
            this.videoLoading.style.display = 'block';
        }
        if (this.videoError) {
            this.videoError.style.display = 'none';
        }
        if (this.modalVideo) {
            this.modalVideo.style.display = 'none';
        }
    }

    hideVideoLoading() {
        if (this.videoLoading) {
            this.videoLoading.style.display = 'none';
        }
        if (this.modalVideo) {
            this.modalVideo.style.display = 'block';
        }
    }

    showVideoError() {
        if (this.videoLoading) {
            this.videoLoading.style.display = 'none';
        }
        if (this.videoError) {
            this.videoError.style.display = 'block';
        }
        if (this.modalVideo) {
            this.modalVideo.style.display = 'none';
        }
        
        console.error('Video loading error for:', this.currentVideo?.video_file);
    }

    resetVideoState() {
        if (this.videoLoading) {
            this.videoLoading.style.display = 'none';
        }
        if (this.videoError) {
            this.videoError.style.display = 'none';
        }
        if (this.modalVideo) {
            this.modalVideo.style.display = 'block';
        }
    }

    retryVideoLoad() {
        if (this.currentVideo && this.modalVideo) {
            console.log('Retrying video load for:', this.currentVideo.title);
            this.hideVideoError();
            
            // Use test_working.mp4 as guaranteed working fallback
            const fallbackUrl = '/video/test_working.mp4';
            console.log('Using fallback video:', fallbackUrl);
            
            this.showVideoLoading();
            this.modalVideo.src = fallbackUrl;
            this.modalVideo.load();
        }
    }

    onVideoEnded() {
        // Optional: Auto-close modal or show related videos
        console.log('Video ended:', this.currentVideo?.title);
    }

    trackVideoOpen(video) {
        // Analytics tracking could be added here
        console.log('Video opened:', video.title);
    }

    // Utility method to handle thumbnail errors
    handleThumbnailError(img) {
        const fallbackSvg = `data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjE3MCIgdmlld0JveD0iMCAwIDMwMCAxNzAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMTcwIiBmaWxsPSIjNjY3RUVBIi8+Cjx0ZXh0IHg9IjE1MCIgeT0iODUiIGZpbGw9IndoaXRlIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBkb21pbmFudC1iYXNlbGluZT0ibWlkZGxlIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPk5vIFRodW1ibmFpbDwvdGV4dD4KPC9zdmc+`;
        img.src = fallbackSvg;
    }

    async downloadVideo(videoId, videoTitle) {
        const downloadBtn = this.downloadBtn;
        const downloadIcon = document.getElementById('downloadIcon');
        const downloadText = document.getElementById('downloadText');
        const downloadProgress = document.getElementById('downloadProgress');
        const progressBar = document.getElementById('progressBar');
        const progressText = document.getElementById('progressText');

        try {
            // Set downloading state
            downloadBtn.classList.add('downloading');
            downloadIcon.className = 'fas fa-spinner';
            downloadText.textContent = 'Preparing...';
            downloadProgress.style.display = 'flex';
            progressBar.style.width = '10%';
            progressText.textContent = '10%';

            // Create download URL
            const downloadUrl = `/download/video/${videoId}`;
            
            // Start download with progress tracking
            const response = await fetch(downloadUrl);
            
            if (!response.ok) {
                throw new Error(`Download failed: ${response.status} ${response.statusText}`);
            }

            // Get the total file size
            const contentLength = response.headers.get('content-length');
            const total = parseInt(contentLength, 10);
            let loaded = 0;

            // Update progress
            downloadText.textContent = 'Downloading...';
            progressBar.style.width = '25%';
            progressText.textContent = '25%';

            // Create reader for progress tracking
            const reader = response.body.getReader();
            const stream = new ReadableStream({
                start(controller) {
                    function pump() {
                        return reader.read().then(({ done, value }) => {
                            if (done) {
                                controller.close();
                                return;
                            }
                            
                            loaded += value.byteLength;
                            const progress = total ? Math.round((loaded / total) * 100) : 75;
                            progressBar.style.width = `${Math.min(progress, 95)}%`;
                            progressText.textContent = `${Math.min(progress, 95)}%`;
                            
                            controller.enqueue(value);
                            return pump();
                        });
                    }
                    return pump();
                }
            });

            // Convert stream to blob
            const newResponse = new Response(stream);
            const blob = await newResponse.blob();

            // Complete progress
            progressBar.style.width = '100%';
            progressText.textContent = '100%';
            downloadText.textContent = 'Completing...';

            // Create download link and trigger download
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = `${videoTitle || 'video'}.mp4`;
            document.body.appendChild(a);
            a.click();
            
            // Cleanup
            setTimeout(() => {
                window.URL.revokeObjectURL(url);
                document.body.removeChild(a);
            }, 100);

            // Success state
            downloadBtn.classList.remove('downloading');
            downloadBtn.classList.add('completed');
            downloadIcon.className = 'fas fa-check';
            downloadText.textContent = 'Downloaded!';
            
            // Reset after 3 seconds
            setTimeout(() => {
                downloadBtn.classList.remove('completed');
                downloadIcon.className = 'fas fa-download';
                downloadText.textContent = 'Download Video';
                downloadProgress.style.display = 'none';
                progressBar.style.width = '0%';
                progressText.textContent = '0%';
            }, 3000);

        } catch (error) {
            console.error('Download failed:', error);
            
            // Error state
            downloadBtn.classList.remove('downloading');
            downloadIcon.className = 'fas fa-exclamation-triangle';
            downloadText.textContent = 'Download Failed';
            
            // Reset after 3 seconds
            setTimeout(() => {
                downloadIcon.className = 'fas fa-download';
                downloadText.textContent = 'Download Video';
                downloadProgress.style.display = 'none';
                progressBar.style.width = '0%';
                progressText.textContent = '0%';
            }, 3000);
        }
    }

    addVideoPreviewToCard(card) {
        const videoId = card.dataset.videoId;
        const video = this.videos.find(v => v.id === videoId);
        
        if (!video) return;

        // Create preview container
        const previewContainer = document.createElement('div');
        previewContainer.className = 'video-preview-container';
        
        // Create video element for preview
        const previewVideo = document.createElement('video');
        previewVideo.className = 'video-preview-player';
        previewVideo.muted = true;
        previewVideo.loop = true;
        previewVideo.preload = 'none';
        previewVideo.src = `/video/${video.video}`;
        
        // Create overlay with video info
        const overlay = document.createElement('div');
        overlay.className = 'video-preview-overlay';
        overlay.innerHTML = `
            <div class="video-preview-title">${video.title}</div>
            <div class="video-preview-duration">${video.duration}</div>
        `;
        
        // Create control buttons
        const controls = document.createElement('div');
        controls.className = 'video-preview-controls';
        controls.innerHTML = `
            <button class="preview-control-btn preview-play-btn" data-action="play">
                <i class="fas fa-play"></i>
            </button>
            <button class="preview-control-btn preview-fullscreen-btn" data-action="fullscreen">
                <i class="fas fa-expand"></i>
            </button>
        `;
        
        // Create loading indicator
        const loading = document.createElement('div');
        loading.className = 'video-preview-loading';
        loading.innerHTML = `
            <i class="fas fa-spinner"></i>
            <span>Loading preview...</span>
        `;
        
        // Assemble preview container
        previewContainer.appendChild(previewVideo);
        previewContainer.appendChild(overlay);
        previewContainer.appendChild(controls);
        previewContainer.appendChild(loading);
        
        // Add event listeners for controls
        const playBtn = controls.querySelector('.preview-play-btn');
        const fullscreenBtn = controls.querySelector('.preview-fullscreen-btn');
        
        playBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.togglePreviewPlayback(previewVideo, playBtn);
        });
        
        fullscreenBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            this.openVideoModal(videoId);
        });
        
        // Add video event listeners
        previewVideo.addEventListener('loadstart', () => {
            loading.style.display = 'flex';
        });
        
        previewVideo.addEventListener('canplay', () => {
            loading.style.display = 'none';
        });
        
        previewVideo.addEventListener('error', () => {
            loading.innerHTML = '<i class="fas fa-exclamation-triangle"></i><span>Preview unavailable</span>';
        });
        
        // Insert preview container into card
        card.appendChild(previewContainer);
    }

    startVideoPreview(card) {
        const previewContainer = card.querySelector('.video-preview-container');
        const previewVideo = card.querySelector('.video-preview-player');
        
        if (!previewContainer || !previewVideo) return;
        
        // Set a delay before starting preview to avoid accidental triggers
        card.hoverTimeout = setTimeout(() => {
            previewVideo.load();
            previewVideo.play().catch(error => {
                console.log('Auto-play prevented:', error);
            });
        }, 500);
    }

    stopVideoPreview(card) {
        const previewVideo = card.querySelector('.video-preview-player');
        const playBtn = card.querySelector('.preview-play-btn');
        
        // Clear hover timeout
        if (card.hoverTimeout) {
            clearTimeout(card.hoverTimeout);
            card.hoverTimeout = null;
        }
        
        if (previewVideo) {
            previewVideo.pause();
            previewVideo.currentTime = 0;
        }
        
        // Reset play button
        if (playBtn) {
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }

    togglePreviewPlayback(video, playBtn) {
        if (video.paused) {
            video.play().then(() => {
                playBtn.innerHTML = '<i class="fas fa-pause"></i>';
            }).catch(error => {
                console.log('Play failed:', error);
            });
        } else {
            video.pause();
            playBtn.innerHTML = '<i class="fas fa-play"></i>';
        }
    }
}

// Loading state management for video cards
class VideoCardLoader {
    static showLoading(card) {
        card.classList.add('loading');
        const spinner = card.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'flex';
        }
    }

    static hideLoading(card) {
        card.classList.remove('loading');
        const spinner = card.querySelector('.loading-spinner');
        if (spinner) {
            spinner.style.display = 'none';
        }
    }
}

// VideoGallery initialization is now handled by template-specific code
// This allows for better timing control and element detection

// Add keyboard navigation for better accessibility
document.addEventListener('DOMContentLoaded', () => {
    document.addEventListener('keydown', (e) => {
        if (e.ctrlKey && e.key === 'm') {
            // Ctrl+M to focus first video card
            const firstCard = document.querySelector('.video-card');
            if (firstCard) {
                firstCard.focus();
            }
        }
    });
});

// Error handling for images
document.addEventListener('DOMContentLoaded', () => {
    const thumbnails = document.querySelectorAll('.video-thumbnail');
    
    thumbnails.forEach(img => {
        img.addEventListener('error', function() {
            if (window.videoGallery) {
                window.videoGallery.handleThumbnailError(this);
            }
        });
    });
});

// Service Worker registration for better caching (optional)
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        // Service worker could be implemented for better caching
        console.log('Service Worker support available');
    });
}
