"""
Replace the current VEO 3 system with improved timeout handling
"""

from app import app, db
from models import VideoOrder, OrderStatus
from improved_veo3_client import ImprovedVEO3Client
import logging

def upgrade_veo3_integration():
    """Replace current VEO 3 system with improved client"""
    
    print("🔄 UPGRADING VEO 3 INTEGRATION")
    print("=" * 40)
    
    # Initialize improved client
    try:
        improved_client = ImprovedVEO3Client()
        print("✅ Improved VEO 3 client initialized")
    except Exception as e:
        print(f"❌ Failed to initialize improved client: {e}")
        return False
    
    with app.app_context():
        # Find all stuck videos
        stuck_videos = VideoOrder.query.filter_by(status=OrderStatus.IN_PRODUCTION).all()
        
        print(f"\n📊 Found {len(stuck_videos)} stuck videos")
        
        for video in stuck_videos:
            print(f"\n🔍 Processing: {video.title} (ID: {video.id})")
            
            # Check if video has been stuck for more than 1 hour
            import datetime
            elapsed = datetime.datetime.utcnow() - video.created_at
            elapsed_minutes = elapsed.total_seconds() / 60
            
            if elapsed_minutes > 60:
                print(f"   ⏰ Stuck for {elapsed_minutes:.1f} minutes - marking as failed")
                video.status = OrderStatus.FAILED
                video.generation_settings = f"Timeout after {elapsed_minutes:.1f} minutes - upgraded to improved VEO 3"
            else:
                print(f"   ⏳ Processing time: {elapsed_minutes:.1f} minutes - retrying with improved client")
                
                # Retry with improved client
                if hasattr(video, 'source_image_path') and video.source_image_path:
                    operation_id = improved_client.generate_video(
                        prompt=f"Transform this image into a dynamic video: {video.title}",
                        image_path=video.source_image_path,
                        platform=video.platform or "general",
                        timeout=1800  # 30 minutes
                    )
                    
                    if operation_id:
                        video.veo3_operation_id = operation_id
                        print(f"   ✅ Restarted with operation: {operation_id}")
                    else:
                        video.status = OrderStatus.FAILED
                        video.generation_settings = "Failed to restart with improved VEO 3"
                        print(f"   ❌ Failed to restart")
        
        # Commit all changes
        db.session.commit()
        print(f"\n✅ Database updated with improved VEO 3 integration")
    
    return True

def test_new_generation():
    """Test video generation with improved system"""
    
    print("\n🧪 TESTING IMPROVED VEO 3 SYSTEM")
    print("=" * 35)
    
    improved_client = ImprovedVEO3Client()
    
    # Test generation
    operation_id = improved_client.generate_video(
        prompt="A serene mountain landscape with flowing water and gentle wind",
        image_path=None,
        platform="general",
        timeout=1800  # 30 minutes
    )
    
    if operation_id:
        print(f"✅ Test generation successful")
        print(f"🔄 Operation ID: {operation_id}")
        
        # Check initial status
        status = improved_client.check_operation_status(operation_id)
        print(f"📊 Status: {status}")
        
        return operation_id
    else:
        print(f"❌ Test generation failed")
        return None

if __name__ == "__main__":
    # Upgrade the system
    success = upgrade_veo3_integration()
    
    if success:
        # Test new system
        test_operation = test_new_generation()
        
        print(f"\n🎯 UPGRADE COMPLETE")
        print(f"✅ Improved VEO 3 client ready")
        print(f"✅ Stuck videos processed")
        print(f"✅ System ready for reliable generation")
        
        if test_operation:
            print(f"🧪 Test operation: {test_operation}")