"""
Social Media Video Sharing Preview Generator
Creates optimized preview images and metadata for different social platforms
"""

import os
try:
    import cv2
except ImportError:
    print("OpenCV not available. Some features may be limited.")
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import json
from datetime import datetime
import hashlib
import logging

# Platform specifications
PLATFORM_SPECS = {
    'facebook': {
        'image_size': (1200, 630),
        'video_size': (1280, 720),
        'aspect_ratio': '16:9',
        'max_title': 100,
        'max_description': 300,
        'overlay_color': '#1877F2',
        'overlay_alpha': 0.8
    },
    'twitter': {
        'image_size': (1200, 675),
        'video_size': (1280, 720),
        'aspect_ratio': '16:9',
        'max_title': 70,
        'max_description': 280,
        'overlay_color': '#1DA1F2',
        'overlay_alpha': 0.8
    },
    'instagram': {
        'image_size': (1080, 1080),
        'video_size': (1080, 1080),
        'aspect_ratio': '1:1',
        'max_title': 50,
        'max_description': 150,
        'overlay_color': '#E4405F',
        'overlay_alpha': 0.7
    },
    'linkedin': {
        'image_size': (1200, 627),
        'video_size': (1280, 720),
        'aspect_ratio': '16:9',
        'max_title': 120,
        'max_description': 200,
        'overlay_color': '#0A66C2',
        'overlay_alpha': 0.8
    },
    'youtube': {
        'image_size': (1280, 720),
        'video_size': (1920, 1080),
        'aspect_ratio': '16:9',
        'max_title': 100,
        'max_description': 5000,
        'overlay_color': '#FF0000',
        'overlay_alpha': 0.7
    }
}

class SocialMediaPreviewGenerator:
    def __init__(self):
        self.output_dir = os.path.join('static', 'social_previews')
        os.makedirs(self.output_dir, exist_ok=True)
        self.logger = logging.getLogger(__name__)
        
    def extract_video_frame(self, video_path, timestamp=None):
        """Extract a frame from video for preview"""
        try:
            cap = cv2.VideoCapture(video_path)
            
            if timestamp:
                # Seek to specific timestamp
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_number = int(timestamp * fps)
                cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            else:
                # Get middle frame
                total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                middle_frame = total_frames // 2
                cap.set(cv2.CAP_PROP_POS_FRAMES, middle_frame)
            
            ret, frame = cap.read()
            cap.release()
            
            if ret:
                # Convert BGR to RGB
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame)
            else:
                return None
                
        except Exception as e:
            self.logger.error(f"Error extracting frame from {video_path}: {e}")
            return None
    
    def create_platform_preview(self, video_info, platform, custom_text=None):
        """Create optimized preview for specific platform"""
        try:
            platform_spec = PLATFORM_SPECS.get(platform, PLATFORM_SPECS['facebook'])
            
            # Get video frame
            video_path = os.path.join('static', 'videos', video_info['video'])
            if not os.path.exists(video_path):
                return None
                
            frame = self.extract_video_frame(video_path)
            if not frame:
                return None
            
            # Create canvas with platform dimensions
            canvas_size = platform_spec['image_size']
            canvas = Image.new('RGB', canvas_size, (0, 0, 0))
            
            # Resize and crop frame to fit aspect ratio
            frame_resized = self._resize_and_crop(frame, canvas_size)
            
            # Apply platform-specific styling
            styled_frame = self._apply_platform_styling(
                frame_resized, platform_spec, video_info, custom_text
            )
            
            # Generate filename
            video_id = video_info.get('id', 'unknown')
            timestamp = int(datetime.now().timestamp())
            filename = f"{video_id}_{platform}_{timestamp}.jpg"
            output_path = os.path.join(self.output_dir, filename)
            
            # Save preview
            styled_frame.save(output_path, 'JPEG', quality=90, optimize=True)
            
            # Generate metadata
            metadata = self._generate_metadata(video_info, platform, custom_text)
            metadata['preview_url'] = f"/static/social_previews/{filename}"
            metadata['filename'] = filename
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error creating {platform} preview: {e}")
            return None
    
    def _resize_and_crop(self, image, target_size):
        """Resize and crop image to target size maintaining aspect ratio"""
        img_width, img_height = image.size
        target_width, target_height = target_size
        
        # Calculate scaling to fit the target size
        scale_w = target_width / img_width
        scale_h = target_height / img_height
        scale = max(scale_w, scale_h)
        
        # Resize image
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        resized = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        
        # Center crop to target size
        left = (new_width - target_width) // 2
        top = (new_height - target_height) // 2
        right = left + target_width
        bottom = top + target_height
        
        return resized.crop((left, top, right, bottom))
    
    def _apply_platform_styling(self, image, platform_spec, video_info, custom_text):
        """Apply platform-specific overlay and branding"""
        overlay = image.copy()
        draw = ImageDraw.Draw(overlay)
        
        width, height = image.size
        
        # Create gradient overlay at bottom
        overlay_height = height // 3
        gradient = Image.new('RGBA', (width, overlay_height), (0, 0, 0, 0))
        gradient_draw = ImageDraw.Draw(gradient)
        
        # Create gradient effect
        for y in range(overlay_height):
            alpha = int(255 * (y / overlay_height) * platform_spec['overlay_alpha'])
            color = tuple(int(platform_spec['overlay_color'][i:i+2], 16) for i in (1, 3, 5))
            gradient_draw.rectangle([(0, y), (width, y+1)], fill=(*color, alpha))
        
        # Apply gradient
        overlay.paste(gradient, (0, height - overlay_height), gradient)
        
        # Add text overlay
        self._add_text_overlay(overlay, video_info, platform_spec, custom_text)
        
        # Add play button
        self._add_play_button(overlay)
        
        # Add platform branding
        self._add_platform_branding(overlay, platform_spec)
        
        return overlay
    
    def _add_text_overlay(self, image, video_info, platform_spec, custom_text):
        """Add text overlay with title and description"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Try to load fonts, fallback to default
        try:
            title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            desc_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 32)
        except:
            title_font = ImageFont.load_default()
            desc_font = ImageFont.load_default()
        
        # Prepare text
        title = custom_text.get('title', video_info.get('title', '')) if custom_text else video_info.get('title', '')
        description = custom_text.get('description', video_info.get('description', '')) if custom_text else video_info.get('description', '')
        
        # Truncate based on platform limits
        title = title[:platform_spec['max_title']] + ('...' if len(title) > platform_spec['max_title'] else '')
        description = description[:platform_spec['max_description']] + ('...' if len(description) > platform_spec['max_description'] else '')
        
        # Position text at bottom
        text_y = height - 120
        
        # Add title with shadow effect
        shadow_offset = 2
        draw.text((52, text_y - 52), title, font=title_font, fill=(0, 0, 0, 180))  # Shadow
        draw.text((50, text_y - 50), title, font=title_font, fill=(255, 255, 255, 255))  # Text
        
        # Add description
        draw.text((52, text_y - 12), description, font=desc_font, fill=(0, 0, 0, 140))  # Shadow
        draw.text((50, text_y - 10), description, font=desc_font, fill=(255, 255, 255, 200))  # Text
    
    def _add_play_button(self, image):
        """Add centered play button overlay"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Play button dimensions
        button_size = min(width, height) // 8
        center_x, center_y = width // 2, height // 2
        
        # Draw play button background circle
        button_bg = (center_x - button_size, center_y - button_size, 
                    center_x + button_size, center_y + button_size)
        draw.ellipse(button_bg, fill=(0, 0, 0, 120), outline=(255, 255, 255, 200), width=4)
        
        # Draw play triangle
        triangle_size = button_size // 2
        triangle = [
            (center_x - triangle_size//2, center_y - triangle_size),
            (center_x - triangle_size//2, center_y + triangle_size),
            (center_x + triangle_size, center_y)
        ]
        draw.polygon(triangle, fill=(255, 255, 255, 220))
    
    def _add_platform_branding(self, image, platform_spec):
        """Add subtle platform branding"""
        draw = ImageDraw.Draw(image)
        width, height = image.size
        
        # Add colored accent bar at top
        accent_height = 8
        color = tuple(int(platform_spec['overlay_color'][i:i+2], 16) for i in (1, 3, 5))
        draw.rectangle([(0, 0), (width, accent_height)], fill=color)
        
        # Add DreamFrame watermark
        try:
            watermark_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            watermark_font = ImageFont.load_default()
        
        watermark_text = "DREAMFRAME LLC"
        draw.text((width - 200, height - 30), watermark_text, 
                 font=watermark_font, fill=(255, 255, 255, 150))
    
    def _generate_metadata(self, video_info, platform, custom_text):
        """Generate social media metadata"""
        title = custom_text.get('title', video_info.get('title', '')) if custom_text else video_info.get('title', '')
        description = custom_text.get('description', video_info.get('description', '')) if custom_text else video_info.get('description', '')
        
        platform_spec = PLATFORM_SPECS[platform]
        
        metadata = {
            'platform': platform,
            'title': title[:platform_spec['max_title']],
            'description': description[:platform_spec['max_description']],
            'video_id': video_info.get('id'),
            'video_title': video_info.get('title'),
            'duration': video_info.get('duration'),
            'category': video_info.get('category'),
            'created_at': datetime.now().isoformat(),
            'platform_specs': platform_spec,
            'sharing_urls': self._generate_sharing_urls(video_info, platform, title, description)
        }
        
        return metadata
    
    def _generate_sharing_urls(self, video_info, platform, title, description):
        """Generate platform-specific sharing URLs"""
        base_url = "https://dreamframe.replit.app"
        video_url = f"{base_url}/gallery?video={video_info.get('id')}"
        
        sharing_urls = {
            'facebook': f"https://www.facebook.com/sharer/sharer.php?u={video_url}",
            'twitter': f"https://twitter.com/intent/tweet?url={video_url}&text={title}",
            'linkedin': f"https://www.linkedin.com/sharing/share-offsite/?url={video_url}",
            'whatsapp': f"https://wa.me/?text={title} {video_url}",
            'email': f"mailto:?subject={title}&body={description} {video_url}"
        }
        
        return sharing_urls.get(platform, video_url)
    
    def generate_all_previews(self, video_info, custom_text=None):
        """Generate previews for all platforms"""
        previews = {}
        
        for platform in PLATFORM_SPECS.keys():
            preview = self.create_platform_preview(video_info, platform, custom_text)
            if preview:
                previews[platform] = preview
        
        return previews
    
    def generate_sharing_kit(self, video_info, custom_text=None):
        """Generate complete sharing kit with all previews and metadata"""
        previews = self.generate_all_previews(video_info, custom_text)
        
        sharing_kit = {
            'video_info': video_info,
            'custom_text': custom_text,
            'previews': previews,
            'generated_at': datetime.now().isoformat(),
            'total_platforms': len(previews)
        }
        
        # Save sharing kit metadata
        kit_filename = f"sharing_kit_{video_info.get('id', 'unknown')}_{int(datetime.now().timestamp())}.json"
        kit_path = os.path.join(self.output_dir, kit_filename)
        
        with open(kit_path, 'w') as f:
            json.dump(sharing_kit, f, indent=2)
        
        sharing_kit['kit_file'] = kit_filename
        
        return sharing_kit

def test_generator():
    """Test the social media preview generator"""
    generator = SocialMediaPreviewGenerator()
    
    # Test with sample video data
    test_video = {
        'id': 'test_video',
        'title': 'Amazing DreamFrame VideoGram',
        'description': 'Professional video production that brings your memories to life',
        'video': 'VideoGram.mp4',
        'duration': '0:05',
        'category': 'professional'
    }
    
    custom_text = {
        'title': 'Transform Your Memories with DreamFrame',
        'description': 'Professional video production services for your most precious moments'
    }
    
    # Generate sharing kit
    sharing_kit = generator.generate_sharing_kit(test_video, custom_text)
    print(f"Generated sharing kit with {sharing_kit['total_platforms']} platform previews")
    
    return sharing_kit

if __name__ == "__main__":
    test_generator()