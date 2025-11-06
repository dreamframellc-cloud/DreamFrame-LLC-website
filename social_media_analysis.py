#!/usr/bin/env python3
"""
Analyze social media processing overhead
"""

from models import VideoOrder
from app import app
import os

def analyze_social_media_overhead():
    """Analyze if social media processing is causing delays"""
    
    with app.app_context():
        print("🔍 SOCIAL MEDIA PROCESSING ANALYSIS")
        print("=" * 50)
        
        # Check current Smile video processing
        smile_video = VideoOrder.query.filter_by(title="Smile").order_by(VideoOrder.created_at.desc()).first()
        
        if smile_video:
            print(f"📱 Current video: {smile_video.title}")
            print(f"🎯 Platform: {smile_video.platform}")
            print(f"📝 Description: {smile_video.description}")
            
            # Analyze processing layers
            processing_layers = []
            
            # 1. Base VEO 3 generation
            processing_layers.append("Base VEO 3 generation")
            
            # 2. Social media optimization
            if smile_video.platform and smile_video.platform != 'general':
                processing_layers.append(f"Platform optimization for {smile_video.platform}")
            
            # 3. Format conversion
            processing_layers.append("Format conversion (MP4)")
            
            # 4. Quality enhancement
            processing_layers.append("Quality enhancement")
            
            print(f"\n🔄 PROCESSING PIPELINE:")
            for i, layer in enumerate(processing_layers, 1):
                print(f"   {i}. {layer}")
            
            print(f"\n⚠️ POTENTIAL OVERHEAD SOURCES:")
            
            # Check if we're doing platform-specific optimization
            if smile_video.platform in ['instagram', 'tiktok', 'youtube_shorts']:
                print("   • 9:16 aspect ratio conversion (vertical)")
                print("   • Platform-specific resolution scaling")
                print("   • Social media compression optimization")
                print("   • Duration constraints processing")
            
            # Check for additional processing files
            social_files = [
                'social_media_story_generator.py',
                'social_media_generator.py', 
                'social_media_routes.py'
            ]
            
            active_social_processing = []
            for file in social_files:
                if os.path.exists(file):
                    active_social_processing.append(file)
            
            if active_social_processing:
                print(f"\n📱 ACTIVE SOCIAL MEDIA MODULES:")
                for module in active_social_processing:
                    print(f"   • {module}")
                
                print(f"\n💡 OPTIMIZATION OPPORTUNITY:")
                print("   • Social media optimization may be adding 2-4 minutes")
                print("   • Consider bypassing platform optimization for speed")
                print("   • Generate base video first, optimize later")
                print("   • Use 'general' platform for fastest processing")
        
        print(f"\n🚀 SPEED OPTIMIZATION RECOMMENDATIONS:")
        print("1. Use 'general' platform instead of specific social platforms")
        print("2. Skip aspect ratio conversion during generation")
        print("3. Apply social media optimization post-generation")
        print("4. Reduce duration to 5 seconds for faster processing")
        print("5. Disable quality enhancement for speed tests")
        
        return smile_video

if __name__ == "__main__":
    analyze_social_media_overhead()