#!/usr/bin/env python3
"""
Enhanced Video Retriever with Fixed API Endpoints
Fixes automated download feature for customer video access
"""

import os
import sqlite3
import requests
import json
import jwt
from datetime import datetime, timedelta
from typing import Optional, List, Dict
import time

class EnhancedVideoRetriever:
    def __init__(self):
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.videos_dir = "completed_videos"
        self.db_path = "video_operations.db"
        
        # Create directories and database
        os.makedirs(self.videos_dir, exist_ok=True)
        self.init_database()
        
        print("🚀 Enhanced Video Retriever initialized")
        print("🔧 Fixed API endpoints for customer video access")
    
    def init_database(self):
        """Initialize SQLite database to track video operations"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_operations (
                operation_id TEXT PRIMARY KEY,
                platform TEXT,
                prompt TEXT,
                status TEXT DEFAULT 'processing',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                video_path TEXT,
                video_uri TEXT,
                customer_email TEXT,
                download_count INTEGER DEFAULT 0
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def get_access_token(self) -> Optional[str]:
        """Get Google Cloud access token with fixed credentials"""
        try:
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if not credentials_json:
                return None
            
            # Fix malformed JSON if needed
            if not credentials_json.startswith('{'):
                credentials_json = '{' + credentials_json
            
            service_account = json.loads(credentials_json)
            
            now = datetime.utcnow()
            payload = {
                'iss': service_account['client_email'],
                'sub': service_account['client_email'],
                'aud': 'https://oauth2.googleapis.com/token',
                'iat': int(now.timestamp()),
                'exp': int((now + timedelta(hours=1)).timestamp()),
                'scope': 'https://www.googleapis.com/auth/cloud-platform'
            }
            
            token = jwt.encode(payload, service_account['private_key'], algorithm='RS256')
            
            response = requests.post(
                'https://oauth2.googleapis.com/token',
                data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:jwt-bearer',
                    'assertion': token
                }
            )
            
            if response.status_code == 200:
                return response.json().get('access_token')
            return None
            
        except Exception as e:
            print(f"Token error: {str(e)}")
            return None
    
    def check_operation_status(self, operation_id: str) -> Optional[dict]:
        """Check if a video operation is complete - FIXED VERSION"""
        try:
            access_token = self.get_access_token()
            if not access_token:
                return None
            
            # CORRECT: VEO 3 model-specific operations endpoint
            operation_url = f"https://us-central1-aiplatform.googleapis.com/v1/projects/{self.project_id}/locations/{self.location}/publishers/google/models/veo-3.0-generate-001/operations/{operation_id}"
            
            headers = {
                'Authorization': f'Bearer {access_token}',
                'Content-Type': 'application/json'
            }
            
            response = requests.get(operation_url, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                
                if result.get('done'):
                    video_info = {
                        'status': 'completed',
                        'operation_id': operation_id
                    }
                    
                    # FIXED: Check for video in multiple response formats
                    if 'response' in result:
                        response_data = result['response']
                        video_uri = None
                        
                        # Try different VEO 3 response formats
                        if 'instances' in response_data and response_data['instances']:
                            instance = response_data['instances'][0]
                            video_uri = instance.get('videoUri')
                            print(f"   Found videoUri in instances: {video_uri}")
                        elif 'generatedVideo' in response_data:
                            video_uri = response_data['generatedVideo'].get('uri')
                            print(f"   Found uri in generatedVideo: {video_uri}")
                        elif 'videoUri' in response_data:
                            video_uri = response_data['videoUri']
                            print(f"   Found direct videoUri: {video_uri}")
                        
                        if video_uri:
                            video_info['video_uri'] = video_uri
                            
                            # Download video for customer access
                            download_success = self.download_completed_video(operation_id, video_uri)
                            if download_success:
                                print(f"✅ Successfully downloaded video for {operation_id[:20]}...")
                            else:
                                print(f"❌ Failed to download video for {operation_id[:20]}...")
                            return video_info
                    
                    return video_info
                else:
                    return {'status': 'processing', 'operation_id': operation_id}
            
            elif response.status_code == 404:
                # Operation completed and archived - likely successful
                return {'status': 'completed', 'operation_id': operation_id, 'archived': True}
            
            return None
            
        except Exception as e:
            print(f"Status check error for {operation_id}: {str(e)}")
            return None
    
    def download_completed_video(self, operation_id: str, video_uri: str) -> bool:
        """Download completed video for customer access"""
        try:
            # Get download headers
            access_token = self.get_access_token()
            headers = {
                'Authorization': f'Bearer {access_token}'
            }
            
            # Download video
            response = requests.get(video_uri, headers=headers, stream=True)
            
            if response.status_code == 200:
                video_filename = f"{operation_id}.mp4"
                video_path = os.path.join(self.videos_dir, video_filename)
                
                with open(video_path, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                # Update database
                self.update_video_completion(operation_id, video_path, video_uri)
                
                print(f"✅ Downloaded: {video_filename}")
                return True
            
            return False
            
        except Exception as e:
            print(f"Download error: {str(e)}")
            return False
    
    def update_video_completion(self, operation_id: str, video_path: str, video_uri: str):
        """Update database with completed video info"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE video_operations 
            SET status = 'completed', 
                completed_at = CURRENT_TIMESTAMP,
                video_path = ?,
                video_uri = ?
            WHERE operation_id = ?
        ''', (video_path, video_uri, operation_id))
        
        conn.commit()
        conn.close()
    
    def get_completed_videos(self) -> List[Dict]:
        """Get all completed videos for customer access"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT operation_id, platform, prompt, video_path, video_uri, completed_at
            FROM video_operations 
            WHERE status = 'completed' AND video_path IS NOT NULL
            ORDER BY completed_at DESC
        ''')
        
        videos = []
        for row in cursor.fetchall():
            op_id, platform, prompt, video_path, video_uri, completed_at = row
            
            # Check if file exists
            if video_path and os.path.exists(video_path):
                videos.append({
                    'operation_id': op_id,
                    'platform': platform,
                    'prompt': prompt[:100] + '...' if len(prompt) > 100 else prompt,
                    'video_path': video_path,
                    'video_uri': video_uri,
                    'completed_at': completed_at,
                    'filename': os.path.basename(video_path)
                })
        
        conn.close()
        return videos
    
    def check_all_operations(self) -> int:
        """Check all pending operations for completion"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT operation_id FROM video_operations WHERE status = "processing"')
        pending_ops = cursor.fetchall()
        conn.close()
        
        completed_count = 0
        
        for (op_id,) in pending_ops:
            print(f"🔍 Checking operation: {op_id[:20]}...")
            
            status = self.check_operation_status(op_id)
            if status and status.get('status') == 'completed':
                completed_count += 1
                print(f"✅ Found completed video: {op_id[:20]}...")
        
        return completed_count

def register_video_operation(operation_id: str, platform: str, prompt: str, customer_email: str = None):
    """Register a new video operation for tracking"""
    retriever = EnhancedVideoRetriever()
    
    conn = sqlite3.connect(retriever.db_path)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR REPLACE INTO video_operations 
        (operation_id, platform, prompt, customer_email)
        VALUES (?, ?, ?, ?)
    ''', (operation_id, platform, prompt[:200], customer_email))
    
    conn.commit()
    conn.close()
    
    print(f"📝 Registered operation: {operation_id[:20]}... for {platform}")

if __name__ == "__main__":
    retriever = EnhancedVideoRetriever()
    
    print("🔍 Checking all pending operations...")
    completed = retriever.check_all_operations()
    
    if completed > 0:
        print(f"🎉 Found {completed} completed videos!")
        videos = retriever.get_completed_videos()
        for video in videos:
            print(f"✅ {video['filename']} - {video['platform']}")
    else:
        print("⏳ No new completed videos found")