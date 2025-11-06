#!/usr/bin/env python3
"""
Video Status Monitor for DreamFrame
Checks and updates pending video operations
"""

import os
import sys
import time
from simple_veo2_client import SimpleVEO2Client

# Add app context
sys.path.append('.')
import app
from app import db
from models import VideoOrder, OrderStatus

def monitor_pending_videos():
    """Monitor and update pending video operations"""
    
    print("🔍 Monitoring pending video operations...")
    
    client = SimpleVEO2Client()
    if not client.credentials:
        print("❌ VEO 2 credentials not available")
        return
    
    with app.app.app_context():
        # Get pending orders
        pending_orders = VideoOrder.query.filter_by(status=OrderStatus.PENDING).all()
        
        print(f"Found {len(pending_orders)} pending orders")
        
        for order in pending_orders:
            if not order.veo3_operation_id:
                print(f"Order {order.id}: No operation ID")
                continue
                
            operation_id = order.veo3_operation_id
            print(f"\nChecking Order {order.id} - Operation {operation_id}")
            
            try:
                status = client.check_operation_status(operation_id)
                
                if status.get('status') == 'completed':
                    print(f"✅ Order {order.id}: Completed!")
                    
                    # Update order status
                    order.status = OrderStatus.COMPLETED
                    
                    # Set video path (VEO 2 would provide download URL)
                    video_filename = f"veo2_customer_{order.id}.mp4"
                    video_path = f"completed_videos/{video_filename}"
                    order.generated_video_path = video_path
                    
                    db.session.commit()
                    print(f"   Updated database for order {order.id}")
                    
                elif status.get('status') == 'processing':
                    print(f"⏳ Order {order.id}: Still processing...")
                    
                    # Update to in_production if still pending
                    if order.status == OrderStatus.PENDING:
                        order.status = OrderStatus.IN_PRODUCTION
                        db.session.commit()
                        
                elif status.get('status') == 'failed':
                    print(f"❌ Order {order.id}: Failed")
                    error_msg = status.get('error', 'Unknown error')
                    print(f"   Error: {error_msg}")
                    
                    order.status = OrderStatus.CANCELLED
                    db.session.commit()
                    
                else:
                    print(f"❓ Order {order.id}: Unknown status - {status}")
                    
            except Exception as e:
                print(f"❌ Error checking order {order.id}: {e}")
        
        print("\n📊 Monitoring complete")

if __name__ == "__main__":
    monitor_pending_videos()