
# Proper VEO 3 route handlers
from proper_veo3_client import ProperVEO3Client
from flask import request, jsonify
import logging

@app.route('/api/proper-video-generation', methods=['POST'])
def proper_video_generation():
    """Generate video using proper VEO 3 client"""
    try:
        data = request.get_json()
        prompt = data.get('prompt')
        platform = data.get('platform', 'general')
        image_path = data.get('image_path')
        
        if not prompt:
            return jsonify({'error': 'Prompt required'}), 400
        
        # Initialize proper client
        client = ProperVEO3Client()
        
        # Start long-running prediction with proper timeout
        operation_id = client.predict_long_running(
            prompt=prompt,
            image_path=image_path,
            platform=platform,
            timeout=1800  # 30 minutes
        )
        
        if operation_id:
            # Create database entry
            video_order = VideoOrder(
                title=prompt[:50],
                status=OrderStatus.IN_PRODUCTION,
                platform=platform,
                veo3_operation_id=operation_id,
                generation_settings=f"Proper VEO 3 - Platform: {platform}"
            )
            db.session.add(video_order)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'video_id': video_order.id,
                'message': 'Video generation started with proper Google Cloud implementation',
                'estimated_time': '2-3 minutes for general platform'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to start video generation'
            }), 500
            
    except Exception as e:
        logging.error(f"Proper video generation error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/proper-video-status/<int:video_id>')
def proper_video_status(video_id):
    """Check video status using proper VEO 3 client"""
    try:
        video = VideoOrder.query.get_or_404(video_id)
        
        if not video.veo3_operation_id:
            return jsonify({
                'status': 'error',
                'error': 'No operation ID found'
            })
        
        # Check status with proper client
        client = ProperVEO3Client()
        status = client.get_operation(video.veo3_operation_id)
        
        # Update database based on status
        if status.get('done'):
            if status['status'] == 'completed':
                video.status = OrderStatus.COMPLETED
                if status.get('video_url'):
                    video.generation_settings = f"Completed - URL: {status['video_url']}"
            elif status['status'] == 'failed' or status['status'] == 'not_found':
                video.status = OrderStatus.CANCELLED
                video.generation_settings = f"Failed: {status.get('error', 'Unknown error')}"
            
            db.session.commit()
        
        return jsonify({
            'video_id': video_id,
            'status': status['status'],
            'done': status.get('done', False),
            'progress': status.get('progress'),
            'video_url': status.get('video_url'),
            'error': status.get('error')
        })
        
    except Exception as e:
        logging.error(f"Proper status check error: {e}")
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500

@app.route('/api/test-proper-veo3')
def test_proper_veo3():
    """Test endpoint for proper VEO 3 implementation"""
    try:
        client = ProperVEO3Client()
        
        # Quick connectivity test
        test_prompt = "A simple test: beautiful sunset over calm water"
        operation_id = client.predict_long_running(
            prompt=test_prompt,
            platform="general",
            timeout=900  # 15 minutes for test
        )
        
        if operation_id:
            return jsonify({
                'success': True,
                'message': 'Proper VEO 3 client working correctly',
                'test_operation_id': operation_id
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Proper VEO 3 client test failed'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })
