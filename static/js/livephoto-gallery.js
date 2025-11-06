/**
 * Live Photo Gallery Management
 * Handles dynamic Live Photo uploads and gallery display
 */

document.addEventListener('DOMContentLoaded', function() {
    // Make placeholder Live Photo slots clickable
    const placeholders = document.querySelectorAll('.livephoto-showcase.placeholder');
    
    placeholders.forEach(placeholder => {
        placeholder.addEventListener('click', function() {
            // Redirect to Live Photo upload page
            window.location.href = '/upload-livephotos';
        });
    });

    // Check for new Live Photos periodically
    checkForNewLivePhotos();
});

function checkForNewLivePhotos() {
    // This function could be expanded to dynamically load new Live Photos
    // For now, it serves as a placeholder for future functionality
    console.log('Live Photo gallery ready');
}

function addLivePhotoToGallery(filename, slot) {
    const placeholder = document.getElementById(slot);
    if (placeholder) {
        // Clear existing content
        placeholder.innerHTML = '';
        
        // Create video element safely
        const video = document.createElement('video');
        video.autoplay = true;
        video.muted = true;
        video.loop = true;
        video.setAttribute('playsinline', '');
        video.className = 'hero-livephoto';
        
        // Create source element safely
        const source = document.createElement('source');
        // Sanitize filename to prevent XSS
        const sanitizedFilename = filename.replace(/[<>"'&]/g, '');
        source.src = `/static/livephotos/${sanitizedFilename}`;
        source.type = 'video/mp4';
        
        // Create overlay safely
        const overlay = document.createElement('div');
        overlay.className = 'livephoto-overlay';
        
        const label = document.createElement('span');
        label.className = 'livephoto-label';
        label.textContent = `Live Photo ${slot.slice(-1)}`;
        
        // Assemble DOM structure
        video.appendChild(source);
        overlay.appendChild(label);
        placeholder.appendChild(video);
        placeholder.appendChild(overlay);
        
        placeholder.classList.remove('placeholder');
        placeholder.classList.add('active');
    }
}