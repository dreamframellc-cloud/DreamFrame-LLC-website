#!/usr/bin/env python3
"""
AI Video Manager Bot
Intelligent process management for video generation
"""

import os
import time
import threading
import requests
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from models import VideoOrder, db
# Lazy import to avoid circular dependency - app will be imported when needed

class AIVideoManager:
    """AI bot that manages the entire video generation process"""
    
    def __init__(self):
        self.active = True
        self.monitoring_interval = 30  # Check every 30 seconds
        self.max_generation_time = 600  # 10 minutes max
        print("🤖 AI Video Manager Bot initialized")
        print("📊 Managing all video generation processes")
        print("⚡ Monitoring for speed optimization opportunities")
    
    def start_management(self):
        """Start the AI management system"""
        print("🚀 AI Video Manager starting active management")
        
        # Start monitoring thread
        management_thread = threading.Thread(target=self._management_loop, daemon=True)
        management_thread.start()
        
        # Start optimization analysis
        optimization_thread = threading.Thread(target=self._optimization_analysis, daemon=True)
        optimization_thread.start()
        
        print("✅ AI Video Manager is now actively managing all processes")
    
    def _management_loop(self):
        """Main AI management loop"""
        while self.active:
            try:
                # Lazy import to avoid circular dependency
                from app import app
                with app.app_context():
                    # Check all active video orders
                    active_videos = VideoOrder.query.filter_by(status='IN_PRODUCTION').all()
                    
                    for video in active_videos:
                        self._manage_video_generation(video)
                    
                    # Look for optimization opportunities
                    self._analyze_performance()
                    
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"🤖 AI Manager error: {str(e)}")
                time.sleep(60)  # Wait longer on error
    
    def _manage_video_generation(self, video: VideoOrder):
        """Manage individual video generation process"""
        try:
            # Calculate elapsed time
            elapsed = datetime.utcnow() - video.created_at
            elapsed_minutes = elapsed.total_seconds() / 60
            
            print(f"🤖 Managing: {video.title} ({elapsed_minutes:.1f}min elapsed)")
            
            # Check if video should be completed by now
            if elapsed_minutes > 8:  # After 8 minutes, aggressive checking
                print(f"⏰ {video.title} taking longer than expected, checking status...")
                self._check_video_status(video)
            elif elapsed_minutes > 5:  # After 5 minutes, regular checking
                print(f"⏱️ {video.title} at {elapsed_minutes:.1f}min, monitoring...")
                self._check_video_status(video)
            
            # Timeout protection
            if elapsed_minutes > self.max_generation_time / 60:
                print(f"⚠️ {video.title} exceeded maximum time, investigating...")
                self._handle_timeout(video)
                
        except Exception as e:
            print(f"🤖 Video management error for {video.title}: {str(e)}")
    
    def _check_video_status(self, video: VideoOrder):
        """Check status of video operation - DISABLED DUE TO 404 ERRORS"""
        # Temporarily disabled due to API endpoint 404 issues
        return
    
    def _process_completed_video(self, video: VideoOrder, operation_data: dict):
        """Process completed video automatically"""
        try:
            print(f"🎬 AI processing completed video: {video.title}")
            
            # Extract video URL from operation result
            video_url = None
            video_data = None
            
            if 'response' in operation_data:
                response_data = operation_data['response']
                
                # Look for video content in various possible locations
                if 'candidates' in response_data:
                    for candidate in response_data['candidates']:
                        if 'content' in candidate:
                            parts = candidate['content'].get('parts', [])
                            for part in parts:
                                # Check for video metadata or URL
                                if 'video_metadata' in part:
                                    video_url = part.get('video_url')
                                elif 'file_data' in part:
                                    video_data = part['file_data']
                                elif 'inline_data' in part:
                                    video_data = part['inline_data']
            
            if video_url:
                print(f"📥 Downloading video from URL: {video_url}")
                self._download_video(video, video_url)
            elif video_data:
                print(f"💾 Processing embedded video data")
                self._save_video_data(video, video_data)
            else:
                print(f"⚠️ No video content found in response for {video.title}")
                self._mark_video_error(video, "No video content in response")
                
        except Exception as e:
            print(f"🤖 Video processing error for {video.title}: {str(e)}")
            self._mark_video_error(video, str(e))
    
    def _download_video(self, video: VideoOrder, video_url: str):
        """Download completed video"""
        try:
            print(f"⬇️ AI downloading: {video.title}")
            
            response = requests.get(video_url, timeout=120)
            
            if response.status_code == 200:
                # Generate filename
                timestamp = int(time.time())
                filename = f"{video.title.lower().replace(' ', '_')}_{timestamp}.mp4"
                filepath = os.path.join('completed_videos', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save video
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                file_size = len(response.content) / (1024 * 1024)  # MB
                print(f"✅ {video.title} saved: {filename} ({file_size:.1f}MB)")
                
                # Update database
                self._mark_video_completed(video, filepath)
                
                # Send completion notification
                self._notify_completion(video, filepath, file_size)
                
            else:
                print(f"❌ Download failed for {video.title}: {response.status_code}")
                self._mark_video_error(video, f"Download failed: {response.status_code}")
                
        except Exception as e:
            print(f"🤖 Download error for {video.title}: {str(e)}")
            self._mark_video_error(video, f"Download error: {str(e)}")
    
    def _save_video_data(self, video: VideoOrder, video_data: dict):
        """Save embedded video data"""
        try:
            import base64
            
            # Decode video data
            if 'data' in video_data:
                video_bytes = base64.b64decode(video_data['data'])
                
                # Generate filename
                timestamp = int(time.time())
                filename = f"{video.title.lower().replace(' ', '_')}_{timestamp}.mp4"
                filepath = os.path.join('completed_videos', filename)
                
                # Ensure directory exists
                os.makedirs(os.path.dirname(filepath), exist_ok=True)
                
                # Save video
                with open(filepath, 'wb') as f:
                    f.write(video_bytes)
                
                file_size = len(video_bytes) / (1024 * 1024)  # MB
                print(f"✅ {video.title} saved from data: {filename} ({file_size:.1f}MB)")
                
                # Update database
                self._mark_video_completed(video, filepath)
                
                # Send completion notification
                self._notify_completion(video, filepath, file_size)
            else:
                print(f"⚠️ No video data found for {video.title}")
                self._mark_video_error(video, "No video data found")
                
        except Exception as e:
            print(f"🤖 Video data save error for {video.title}: {str(e)}")
            self._mark_video_error(video, f"Data save error: {str(e)}")
    
    def _mark_video_completed(self, video: VideoOrder, filepath: str):
        """Mark video as completed in database"""
        try:
            video.status = 'COMPLETED'
            video.generated_video_path = filepath
            video.completed_at = datetime.utcnow()
            
            # Calculate generation time
            generation_time = video.completed_at - video.created_at
            video.generation_settings = f"AI managed completion in {generation_time}"
            
            db.session.commit()
            
            print(f"📊 {video.title} marked as completed in database")
            
        except Exception as e:
            print(f"🤖 Database update error for {video.title}: {str(e)}")
    
    def _mark_video_error(self, video: VideoOrder, error_message: str):
        """Mark video as failed"""
        try:
            video.status = 'FAILED'
            video.error_message = error_message
            video.completed_at = datetime.utcnow()
            
            db.session.commit()
            
            print(f"❌ {video.title} marked as failed: {error_message}")
            
        except Exception as e:
            print(f"🤖 Error marking failure for {video.title}: {str(e)}")
    
    def _notify_completion(self, video: VideoOrder, filepath: str, file_size: float):
        """Send completion notification"""
        try:
            generation_time = video.completed_at - video.created_at
            minutes = generation_time.total_seconds() / 60
            
            print(f"🎉 AI COMPLETION NOTIFICATION")
            print(f"📹 Video: {video.title}")
            print(f"📁 File: {filepath}")
            print(f"📊 Size: {file_size:.1f}MB")
            print(f"⏱️ Generation Time: {minutes:.1f} minutes")
            print(f"🤖 AI managed end-to-end process")
            
            # Send SMS notification
            try:
                from send_message import send_twilio_message
                message = f"🎬 DreamFrame Video Complete!\n\n'{video.title}' has finished generating in {minutes:.1f} minutes.\n\nYour professional VEO 3 video is ready to view in your dashboard.\n\n- Size: {file_size:.1f}MB\n- Generation Time: {minutes:.1f} min\n- Quality: Professional VEO 3\n- Status: Ready for download"
                
                # Send notification (replace with actual phone number)
                phone_number = "+1234567890"  # Update with real number when provided
                send_twilio_message(phone_number, message)
                print(f"📱 SMS completion notification sent!")
                
            except Exception as e:
                print(f"📱 SMS notification failed: {e}")
            
        except Exception as e:
            print(f"🤖 Notification error: {str(e)}")
    
    def _handle_timeout(self, video: VideoOrder):
        """Handle video generation timeout"""
        try:
            print(f"⏰ Handling timeout for {video.title}")
            
            # Mark as timed out but check one more time
            self._check_video_status(video)
            
            # If still not done, mark as failed
            if video.status == 'IN_PRODUCTION':
                self._mark_video_error(video, "Generation timeout exceeded")
                
        except Exception as e:
            print(f"🤖 Timeout handling error: {str(e)}")
    
    def _optimization_analysis(self):
        """Analyze performance for optimization opportunities"""
        while self.active:
            try:
                time.sleep(300)  # Run every 5 minutes
                
                # Lazy import to avoid circular dependency
                from app import app
                with app.app_context():
                    # Analyze recent completions
                    recent_videos = VideoOrder.query.filter(
                        VideoOrder.completed_at > datetime.utcnow() - timedelta(hours=1)
                    ).all()
                    
                    if recent_videos:
                        avg_time = sum([
                            (v.completed_at - v.created_at).total_seconds() / 60 
                            for v in recent_videos if v.completed_at
                        ]) / len(recent_videos)
                        
                        print(f"📊 AI Performance Analysis:")
                        print(f"🎯 Recent videos: {len(recent_videos)}")
                        print(f"⏱️ Average time: {avg_time:.1f} minutes")
                        
                        if avg_time > 5:
                            print("⚡ Optimization opportunity detected")
                            print("💡 Consider implementing speed optimizations")
                        elif avg_time <= 3:
                            print("🏆 Excellent performance - beating Kling AI!")
                            
            except Exception as e:
                print(f"🤖 Analysis error: {str(e)}")
    
    def _analyze_performance(self):
        """Quick performance check during management loop"""
        try:
            # Count active generations
            active_count = VideoOrder.query.filter_by(status='IN_PRODUCTION').count()
            
            if active_count > 0:
                print(f"🤖 AI managing {active_count} active video generation(s)")
                
        except Exception as e:
            print(f"🤖 Performance check error: {str(e)}")

# No module-level instantiation - will be created lazily in app.py
# This avoids circular import issues and Flask application context errors

if __name__ == "__main__":
    print("🤖 Starting AI Video Manager...")
    manager = AIVideoManager()
    manager.start_management()
    # Keep running
    try:
        while True:
            time.sleep(60)
            print("🤖 AI Video Manager running...")
    except KeyboardInterrupt:
        print("🤖 Stopping AI Video Manager...")
        manager.active = False
        print("🤖 AI Video Manager stopped")