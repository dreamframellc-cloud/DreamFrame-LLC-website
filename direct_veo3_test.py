"""
Direct VEO 3 Test using Google Cloud AI Platform
Test the direct aiplatform approach suggested by user
"""

import os
import sys
sys.path.append('.')

from google.cloud import aiplatform
from datetime import datetime
import json
import time

def test_direct_aiplatform_veo3():
    """Test VEO 3 using direct aiplatform approach"""
    
    print("🎬 Testing Direct AI Platform VEO 3 Access")
    print("=" * 50)
    
    try:
        # Initialize AI Platform as suggested by user
        print("🔧 Initializing AI Platform...")
        aiplatform.init(project="dreamframe", location="us-central1")
        print("✅ AI Platform initialized successfully")
        
        # Test prompt
        test_prompt = "A majestic waterfall cascading down rocky cliffs in a lush forest, cinematic nature shot"
        
        print(f"📝 Test prompt: {test_prompt}")
        print(f"⏰ Start time: {datetime.now().strftime('%H:%M:%S')}")
        
        # Try the direct endpoint approach
        print("🚀 Accessing VEO 3 endpoint directly...")
        
        try:
            endpoint = aiplatform.Endpoint("veo-3.0-generate-preview")
            print("✅ VEO 3 endpoint created")
            
            # Test prediction
            print("📡 Sending prediction request...")
            response = endpoint.predict(prompt=test_prompt)
            
            print("🎉 DIRECT PREDICTION SUCCESSFUL!")
            print(f"📊 Response type: {type(response)}")
            print(f"📋 Response content:")
            
            if hasattr(response, 'predictions'):
                print(f"Predictions: {response.predictions}")
            
            if hasattr(response, 'deployed_model_id'):
                print(f"Model ID: {response.deployed_model_id}")
            
            # Print full response
            print("📊 Full response:")
            print(json.dumps(str(response), indent=2))
            
            return {
                'success': True,
                'method': 'direct_aiplatform',
                'response': response
            }
            
        except Exception as endpoint_error:
            print(f"❌ Endpoint error: {endpoint_error}")
            
            # Try alternative approach with model name
            print("🔄 Trying alternative model access...")
            
            try:
                # Alternative: Use model directly
                model = aiplatform.Model(model_name="veo-3.0-generate-preview")
                print("✅ Model accessed directly")
                
                # Try batch prediction
                print("📡 Trying batch prediction...")
                job = model.batch_predict(
                    job_display_name="veo3_test",
                    instances=[{"prompt": test_prompt}],
                    predictions_format="jsonl"
                )
                
                print(f"🎉 BATCH PREDICTION STARTED!")
                print(f"📋 Job name: {job.name}")
                
                return {
                    'success': True,
                    'method': 'batch_prediction',
                    'job': job
                }
                
            except Exception as model_error:
                print(f"❌ Model error: {model_error}")
                return None
                
    except Exception as e:
        print(f"❌ AI Platform initialization error: {e}")
        return None

def test_alternative_veo3_access():
    """Test alternative VEO 3 access methods"""
    
    print("\n🔬 Testing Alternative VEO 3 Access Methods")
    print("-" * 45)
    
    try:
        # Initialize with explicit credentials
        print("🔐 Initializing with explicit authentication...")
        
        aiplatform.init(
            project="dreamframe", 
            location="us-central1",
            credentials=None  # Use environment credentials
        )
        
        # List available models
        print("📋 Listing available models...")
        
        try:
            models = aiplatform.Model.list()
            print(f"✅ Found {len(models)} models")
            
            # Look for VEO models
            veo_models = []
            for model in models:
                if 'veo' in str(model.display_name).lower():
                    veo_models.append(model)
                    print(f"🎥 VEO Model: {model.display_name}")
            
            if veo_models:
                print(f"✅ Found {len(veo_models)} VEO models")
                return veo_models
            else:
                print("⚠️  No VEO models found in listing")
                
        except Exception as list_error:
            print(f"❌ Model listing error: {list_error}")
            
        # Try direct prediction service
        print("🔄 Trying prediction service...")
        
        from google.cloud import aiplatform_v1
        
        client = aiplatform_v1.PredictionServiceClient()
        
        # Construct endpoint path
        endpoint_path = client.endpoint_path(
            project="dreamframe",
            location="us-central1", 
            endpoint="veo-3.0-generate-preview"
        )
        
        print(f"📍 Endpoint path: {endpoint_path}")
        
        # Create prediction request
        instance = {"prompt": "Test video generation"}
        instances = [instance]
        
        request = aiplatform_v1.PredictRequest(
            endpoint=endpoint_path,
            instances=instances
        )
        
        print("📡 Sending prediction service request...")
        response = client.predict(request=request)
        
        print("🎉 PREDICTION SERVICE SUCCESS!")
        print(f"📊 Response: {response}")
        
        return {
            'success': True,
            'method': 'prediction_service',
            'response': response
        }
        
    except Exception as e:
        print(f"❌ Alternative access error: {e}")
        return None

def main():
    """Test direct AI Platform VEO 3 access"""
    
    print("🚀 Direct Google Cloud AI Platform VEO 3 Test")
    print("=" * 55)
    
    # Test direct approach
    result1 = test_direct_aiplatform_veo3()
    
    # Test alternatives
    result2 = test_alternative_veo3_access()
    
    print("\n" + "=" * 55)
    print("📊 DIRECT AI PLATFORM TEST RESULTS")
    
    if result1:
        print("🎉 SUCCESS with direct AI Platform approach!")
        print(f"✅ Method: {result1.get('method', 'unknown')}")
        
        if result1['method'] == 'batch_prediction':
            print("✅ Batch prediction job started")
            print("⏱️  Monitor job for completion")
        else:
            print("✅ Direct prediction completed")
            
    elif result2:
        print("🎉 SUCCESS with alternative method!")
        print(f"✅ Method: {result2.get('method', 'unknown')}")
        
    else:
        print("⚠️  No successful connections established")
        print("📋 This may indicate:")
        print("   - VEO 3 requires different access method")
        print("   - Model name or endpoint format incorrect")
        print("   - Additional permissions needed")
    
    print("\n💡 USER SUGGESTION ANALYSIS:")
    print("   Your direct aiplatform.Endpoint approach is promising")
    print("   This method bypasses the REST API complexity")
    print("   Should provide better video access control")
    print("   May need correct endpoint identifier format")

if __name__ == "__main__":
    main()