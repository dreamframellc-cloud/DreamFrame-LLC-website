#!/usr/bin/env python3
"""
Stop AI Manager - Clean up failed monitoring processes
"""

from models import VideoOrder, db, OrderStatus
from app import app
from datetime import datetime

def stop_failed_monitoring():
    """Stop the AI manager from monitoring failed operations"""
    
    with app.app_context():
        # Update all stuck videos to failed status
        stuck_videos = VideoOrder.query.filter(
            VideoOrder.status == 'in_production',
            VideoOrder.veo3_operation_id.isnot(None)
        ).all()
        
        print(f"Found {len(stuck_videos)} stuck videos to clean up")
        
        for video in stuck_videos:
            if video.veo3_operation_id and ('27e7cf8f-5d2b-4304-9865-d05d046198ce' in video.veo3_operation_id or 
                                             'af5054c0-2907-4274-9336-e8706954af94' in video.veo3_operation_id):
                print(f"Marking video {video.id} as failed: {video.title}")
                
                video.status = 'cancelled'
                video.error_message = "VEO 3 operation timed out - cleaned up by fixed system"
                video.completed_at = datetime.utcnow()
        
        db.session.commit()
        print("✅ Cleaned up stuck video monitoring")

if __name__ == "__main__":
    stop_failed_monitoring()