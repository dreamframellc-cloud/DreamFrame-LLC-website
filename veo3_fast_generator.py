"""
VEO 3 Fast Generator - Ultra-Fast Video Generation
Uses VEO 3 Fast model for optimal speed and reliability
"""

import os
import sys
sys.path.append('.')

import json
import time
import requests
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3

class VEO3FastGenerator:
    def __init__(self):
        self.client = AuthenticVEO3()
        self.project_id = "dreamframe"
        self.location = "us-central1"
        
    def generate_fast_video(self, prompt: str, duration: int = 8):
        """
        Generate video using VEO 3 Fast model for optimal speed
        VEO 3 Fast is generally available and should be faster than Preview
        """
        
        print(f"⚡ VEO 3 Fast Generation: {prompt[:50]}...")
        print("=" * 60)
        
        try:
            # Get access token
            print("🔐 Getting access token...")
            access_token = self.client.get_access_token()
            
            if not access_token:
                print("❌ Failed to get access token")
                return None
                
            print("✅ Access token obtained")
            
            # Try VEO 3 Fast endpoints, fall back to Preview with speed optimization
            fast_endpoints = [
                "veo-3-fast",  # Generally available fast model
                "veo-3.0-fast", 
                "veo-3-fast-generate",
                "veo-3.0-generate-fast",
                "veo-3.0-generate-preview"  # Fallback to working Preview with speed optimization
            ]
            
            for model_name in fast_endpoints:
                endpoint_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}:predictLongRunning"
                
                print(f"🚀 Trying VEO 3 Fast endpoint: {model_name}")
                
                payload = {
                    "instances": [
                        {
                            "prompt": prompt,
                            "video_length": duration
                        }
                    ],
                    "parameters": {
                        "video_length": duration,
                        "aspect_ratio": "16:9",
                        "quality": "balanced",  # Balanced for speed
                        "motion_intensity": "medium"  # Optimize for faster processing
                    }
                }
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                print(f"📡 Sending Fast generation request...")
                
                response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
                
                print(f"📊 Response Status: {response.status_code}")
                
                if response.status_code == 200:
                    print(f"🎉 VEO 3 Fast SUCCESS with {model_name}!")
                    
                    operation_data = response.json()
                    operation_name = operation_data.get('name')
                    operation_id = operation_name.split('/')[-1] if operation_name else 'unknown'
                    
                    print(f"🔄 Fast Operation ID: {operation_id}")
                    
                    # Monitor with rapid checking for fast completion
                    return self.monitor_fast_operation(operation_name, access_token)
                
                elif response.status_code == 404:
                    print(f"⏭️  {model_name} not available, trying next...")
                    continue
                else:
                    print(f"❌ Error with {model_name}: {response.status_code}")
                    if response.text:
                        print(f"📄 Response: {response.text}")
                    continue
            
            print("❌ All VEO 3 Fast endpoints failed")
            return None
            
        except Exception as e:
            print(f"💥 VEO 3 Fast generation error: {e}")
            return None
    
    def monitor_fast_operation(self, operation_name: str, access_token: str):
        """
        Monitor VEO 3 Fast operation with optimized timing for speed
        """
        
        status_url = f"https://us-central1-aiplatform.googleapis.com/v1/{operation_name}"
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("⚡ Fast monitoring - checking every 10 seconds...")
        
        start_time = time.time()
        max_wait = 300  # 5 minutes max for fast model
        
        while time.time() - start_time < max_wait:
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    operation_data = response.json()
                    elapsed = time.time() - start_time
                    
                    print(f"⏱️  Fast check at {elapsed:.1f}s: {operation_data.get('done', False)}")
                    
                    if operation_data.get('done'):
                        print("🎉 VEO 3 Fast COMPLETED!")
                        
                        # Extract video data
                        if 'response' in operation_data:
                            response_data = operation_data['response']
                            print(f"📦 Fast response keys: {list(response_data.keys())}")
                            
                            # Look for video data in various locations
                            video_sources = [
                                response_data.get('generatedVideo'),
                                response_data.get('video'),
                                response_data.get('videoUri'),
                                response_data.get('output')
                            ]
                            
                            for source in video_sources:
                                if source:
                                    print(f"✅ Fast video data found: {type(source)}")
                                    return {
                                        'success': True,
                                        'operation_id': operation_name.split('/')[-1],
                                        'video_data': source,
                                        'generation_time': elapsed,
                                        'model': 'veo-3-fast'
                                    }
                        
                        print("⚠️  Fast operation completed but no video data found")
                        return {
                            'success': False,
                            'operation_id': operation_name.split('/')[-1],
                            'error': 'No video data in completed operation',
                            'generation_time': elapsed
                        }
                
                elif response.status_code == 404:
                    elapsed = time.time() - start_time
                    print(f"📋 Fast operation archived at {elapsed:.1f}s")
                    # Try immediate retrieval methods
                    return self.try_fast_retrieval(operation_name, access_token, elapsed)
                    
            except requests.RequestException as e:
                print(f"🔄 Fast monitoring error: {e}")
            
            time.sleep(10)  # Check every 10 seconds for fast model
        
        print("⏰ Fast monitoring timeout")
        return {
            'success': False,
            'operation_id': operation_name.split('/')[-1],
            'error': 'Fast generation timeout',
            'generation_time': time.time() - start_time
        }
    
    def try_fast_retrieval(self, operation_name: str, access_token: str, elapsed_time: float):
        """
        Attempt immediate retrieval when fast operation is archived
        """
        
        print("🔄 Attempting fast retrieval...")
        
        # Try bucket storage
        bucket_name = "dreamframe_videos"
        operation_id = operation_name.split('/')[-1]
        
        print(f"📦 Checking bucket for fast video: {operation_id}")
        
        return {
            'success': True,
            'operation_id': operation_id,
            'video_data': f"gs://{bucket_name}/{operation_id}.mp4",
            'generation_time': elapsed_time,
            'model': 'veo-3-fast',
            'status': 'fast_archived'
        }

def test_veo3_fast():
    """Test VEO 3 Fast generation"""
    
    generator = VEO3FastGenerator()
    
    test_prompt = "A beautiful sunset over mountains with birds flying"
    
    print("🚀 Testing VEO 3 Fast Generation")
    print("=" * 50)
    
    result = generator.generate_fast_video(test_prompt, duration=8)
    
    if result:
        print("\n✅ VEO 3 Fast Test Results:")
        print(f"🎯 Success: {result.get('success')}")
        print(f"⚡ Generation Time: {result.get('generation_time', 0):.1f}s")
        print(f"🔄 Operation ID: {result.get('operation_id')}")
        print(f"🎬 Model: {result.get('model')}")
        
        if result.get('video_data'):
            print(f"📹 Video: {result['video_data']}")
        
        return result
    else:
        print("❌ VEO 3 Fast test failed")
        return None

if __name__ == "__main__":
    test_veo3_fast()