#!/usr/bin/env python3
"""
VEO 2 Integration for DreamFrame Platform
Interim solution while awaiting VEO 3 approval
"""

import os
import json
import time
import logging
from typing import Optional, Dict, Any

try:
    from google.cloud import aiplatform
    from google.oauth2 import service_account
    from google.api_core import retry
    from google.api_core.exceptions import GoogleAPIError
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError as e:
    print(f"Google Cloud libraries not available: {e}")
    GOOGLE_CLOUD_AVAILABLE = False

class VEO2VideoGenerator:
    """VEO 2 video generation client for DreamFrame platform"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.project_id = os.environ.get('GOOGLE_CLOUD_PROJECT_ID')
        self.location = 'us-central1'  # VEO 2 available region
        
        # Check if Google Cloud is available
        if not GOOGLE_CLOUD_AVAILABLE:
            self.logger.error("Google Cloud libraries not available")
            return
        
        # VEO 2 model configurations (updated model IDs based on research)
        self.veo2_models = {
            'standard': 'veo-2.0-generate-001',
            'fast': 'veo-2.0-generate-001'  # Same model, different parameters
        }
        
        # Initialize Vertex AI
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize Google Cloud Vertex AI client"""
        if not GOOGLE_CLOUD_AVAILABLE:
            return
            
        try:
            # Use service account credentials from environment
            credentials_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            if credentials_json:
                # Handle both file path and JSON string
                if os.path.isfile(credentials_json):
                    credentials = service_account.Credentials.from_service_account_file(credentials_json)
                else:
                    # Assume it's JSON content
                    credentials_info = json.loads(credentials_json)
                    credentials = service_account.Credentials.from_service_account_info(credentials_info)
            else:
                credentials = None
            
            # Initialize Vertex AI
            aiplatform.init(
                project=self.project_id,
                location=self.location,
                credentials=credentials
            )
            
            self.logger.info(f"VEO 2 client initialized for project {self.project_id} in {self.location}")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize VEO 2 client: {str(e)}")
            raise
    
    @retry.Retry(
        predicate=retry.if_exception_type(GoogleAPIError),
        initial=1.0,
        maximum=60.0,
        multiplier=2.0,
        timeout=300.0
    )
    def generate_video(
        self, 
        prompt: str, 
        duration: int = 5, 
        model_type: str = 'fast',
        aspect_ratio: str = '16:9'
    ) -> Optional[Dict[str, Any]]:
        """
        Generate video using VEO 2
        
        Args:
            prompt: Text description for video generation
            duration: Video duration in seconds (2-10 for VEO 2)
            model_type: 'standard' or 'fast'
            aspect_ratio: Video aspect ratio ('16:9', '9:16', '1:1')
        
        Returns:
            Dictionary with generation result or None if failed
        """
        
        try:
            model_name = self.veo2_models.get(model_type, 'veo-2.0-generate-fast')
            
            self.logger.info(f"Starting VEO 2 generation: {prompt[:50]}... (Duration: {duration}s)")
            
            # Prepare the request payload
            request_payload = {
                "instances": [{
                    "prompt": prompt,
                    "parameters": {
                        "duration": duration,
                        "aspect_ratio": aspect_ratio,
                        "quality": "standard",
                        "seed": int(time.time()) % 1000000  # Random seed
                    }
                }]
            }
            
            # Get the model endpoint
            endpoint_name = f"projects/{self.project_id}/locations/{self.location}/publishers/google/models/{model_name}"
            
            # Make prediction request
            endpoint = aiplatform.Endpoint(endpoint_name=endpoint_name)
            response = endpoint.predict(
                instances=request_payload["instances"],
                parameters=request_payload.get("parameters", {})
            )
            
            if response and hasattr(response, 'predictions') and response.predictions:
                prediction = response.predictions[0]
                
                result = {
                    'success': True,
                    'operation_id': prediction.get('name', f'veo2_{int(time.time())}'),
                    'status': 'completed',
                    'video_url': prediction.get('video_uri') or prediction.get('uri'),
                    'model_used': model_name,
                    'duration': duration,
                    'prompt': prompt,
                    'generated_at': time.time()
                }
                
                self.logger.info(f"VEO 2 generation successful: {result['operation_id']}")
                return result
            
            else:
                self.logger.error("VEO 2 response missing predictions")
                return None
                
        except GoogleAPIError as e:
            self.logger.error(f"VEO 2 API error: {str(e)}")
            
            # Check if it's a model availability issue
            if "not found" in str(e).lower() or "404" in str(e):
                self.logger.warning("VEO 2 model not available - may need access request")
                return {
                    'success': False,
                    'error': 'model_not_available',
                    'message': 'VEO 2 model not accessible in current project'
                }
            
            return None
            
        except Exception as e:
            self.logger.error(f"Unexpected VEO 2 error: {str(e)}")
            return None
    
    def generate_customer_video(
        self,
        prompt: str,
        duration: int = 5,
        image_path: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Generate customer video with VEO 2 (optimized for DreamFrame)
        
        Args:
            prompt: Customer's video description
            duration: Video length in seconds
            image_path: Optional source image path
        
        Returns:
            Generation result dictionary
        """
        
        # Optimize prompt for VEO 2
        optimized_prompt = self._optimize_prompt_for_veo2(prompt)
        
        # Use fast model for better speed
        result = self.generate_video(
            prompt=optimized_prompt,
            duration=min(duration, 8),  # VEO 2 max duration
            model_type='fast',
            aspect_ratio='16:9'
        )
        
        if result and result.get('success'):
            self.logger.info(f"VEO 2 customer video generated successfully")
            return result
        else:
            self.logger.error("VEO 2 customer video generation failed")
            return result
    
    def _optimize_prompt_for_veo2(self, prompt: str) -> str:
        """Optimize prompt for VEO 2 capabilities"""
        
        # VEO 2 prompt enhancements
        enhancements = {
            'quality_modifiers': [
                'high quality', 'detailed', 'professional',
                'cinematic', 'smooth motion'
            ],
            'technical_specs': [
                '16:9 aspect ratio', 'steady camera',
                'good lighting', 'clear focus'
            ]
        }
        
        # Add quality enhancements if not present
        enhanced_prompt = prompt
        if not any(mod in prompt.lower() for mod in enhancements['quality_modifiers']):
            enhanced_prompt = f"High quality, cinematic {prompt}"
        
        # Ensure proper formatting
        enhanced_prompt = enhanced_prompt.strip()
        if not enhanced_prompt.endswith('.'):
            enhanced_prompt += '.'
        
        return enhanced_prompt
    
    def check_availability(self) -> Dict[str, Any]:
        """Check VEO 2 model availability"""
        
        try:
            # Test with a simple prompt
            test_result = self.generate_video(
                prompt="A simple test video of a sunset",
                duration=3,
                model_type='fast'
            )
            
            if test_result and test_result.get('success'):
                return {
                    'available': True,
                    'models': list(self.veo2_models.keys()),
                    'test_result': 'success'
                }
            elif test_result and test_result.get('error') == 'model_not_available':
                return {
                    'available': False,
                    'error': 'VEO 2 requires access request',
                    'models': list(self.veo2_models.keys())
                }
            else:
                return {
                    'available': False,
                    'error': 'Unknown VEO 2 issue',
                    'models': list(self.veo2_models.keys())
                }
                
        except Exception as e:
            return {
                'available': False,
                'error': str(e),
                'models': list(self.veo2_models.keys())
            }

# Initialize VEO 2 generator
veo2_generator = VEO2VideoGenerator()

def generate_veo2_video(prompt: str, duration: int = 5) -> Optional[Dict[str, Any]]:
    """Main function for VEO 2 video generation"""
    return veo2_generator.generate_customer_video(prompt, duration)

if __name__ == "__main__":
    # Test VEO 2 availability
    print("🎬 Testing VEO 2 Integration")
    print("=" * 40)
    
    availability = veo2_generator.check_availability()
    print(f"VEO 2 Available: {availability['available']}")
    
    if availability['available']:
        print("✅ VEO 2 ready for DreamFrame integration")
        
        # Test generation
        test_prompt = "A beautiful sunset over calm waters with gentle waves"
        result = generate_veo2_video(test_prompt, 5)
        
        if result and result.get('success'):
            print(f"✅ Test video generated: {result['operation_id']}")
        else:
            print("❌ Test video generation failed")
    
    else:
        print(f"❌ VEO 2 not available: {availability.get('error', 'Unknown error')}")
        print("📋 Next step: Request VEO 2 access from Google")