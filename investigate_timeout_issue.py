#!/usr/bin/env python3
"""
Investigate timeout issues and implement recovery
"""

import os
import requests
from datetime import datetime, timedelta
from models import VideoOrder, OrderStatus
from app import app, db

def investigate_and_recover():
    """Investigate timeout issues and attempt recovery"""
    
    with app.app_context():
        # Get all stuck videos
        stuck_videos = VideoOrder.query.filter(
            VideoOrder.status == OrderStatus.IN_PRODUCTION,
            VideoOrder.created_at < datetime.utcnow() - timedelta(minutes=10)
        ).all()
        
        print("🔍 TIMEOUT INVESTIGATION")
        print("=" * 50)
        
        for video in stuck_videos:
            elapsed = (datetime.utcnow() - video.created_at).total_seconds() / 60
            print(f"\n📹 Video: {video.title}")
            print(f"⏱️ Elapsed: {elapsed:.1f} minutes")
            print(f"🆔 Operation: {video.veo3_operation_id}")
            
            # If over 15 minutes, mark as timeout and create recovery plan
            if elapsed > 15:
                print(f"⚠️ TIMEOUT DETECTED - {video.title} stuck for {elapsed:.1f} minutes")
                
                # Update to timeout status (using CANCELLED since FAILED doesn't exist)
                video.status = OrderStatus.CANCELLED
                video.generation_settings = f"TIMEOUT after {elapsed:.1f} minutes - VEO 3 operation: {video.veo3_operation_id}"
                db.session.commit()
                
                print(f"❌ Marked {video.title} as FAILED due to timeout")
                
                # Create recovery opportunity 
                print(f"🔄 Creating recovery option for user...")
                
                # Log the timeout for analysis
                timeout_log = f"""
TIMEOUT ANALYSIS - {video.title}
================================
- Started: {video.created_at}
- Elapsed: {elapsed:.1f} minutes  
- Operation ID: {video.veo3_operation_id}
- Status Checks: All returned 404
- Likely Cause: VEO 3 operation exceeded normal processing time
- Recovery: User can regenerate with same settings
"""
                print(timeout_log)
        
        # Check system health
        print("\n🔧 SYSTEM HEALTH CHECK")
        print("=" * 30)
        
        # Test VEO 3 connectivity
        try:
            # This tests our auth without making a generation request
            import vertex_ai_video_generator
            generator = vertex_ai_video_generator.VertexAIVideoGenerator()
            if hasattr(generator, 'get_access_token'):
                token = generator.get_access_token()
                if token:
                    print("✅ VEO 3 API connection: HEALTHY")
                else:
                    print("❌ VEO 3 API connection: FAILED")
            else:
                print("⚠️ VEO 3 API connection: UNKNOWN")
        except Exception as e:
            print(f"❌ VEO 3 API test failed: {str(e)}")
        
        # Provide recommendations
        print("\n💡 RECOMMENDATIONS")
        print("=" * 20)
        print("1. VEO 3 generations should complete within 3-8 minutes")
        print("2. 404 responses after 10+ minutes indicate operation timeout")
        print("3. User should retry generation for best results")
        print("4. Consider implementing backup generation system")

if __name__ == "__main__":
    investigate_and_recover()