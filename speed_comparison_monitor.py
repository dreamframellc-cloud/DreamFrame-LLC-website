#!/usr/bin/env python3
"""
Monitor speed comparison between social media optimized and general videos
"""

from datetime import datetime
from models import VideoOrder, OrderStatus
from app import app

def monitor_speed_comparison():
    """Compare processing times between different video types"""
    
    with app.app_context():
        print("⚡ SPEED COMPARISON ANALYSIS")
        print("=" * 40)
        
        # Get recent videos for comparison
        recent_videos = VideoOrder.query.order_by(VideoOrder.created_at.desc()).limit(5).all()
        
        comparisons = []
        
        for video in recent_videos:
            elapsed = 0
            if video.created_at:
                if video.completed_at:
                    elapsed = (video.completed_at - video.created_at).total_seconds() / 60
                else:
                    elapsed = (datetime.utcnow() - video.created_at).total_seconds() / 60
            
            platform_type = "Social Media" if video.platform in ['instagram', 'tiktok', 'youtube_shorts'] else "General"
            
            comparison = {
                'title': video.title,
                'platform': video.platform,
                'type': platform_type,
                'elapsed': elapsed,
                'status': video.status.value if hasattr(video.status, 'value') else str(video.status),
                'operation_id': getattr(video, 'veo3_operation_id', None) is not None
            }
            comparisons.append(comparison)
        
        print("📊 PROCESSING TIME COMPARISON:")
        print()
        
        social_times = []
        general_times = []
        
        for comp in comparisons:
            status_icon = "✅" if comp['status'] == 'completed' else "⏳" if comp['status'] == 'in_production' else "❌"
            op_icon = "🔄" if comp['operation_id'] else "⚠️"
            
            print(f"{status_icon} {comp['title']}")
            print(f"   Platform: {comp['platform']} ({comp['type']})")
            print(f"   Time: {comp['elapsed']:.1f} minutes {op_icon}")
            print()
            
            if comp['status'] == 'completed':
                if comp['type'] == 'Social Media':
                    social_times.append(comp['elapsed'])
                else:
                    general_times.append(comp['elapsed'])
        
        # Calculate averages
        if social_times:
            avg_social = sum(social_times) / len(social_times)
            print(f"📱 Social Media Average: {avg_social:.1f} minutes")
        
        if general_times:
            avg_general = sum(general_times) / len(general_times)
            print(f"⚡ General Platform Average: {avg_general:.1f} minutes")
        
        # Current status
        smile_video = next((v for v in recent_videos if v.title == "Smile"), None)
        speed_test = next((v for v in recent_videos if v.title == "Speed Test"), None)
        
        if smile_video:
            smile_elapsed = (datetime.utcnow() - smile_video.created_at).total_seconds() / 60
            print(f"\n📱 Current Smile (Instagram): {smile_elapsed:.1f} minutes")
        
        if speed_test:
            speed_elapsed = (datetime.utcnow() - speed_test.created_at).total_seconds() / 60
            print(f"⚡ Current Speed Test (General): {speed_elapsed:.1f} minutes")
        
        print(f"\n💡 HYPOTHESIS TEST:")
        print(f"   Social media optimization adds 2-4 minutes overhead")
        print(f"   General platform should complete in 2-3 minutes")

if __name__ == "__main__":
    monitor_speed_comparison()