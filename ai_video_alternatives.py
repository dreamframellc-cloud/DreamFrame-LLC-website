#!/usr/bin/env python3
"""
AI Video Generation Alternatives - Reliable services for authentic AI video generation
"""

import requests
import json
import os
from datetime import datetime
from models import VideoOrder, db
from app import app

class AIVideoAlternatives:
    def __init__(self):
        self.services = {
            'runwayml': {
                'name': 'RunwayML Gen-3',
                'api_base': 'https://api.runwayml.com/v1',
                'supports_image_to_video': True,
                'reliable_download': True,
                'max_duration': 10,
                'quality': 'High'
            },
            'stability': {
                'name': 'Stability AI Video',
                'api_base': 'https://api.stability.ai/v2beta',
                'supports_image_to_video': True,
                'reliable_download': True,
                'max_duration': 4,
                'quality': 'High'
            },
            'pika': {
                'name': 'Pika Labs',
                'api_base': 'https://api.pika.art/v1',
                'supports_image_to_video': True,
                'reliable_download': True,
                'max_duration': 3,
                'quality': 'High'
            },
            'luma': {
                'name': 'Luma Dream Machine',
                'api_base': 'https://api.lumalabs.ai/dream-machine/v1',
                'supports_image_to_video': True,
                'reliable_download': True,
                'max_duration': 5,
                'quality': 'High'
            }
        }
    
    def generate_with_runwayml(self, image_path, prompt):
        """Generate video using RunwayML Gen-3 (more reliable than VEO 3)"""
        api_key = os.environ.get('RUNWAYML_API_KEY')
        if not api_key:
            return {'error': 'RUNWAYML_API_KEY not found', 'needs_key': True}
        
        print("🎬 Generating with RunwayML Gen-3...")
        
        # Upload image
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
        
        # Create image-to-video generation
        generation_data = {
            'model': 'gen3a_turbo',
            'prompt': prompt,
            'image': image_data.hex(),  # Convert to hex for API
            'duration': 5,
            'resolution': '1280x720',
            'motion_bucket_id': 127,
            'fps': 24
        }
        
        try:
            response = requests.post(
                f"{self.services['runwayml']['api_base']}/image_to_video",
                headers=headers,
                json=generation_data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'generation_id': result.get('id'),
                    'status': result.get('status'),
                    'service': 'runwayml'
                }
            else:
                return {'error': f'RunwayML API error: {response.status_code}', 'response': response.text}
                
        except Exception as e:
            return {'error': f'RunwayML request failed: {e}'}
    
    def generate_with_stability(self, image_path, prompt):
        """Generate video using Stability AI Video"""
        api_key = os.environ.get('STABILITY_API_KEY')
        if not api_key:
            return {'error': 'STABILITY_API_KEY not found', 'needs_key': True}
        
        print("🎨 Generating with Stability AI Video...")
        
        headers = {
            'Authorization': f'Bearer {api_key}',
        }
        
        # Prepare files
        files = {
            'image': open(image_path, 'rb'),
        }
        
        data = {
            'seed': 0,
            'cfg_scale': 1.8,
            'motion_bucket_id': 127,
            'prompt': prompt
        }
        
        try:
            response = requests.post(
                f"{self.services['stability']['api_base']}/image-to-video",
                headers=headers,
                files=files,
                data=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'generation_id': result.get('id'),
                    'status': 'processing',
                    'service': 'stability'
                }
            else:
                return {'error': f'Stability API error: {response.status_code}', 'response': response.text}
                
        except Exception as e:
            return {'error': f'Stability request failed: {e}'}
        finally:
            files['image'].close()
    
    def check_generation_status(self, service, generation_id):
        """Check generation status for any service"""
        if service == 'runwayml':
            return self._check_runwayml_status(generation_id)
        elif service == 'stability':
            return self._check_stability_status(generation_id)
        else:
            return {'error': f'Unknown service: {service}'}
    
    def _check_runwayml_status(self, generation_id):
        """Check RunwayML generation status"""
        api_key = os.environ.get('RUNWAYML_API_KEY')
        if not api_key:
            return {'error': 'RUNWAYML_API_KEY not found'}
        
        headers = {'Authorization': f'Bearer {api_key}'}
        
        try:
            response = requests.get(
                f"{self.services['runwayml']['api_base']}/tasks/{generation_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': result.get('status'),
                    'progress': result.get('progress', 0),
                    'video_url': result.get('output', [{}])[0].get('url') if result.get('status') == 'SUCCEEDED' else None
                }
            else:
                return {'error': f'Status check failed: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'Status check error: {e}'}
    
    def _check_stability_status(self, generation_id):
        """Check Stability AI generation status"""
        api_key = os.environ.get('STABILITY_API_KEY')
        if not api_key:
            return {'error': 'STABILITY_API_KEY not found'}
        
        headers = {'Authorization': f'Bearer {api_key}'}
        
        try:
            response = requests.get(
                f"{self.services['stability']['api_base']}/image-to-video/result/{generation_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'status': 'completed' if result.get('video') else 'processing',
                    'video_url': result.get('video')
                }
            elif response.status_code == 202:
                return {'status': 'processing'}
            else:
                return {'error': f'Status check failed: {response.status_code}'}
                
        except Exception as e:
            return {'error': f'Status check error: {e}'}
    
    def download_video(self, video_url, output_path):
        """Download video from URL with reliable error handling"""
        try:
            print(f"Downloading video from: {video_url}")
            
            headers = {
                'User-Agent': 'DreamFrame-AIVideo-Client/1.0'
            }
            
            response = requests.get(video_url, headers=headers, stream=True, timeout=120)
            
            if response.status_code == 200:
                total_bytes = 0
                with open(output_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=32768):
                        if chunk:
                            f.write(chunk)
                            total_bytes += len(chunk)
                
                print(f"Successfully downloaded {total_bytes:,} bytes to {output_path}")
                return True
            else:
                print(f"Download failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Download error: {e}")
            return False

def generate_flag_video_alternative():
    """Generate flag video using alternative AI service"""
    alternatives = AIVideoAlternatives()
    
    # Enhanced flag prompt
    flag_prompt = """A beautiful flag waving gracefully in natural wind. The flag displays realistic fabric physics with natural ripples, waves, and flowing motion. Mounted on a tall flagpole, the flag flutters naturally with smooth, elegant movement. Professional cinematic quality with natural outdoor lighting, realistic wind effects, and ambient audio."""
    
    image_path = "uploads/2_1754017939_IMG_7008.jpeg"
    
    print("🚀 Attempting AI video generation with alternative services...")
    
    # Try RunwayML first
    print("\n1. Trying RunwayML Gen-3...")
    result = alternatives.generate_with_runwayml(image_path, flag_prompt)
    
    if result.get('needs_key'):
        print("❌ RunwayML API key needed")
        
        # Try Stability AI
        print("\n2. Trying Stability AI Video...")
        result = alternatives.generate_with_stability(image_path, flag_prompt)
        
        if result.get('needs_key'):
            print("❌ Stability AI API key needed")
            print("\n📋 Available alternative services:")
            for service_id, service_info in alternatives.services.items():
                print(f"   • {service_info['name']}: {service_info['quality']} quality, {service_info['max_duration']}s max")
            return False
    
    if result.get('success'):
        print(f"✅ Generation started with {result['service']}")
        print(f"Generation ID: {result['generation_id']}")
        return result
    else:
        print(f"❌ Generation failed: {result.get('error', 'Unknown error')}")
        return False

if __name__ == "__main__":
    generate_flag_video_alternative()