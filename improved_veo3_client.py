"""
Improved VEO 3 Client with Proper Timeout Handling
Using Google Cloud AI Platform client library for better reliability
"""

import os
import time
import logging
from typing import Optional, Dict, Any
from google.cloud import aiplatform
from google.cloud.aiplatform import gapic
from google.api_core import exceptions
import json

class ImprovedVEO3Client:
    def __init__(self):
        """Initialize VEO 3 client with proper configuration"""
        self.project_id = "dreamframe"
        self.location = "us-central1"
        self.model_name = "veo-3.0-generate-001"
        
        # Initialize AI Platform
        aiplatform.init(project=self.project_id, location=self.location)
        
        # Create prediction service client
        self.client = aiplatform.gapic.PredictionServiceClient()
        
        logging.info("🚀 Improved VEO 3 client initialized")
    
    def generate_video(self, 
                      prompt: str, 
                      image_path: str, 
                      platform: str = "general",
                      timeout: int = 3600) -> Optional[str]:
        """
        Generate video with improved timeout handling
        
        Args:
            prompt: Text description for video generation
            image_path: Path to source image
            platform: Target platform (general, instagram, etc.)
            timeout: Maximum wait time in seconds (default 1 hour)
            
        Returns:
            Operation ID if successful, None if failed
        """
        try:
            # Build the request payload
            endpoint = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{self.model_name}"
            
            # Optimize prompt based on platform
            optimized_prompt = self._optimize_prompt_for_platform(prompt, platform)
            
            # Prepare the request
            request_payload = {
                "prompt": optimized_prompt,
                "aspect_ratio": "16:9" if platform == "general" else "9:16",
                "duration": "5s",
                "quality": "high"
            }
            
            # Add image if provided
            if image_path and os.path.exists(image_path):
                with open(image_path, 'rb') as f:
                    image_data = f.read()
                request_payload["image"] = {
                    "bytesBase64Encoded": image_data
                }
            
            request = gapic.PredictRequest(
                endpoint=endpoint,
                instances=[request_payload]
            )
            
            logging.info(f"🎬 Starting VEO 3 generation with {timeout}s timeout")
            logging.info(f"📱 Platform: {platform} (optimized)")
            
            # Make the long-running prediction with timeout
            operation = self.client.predict_long_running(
                request=request, 
                timeout=timeout
            )
            
            if operation:
                operation_id = operation.name
                logging.info(f"✅ VEO 3 operation started: {operation_id}")
                return operation_id
            else:
                logging.error("❌ No operation returned from VEO 3")
                return None
                
        except exceptions.DeadlineExceeded:
            logging.error(f"⏰ VEO 3 request timed out after {timeout} seconds")
            return None
        except exceptions.InvalidArgument as e:
            logging.error(f"❌ Invalid VEO 3 request: {e}")
            return None
        except Exception as e:
            logging.error(f"❌ VEO 3 generation failed: {e}")
            return None
    
    def check_operation_status(self, operation_id: str) -> Dict[str, Any]:
        """
        Check operation status with improved error handling
        
        Args:
            operation_id: The operation ID to check
            
        Returns:
            Dictionary with status information
        """
        try:
            # Get operation status
            operation = self.client.get_operation(name=operation_id)
            
            if operation.done:
                if operation.error:
                    return {
                        "status": "failed",
                        "error": str(operation.error),
                        "done": True
                    }
                else:
                    # Extract video URL from response
                    result = operation.response
                    video_url = self._extract_video_url(result)
                    
                    return {
                        "status": "completed",
                        "done": True,
                        "video_url": video_url,
                        "result": result
                    }
            else:
                return {
                    "status": "running",
                    "done": False,
                    "progress": "Processing..."
                }
                
        except exceptions.NotFound:
            logging.warning(f"⚠️ Operation {operation_id} not found (404)")
            return {
                "status": "not_found",
                "error": "Operation not found or expired",
                "done": True
            }
        except Exception as e:
            logging.error(f"❌ Status check failed: {e}")
            return {
                "status": "error",
                "error": str(e),
                "done": False
            }
    
    def _optimize_prompt_for_platform(self, prompt: str, platform: str) -> str:
        """Optimize prompt based on target platform"""
        
        if platform == "general":
            # General platform: focus on quality and speed
            return f"High-quality cinematic video: {prompt}. Professional lighting, smooth motion, detailed textures."
        
        elif platform == "instagram":
            # Instagram: vertical format optimization
            return f"Instagram story video: {prompt}. Vertical composition, vibrant colors, engaging motion."
        
        elif platform == "tiktok":
            # TikTok: dynamic and engaging
            return f"Dynamic TikTok video: {prompt}. Fast-paced, eye-catching, trending style."
        
        else:
            return prompt
    
    def _extract_video_url(self, response: Any) -> Optional[str]:
        """Extract video URL from VEO 3 response"""
        try:
            # Parse the response to find video URL
            if hasattr(response, 'predictions'):
                for prediction in response.predictions:
                    if 'videoUri' in prediction:
                        return prediction['videoUri']
                    if 'video_uri' in prediction:
                        return prediction['video_uri']
            
            # Alternative parsing methods
            response_dict = dict(response)
            for key in ['videoUri', 'video_uri', 'uri', 'url']:
                if key in response_dict:
                    return response_dict[key]
            
            logging.warning("⚠️ Could not extract video URL from response")
            return None
            
        except Exception as e:
            logging.error(f"❌ Error extracting video URL: {e}")
            return None

def test_improved_client():
    """Test the improved VEO 3 client"""
    client = ImprovedVEO3Client()
    
    # Test with a simple prompt
    operation_id = client.generate_video(
        prompt="A beautiful sunset over mountains",
        image_path=None,
        platform="general",
        timeout=1800  # 30 minutes
    )
    
    if operation_id:
        print(f"✅ Test generation started: {operation_id}")
        
        # Check status
        status = client.check_operation_status(operation_id)
        print(f"📊 Initial status: {status}")
        
        return operation_id
    else:
        print("❌ Test generation failed")
        return None

if __name__ == "__main__":
    test_improved_client()