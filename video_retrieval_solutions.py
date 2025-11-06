"""
Video Retrieval Solutions for VEO 3
Multiple approaches to solve the video access issue
"""

import os
import sys
sys.path.append('.')

import json
import time
import requests
from datetime import datetime
from authentic_veo3_vertex import AuthenticVEO3
from google.cloud import storage
import base64

class VideoRetrievalSolutions:
    def __init__(self):
        self.veo3_client = AuthenticVEO3()
        self.project_id = "dreamframe"
        self.location = "us-central1"
        
    def solution_1_millisecond_capture(self, prompt: str):
        """Solution 1: Ultra-fast response capture within milliseconds"""
        
        print("🚀 Solution 1: Millisecond Response Capture")
        print("=" * 50)
        
        access_token = self.veo3_client.get_access_token()
        if not access_token:
            return None
            
        # Generate video
        endpoint_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
        
        payload = {
            "instances": [{"prompt": prompt, "video_length": 8}],
            "parameters": {"video_length": 8, "aspect_ratio": "16:9"}
        }
        
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        
        print("📡 Starting generation with immediate monitoring...")
        response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
        
        if response.status_code != 200:
            print(f"❌ Generation failed: {response.status_code}")
            return None
            
        operation_data = response.json()
        operation_name = operation_data.get('name')
        operation_id = operation_name.split('/')[-1]
        
        print(f"✅ Operation started: {operation_id}")
        
        # Ultra-fast monitoring (every 100ms for first few seconds)
        status_url = f"https://us-central1-aiplatform.googleapis.com/v1/{operation_name}"
        
        print("⚡ Starting millisecond-level monitoring...")
        
        # Check every 100ms for first 2 seconds
        for check in range(20):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get('done'):
                        print(f"🎉 CAPTURED! Operation completed in check #{check}")
                        
                        # Extract video data immediately
                        video_data = self.extract_comprehensive_video_data(status_data)
                        
                        return {
                            'success': True,
                            'method': 'millisecond_capture',
                            'capture_time': check * 100,  # milliseconds
                            'video_data': video_data,
                            'operation_id': operation_id
                        }
                
                time.sleep(0.1)  # 100ms intervals
                
            except Exception as e:
                print(f"Check #{check} error: {e}")
                time.sleep(0.1)
        
        # Continue with longer intervals
        print("🔄 Continuing with standard monitoring...")
        
        for check in range(20, 50):
            try:
                response = requests.get(status_url, headers=headers, timeout=10)
                
                if response.status_code == 200:
                    status_data = response.json()
                    
                    if status_data.get('done'):
                        print(f"🎉 CAPTURED! Operation completed in check #{check}")
                        
                        video_data = self.extract_comprehensive_video_data(status_data)
                        
                        return {
                            'success': True,
                            'method': 'standard_capture',
                            'capture_time': check * 500,  # milliseconds  
                            'video_data': video_data,
                            'operation_id': operation_id
                        }
                
                elif response.status_code == 404:
                    print(f"❌ Operation archived at check #{check}")
                    break
                
                time.sleep(0.5)  # 500ms intervals
                
            except Exception as e:
                print(f"Check #{check} error: {e}")
                time.sleep(0.5)
        
        return {'success': False, 'reason': 'capture_timeout'}
    
    def solution_2_bucket_configuration(self, prompt: str):
        """Solution 2: Configure Google Cloud Storage bucket for video delivery"""
        
        print("🚀 Solution 2: Bucket Configuration")
        print("=" * 40)
        
        try:
            # Initialize storage client
            storage_client = storage.Client(project=self.project_id)
            
            # Create or get bucket for video storage
            bucket_name = f"{self.project_id}-veo3-videos"
            
            try:
                bucket = storage_client.bucket(bucket_name)
                if not bucket.exists():
                    print(f"📦 Creating bucket: {bucket_name}")
                    bucket = storage_client.create_bucket(bucket_name, location="us-central1")
                else:
                    print(f"✅ Using existing bucket: {bucket_name}")
                    
            except Exception as bucket_error:
                print(f"❌ Bucket setup error: {bucket_error}")
                return None
            
            # Generate video with explicit storage configuration
            access_token = self.veo3_client.get_access_token()
            endpoint_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
            
            payload = {
                "instances": [{"prompt": prompt, "video_length": 8}],
                "parameters": {
                    "video_length": 8,
                    "aspect_ratio": "16:9",
                    "storageUri": f"gs://{bucket_name}/"
                }
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print("📡 Generating with bucket storage...")
            response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Generation failed: {response.status_code}")
                return None
                
            operation_data = response.json()
            operation_id = operation_data.get('name', '').split('/')[-1]
            
            print(f"✅ Generation started: {operation_id}")
            
            # Monitor bucket for new files
            print("🔍 Monitoring bucket for video files...")
            
            initial_blobs = list(bucket.list_blobs())
            initial_count = len(initial_blobs)
            
            print(f"📊 Initial bucket files: {initial_count}")
            
            # Check bucket every 5 seconds for new videos
            for check in range(24):  # 2 minutes total
                time.sleep(5)
                
                current_blobs = list(bucket.list_blobs())
                
                if len(current_blobs) > initial_count:
                    print("🎉 NEW VIDEO FILE DETECTED!")
                    
                    # Find the new video file
                    new_blobs = [blob for blob in current_blobs if blob not in initial_blobs]
                    
                    for blob in new_blobs:
                        if any(ext in blob.name.lower() for ext in ['.mp4', '.mov', 'video']):
                            print(f"🎥 Video file found: {blob.name}")
                            
                            # Generate signed URL for download
                            download_url = blob.generate_signed_url(
                                expiration=datetime.now().timestamp() + 3600,  # 1 hour
                                method='GET'
                            )
                            
                            return {
                                'success': True,
                                'method': 'bucket_storage',
                                'video_file': blob.name,
                                'download_url': download_url,
                                'bucket_name': bucket_name,
                                'operation_id': operation_id
                            }
                
                print(f"🔄 Check #{check + 1}: {len(current_blobs)} files")
            
            print("⏰ Bucket monitoring timeout")
            return {'success': False, 'reason': 'bucket_timeout'}
            
        except Exception as e:
            print(f"❌ Bucket solution error: {e}")
            return None
    
    def solution_3_webhook_notifications(self, prompt: str):
        """Solution 3: Set up Pub/Sub webhooks for completion notifications"""
        
        print("🚀 Solution 3: Webhook Notifications")
        print("=" * 38)
        
        try:
            from google.cloud import pubsub_v1
            
            # Initialize Pub/Sub
            publisher = pubsub_v1.PublisherClient()
            subscriber = pubsub_v1.SubscriberClient()
            
            # Create topic for VEO 3 notifications
            topic_name = f"projects/{self.project_id}/topics/veo3-completions"
            
            try:
                topic = publisher.create_topic(request={"name": topic_name})
                print(f"✅ Created topic: {topic.name}")
            except Exception:
                print(f"✅ Using existing topic: {topic_name}")
            
            # Create subscription
            subscription_name = f"projects/{self.project_id}/subscriptions/veo3-completion-sub"
            
            try:
                subscription = subscriber.create_subscription(
                    request={
                        "name": subscription_name,
                        "topic": topic_name,
                        "ack_deadline_seconds": 60
                    }
                )
                print(f"✅ Created subscription: {subscription.name}")
            except Exception:
                print(f"✅ Using existing subscription: {subscription_name}")
            
            # Generate video with webhook notification
            access_token = self.veo3_client.get_access_token()
            endpoint_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-preview:predictLongRunning"
            
            payload = {
                "instances": [{"prompt": prompt, "video_length": 8}],
                "parameters": {
                    "video_length": 8,
                    "aspect_ratio": "16:9",
                    "notification_config": {
                        "pubsub_topic": topic_name
                    }
                }
            }
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            print("📡 Generating with webhook notifications...")
            response = requests.post(endpoint_url, json=payload, headers=headers, timeout=30)
            
            if response.status_code != 200:
                print(f"❌ Generation failed: {response.status_code}")
                return None
                
            operation_data = response.json()
            operation_id = operation_data.get('name', '').split('/')[-1]
            
            print(f"✅ Generation started: {operation_id}")
            print("🔔 Listening for completion notification...")
            
            # Listen for completion messages
            def callback(message):
                print(f"🎉 WEBHOOK NOTIFICATION RECEIVED!")
                
                try:
                    notification_data = json.loads(message.data.decode())
                    print(f"📋 Notification: {notification_data}")
                    
                    # Extract video information from notification
                    if 'video_uri' in notification_data:
                        print(f"🎥 Video URI: {notification_data['video_uri']}")
                        
                    message.ack()
                    
                    return {
                        'success': True,
                        'method': 'webhook_notification',
                        'notification_data': notification_data,
                        'operation_id': operation_id
                    }
                    
                except Exception as e:
                    print(f"❌ Notification processing error: {e}")
                    message.ack()
            
            # Start listening with timeout
            flow_control = pubsub_v1.types.FlowControl(max_messages=10)
            streaming_pull_future = subscriber.subscribe(
                subscription_name, 
                callback=callback,
                flow_control=flow_control
            )
            
            print("👂 Listening for notifications...")
            
            try:
                # Listen for 60 seconds
                streaming_pull_future.result(timeout=60)
            except Exception as timeout_error:
                streaming_pull_future.cancel()
                print("⏰ Webhook timeout")
                
            return {'success': False, 'reason': 'webhook_timeout'}
            
        except Exception as e:
            print(f"❌ Webhook solution error: {e}")
            return None
    
    def solution_4_alternative_endpoints(self, prompt: str):
        """Solution 4: Try alternative Google AI endpoints for video access"""
        
        print("🚀 Solution 4: Alternative Endpoints")
        print("=" * 37)
        
        access_token = self.veo3_client.get_access_token()
        
        # Alternative endpoints to try
        alternative_endpoints = [
            # Standard predict (synchronous)
            f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-preview:predict",
            
            # AI Studio endpoint
            f"https://generativelanguage.googleapis.com/v1beta/models/veo-3:generateVideo",
            
            # Alternative model versions
            f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3:predict",
            
            # Batch prediction
            f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-preview:batchPredict"
        ]
        
        for i, endpoint in enumerate(alternative_endpoints, 1):
            print(f"\n🧪 Testing Alternative #{i}")
            print(f"📍 Endpoint: {endpoint}")
            
            try:
                payload = {
                    "instances": [{"prompt": prompt, "video_length": 8}],
                    "parameters": {"video_length": 8, "aspect_ratio": "16:9"}
                }
                
                headers = {
                    'Authorization': f'Bearer {access_token}',
                    'Content-Type': 'application/json'
                }
                
                response = requests.post(endpoint, json=payload, headers=headers, timeout=30)
                
                print(f"📊 Status: {response.status_code}")
                
                if response.status_code == 200:
                    response_data = response.json()
                    
                    print(f"🎉 SUCCESS with Alternative #{i}!")
                    print("📋 Response:")
                    print(json.dumps(response_data, indent=2))
                    
                    # Check for immediate video data
                    video_data = self.extract_comprehensive_video_data(response_data)
                    
                    if video_data:
                        return {
                            'success': True,
                            'method': f'alternative_endpoint_{i}',
                            'endpoint': endpoint,
                            'video_data': video_data,
                            'response_data': response_data
                        }
                    else:
                        print("⚠️  No video data in immediate response")
                        
                else:
                    print(f"❌ Failed: {response.status_code} - {response.text[:200]}")
                    
            except Exception as e:
                print(f"❌ Alternative #{i} error: {e}")
        
        return {'success': False, 'reason': 'all_alternatives_failed'}
    
    def extract_comprehensive_video_data(self, response_data):
        """Extract video data from any response format"""
        
        # Check all possible locations for video data
        video_sources = [
            # Direct response fields
            response_data.get('response', {}),
            response_data.get('predictions', []),
            response_data.get('generatedVideos', []),
            response_data.get('videos', []),
            response_data.get('results', []),
            
            # Nested response fields
            response_data.get('response', {}).get('predictions', []),
            response_data.get('response', {}).get('generatedVideos', []),
        ]
        
        for source in video_sources:
            if isinstance(source, list):
                for item in source:
                    video_data = self.extract_from_item(item)
                    if video_data:
                        return video_data
            elif isinstance(source, dict):
                video_data = self.extract_from_item(source)
                if video_data:
                    return video_data
        
        return None
    
    def extract_from_item(self, item):
        """Extract video data from a single item"""
        if not isinstance(item, dict):
            return None
            
        # Check for video URLs
        url_fields = ['videoUri', 'uri', 'url', 'video_url', 'downloadUrl', 'signedUrl']
        for field in url_fields:
            if field in item and item[field]:
                return {
                    'type': 'url',
                    'url': item[field],
                    'source': field
                }
        
        # Check for base64 video data
        data_fields = ['videoData', 'data', 'video_data', 'content', 'bytes']
        for field in data_fields:
            if field in item and item[field]:
                return {
                    'type': 'base64',
                    'data': item[field],
                    'source': field
                }
        
        # Check for storage paths
        if 'storageUri' in item and item['storageUri']:
            return {
                'type': 'storage',
                'path': item['storageUri'],
                'source': 'storageUri'
            }
        
        return None

def test_all_retrieval_solutions():
    """Test all video retrieval solutions"""
    
    print("🎬 Testing All Video Retrieval Solutions")
    print("=" * 50)
    
    solutions = VideoRetrievalSolutions()
    test_prompt = "A golden sunset over a calm mountain lake, peaceful nature scene"
    
    print(f"🏞️  Test prompt: {test_prompt}")
    print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test each solution
    results = {}
    
    print("\n" + "🚀" * 20)
    result1 = solutions.solution_1_millisecond_capture(test_prompt)
    results['millisecond_capture'] = result1
    
    if not result1 or not result1.get('success'):
        print("\n" + "🚀" * 20)
        result2 = solutions.solution_2_bucket_configuration(test_prompt)
        results['bucket_configuration'] = result2
        
        if not result2 or not result2.get('success'):
            print("\n" + "🚀" * 20)
            result3 = solutions.solution_3_webhook_notifications(test_prompt)
            results['webhook_notifications'] = result3
            
            if not result3 or not result3.get('success'):
                print("\n" + "🚀" * 20)
                result4 = solutions.solution_4_alternative_endpoints(test_prompt)
                results['alternative_endpoints'] = result4
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 VIDEO RETRIEVAL SOLUTIONS SUMMARY")
    
    successful_solutions = []
    
    for solution_name, result in results.items():
        if result and result.get('success'):
            successful_solutions.append((solution_name, result))
            print(f"✅ {solution_name.replace('_', ' ').title()}: SUCCESS")
            
            if result.get('video_data'):
                video_data = result['video_data']
                print(f"   🎥 Video {video_data['type']}: {video_data.get('url', 'Found')}")
            
        else:
            print(f"❌ {solution_name.replace('_', ' ').title()}: Failed")
    
    if successful_solutions:
        print(f"\n🎉 SUCCESS! {len(successful_solutions)} working solution(s) found")
        
        best_solution = successful_solutions[0]
        print(f"🏆 Best solution: {best_solution[0].replace('_', ' ').title()}")
        
        return best_solution[1]
    else:
        print("\n⚠️  All solutions need further refinement")
        print("💡 Recommendations:")
        print("   - Configure Google Cloud Storage permissions")
        print("   - Set up Pub/Sub notifications")
        print("   - Contact Google Cloud support for VEO 3 video access")
        
        return None

if __name__ == "__main__":
    test_all_retrieval_solutions()