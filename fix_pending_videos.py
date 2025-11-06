#!/usr/bin/env python3
"""
Fix pending videos by understanding the actual VEO 2 status
"""

import sys
sys.path.append('.')
import app
from app import db
from models import VideoOrder, OrderStatus
from simple_veo2_client import SimpleVEO2Client

def fix_pending_videos():
    """Analyze and fix pending video issues"""
    
    print("🔧 Analyzing pending video operations...")
    
    client = SimpleVEO2Client()
    
    # Test VEO 2 accessibility first
    print("Testing VEO 2 accessibility...")
    test_result = client.generate_video("Test prompt", 3)
    
    if not test_result.get('success'):
        print(f"❌ VEO 2 Issue: {test_result.get('error')} - {test_result.get('message')}")
        
        if test_result.get('status_code') == 404:
            print("🔍 VEO 2 model not available - need access approval")
        elif test_result.get('status_code') == 403:
            print("🔍 VEO 2 permission denied - check project settings")
            
        print("\n💡 Solutions:")
        print("1. VEO 2 requires Google Cloud approval for access")
        print("2. Operations are in pending state because VEO 2 isn't accessible")
        print("3. Need to either:")
        print("   - Request VEO 2 access from Google")
        print("   - Use VEO 3 as primary system")
        print("   - Implement fallback to working video generation")
        
        return False
    else:
        print("✅ VEO 2 is accessible")
        return True

def update_pending_orders():
    """Update pending orders based on VEO 2 accessibility"""
    
    with app.app.app_context():
        pending_orders = VideoOrder.query.filter_by(status=OrderStatus.PENDING).all()
        
        print(f"\nFound {len(pending_orders)} pending orders")
        
        # Check VEO 2 accessibility
        veo2_accessible = fix_pending_videos()
        
        if not veo2_accessible:
            print("\n🔄 Updating pending orders to use fallback system...")
            
            for order in pending_orders:
                print(f"Order {order.id}: Switching to fallback generation")
                
                # Try to generate with enhanced system (VEO 3 fallback)
                try:
                    from enhanced_video_system import create_enhanced_dreamframe_video
                    
                    result = create_enhanced_dreamframe_video(
                        image_path=order.source_image_path,
                        prompt=order.description or order.title,
                        order_id=order.id
                    )
                    
                    if result.get('success'):
                        order.status = OrderStatus.IN_PRODUCTION
                        order.veo3_operation_id = result.get('operation_id')
                        print(f"  ✅ Fallback generation started: {result.get('operation_id')}")
                    else:
                        order.status = OrderStatus.CANCELLED
                        print(f"  ❌ Fallback generation failed")
                        
                except Exception as e:
                    print(f"  ❌ Error: {e}")
                    order.status = OrderStatus.CANCELLED
            
            db.session.commit()
            print("✅ Orders updated")

if __name__ == "__main__":
    update_pending_orders()