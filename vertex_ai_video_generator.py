#!/usr/bin/env python3
"""
Vertex AI VEO 3 Video Generation System
Integrates Google's VEO 3 API for professional video creation
"""

import os
import json
import time
import requests
import logging
from datetime import datetime
from typing import Dict, Optional, Any
# Import will be done locally to avoid circular imports

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VertexAIVideoGenerator:
    """Professional video generator using Google's VEO 3 API via Vertex AI"""
    
    def __init__(self):
        # Extract project ID from credentials if needed
        project_id_raw = os.environ.get("GOOGLE_CLOUD_PROJECT_ID")
        if project_id_raw and project_id_raw.startswith('{'):
            # Parse JSON to extract project_id
            try:
                import json
                creds = json.loads(project_id_raw)
                self.project_id = creds.get("project_id", "dreamframe")
            except:
                self.project_id = "dreamframe"  # Fallback
        else:
            self.project_id = project_id_raw or "dreamframe"
            
        self.api_key = os.environ.get("VEO3_API_KEY")
        self.location = "us-central1"  # Standard location for VEO 3
        self.base_url = f"https://{self.location}-aiplatform.googleapis.com/v1"
        
        # VEO 3 model configuration
        self.model_name = "veo-3-hd"
        self.default_settings = {
            "temperature": 0.7,
            "max_output_tokens": 8192,
            "top_p": 0.8,
            "top_k": 40
        }
        
        logger.info("🎬 Vertex AI VEO 3 Generator initialized")
    
    def generate_video_from_image(self, image_path: str, prompt: str, 
                                video_order_id: int, duration: int = 5) -> Dict[str, Any]:
        """
        Generate video from image using VEO 3
        
        Args:
            image_path: Path to source image
            prompt: Video generation prompt
            video_order_id: Database order ID
            duration: Video duration in seconds (3-30)
        
        Returns:
            Dict with generation result
        """
        try:
            # Import here to avoid circular imports
            from models import VideoOrder
            from app import app, db
            
            # Update order status
            with app.app_context():
                order = VideoOrder.query.get(video_order_id)
                if not order:
                    return {"success": False, "error": "Video order not found"}
                
                # Import OrderStatus
                from models import OrderStatus
                order.status = OrderStatus.IN_PRODUCTION
                order.generation_settings = f"Vertex AI VEO 3 - {duration}s duration"
                db.session.commit()
            
            # Prepare VEO 3 request
            generation_request = self._prepare_generation_request(
                image_path, prompt, duration
            )
            
            logger.info(f"🚀 Starting VEO 3 generation for order {video_order_id}")
            
            # Submit to Vertex AI
            operation_response = self._submit_generation_request(generation_request)
            
            if not operation_response.get("success"):
                return operation_response
            
            # Monitor generation progress
            operation_id = operation_response["operation_id"]
            result = self._monitor_generation_progress(operation_id, video_order_id)
            
            return result
            
        except Exception as e:
            logger.error(f"❌ VEO 3 generation failed: {str(e)}")
            
            # Import here to avoid circular imports
            from models import VideoOrder
            from app import app, db
            
            # Update order with error
            with app.app_context():
                order = VideoOrder.query.get(video_order_id)
                if order:
                    # Import OrderStatus
                    from models import OrderStatus
                    order.status = OrderStatus.CANCELLED
                    order.generation_settings = f"VEO 3 Error: {str(e)}"
                    db.session.commit()
            
            return {"success": False, "error": str(e)}
    
    def _prepare_generation_request(self, image_path: str, prompt: str, 
                                  duration: int) -> Dict[str, Any]:
        """Prepare VEO 3 generation request payload"""
        
        # Encode image to base64
        import base64
        with open(image_path, "rb") as image_file:
            image_base64 = base64.b64encode(image_file.read()).decode('utf-8')
        
        # Enhanced prompt engineering for VEO 3
        enhanced_prompt = self._enhance_prompt_for_veo3(prompt, duration)
        
        request_payload = {
            "model": f"projects/{self.project_id}/locations/{self.location}/models/{self.model_name}",
            "contents": [
                {
                    "role": "user",
                    "parts": [
                        {
                            "text": enhanced_prompt
                        },
                        {
                            "inline_data": {
                                "mime_type": "image/jpeg",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ],
            "generation_config": {
                **self.default_settings,
                "video_config": {
                    "duration_seconds": duration,
                    "resolution": "1280x720",  # HD resolution
                    "frame_rate": 30,
                    "motion_intensity": "medium",
                    "quality": "high"
                }
            }
        }
        
        return request_payload
    
    def _enhance_prompt_for_veo3(self, prompt: str, duration: int) -> str:
        """Enhance prompt with VEO 3 optimization"""
        
        enhancement_prefix = f"""
        Create a {duration}-second professional video based on this image.
        
        Video Requirements:
        - Smooth, cinematic motion
        - Professional lighting and effects
        - High-quality output suitable for commercial use
        - Natural transitions and movements
        - Maintain image subject integrity
        
        Creative Direction: {prompt}
        
        Technical Specifications:
        - Output: MP4 format, H.264 codec
        - Resolution: 1280x720 HD
        - Frame rate: 30fps
        - Audio: Optional ambient sound
        """
        
        return enhancement_prefix.strip()
    
    def _submit_generation_request(self, request_payload: Dict[str, Any]) -> Dict[str, Any]:
        """Submit generation request to Vertex AI"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "X-Goog-User-Project": self.project_id
        }
        
        endpoint = f"{self.base_url}/projects/{self.project_id}/locations/{self.location}:generateContent"
        
        try:
            response = requests.post(
                endpoint,
                headers=headers,
                json=request_payload,
                timeout=60
            )
            
            if response.status_code == 200:
                result = response.json()
                operation_id = result.get("name", "unknown")
                
                logger.info("✅ VEO 3 generation request submitted successfully")
                return {
                    "success": True,
                    "operation_id": operation_id,
                    "response": result
                }
            else:
                logger.error(f"❌ VEO 3 API error: {response.status_code} - {response.text}")
                return {
                    "success": False,
                    "error": f"API error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            logger.error(f"❌ Request failed: {str(e)}")
            return {"success": False, "error": f"Request failed: {str(e)}"}
    
    def _monitor_generation_progress(self, operation_id: str, 
                                   video_order_id: int) -> Dict[str, Any]:
        """Monitor VEO 3 generation progress"""
        
        max_attempts = 60  # 5 minutes max
        attempt = 0
        
        while attempt < max_attempts:
            try:
                status = self._check_operation_status(operation_id)
                
                if status.get("done"):
                    # Generation complete
                    if "error" in status:
                        logger.error(f"❌ VEO 3 generation failed: {status['error']}")
                        return {"success": False, "error": status["error"]}
                    
                    # Extract video URL/data
                    video_result = self._extract_video_result(status["response"])
                    
                    if video_result.get("success"):
                        # Download and save video
                        saved_path = self._save_generated_video(
                            video_result["video_url"], 
                            video_order_id
                        )
                        
                        if saved_path:
                            # Import here to avoid circular imports
                            from models import VideoOrder
                            from app import app, db
                            
                            # Update database
                            with app.app_context():
                                order = VideoOrder.query.get(video_order_id)
                                if order:
                                    order.status = 'COMPLETED'
                                    order.generated_video_path = saved_path
                                    order.generation_settings += " - VEO 3 Complete"
                                    db.session.commit()
                            
                            logger.info(f"🎉 VEO 3 video generated successfully: {saved_path}")
                            return {
                                "success": True,
                                "video_path": saved_path,
                                "operation_id": operation_id
                            }
                    
                    return video_result
                
                # Still processing
                logger.info(f"⏳ VEO 3 generation in progress... ({attempt + 1}/{max_attempts})")
                time.sleep(5)
                attempt += 1
                
            except Exception as e:
                logger.error(f"❌ Error monitoring progress: {str(e)}")
                attempt += 1
                time.sleep(5)
        
        # Timeout
        logger.error("⏰ VEO 3 generation timeout")
        return {"success": False, "error": "Generation timeout"}
    
    def _check_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """Check VEO 3 operation status"""
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "X-Goog-User-Project": self.project_id
        }
        
        endpoint = f"{self.base_url}/operations/{operation_id}"
        
        response = requests.get(endpoint, headers=headers, timeout=30)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"Status check failed: {response.status_code}"}
    
    def _extract_video_result(self, response_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract video URL from VEO 3 response"""
        
        try:
            # VEO 3 typically returns video in response.candidates[0].content.parts[0]
            candidates = response_data.get("candidates", [])
            
            if not candidates:
                return {"success": False, "error": "No video candidates in response"}
            
            content = candidates[0].get("content", {})
            parts = content.get("parts", [])
            
            for part in parts:
                if "video_data" in part or "file_data" in part:
                    video_url = part.get("video_data", {}).get("uri") or part.get("file_data", {}).get("uri")
                    
                    if video_url:
                        return {"success": True, "video_url": video_url}
            
            return {"success": False, "error": "No video data found in response"}
            
        except Exception as e:
            return {"success": False, "error": f"Failed to extract video: {str(e)}"}
    
    def _save_generated_video(self, video_url: str, video_order_id: int) -> Optional[str]:
        """Download and save generated video"""
        
        try:
            # Download video
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "X-Goog-User-Project": self.project_id
            }
            
            response = requests.get(video_url, headers=headers, stream=True, timeout=300)
            
            if response.status_code == 200:
                # Generate filename
                timestamp = int(time.time())
                filename = f"veo3_video_{video_order_id}_{timestamp}.mp4"
                filepath = os.path.join("completed_videos", filename)
                
                # Ensure directory exists
                os.makedirs("completed_videos", exist_ok=True)
                
                # Save video
                with open(filepath, "wb") as video_file:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            video_file.write(chunk)
                
                logger.info(f"💾 VEO 3 video saved: {filepath}")
                return filepath
            
            else:
                logger.error(f"❌ Failed to download video: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"❌ Error saving video: {str(e)}")
            return None

def create_vertex_ai_video(image_path: str, prompt: str, video_order_id: int, 
                          duration: int = 5) -> Dict[str, Any]:
    """
    Main function to create video using Vertex AI VEO 3
    
    Args:
        image_path: Path to source image
        prompt: Generation prompt
        video_order_id: Database order ID
        duration: Video duration (3-30 seconds)
    
    Returns:
        Generation result dictionary
    """
    generator = VertexAIVideoGenerator()
    return generator.generate_video_from_image(image_path, prompt, video_order_id, duration)

if __name__ == "__main__":
    # Test the system
    test_prompt = "Create a cinematic video with smooth camera movements and professional lighting"
    print("🎬 Vertex AI VEO 3 Video Generator Ready")
    print(f"📊 Project ID: {os.environ.get('GOOGLE_CLOUD_PROJECT_ID', 'Not configured')}")
    print(f"🔑 API Key: {'✅ Available' if os.environ.get('VEO3_API_KEY') else '❌ Missing'}")