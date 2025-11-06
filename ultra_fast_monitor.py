#!/usr/bin/env python3
"""
Ultra-Fast VEO 3 Monitor
Aggressive monitoring system to ensure 5-minute completion times
"""

import time
import requests
import json
from datetime import datetime
from ultra_fast_veo3 import ultra_fast_veo3
from models import VideoOrder, db
from app import app

def check_active_generations():
    """Check all active video generations and their status"""
    with app.app_context():
        # Get all generating videos
        generating_videos = VideoOrder.query.filter_by(status='IN_PRODUCTION').all()
        
        print(f"🔍 Checking {len(generating_videos)} active generations...")
        
        for video in generating_videos:
            elapsed_minutes = (datetime.now() - video.created_at).total_seconds() / 60
            
            print(f"\n📹 Video: {video.title}")
            print(f"⏱️  Elapsed: {elapsed_minutes:.1f} minutes")
            print(f"🔄 Operation: {video.veo3_operation_id}")
            
            # Check if it's taking too long (over 6 minutes)
            if elapsed_minutes > 6:
                print(f"⚠️  WARNING: Video taking longer than expected!")
                
                # Check status one more time
                if video.veo3_operation_id:
                    status = ultra_fast_veo3.check_operation_status(video.veo3_operation_id)
                    if status and status.get('done'):
                        print(f"✅ Actually completed! Updating status...")
                        # Update video status
                        video.status = 'COMPLETED'
                        if 'response' in status and 'generatedVideo' in status['response']:
                            video.download_url = status['response']['generatedVideo']['uri']
                        db.session.commit()
                    else:
                        print(f"❌ Still processing after {elapsed_minutes:.1f} minutes")
            
            elif elapsed_minutes > 3:
                print(f"⏳ Processing longer than 3 minutes - checking status...")
                if video.veo3_operation_id:
                    status = ultra_fast_veo3.check_operation_status(video.veo3_operation_id)
                    if status and status.get('done'):
                        print(f"✅ Completed! Processing took {elapsed_minutes:.1f} minutes")
                        video.status = 'COMPLETED'
                        if 'response' in status and 'generatedVideo' in status['response']:
                            video.download_url = status['response']['generatedVideo']['uri']
                        db.session.commit()
                        
                        # Log successful completion time
                        with open('completion_times.log', 'a') as f:
                            f.write(f"{datetime.now()}: {video.title} completed in {elapsed_minutes:.1f} minutes\n")
            else:
                print(f"✅ Within target time - continue monitoring")

def monitor_completion_times():
    """Monitor and log completion times to optimize parameters"""
    print("🚀 Ultra-Fast VEO 3 Monitor Starting...")
    print("🎯 Target: 5-minute completion times")
    
    while True:
        try:
            check_active_generations()
            print(f"\n⏰ Next check in 30 seconds...")
            time.sleep(30)  # Check every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Monitor stopped")
            break
        except Exception as e:
            print(f"❌ Monitor error: {str(e)}")
            time.sleep(60)  # Wait longer on error

if __name__ == "__main__":
    monitor_completion_times()