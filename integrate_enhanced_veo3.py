"""
Integrate Enhanced VEO 3 Manager into the main application
"""

from app import app, db
from models import VideoOrder, OrderStatus
from enhanced_veo3_manager import EnhancedVEO3Manager, clean_stuck_operations
import logging

def upgrade_to_enhanced_veo3():
    """Replace current VEO 3 system with enhanced manager"""
    
    print("🔄 UPGRADING TO ENHANCED VEO 3 SYSTEM")
    print("=" * 45)
    
    # Clean stuck operations first
    clean_stuck_operations()
    
    # Initialize enhanced manager
    enhanced_manager = EnhancedVEO3Manager()
    
    # Test the system
    test_prompt = "A beautiful mountain landscape with gentle flowing water"
    
    print(f"\n🧪 Testing Enhanced VEO 3 Manager")
    operation_id = enhanced_manager.generate_video_with_retry(
        prompt=test_prompt,
        platform="general",
        max_retries=2
    )
    
    if operation_id:
        print(f"✅ Test generation successful!")
        print(f"🔄 Operation ID: {operation_id}")
        
        # Check initial status
        status = enhanced_manager.check_operation_with_fallback(operation_id)
        print(f"📊 Initial status: {status['status']}")
        
        # Create a test video entry in database
        with app.app_context():
            test_video = VideoOrder(
                title="Enhanced VEO 3 Test",
                status=OrderStatus.IN_PRODUCTION,
                platform="general",
                veo3_operation_id=operation_id,
                generation_settings="Enhanced VEO 3 Manager test generation"
            )
            db.session.add(test_video)
            db.session.commit()
            
            print(f"✅ Test video created in database (ID: {test_video.id})")
        
        return operation_id
    else:
        print(f"❌ Test generation failed")
        return None

def create_enhanced_route_handler():
    """Create route handler using enhanced VEO 3 manager"""
    
    route_code = '''
# Enhanced VEO 3 route handler
from enhanced_veo3_manager import EnhancedVEO3Manager

@app.route('/api/enhanced-video-generation', methods=['POST'])
def enhanced_video_generation():
    """Generate video using enhanced VEO 3 manager"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        platform = data.get('platform', 'general')
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        # Initialize enhanced manager
        manager = EnhancedVEO3Manager()
        
        # Generate video with retry logic
        operation_id = manager.generate_video_with_retry(
            prompt=prompt,
            platform=platform,
            max_retries=3
        )
        
        if operation_id:
            # Create database entry
            video_order = VideoOrder(
                title=prompt[:50],
                status=OrderStatus.IN_PRODUCTION,
                platform=platform,
                veo3_operation_id=operation_id,
                generation_settings=f"Enhanced VEO 3 - Platform: {platform}"
            )
            db.session.add(video_order)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'video_id': video_order.id,
                'message': 'Video generation started with enhanced reliability'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start video generation after retries'
            }), 500
            
    except Exception as e:
        logging.error(f"Enhanced video generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/enhanced-video-status/<int:video_id>')
def enhanced_video_status(video_id):
    """Check video status using enhanced manager"""
    try:
        video = VideoOrder.query.get_or_404(video_id)
        
        if not video.veo3_operation_id:
            return jsonify({
                'status': 'error',
                'error': 'No operation ID found'
            })
        
        # Check status with enhanced manager
        manager = EnhancedVEO3Manager()
        status = manager.check_operation_with_fallback(video.veo3_operation_id)
        
        # Update database if completed or failed
        if status.get('done'):
            if status['status'] == 'completed':
                video.status = OrderStatus.COMPLETED
                if status.get('video_url'):
                    video.generation_settings = f"Completed - URL: {status['video_url']}"
            elif status['status'] == 'failed' or status['status'] == 'not_found':
                video.status = OrderStatus.FAILED
                video.generation_settings = f"Failed: {status.get('error', 'Unknown error')}"
            
            db.session.commit()
        
        return jsonify({
            'video_id': video_id,
            'status': status['status'],
            'done': status.get('done', False),
            'video_url': status.get('video_url'),
            'error': status.get('error')
        })
        
    except Exception as e:
        logging.error(f"Enhanced status check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500
'''
    
    with open('enhanced_veo3_routes.py', 'w') as f:
        f.write(route_code)
    
    print("✅ Enhanced VEO 3 route handlers created")

if __name__ == "__main__":
    # Upgrade to enhanced system
    test_operation = upgrade_to_enhanced_veo3()
    
    # Create route handlers
    create_enhanced_route_handler()
    
    print(f"\n🎯 ENHANCED VEO 3 UPGRADE COMPLETE")
    print(f"✅ Enhanced manager with retry logic ready")
    print(f"✅ Better timeout and error handling implemented")
    print(f"✅ Stuck operations cleaned up")
    print(f"✅ Route handlers created")
    
    if test_operation:
        print(f"🧪 Test operation running: {test_operation}")
        print(f"💡 Use enhanced_veo3_manager.py for reliable video generation")
    
    print(f"\n📋 NEXT STEPS:")
    print(f"1. Import enhanced_veo3_manager in your main routes")
    print(f"2. Replace current VEO 3 calls with EnhancedVEO3Manager")
    print(f"3. Use generate_video_with_retry() for new generations")
    print(f"4. Use check_operation_with_fallback() for status checks")