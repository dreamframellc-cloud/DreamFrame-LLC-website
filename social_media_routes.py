"""
Social Media Video Sharing Routes
Flask routes for generating and serving social media previews
"""

from flask import Blueprint, render_template, request, jsonify, send_file
import os
import json
from social_media_generator import SocialMediaPreviewGenerator
from app import app
import logging

# Create blueprint
social_bp = Blueprint('social', __name__, url_prefix='/social')

# Initialize generator
preview_generator = SocialMediaPreviewGenerator()

@social_bp.route('/generate-preview', methods=['POST'])
def generate_preview():
    """Generate social media preview for a specific video and platform"""
    try:
        data = request.get_json()
        
        video_id = data.get('video_id')
        platform = data.get('platform', 'facebook')
        custom_text = data.get('custom_text', {})
        
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        # Get video info from gallery data
        video_info = get_video_info(video_id)
        if not video_info:
            return jsonify({'error': 'Video not found'}), 404
        
        # Generate preview for specific platform
        preview = preview_generator.create_platform_preview(video_info, platform, custom_text)
        
        if preview:
            return jsonify({
                'success': True,
                'preview': preview,
                'platform': platform
            })
        else:
            return jsonify({'error': 'Failed to generate preview'}), 500
            
    except Exception as e:
        app.logger.error(f"Error generating social preview: {e}")
        return jsonify({'error': 'Failed to generate preview'}), 500

@social_bp.route('/generate-sharing-kit', methods=['POST'])
def generate_sharing_kit():
    """Generate complete sharing kit for all platforms"""
    try:
        data = request.get_json()
        
        video_id = data.get('video_id')
        custom_text = data.get('custom_text', {})
        
        if not video_id:
            return jsonify({'error': 'Video ID is required'}), 400
        
        # Get video info
        video_info = get_video_info(video_id)
        if not video_info:
            return jsonify({'error': 'Video not found'}), 404
        
        # Generate complete sharing kit
        sharing_kit = preview_generator.generate_sharing_kit(video_info, custom_text)
        
        return jsonify({
            'success': True,
            'sharing_kit': sharing_kit
        })
        
    except Exception as e:
        app.logger.error(f"Error generating sharing kit: {e}")
        return jsonify({'error': 'Failed to generate sharing kit'}), 500

@social_bp.route('/preview/<platform>/<video_id>')
def serve_preview(platform, video_id):
    """Serve a specific platform preview image"""
    try:
        preview_dir = os.path.join('static', 'social_previews')
        
        # Find the most recent preview for this video and platform
        preview_files = [f for f in os.listdir(preview_dir) 
                        if f.startswith(f"{video_id}_{platform}_") and f.endswith('.jpg')]
        
        if not preview_files:
            return "Preview not found", 404
        
        # Get the most recent file
        latest_file = sorted(preview_files)[-1]
        preview_path = os.path.join(preview_dir, latest_file)
        
        return send_file(preview_path, mimetype='image/jpeg')
        
    except Exception as e:
        app.logger.error(f"Error serving preview: {e}")
        return "Error serving preview", 500

@social_bp.route('/sharing-widget/<video_id>')
def sharing_widget(video_id):
    """Render social media sharing widget for a video"""
    try:
        video_info = get_video_info(video_id)
        if not video_info:
            return "Video not found", 404
        
        return render_template('social_sharing_widget.html', 
                             video_info=video_info)
        
    except Exception as e:
        app.logger.error(f"Error loading sharing widget: {e}")
        return "Error loading sharing widget", 500

@social_bp.route('/meta-tags/<video_id>')
def generate_meta_tags(video_id):
    """Generate Open Graph and Twitter Card meta tags for a video"""
    try:
        video_info = get_video_info(video_id)
        if not video_info:
            return jsonify({'error': 'Video not found'}), 404
        
        base_url = request.host_url.rstrip('/')
        video_url = f"{base_url}/gallery?video={video_id}"
        
        # Check if previews exist
        preview_dir = os.path.join('static', 'social_previews')
        og_image = None
        twitter_image = None
        
        # Look for existing previews
        facebook_files = [f for f in os.listdir(preview_dir) 
                         if f.startswith(f"{video_id}_facebook_") and f.endswith('.jpg')]
        twitter_files = [f for f in os.listdir(preview_dir) 
                        if f.startswith(f"{video_id}_twitter_") and f.endswith('.jpg')]
        
        if facebook_files:
            og_image = f"{base_url}/static/social_previews/{sorted(facebook_files)[-1]}"
        if twitter_files:
            twitter_image = f"{base_url}/static/social_previews/{sorted(twitter_files)[-1]}"
        
        meta_tags = {
            'og:title': video_info.get('title', 'DreamFrame Video'),
            'og:description': video_info.get('description', 'Professional video by DreamFrame LLC'),
            'og:url': video_url,
            'og:type': 'video.other',
            'og:site_name': 'DreamFrame LLC',
            'og:image': og_image or f"{base_url}/static/homepage_hero_clean.jpg",
            'twitter:card': 'summary_large_image',
            'twitter:title': video_info.get('title', 'DreamFrame Video'),
            'twitter:description': video_info.get('description', 'Professional video by DreamFrame LLC'),
            'twitter:image': twitter_image or og_image or f"{base_url}/static/homepage_hero_clean.jpg",
            'twitter:site': '@dreamframe',
            'video:duration': video_info.get('duration', ''),
            'video:tag': video_info.get('category', 'video')
        }
        
        return jsonify({
            'success': True,
            'meta_tags': meta_tags,
            'video_url': video_url
        })
        
    except Exception as e:
        app.logger.error(f"Error generating meta tags: {e}")
        return jsonify({'error': 'Failed to generate meta tags'}), 500

def get_video_info(video_id):
    """Get video information from gallery data"""
    # Import videos data directly
    videos_data = [
        {"id": "videogram", "title": "VideoGram", "description": "5-second promotional video showcase", "video": "VideoGram.mp4", "thumbnail": "VideoGram.jpg", "duration": "0:05", "category": "professional"},
        {"id": "siblings", "title": "Siblings", "description": "Family memories and bonds", "video": "Siblings_.MP4", "thumbnail": "Siblings_.jpg", "duration": "0:35", "category": "family"},
        {"id": "memories", "title": "Memories", "description": "Precious family moments captured", "video": "Memories.mp4", "thumbnail": "Memories.jpeg.png", "duration": "0:35", "category": "family"},
        {"id": "puppy", "title": "Puppy", "description": "Adorable puppy moments", "video": "Puppy.mp4.MP4", "thumbnail": "Puppy.jpeg.jpg", "duration": "0:08", "category": "family"},
        {"id": "boom", "title": "Boom", "description": "Dynamic 4K action sequence", "video": "Boom_video.mp4_4K.MOV.mp4", "thumbnail": "Boom_thumbnail.jpeg.PNG", "duration": "0:15", "category": "creative"},
        {"id": "fembot", "title": "Fembot", "description": "Futuristic android character showcase", "video": "Fembot.mp4", "thumbnail": "Fembot_thumbnail.jpg", "duration": "0:20", "category": "creative"},
        {"id": "horror", "title": "Horror", "description": "Spine-chilling horror sequence", "video": "Horror_fixed.mp4", "thumbnail": "Horror_thumbnail.jpg", "duration": "0:12", "category": "horror"},
        {"id": "bull", "title": "Bull", "description": "Powerful bull in natural habitat", "video": "Bull.mp4", "thumbnail": "Bull_thumbnail.jpg", "duration": "0:60", "category": "nature"},
        {"id": "balloon", "title": "Balloon", "description": "Whimsical balloon adventure", "video": "Balloon.mp4", "thumbnail": "Balloon_thumbnail.jpg", "duration": "0:18", "category": "creative"},
        {"id": "wwii", "title": "WWII Family", "description": "Historical family tribute", "video": "WWII_Family.mp4", "thumbnail": "WWII_thumbnail.jpg", "duration": "2:40", "category": "military"},
        {"id": "papaw", "title": "Papaw", "description": "Honoring military service", "video": "Papaw.mp4", "thumbnail": "Papaw_thumbnail.jpg", "duration": "0:35", "category": "military"},
        {"id": "dragon", "title": "Dragon", "description": "Mythical dragon fantasy", "video": "Dragon.mp4", "thumbnail": "Dragon_thumbnail.jpg", "duration": "0:15", "category": "creative"},
        {"id": "grandpa", "title": "Grandpa", "description": "Military veteran tribute", "video": "Grandpa.mp4", "thumbnail": "Grandpa_thumbnail.jpg", "duration": "1:50", "category": "military"},
        {"id": "wedding", "title": "Wedding", "description": "Beautiful wedding celebration", "video": "Wedding.mp4", "thumbnail": "Wedding_thumbnail.jpg", "duration": "0:18", "category": "weddings"},
        {"id": "sharks", "title": "Sharks", "description": "Ocean predators in action", "video": "Sharks.mp4", "thumbnail": "Sharks_thumbnail.jpg", "duration": "0:55", "category": "nature"},
        {"id": "elephant", "title": "Elephant", "description": "Majestic elephant showcase", "video": "Elephant.mp4", "thumbnail": "Elephant_thumbnail.jpg", "duration": "0:16", "category": "nature"},
        {"id": "jaws", "title": "JAWS", "description": "Great white shark encounter", "video": "JAWS.mp4", "thumbnail": "JAWS_thumbnail.jpg", "duration": "0:17", "category": "nature"},
        {"id": "hangten", "title": "Hang 10", "description": "Epic 4K surfing action", "video": "Hang10_4K.mp4", "thumbnail": "Hang10_thumbnail.jpg", "duration": "0:12", "category": "nature"},
        {"id": "werewolf", "title": "Werewolf", "description": "Supernatural werewolf transformation", "video": "Werewolf.mp4", "thumbnail": "Werewolf_thumbnail.jpg", "duration": "0:04", "category": "horror"},
        {"id": "fullmoon", "title": "Full Moon", "description": "Mysterious moonlit atmosphere", "video": "Full_Moon.mp4", "thumbnail": "Full_Moon_thumbnail.jpg", "duration": "0:03", "category": "horror"}
    ]
    
    try:
        for video in videos_data:
            if video.get('id') == video_id:
                return video
        return None
    except Exception as e:
        app.logger.error(f"Error getting video info for {video_id}: {e}")
        return None

# Register routes with main app
@app.route('/social-share/<video_id>')
def social_share_page(video_id):
    """Dedicated social sharing page for a video"""
    try:
        video_info = get_video_info(video_id)
        if not video_info:
            return "Video not found", 404
        
        return render_template('social_share_page.html', 
                             video_info=video_info,
                             video_id=video_id)
        
    except Exception as e:
        app.logger.error(f"Error loading social share page: {e}")
        return "Error loading social share page", 500