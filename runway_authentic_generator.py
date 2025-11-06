#!/usr/bin/env python3
"""
RunwayML Authentic Video Generator - Reliable AI video generation with guaranteed downloads
"""

import os
import time
import requests
import json
from datetime import datetime
from models import VideoOrder, db
from app import app

class RunwayAuthenticGenerator:
    def __init__(self):
        self.api_key = os.environ.get('RUNWAYML_API_KEY')
        self.base_url = "https://api.dev.runwayml.com/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
            'X-Runway-Version': '2024-11-06'
        }
        
    def generate_authentic_video(self, video_id, image_path, prompt):
        """Generate authentic AI video using RunwayML Gen-3"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            print(f"🎬 Starting RunwayML Gen-3 generation for: {video.title}")
            
            # Upload image first
            image_url = self._upload_image(image_path)
            if not image_url:
                print("❌ Failed to upload image to RunwayML")
                return False
            
            # Enhanced prompt for professional results
            enhanced_prompt = f"{prompt}. Professional cinematic quality, realistic physics, natural lighting, smooth motion, high definition video with synchronized ambient audio."
            
            # Create generation request with correct Gen-3 format
            generation_data = {
                "model": "gen3a_turbo", 
                "promptImage": image_url,
                "promptText": enhanced_prompt,
                "duration": 5,
                "ratio": "1280:768",  # Landscape format supported by RunwayML
                "watermark": False
            }
            
            print("🚀 Submitting to RunwayML Gen-3...")
            response = requests.post(
                f"{self.base_url}/image_to_video",
                headers=self.headers,
                json=generation_data,
                timeout=30
            )
            
            if response.status_code == 201:
                result = response.json()
                generation_id = result.get('id')
                
                print(f"✅ RunwayML generation started: {generation_id}")
                
                # Update database
                video.veo3_operation_id = generation_id  # Reuse field for RunwayML ID
                video.status = 'IN_PRODUCTION'
                video.prompt_used = enhanced_prompt[:100]
                db.session.commit()
                
                # Start monitoring and download
                return self._monitor_and_download(video_id, generation_id)
            else:
                print(f"❌ RunwayML API error: {response.status_code} - {response.text}")
                return False
    
    def _upload_image(self, image_path):
        """Upload image to RunwayML and return URL"""
        try:
            # Convert to base64 for RunwayML API
            import base64
            with open(image_path, 'rb') as f:
                image_data = base64.b64encode(f.read()).decode('utf-8')
            
            # Get image format
            if image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg'):
                mime_type = 'image/jpeg'
            elif image_path.lower().endswith('.png'):
                mime_type = 'image/png'
            else:
                mime_type = 'image/jpeg'
            
            # Create data URL
            image_url = f"data:{mime_type};base64,{image_data}"
            print(f"✅ Image converted to base64 format for RunwayML")
            return image_url
            
        except Exception as e:
            print(f"❌ Image processing error: {e}")
            return None
    
    def _monitor_and_download(self, video_id, generation_id):
        """Monitor RunwayML generation and download when complete"""
        print(f"⏱️ Monitoring RunwayML generation: {generation_id}")
        
        max_attempts = 120  # 10 minutes with 5-second intervals
        
        for attempt in range(max_attempts):
            try:
                # Check generation status
                response = requests.get(
                    f"{self.base_url}/tasks/{generation_id}",
                    headers=self.headers,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    status = result.get('status')
                    
                    print(f"Status: {status} (attempt {attempt + 1})")
                    
                    if status == 'SUCCEEDED':
                        video_url = result.get('output', [])
                        if video_url and len(video_url) > 0:
                            download_url = video_url[0]
                            print(f"🎉 RunwayML generation completed!")
                            print(f"Download URL: {download_url}")
                            
                            # Download the video immediately
                            success = self._download_video(video_id, download_url)
                            if success:
                                print("✅ Authentic RunwayML video successfully downloaded!")
                                return True
                            else:
                                print("❌ Download failed")
                                return False
                        else:
                            print("❌ No video URL in successful response")
                            return False
                    
                    elif status == 'FAILED':
                        error_msg = result.get('failure_reason', 'Unknown error')
                        print(f"❌ RunwayML generation failed: {error_msg}")
                        return False
                    
                    elif status in ['PENDING', 'RUNNING']:
                        progress = result.get('progress', 0)
                        if attempt % 12 == 0:  # Log every minute
                            print(f"⏳ Processing... {progress}% complete")
                    
                else:
                    print(f"❌ Status check failed: {response.status_code}")
                
                time.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                print(f"⚠️ Monitoring error (attempt {attempt + 1}): {e}")
                time.sleep(5)
        
        print("❌ Monitoring timeout - generation may still be processing")
        return False
    
    def _download_video(self, video_id, download_url):
        """Download the generated video"""
        with app.app_context():
            video = VideoOrder.query.get(video_id)
            if not video:
                return False
            
            try:
                print(f"⬇️ Downloading authentic RunwayML video...")
                
                response = requests.get(download_url, timeout=300, stream=True)
                
                if response.status_code == 200:
                    timestamp = int(time.time())
                    filename = f"{video.title.lower().replace(' ', '_')}_runway_authentic_{timestamp}.mp4"
                    video_path = f"completed_videos/{filename}"
                    
                    total_bytes = 0
                    with open(video_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=32768):
                            if chunk:
                                f.write(chunk)
                                total_bytes += len(chunk)
                    
                    print(f"✅ Downloaded {total_bytes:,} bytes ({total_bytes/1024/1024:.1f} MB)")
                    
                    # Update database
                    video.generated_video_path = video_path
                    video.status = 'COMPLETED'
                    video.completed_at = datetime.now()
                    db.session.commit()
                    
                    print(f"🎉 Authentic RunwayML video ready: {video_path}")
                    return True
                else:
                    print(f"❌ Download failed: HTTP {response.status_code}")
                    return False
                    
            except Exception as e:
                print(f"❌ Download error: {e}")
                return False

def generate_flag_video():
    """Generate authentic flag video using RunwayML"""
    generator = RunwayAuthenticGenerator()
    
    flag_prompt = """A beautiful flag waving gracefully in natural wind. The flag displays realistic fabric physics with natural ripples, waves, and flowing motion. Mounted on a flagpole, the flag flutters naturally with smooth, elegant movement. Professional cinematic quality with natural outdoor lighting and realistic wind effects."""
    
    print("🎬 RUNWAYML AUTHENTIC VIDEO GENERATION")
    print("This will create real AI-generated content using your uploaded flag image")
    
    success = generator.generate_authentic_video(
        video_id=5,
        image_path="uploads/2_1754017939_IMG_7008.jpeg",
        prompt=flag_prompt
    )
    
    if success:
        print("🎉 SUCCESS! Authentic RunwayML video generated and downloaded")
    else:
        print("❌ Failed to generate authentic video")
    
    return success

if __name__ == "__main__":
    generate_flag_video()