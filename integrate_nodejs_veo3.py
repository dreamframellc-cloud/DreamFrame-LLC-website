"""
Integration script for Node.js VEO 3 server
Combines Python Flask frontend with Node.js VEO 3 backend
"""

import requests
import json
import logging
from app import app, db
from models import VideoOrder, OrderStatus
from datetime import datetime
import subprocess
import time
import threading

class NodeJSVEO3Integration:
    def __init__(self):
        self.nodejs_server_url = "http://localhost:3000"
        self.server_process = None
        self.server_started = False
        
        logging.info("🔗 Node.js VEO 3 integration initialized")
    
    def start_nodejs_server(self):
        """Start the Node.js VEO 3 server"""
        try:
            # Check if server is already running
            if self.is_server_running():
                logging.info("✅ Node.js VEO 3 server already running")
                self.server_started = True
                return True
            
            logging.info("🚀 Starting Node.js VEO 3 server...")
            
            # Start Node.js server in background
            self.server_process = subprocess.Popen(
                ['node', 'nodejs_veo3_server.js'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            for i in range(10):  # Wait up to 10 seconds
                time.sleep(1)
                if self.is_server_running():
                    logging.info("✅ Node.js VEO 3 server started successfully")
                    self.server_started = True
                    return True
            
            logging.error("❌ Failed to start Node.js VEO 3 server")
            return False
            
        except Exception as e:
            logging.error(f"❌ Error starting Node.js server: {e}")
            return False
    
    def is_server_running(self):
        """Check if Node.js server is running"""
        try:
            response = requests.get(f"{self.nodejs_server_url}/health", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def generate_video_nodejs(self, prompt, image_path=None, platform="general"):
        """Generate video using Node.js VEO 3 server"""
        try:
            if not self.server_started:
                if not self.start_nodejs_server():
                    return None
            
            # Prepare request data
            aspect_ratio = "16:9" if platform == "general" else "9:16"
            
            request_data = {
                "prompt": self.optimize_prompt(prompt, platform),
                "aspectRatio": aspect_ratio,
                "durationSeconds": 5,
                "resolution": "720p"
            }
            
            logging.info(f"🎬 Node.js VEO 3 generation request")
            logging.info(f"📱 Platform: {platform}")
            logging.info(f"📝 Prompt: {prompt}")
            
            # Send request to Node.js server
            response = requests.post(
                f"{self.nodejs_server_url}/generate-video",
                json=request_data,
                timeout=120
            )
            
            logging.info(f"📊 Node.js response status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get('operationId')
                video_uri = result.get('videoUri')
                
                if operation_id:
                    logging.info(f"✅ Node.js VEO 3 operation started: {operation_id}")
                    return {
                        'operation_id': operation_id,
                        'video_uri': video_uri,
                        'status': 'started'
                    }
                else:
                    logging.warning("⚠️ No operation ID in Node.js response")
                    return None
            else:
                logging.error(f"❌ Node.js VEO 3 generation failed: {response.status_code}")
                logging.error(f"Response: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"❌ Node.js VEO 3 generation error: {e}")
            return None
    
    def optimize_prompt(self, prompt, platform):
        """Optimize prompt for platform"""
        base_prompt = prompt.strip()
        
        if platform == "general":
            return f"Create a high-quality cinematic video: {base_prompt}. Professional cinematography, smooth camera movements, detailed textures, 16:9 aspect ratio, 5 seconds."
        elif platform == "instagram":
            return f"Create an engaging Instagram story: {base_prompt}. Vertical 9:16 format, vibrant colors, dynamic motion, social media optimized, 5 seconds."
        else:
            return base_prompt
    
    def stop_server(self):
        """Stop Node.js server"""
        if self.server_process:
            self.server_process.terminate()
            self.server_process = None
            self.server_started = False
            logging.info("🛑 Node.js VEO 3 server stopped")

def test_nodejs_integration():
    """Test Node.js VEO 3 integration"""
    integration = NodeJSVEO3Integration()
    
    # Test prompt
    test_prompt = "A peaceful ocean sunset with gentle waves"
    
    print("🧪 Testing Node.js VEO 3 integration")
    print(f"📝 Prompt: {test_prompt}")
    
    # Generate video
    result = integration.generate_video_nodejs(
        prompt=test_prompt,
        platform="general"
    )
    
    if result:
        print(f"✅ Node.js VEO 3 integration working")
        print(f"🔄 Operation ID: {result['operation_id']}")
        print(f"📊 Status: {result['status']}")
        if result.get('video_uri'):
            print(f"🎥 Video URI: {result['video_uri']}")
    else:
        print(f"❌ Node.js VEO 3 integration failed")
    
    # Clean up
    integration.stop_server()
    return result

def update_flask_routes():
    """Update Flask routes to use Node.js VEO 3"""
    print("🔗 Integration ready - Flask can now use Node.js VEO 3 backend")
    print("📋 To integrate:")
    print("1. Import NodeJSVEO3Integration in your Flask routes")
    print("2. Replace VEO 3 calls with nodejs_integration.generate_video_nodejs()")
    print("3. Handle the response with operation_id and video_uri")

if __name__ == "__main__":
    # Test the integration
    test_result = test_nodejs_integration()
    
    if test_result:
        update_flask_routes()
    else:
        print("❌ Node.js integration test failed")