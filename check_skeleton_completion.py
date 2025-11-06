"""
Check if skeleton video completed in completed_videos folder
Sometimes videos complete despite 404 status check errors
"""

import os
import glob
from datetime import datetime

def check_skeleton_completion():
    print("🔍 Checking for Skeleton Video Completion")
    print("=" * 45)
    
    # Check completed_videos folder for new files
    completed_dir = "completed_videos"
    
    if not os.path.exists(completed_dir):
        print(f"❌ {completed_dir} directory not found")
        return False
    
    # Get all MP4 files
    mp4_files = glob.glob(os.path.join(completed_dir, "*.mp4"))
    
    print(f"📁 Found {len(mp4_files)} MP4 files in {completed_dir}")
    
    # Check for recent files (last 2 hours)
    recent_files = []
    skeleton_files = []
    
    for file_path in mp4_files:
        file_name = os.path.basename(file_path)
        file_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(file_time)
        
        # Check if file was modified in last 2 hours
        time_diff = datetime.now() - file_date
        hours_ago = time_diff.total_seconds() / 3600
        
        if hours_ago <= 2:
            recent_files.append((file_name, file_date, hours_ago))
        
        # Check for skeleton-related files
        if 'skeleton' in file_name.lower():
            skeleton_files.append((file_name, file_date, hours_ago))
    
    print(f"\n📅 Files modified in last 2 hours:")
    if recent_files:
        for file_name, file_date, hours_ago in recent_files:
            print(f"  - {file_name} ({hours_ago:.1f}h ago)")
    else:
        print("  No recent files found")
    
    print(f"\n💀 Skeleton-related files:")
    if skeleton_files:
        for file_name, file_date, hours_ago in skeleton_files:
            print(f"  - {file_name} ({hours_ago:.1f}h ago)")
            if hours_ago <= 1:
                print("    🎉 RECENT SKELETON VIDEO FOUND!")
                return True
    else:
        print("  No skeleton files found")
    
    # Check newest 5 files
    print(f"\n📋 5 Most Recent Files:")
    sorted_files = sorted(mp4_files, key=os.path.getmtime, reverse=True)[:5]
    
    for file_path in sorted_files:
        file_name = os.path.basename(file_path)
        file_time = os.path.getmtime(file_path)
        file_date = datetime.fromtimestamp(file_time)
        file_size = os.path.getsize(file_path)
        
        print(f"  - {file_name}")
        print(f"    Size: {file_size:,} bytes")
        print(f"    Modified: {file_date.strftime('%Y-%m-%d %H:%M:%S')}")
    
    return len(skeleton_files) > 0

def check_database_skeleton_status():
    """Check database for skeleton video status"""
    try:
        from app import app, db
        from models import VideoOrder, OrderStatus
        
        with app.app_context():
            print(f"\n🗄️  DATABASE STATUS CHECK:")
            print("=" * 30)
            
            skeleton_video = VideoOrder.query.filter_by(title='Skeleton').order_by(VideoOrder.id.desc()).first()
            
            if skeleton_video:
                elapsed = datetime.utcnow() - skeleton_video.created_at
                elapsed_minutes = elapsed.total_seconds() / 60
                
                print(f"📊 Video: {skeleton_video.title} (ID: {skeleton_video.id})")
                print(f"📈 Status: {skeleton_video.status.value.upper()}")
                print(f"⏱️  Elapsed: {elapsed_minutes:.1f} minutes")
                
                if skeleton_video.veo3_operation_id:
                    op_short = skeleton_video.veo3_operation_id.split('/')[-1][:8]
                    print(f"🔄 Operation: {op_short}...")
                
                # Check if it should be marked as completed
                if skeleton_video.status == OrderStatus.IN_PRODUCTION and elapsed_minutes > 10:
                    print(f"⚠️  Video running for {elapsed_minutes:.1f} minutes - may need status update")
                
                return skeleton_video
            else:
                print("❌ No skeleton video found in database")
                return None
                
    except Exception as e:
        print(f"❌ Database check error: {e}")
        return None

if __name__ == "__main__":
    # Check both file system and database
    file_found = check_skeleton_completion()
    db_status = check_database_skeleton_status()
    
    print(f"\n📋 SUMMARY:")
    print(f"📁 File system: {'✅ Recent skeleton video found' if file_found else '❌ No recent skeleton videos'}")
    print(f"🗄️  Database: {'✅ Skeleton video tracked' if db_status else '❌ No skeleton video in database'}")
    
    if not file_found and db_status and db_status.status.value == 'in_production':
        print(f"\n💡 RECOMMENDATION:")
        print(f"Video may still be processing in VEO 3 despite 404 status check errors.")
        print(f"This is a known issue with Google's VEO 3 API reliability.")
        print(f"Monitor the completed_videos folder for automatic completion.")