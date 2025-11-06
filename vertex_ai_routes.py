#!/usr/bin/env python3
"""
Flask routes for Vertex AI VEO 3 video generation
"""

import os
import json
import logging
from flask import Blueprint, request, jsonify, render_template, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import VideoOrder, OrderStatus, User, db
# Import will be done locally to avoid circular imports
from app import app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create blueprint
vertex_bp = Blueprint('vertex_ai', __name__, url_prefix='/vertex-ai')

@vertex_bp.route('/')
def vertex_ai_home():
    """Vertex AI VEO 3 video generation home page"""
    return render_template('vertex_ai_generator.html')

@vertex_bp.route('/generate', methods=['GET', 'POST'])
@login_required
def generate_video():
    """Generate video using Vertex AI VEO 3"""
    
    if request.method == 'GET':
        return render_template('vertex_ai_generate.html')
    
    try:
        # Get form data
        title = request.form.get('title', 'Vertex AI Video')
        prompt = request.form.get('prompt', '')
        duration = int(request.form.get('duration', 5))
        
        # Validate duration
        if not (3 <= duration <= 30):
            flash('Duration must be between 3 and 30 seconds', 'error')
            return redirect(url_for('vertex_ai.generate_video'))
        
        # Handle file upload
        if 'image' not in request.files:
            flash('Please upload an image', 'error')
            return redirect(url_for('vertex_ai.generate_video'))
        
        file = request.files['image']
        if file.filename == '':
            flash('Please select an image file', 'error')
            return redirect(url_for('vertex_ai.generate_video'))
        
        # Save uploaded file
        if file and file.filename and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            timestamp = int(time.time())
            filename = f"{timestamp}_{filename}"
            
            upload_path = os.path.join('uploads', filename)
            os.makedirs('uploads', exist_ok=True)
            file.save(upload_path)
            
            # Create video order in database
            video_order = VideoOrder()
            video_order.title = title
            video_order.customer_email = current_user.email
            video_order.status = 'PENDING'
            video_order.generation_settings = f"Vertex AI VEO 3 - {duration}s - {prompt[:100]}..."
            
            db.session.add(video_order)
            db.session.commit()
            
            logger.info(f"🎬 Created Vertex AI video order {video_order.id} for {current_user.email}")
            
            # Start video generation in background
            try:
                from vertex_ai_video_generator import create_vertex_ai_video
                result = create_vertex_ai_video(
                    image_path=upload_path,
                    prompt=prompt,
                    video_order_id=video_order.id,
                    duration=duration
                )
                
                if result.get('success'):
                    flash(f'Video generation started! Order ID: {video_order.id}', 'success')
                    return redirect(url_for('vertex_ai.generation_status', order_id=video_order.id))
                else:
                    flash(f'Generation failed: {result.get("error")}', 'error')
                    return redirect(url_for('vertex_ai.generate_video'))
                    
            except Exception as e:
                logger.error(f"❌ Generation error: {str(e)}")
                flash(f'Generation error: {str(e)}', 'error')
                return redirect(url_for('vertex_ai.generate_video'))
        
        else:
            flash('Invalid file type. Please upload JPG, PNG, or GIF', 'error')
            return redirect(url_for('vertex_ai.generate_video'))
    
    except Exception as e:
        logger.error(f"❌ Route error: {str(e)}")
        flash(f'Error: {str(e)}', 'error')
        return redirect(url_for('vertex_ai.generate_video'))

@vertex_bp.route('/status/<int:order_id>')
@login_required
def generation_status(order_id):
    """Check generation status"""
    
    video_order = VideoOrder.query.get_or_404(order_id)
    
    # Verify ownership
    if video_order.customer_email != current_user.email:
        flash('Access denied', 'error')
        return redirect(url_for('vertex_ai.vertex_ai_home'))
    
    return render_template('vertex_ai_status.html', order=video_order)

@vertex_bp.route('/api/status/<int:order_id>')
@login_required
def api_generation_status(order_id):
    """API endpoint for generation status"""
    
    video_order = VideoOrder.query.get_or_404(order_id)
    
    # Verify ownership
    if video_order.customer_email != current_user.email:
        return jsonify({'error': 'Access denied'}), 403
    
    status_data = {
        'id': video_order.id,
        'title': video_order.title,
        'status': video_order.status.value,
        'generation_settings': video_order.generation_settings,
        'created_at': video_order.created_at.isoformat() if video_order.created_at else None,
        'completed': video_order.status == 'COMPLETED',
        'video_available': bool(video_order.generated_video_path),
        'download_url': url_for('download_customer_video', video_id=video_order.id) if video_order.generated_video_path else None
    }
    
    return jsonify(status_data)

@vertex_bp.route('/my-videos')
@login_required
def my_vertex_videos():
    """Display user's Vertex AI generated videos"""
    
    videos = VideoOrder.query.filter_by(
        customer_email=current_user.email
    ).order_by(VideoOrder.created_at.desc()).all()
    
    # Filter videos that contain 'Vertex AI' in generation settings
    vertex_videos = [video for video in videos if video.generation_settings and 'Vertex AI' in video.generation_settings]
    
    return render_template('vertex_ai_my_videos.html', videos=vertex_videos)

@vertex_bp.route('/quick-generate', methods=['POST'])
@login_required
def quick_generate():
    """Quick generation API endpoint"""
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Validate required fields
        required_fields = ['image_data', 'prompt']
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Save base64 image
        import base64
        import tempfile
        
        image_data = data['image_data'].split(',')[1]  # Remove data:image/jpeg;base64,
        image_bytes = base64.b64decode(image_data)
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as temp_file:
            temp_file.write(image_bytes)
            temp_path = temp_file.name
        
        # Create video order
        video_order = VideoOrder()
        video_order.title = data.get('title', 'Quick Vertex AI Video')
        video_order.customer_email = current_user.email
        video_order.status = 'PENDING'
        video_order.generation_settings = f"Vertex AI VEO 3 Quick - {data.get('duration', 5)}s"
        
        db.session.add(video_order)
        db.session.commit()
        
        # Start generation
        from vertex_ai_video_generator import create_vertex_ai_video
        result = create_vertex_ai_video(
            image_path=temp_path,
            prompt=data['prompt'],
            video_order_id=video_order.id,
            duration=data.get('duration', 5)
        )
        
        # Clean up temp file
        os.unlink(temp_path)
        
        if result.get('success'):
            return jsonify({
                'success': True,
                'order_id': video_order.id,
                'message': 'Video generation started'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error')
            }), 500
    
    except Exception as e:
        logger.error(f"❌ Quick generate error: {str(e)}")
        return jsonify({'error': str(e)}), 500

def allowed_file(filename):
    """Check if file extension is allowed"""
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Add import at the top
import time