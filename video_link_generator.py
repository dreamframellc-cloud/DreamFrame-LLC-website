#!/usr/bin/env python3
"""
Generate direct video access links
"""

import os
from models import VideoOrder
from app import app

def generate_video_link(video_id):
    """Generate direct access link for video"""
    
    with app.app_context():
        video = VideoOrder.query.get(video_id)
        if not video or not video.generated_video_path:
            return None
        
        # Check if file exists
        if not os.path.exists(video.generated_video_path):
            return None
        
        # Generate access URLs
        base_url = "https://your-app-domain.replit.app"  # Will be replaced with actual domain
        download_url = f"{base_url}/download-customer-video/{video_id}"
        direct_file_url = f"{base_url}/completed_videos/{os.path.basename(video.generated_video_path)}"
        
        file_size = os.path.getsize(video.generated_video_path) / (1024 * 1024)
        
        return {
            'title': video.title,
            'download_url': download_url,
            'direct_url': direct_file_url,
            'file_path': video.generated_video_path,
            'file_size': f"{file_size:.1f}MB",
            'status': video.status.value
        }

def create_video_links():
    """Create links for all completed videos"""
    
    with app.app_context():
        completed_videos = VideoOrder.query.filter_by(status='COMPLETED').all()
        
        print("🔗 Available Video Links:")
        print("=" * 50)
        
        for video in completed_videos:
            link_info = generate_video_link(video.id)
            if link_info:
                print(f"\n📹 {link_info['title']} (ID: {video.id})")
                print(f"📊 Size: {link_info['file_size']}")
                print(f"🔗 Download: {link_info['download_url']}")
                print(f"📁 File: {link_info['file_path']}")
        
        print("\n" + "=" * 50)

if __name__ == "__main__":
    create_video_links()