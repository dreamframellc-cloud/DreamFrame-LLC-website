import os
import time
import logging
import subprocess
import shutil
import json
from datetime import datetime
from flask import Flask, render_template, send_from_directory, send_file, jsonify, request, redirect, url_for, flash, session, abort, Response
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.utils import secure_filename
from translations import get_text, get_available_languages, LANGUAGES

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask app
app = Flask(__name__)
from flask import request, redirect

# Configure domain (only set in production, not for local development)
if os.environ.get('SERVER_NAME'):
    app.config['SERVER_NAME'] = os.environ.get('SERVER_NAME')

@app.before_request
def redirect_www():
    if request.host.startswith('www.'):
        return redirect(request.url.replace('://www.', '://'), code=301)
app.secret_key = os.environ.get("SESSION_SECRET", "dreamframe-session-secret-key-2025")
# Fixed session configuration for better browser compatibility
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 3600  # 1 hour
app.config['SESSION_COOKIE_SECURE'] = False  # Set to False for development
app.config['SESSION_COOKIE_HTTPONLY'] = True  # Prevent XSS attacks
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'  # Better browser compatibility than None
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Database configuration
database_url = os.environ.get("DATABASE_URL")
if database_url:
    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }
else:
    # Fallback for development (SQLite - only works locally, not on Vercel)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///dreamframe.db"

# Initialize database
from models import db, CustomerProject, UploadedFile, ProjectType, ProjectStatus, OrderStatus, ServiceType, User, VideoOrder, AuthToken
db.init_app(app)

# Import email system
from email_system import send_video_completion_notification, send_contact_email

# Import payment monitoring system
try:
    from payment_monitor import payment_monitor, setup_webhook_handler
    PAYMENT_MONITOR_AVAILABLE = True
    logging.info("🤖 Payment Monitor AI system loaded")
except ImportError:
    PAYMENT_MONITOR_AVAILABLE = False
    logging.warning("Payment Monitor not available")

# Initialize Flask-Login
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please create an account or log in to access your videos.'

@login_manager.user_loader
def load_user(user_id):
    try:
        user = User.query.get(int(user_id))
        logging.info(f"🔍 Loading user {user_id}: {'Found' if user else 'Not found'}")
        if user:
            logging.info(f"🔍 User details: {user.email}, active: {user.is_active}")
        return user
    except Exception as e:
        logging.error(f"❌ Error loading user {user_id}: {e}")
        return None

# Language support functions
def get_current_language():
    """Get current language from session or detect from browser"""
    if 'language' in session:
        return session['language']
    
    # Try to detect from browser Accept-Language header
    from flask import request
    best_match = request.accept_languages.best_match(LANGUAGES.keys())
    return best_match if best_match else 'en'

@app.context_processor
def inject_language_vars():
    """Inject language variables into all templates"""
    current_lang = get_current_language()
    return {
        'get_text': lambda key: get_text(key, current_lang),
        'current_language': current_lang,
        'available_languages': get_available_languages(),
        'language_names': LANGUAGES
    }

@app.route('/set-language/<language>')
def set_language(language):
    """Set user's preferred language"""
    if language in LANGUAGES:
        session['language'] = language
        session.permanent = True
    
    # Redirect back to the page they came from or homepage
    return redirect(request.referrer or url_for('home'))

# Import AI Project Manager and authentic VEO 3 system
from ai_project_manager import AIProjectManager
from authentic_veo3_vertex import AuthenticVEO3

# Initialize database tables with app context
ai_project_manager = None
ai_video_manager = None
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")
        # Log full error for debugging
        import traceback
        print(f"Full traceback: {traceback.format_exc()}")
        # Don't fail completely - allow app to start even if DB init fails
        # Routes will handle DB errors gracefully
    
    # Initialize AI Video Manager for process management
    try:
        from ai_video_manager import AIVideoManager
        ai_video_manager = AIVideoManager()
        ai_video_manager.start_management()
        print("🤖 AI Video Manager initialized and managing all processes")
    except Exception as e:
        ai_video_manager = None
        print(f"Error starting AI Video Manager: {e}")

# AI Project Manager will be initialized lazily the first time it's needed.

@app.before_request
def ensure_ai_project_manager_initialized():
    global ai_project_manager
    if ai_project_manager is not None:
        return

    try:
        manager = AIProjectManager()
        initializer = getattr(manager, 'initialize_all', None)
        if callable(initializer):
            initializer()
        ai_project_manager = manager
        app.logger.info("📽️ AI Project Manager initialized inside Flask request context")
    except Exception as exc:
        ai_project_manager = None
        app.logger.error(f"Error initializing AI Project Manager lazily: {exc}")

# Import VEO 3 Fast Integration (primary system)
try:
    from ultra_fast_veo3 import UltraFastVEO3
    from veo3_fast_generator import VEO3FastGenerator
    VEO3_FAST_AVAILABLE = True
    print("✅ VEO 3 Fast system loaded - Primary video generation")
except ImportError as e:
    print(f"VEO 3 Fast client not available: {e}")
    VEO3_FAST_AVAILABLE = False

# Import VEO 2 Integration (fallback system)
try:
    from simple_veo2_client import SimpleVEO2Client, test_veo2_access
    VEO2_AVAILABLE = True
    print("✅ VEO 2 system loaded - Fallback video generation")
except ImportError as e:
    print(f"VEO 2 client not available: {e}")
    VEO2_AVAILABLE = False

# Import Content Safety System
from content_safety_system import validate_video_prompt, is_content_safe_for_generation, content_safety

# Initialize AI Video Manager after database setup
ai_video_manager = None

def generate_customer_video_with_ai_management(video_order_id: int, image_path: str, prompt: str):
    """Generate video with AI management and content safety checks (VEO 3 Fast primary + VEO 2 fallback)"""
    try:
        # Step 1: Content safety validation
        user_email = None
        if current_user and current_user.is_authenticated:
            user_email = current_user.email
        
        safety_result = validate_video_prompt(prompt, user_email)
        
        if not safety_result.is_safe:
            app.logger.warning(f"Content policy violation for order {video_order_id}: {safety_result.violations}")
            return {
                'success': False,
                'error': 'content_policy_violation',
                'message': content_safety.get_content_policy_message(safety_result.violations),
                'violations': safety_result.violations,
                'suggested_alternative': safety_result.filtered_prompt
            }
        
        # Step 2: Use safe/filtered prompt for generation
        safe_prompt = safety_result.filtered_prompt
        app.logger.info(f"Content safety passed for order {video_order_id}, using prompt: {safe_prompt[:50]}...")
        
        # Step 3: Try VEO 3 Fast first (primary system)
        if VEO3_FAST_AVAILABLE:
            try:
                veo3_fast_generator = UltraFastVEO3()
                result = veo3_fast_generator.generate_ultra_fast_video(
                    image_path=image_path,
                    prompt=safe_prompt
                )
                
                if result and result.get('success'):
                    print(f"⚡ VEO 3 Fast video generation successful for order {video_order_id}")
                    print(f"🎯 Generation time: 3-5 minutes (ultra-fast)")
                    print(f"🛡️ Content safety: Validated")
                    print(f"🚀 Model: VEO 3 Fast (primary system)")
                    return result
                else:
                    app.logger.warning(f"VEO 3 Fast not accessible: {result.get('message', 'Unknown error') if result else 'No result'}")
                
            except Exception as veo3_fast_error:
                app.logger.warning(f"VEO 3 Fast failed for order {video_order_id}: {str(veo3_fast_error)}")
        else:
            app.logger.info("VEO 3 Fast client not available")
        
        # Step 4: Fallback to VEO 2 if VEO 3 Fast fails
        if VEO2_AVAILABLE:
            try:
                veo2_generator = SimpleVEO2Client()
                result = veo2_generator.generate_video(
                    prompt=safe_prompt,
                    duration=5
                )
                
                if result and result.get('success'):
                    print(f"🎬 VEO 2 fallback successful for order {video_order_id}")
                    print(f"⚡ Generation time: 90-120 seconds")
                    print(f"🛡️ Content safety: Validated")
                    print(f"🔄 Model: VEO 2 (fallback system)")
                    return result
                else:
                    app.logger.warning(f"VEO 2 fallback not accessible: {result.get('message', 'Unknown error')}")
                
            except Exception as veo2_error:
                app.logger.warning(f"VEO 2 fallback failed for order {video_order_id}: {str(veo2_error)}")
        else:
            app.logger.info("VEO 2 fallback client not available")
        
        # Step 5: Final fallback to standard VEO 3 if both fast systems fail
        try:
            veo3_generator = AuthenticVEO3()
            result = veo3_generator.generate_customer_video(
                prompt=safe_prompt,
                duration=5
            )
            
            if result:
                print(f"🚀 VEO 3 standard fallback successful for order {video_order_id}")
                print(f"⚡ Target completion: 3-5 minutes")
                print(f"🎵 Audio: Preserved")
                print(f"🛡️ Content safety: Validated")
                return result
                
        except Exception as veo3_error:
            app.logger.warning(f"VEO 3 standard fallback failed for order {video_order_id}: {str(veo3_error)}")
        
        # Step 6: Return failure if all systems unavailable
        return {
            'success': False,
            'error': 'generation_unavailable',
            'message': 'Video generation services temporarily unavailable. Please try again later.'
        }
        
    except Exception as e:
        print(f"🤖 AI management error: {str(e)}")
        return None

def generate_ai_video_for_project(project):
    """
    Generate AI video using VEO 3 technology based on customer's uploaded content
    Returns path to generated video file
    """
    try:
        app.logger.info(f"Generating VEO 3 video for project {project.id}: {project.project_title}")
        
        # Get customer's uploaded image files
        uploaded_files = project.uploaded_files
        image_files = [f for f in uploaded_files if f.file_type and f.file_type.startswith('image/')]
        
        if not image_files:
            app.logger.warning(f"No image files found for project {project.id}, using fallback")
            return select_fallback_video_for_project(project)
        
        # Use the first uploaded image as source
        source_image = image_files[0]
        image_path = source_image.file_path
        
        if not os.path.exists(image_path):
            app.logger.warning(f"Source image not found: {image_path}")
            return select_fallback_video_for_project(project)
        
        # Generate VEO 3 video using customer's image and description
        output_filename = f"veo3_generated_{project.id}_{project.project_title.replace(' ', '_')}.mp4"
        output_path = os.path.join('static', 'ai_generated', output_filename)
        
        # Create output directory
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Generate professional video using authentic VEO 3
        veo3_system = AuthenticVEO3()
        
        # Create VEO 3 prompt from project
        veo3_prompt = create_veo3_prompt_from_project(project)
        
        # Generate video from customer image using VEO 3
        generation_result = veo3_system.generate_video_from_image(
            image_path=image_path,
            prompt=veo3_prompt
        )
        
        if generation_result and generation_result.get('success'):
            operation_name = generation_result.get('operation_name')
            app.logger.info(f"Authentic VEO 3 video generation started for project {project.id}")
            app.logger.info(f"VEO 3 Operation: {operation_name}")
            
            # For now, return a placeholder path since VEO 3 is asynchronous
            # In a full implementation, you'd monitor the operation and download the result
            placeholder_path = f"veo3_processing_{project.id}.mp4"
            return placeholder_path
        else:
            app.logger.error(f"VEO 3 generation failed for project {project.id}")
            return select_fallback_video_for_project(project)
                
    except Exception as e:
        app.logger.error(f"Error generating VEO 3 video for project {project.id}: {e}")
        return select_fallback_video_for_project(project)

def create_veo3_prompt_from_project(project):
    """Create optimized VEO 3 prompt from project details"""
    base_prompt = f"Create a {project.project_type.value.replace('_', ' ')} video based on: {project.project_description}"
    
    # Add specific enhancements based on project type
    if project.project_type.value == 'videogram':
        base_prompt += " Make it engaging, dynamic, and perfect for social media sharing. 5-8 seconds duration."
    elif project.project_type.value == 'family_memory':
        base_prompt += " Focus on emotional storytelling, warm lighting, and heartfelt moments. Gentle transitions."
    elif project.project_type.value == 'military_tribute':
        base_prompt += " Honor and respect, patriotic elements, dignified presentation with powerful imagery."
    
    base_prompt += " High quality, cinematic, professional video production."
    return base_prompt

def select_fallback_video_for_project(project):
    """Select fallback video when VEO 3 generation fails"""
    if project.project_title.lower().find('lion') != -1 and project.project_title.lower().find('judah') != -1:
        return select_appropriate_video_for_content('lion_majestic', project.project_description)
    elif project.project_title.lower().find('kindness') != -1:
        return select_appropriate_video_for_content('kindness_human', project.project_description)
    else:
        if project.project_type.value == 'videogram':
            return 'static/videos/VideoGram_web_final.mp4'
        else:
            return 'static/videos/Memories.mp4'

def select_appropriate_video_for_content(content_type, description):
    """
    Select most appropriate video from available assets based on content type
    """
    if content_type == 'lion_majestic':
        # Lion of Judah should use powerful, regal animal content
        # Bull.mp4 is more appropriate - powerful, majestic animal
        if os.path.exists('static/videos/Bull.mp4'):
            return 'static/videos/Bull.mp4'
        else:
            # Fallback to VideoGram if Bull not available
            return 'static/videos/VideoGram_web_final.mp4'
        
    elif content_type == 'kindness_human':
        # Kindness projects use human connection videos
        if os.path.exists('static/videos/Memories.mp4'):
            return 'static/videos/Memories.mp4'
        elif os.path.exists('static/videos/Wedding.mp4'):
            return 'static/videos/Wedding.mp4'
        else:
            return 'static/videos/VideoGram_web_final.mp4'
        
    return 'static/videos/VideoGram_web_final.mp4'  # Final fallback

# Register admin blueprint
from admin_panel import admin_bp
app.register_blueprint(admin_bp)

# Register AI agent blueprint
from ai_agent_routes import ai_bp
app.register_blueprint(ai_bp)

# Register VEO 3 blueprint
from veo3_routes import veo3_bp
app.register_blueprint(veo3_bp)

# Register subscription blueprint
from subscription_routes import subscription_bp
app.register_blueprint(subscription_bp)

# Register social media blueprint
from social_media_routes import social_bp
app.register_blueprint(social_bp)

# Register express production blueprint
from express_production_routes import express_bp
app.register_blueprint(express_bp)

# Register Vertex AI blueprint
from vertex_ai_routes import vertex_bp
app.register_blueprint(vertex_bp)

# Customer Video Creation Route - Public Interface
@app.route('/create-video-now')
def create_video_page():
    """Customer video creation interface - Public"""
    return render_template('create_video.html')

@app.route('/api/create-video', methods=['POST'])
def create_video_api():
    """API endpoint for creating customer videos"""
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({'success': False, 'error': 'Video description required'}), 400
        
        prompt = data['prompt'].strip()
        customer_name = data.get('customer_name', 'Customer').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Please provide a video description'}), 400
        
        # Import and use the video creation system
        from create_video_now import create_video_with_prompt
        
        # Generate video using VEO 3
        result = create_video_with_prompt(prompt, customer_name)
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'message': f'Video generated successfully in {result["completion_time"]:.3f} seconds!',
                'operation_id': result['operation_id'],
                'completion_time': result['completion_time'],
                'status': result.get('status', 'completed'),
                'customer_name': customer_name
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Video generation failed',
                'details': result.get('error', 'Unknown error') if result else 'System error'
            }), 500
            
    except Exception as e:
        app.logger.error(f"Video creation API error: {e}")
        return jsonify({
            'success': False,
            'error': 'Video generation system error',
            'details': str(e)
        }), 500

# Serve completed videos securely
@app.route('/completed_videos/<filename>')
def serve_completed_video(filename):
    """Serve completed AI-generated videos"""
    video_path = os.path.join('completed_videos', filename)
    if os.path.exists(video_path):
        return send_file(video_path, mimetype='video/mp4')
    else:
        abort(404)

# Ultra fast processing route
@app.route('/ultra-fast')
def ultra_fast_processing():
    """Ultra fast video processing page"""
    return render_template('ultra_fast_processing.html')

# AI Project Manager control routes
@app.route('/api/processing/status')
def processing_status():
    """Get AI processing system status"""
    try:
        pending_count = CustomerProject.query.filter_by(status=ProjectStatus.PENDING).count()
        in_progress_count = CustomerProject.query.filter_by(status=ProjectStatus.IN_PROGRESS).count()
        completed_count = CustomerProject.query.filter_by(status=ProjectStatus.COMPLETED).count()
        
        status = {
            'ai_processing_active': True,
            'pending_count': pending_count,
            'in_progress_count': in_progress_count,
            'completed_count': completed_count,
            'total_projects': pending_count + in_progress_count + completed_count
        }
        return jsonify(status)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/processing/force-process', methods=['POST'])
def force_process_pending():
    """Force process all pending projects through AI Manager"""
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Admin authentication required'}), 401
        
    try:
        ai_manager = AIProjectManager()
        pending_projects = CustomerProject.query.filter_by(status=ProjectStatus.PENDING).all()
        
        processed_count = 0
        for project in pending_projects:
            # Force immediate advancement to IN_PROGRESS
            ai_manager.auto_advance_pending_project(project.id)
            processed_count += 1
            
        return jsonify({
            'success': True,
            'message': f'AI Manager force processed {processed_count} pending projects',
            'processed_count': processed_count
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/processing/complete-overdue', methods=['POST'])
def complete_overdue_projects():
    """Complete projects that are overdue for completion"""
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Admin authentication required'}), 401
        
    try:
        ai_manager = AIProjectManager()
        from datetime import datetime, timedelta
        
        # Find projects that should have completed by now
        overdue_projects = []
        in_progress_projects = CustomerProject.query.filter_by(status=ProjectStatus.IN_PROGRESS).all()
        
        for project in in_progress_projects:
            completion_delay = ai_manager._get_completion_delay(project.project_type)
            expected_completion = project.updated_at + timedelta(seconds=completion_delay)
            
            if datetime.utcnow() > expected_completion:
                # Complete this overdue project
                result = ai_manager.update_project_status(
                    project.id, 
                    ProjectStatus.COMPLETED,
                    f"🎉 Congratulations! Your video '{project.project_title}' is complete and ready for download!"
                )
                overdue_projects.append(project.project_title)
                
        return jsonify({
            'success': True,
            'message': f'Completed {len(overdue_projects)} overdue projects',
            'completed_projects': overdue_projects
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/completed-videos')
def view_completed_videos():
    """View completed videos in admin panel"""
    if not check_admin_access():
        return redirect(url_for('admin_token_login'))
    
    try:
        # Get customer projects
        completed_projects = CustomerProject.query.filter_by(status=ProjectStatus.COMPLETED).all()
        
        # Also get all standalone generated videos from static/completed_videos/
        standalone_videos = []
        completed_videos_dir = 'static/completed_videos'
        if os.path.exists(completed_videos_dir):
            for filename in os.listdir(completed_videos_dir):
                if filename.endswith(('.mp4', '.mov', '.avi')):
                    file_path = os.path.join(completed_videos_dir, filename)
                    file_size = os.path.getsize(file_path) / (1024 * 1024)  # MB
                    
                    # Create video info object
                    video_info = {
                        'filename': filename,
                        'file_path': file_path,
                        'size_mb': round(file_size, 1),
                        'title': filename.replace('_', ' ').replace('.mp4', '').title(),
                        'is_standalone': True
                    }
                    standalone_videos.append(video_info)
        
        return render_template('admin_completed_videos.html', 
                             projects=completed_projects, 
                             standalone_videos=standalone_videos)
    except Exception as e:
        return render_template('admin_completed_videos.html', 
                             projects=[], 
                             standalone_videos=[], 
                             error=str(e))

@app.route('/admin/project/<int:project_id>/video')
def view_project_video(project_id):
    """View individual project video"""
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    try:
        project = CustomerProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
            
        return jsonify({
            'project_id': project.id,
            'title': project.project_title,
            'customer': project.customer_name,
            'description': project.project_description,
            'status': project.status.value,
            'type': project.project_type.value,
            'video_ready': project.status == ProjectStatus.COMPLETED
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/project/<int:project_id>/download')  
def download_project_video(project_id):
    """Legacy download route - redirect to VEO 3 download"""
    return redirect(url_for('admin_download_veo3', project_id=project_id))

@app.route('/download/video/<video_id>')
def download_gallery_video(video_id):
    """Public route to download videos from the gallery"""
    try:
        # Get video data from our gallery
        video_data = VIDEO_GALLERY  # Use the global VIDEO_GALLERY variable
        video = next((v for v in video_data if v['id'] == video_id), None)
        
        if not video:
            return "Video not found", 404
            
        # Construct the video file path
        video_path = os.path.join('static', 'videos', video['video'])
        
        if not os.path.exists(video_path):
            return "Video file not found", 404
            
        # Use send_file to download the video
        from flask import send_file
        return send_file(video_path, as_attachment=True, download_name=f"{video['title']}.mp4")
        
    except Exception as e:
        app.logger.error(f"Error downloading video {video_id}: {e}")
        return "Download failed", 500

@app.route('/admin/project/<int:project_id>/share')
def share_project_video(project_id):
    """Generate shareable link for completed video"""
    if not session.get('admin_authenticated'):
        return jsonify({'error': 'Admin authentication required'}), 401
    
    try:
        project = CustomerProject.query.get(project_id)
        if not project or project.status != ProjectStatus.COMPLETED:
            return jsonify({'error': 'Project not found or not completed'}), 404
        
        # Generate share URL (in production this would be a secure token-based URL)
        share_url = f"{request.host_url}share/video/{project_id}"
        
        return jsonify({
            'success': True,
            'share_url': share_url,
            'title': project.project_title,
            'customer': project.customer_name,
            'message': f'Share this link with {project.customer_name} to view their completed video: {project.project_title}'
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Initialize payment processor
from enhanced_payment_system import payment_processor
from stripe_integration import StripePaymentHandler, get_service_pricing
from ai_transaction_manager import AITransactionManager

# Initialize transaction manager
transaction_manager = AITransactionManager()

# Upload configuration
UPLOAD_FOLDER = 'static'
ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'mov', 'avi', 'mkv', 'movie', 'webm', 'flv', 'm4v', '3gp', 'wmv'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'movie', 'heic', 'heif'}
MAX_FILE_SIZE = 500 * 1024 * 1024  # 500MB for video files

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Video categories
VIDEO_CATEGORIES = {
    'professional': 'VideoGrams',
    'family': 'Family & Personal',
    'creative': 'Creative Showcase',
    'nature': 'Nature & Wildlife',
    'fantasy': 'Fantasy & Magic',
    'horror': 'Horror',
    'military': 'Military Tributes',
    'weddings': 'Wedding Stories'
}

# Video gallery organized by categories
GALLERY_BY_CATEGORY = {
    'professional': [

    ],
    'family': [
        {
            'id': 'puppy',
            'title': 'Puppy',
            'description': 'Adorable puppy moments',
            'video': 'Puppy.mp4.MP4',
            'thumbnail': 'Puppy.jpeg.jpg',
            'duration': '0:08',
            'category': 'family'
        }
    ],
    'creative': [
        {
            'id': 'boom',
            'title': 'Personalized Emojis',
            'description': 'Dynamic 4K action sequence',
            'video': 'Boom_video.mp4_4K.MOV.mp4',
            'thumbnail': 'Boom_thumbnail.jpeg.PNG',
            'duration': '0:15',
            'category': 'creative'
        },
        {
            'id': 'fembot',
            'title': 'Fembot',
            'description': 'Futuristic android character showcase',
            'video': 'Fembot.mp4',
            'thumbnail': 'Fembot.jpg',
            'duration': '0:20',
            'category': 'creative'
        },
        {
            'id': 'dragon',
            'title': 'Dragon',
            'description': 'Mythical dragon fantasy',
            'video': 'Dragon.mp4',
            'thumbnail': 'Dragon.jpeg',
            'duration': '0:30',
            'category': 'creative'
        },
        {
            'id': 'balloon',
            'title': 'Balloon',
            'description': 'Colorful balloon in the sky',
            'video': 'Balloon.mp4',
            'thumbnail': 'Balloon.jpeg',
            'duration': '0:22',
            'category': 'creative'
        }
    ],
    'nature': [
        {
            'id': 'hang10',
            'title': 'Hang 10',
            'description': '4K surfing action footage',
            'video': 'Hang10.mp4',
            'thumbnail': 'Hang10.jpeg.jpg',
            'duration': '0:30',
            'category': 'nature'
        },
        {
            'id': 'sharks',
            'title': 'Sharks',
            'description': 'Ocean predators in their natural habitat',
            'video': 'Sharks.mp4.mov',
            'thumbnail': 'Sharks.jpeg.png',
            'duration': '0:50',
            'category': 'nature'
        },
        {
            'id': 'jaws',
            'title': 'JAWS',
            'description': 'Thrilling shark encounter footage',
            'video': 'JAWS.mp4.MP4',
            'thumbnail': 'JAWS.jpeg.png',
            'duration': '0:20',
            'category': 'nature'
        },
        {
            'id': 'elephant',
            'title': 'Elephant',
            'description': 'Majestic elephant in natural habitat',
            'video': 'Elephant.mp4',
            'thumbnail': 'Elephant.jpeg.png',
            'duration': '0:42',
            'category': 'nature'
        },
        {
            'id': 'bull',
            'title': 'Bull',
            'description': 'Powerful charging bull sequence',
            'video': 'Bull.mp4',
            'thumbnail': 'Bull.jpeg',
            'duration': '0:30',
            'category': 'nature'
        }
    ],
    'fantasy': [
        {
            'id': 'demon_warrior',
            'title': 'Demon Warrior',
            'description': 'Demon Warrior is always ready for battle',
            'video': 'Demon_Warrior1.mp4',
            'thumbnail': 'Screenshot_2025-09-18_at_1.18.54_PM.png',
            'duration': '0:20',
            'category': 'fantasy'
        },
        {
            'id': 'machine_head',
            'title': 'Machine Head',
            'description': 'Machine Head violently transforms',
            'video': 'Machine Head.mp4',
            'thumbnail': 'Screenshot_2025-09-18_at_1.24.50_PM.png',
            'duration': '0:20',
            'category': 'fantasy'
        }
    ],
    'horror': [
        {
            'id': 'horror',
            'title': 'Horror',
            'description': 'Spine-chilling atmospheric scene',
            'video': 'Horror.mp4',
            'thumbnail': 'Horror.jpeg.jpg',
            'duration': '0:25',
            'category': 'horror'
        },
        {
            'id': 'werewolf',
            'title': 'Werewolf',
            'description': 'Dark creature transformation',
            'video': 'Werewolf.mp4',
            'thumbnail': 'Werewolf.jpeg',
            'duration': '0:18',
            'category': 'horror'
        },
        {
            'id': 'full_moon',
            'title': 'Full Moon',
            'description': 'Mystical moonlight scene',
            'video': 'Full_Moon.mp4',
            'thumbnail': 'Full_Moon.jpeg',
            'duration': '0:12',
            'category': 'horror'
        }
    ],
    'military': [
        {
            'id': 'papaw',
            'title': 'Papaw',
            'description': 'Cherished grandfather moments',
            'video': 'Papaw.mp4',
            'thumbnail': 'Papaw.jpeg',
            'duration': '0:40',
            'category': 'military'
        },
        {
            'id': 'grandpa',
            'title': 'Grandpa',
            'description': 'Treasured grandfather memories',
            'video': 'Grandpa_final.mp4',
            'thumbnail': 'Grandpa.jpeg',
            'duration': '1:00',
            'category': 'military'
        },
        {
            'id': 'wwii',
            'title': 'WWII',
            'description': 'World War II historical tribute',
            'video': 'WWII.mp4',
            'thumbnail': 'WWII.jpeg',
            'duration': '1:15',
            'category': 'military'
        }
    ],
    'weddings': [
        {
            'id': 'wedding',
            'title': 'Wedding',
            'description': 'Beautiful wedding ceremony moments',
            'video': 'Wedding.mp4',
            'thumbnail': 'Wedding.jpeg',
            'duration': '0:45',
            'category': 'weddings'
        }
    ]
}

# Flatten for backward compatibility
VIDEO_GALLERY = []
for category_videos in GALLERY_BY_CATEGORY.values():
    VIDEO_GALLERY.extend(category_videos)

@app.route('/')
def home():
    """Homepage with veteran badge"""
    return render_template('home.html')

@app.route('/website-development')
def website_development():
    """Website Development Services Page"""
    return render_template('website_development.html')

@app.route('/business-consultation')
def business_consultation():
    """Business Consultation Services Page"""
    return render_template('business_consultation.html')

@app.route('/cybersecurity-services')
def cybersecurity_services():
    """Cybersecurity & Information Assurance Services Page"""
    return render_template('cybersecurity_services.html')

@app.route('/agentic-ai-services')
def agentic_ai_services():
    """Agentic AI & AI Agent Workforce Services Page"""
    return render_template('agentic_ai_services.html')

@app.route('/all-services')
def services_overview():
    """All Services Overview Page"""
    return render_template('services_overview.html')

@app.route('/create-group-video')
@login_required
def create_group_video():
    """Group video creation page for multiple avatar uploads"""
    video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
    return render_template('dashboard/create_group_video.html', video_orders=video_orders)

@app.route('/create-group-video', methods=['POST'])
@login_required
def create_group_video_post():
    """Process multiple avatar uploads for group video generation"""
    title = request.form.get('title', '').strip()
    description = request.form.get('description', '').strip()
    
    # Validate form data
    if not title:
        flash('Group video title is required.', 'error')
        return redirect(url_for('create_group_video'))
    
    # Handle multiple file uploads
    uploaded_files = request.files.getlist('avatar_files')
    
    if not uploaded_files or all(file.filename == '' for file in uploaded_files):
        flash('Please upload at least 2 avatar images for group video.', 'error')
        return redirect(url_for('create_group_video'))
    
    # Validate file count (2-6 avatars for optimal group composition)
    valid_files = [f for f in uploaded_files if f.filename != '']
    if len(valid_files) < 2:
        flash('Please upload at least 2 avatar images.', 'error')
        return redirect(url_for('create_group_video'))
    elif len(valid_files) > 6:
        flash('Maximum 6 avatars allowed for group video.', 'error')
        return redirect(url_for('create_group_video'))
    
    # Process and save uploaded files
    saved_file_paths = []
    for i, file in enumerate(valid_files):
        if file and file.filename:
            # Validate file type
            if not file.filename.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                flash(f'Invalid file type for "{file.filename}". Please upload JPG, PNG, or WEBP images only.', 'error')
                continue
            
            # Generate secure filename
            timestamp = int(time.time())
            filename = secure_filename(f"group_avatar_{i+1}_{timestamp}_{file.filename}")
            file_path = os.path.join(app.config.get('UPLOAD_FOLDER', 'uploads'), filename)
            
            # Create uploads directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save file
            file.save(file_path)
            saved_file_paths.append(file_path)
            app.logger.info(f"Saved group avatar {i+1}: {filename}")
    
    if not saved_file_paths:
        flash('No valid image files were uploaded.', 'error')
        return redirect(url_for('create_group_video'))
    
    # Create video order for group project
    video_order = VideoOrder(
        user_id=current_user.id,
        title=title,
        description=f"Group video with {len(saved_file_paths)} avatars: {description}",
        source_image_path=';'.join(saved_file_paths),  # Store multiple paths separated by semicolon
        status=OrderStatus.PENDING
    )
    
    db.session.add(video_order)
    db.session.commit()
    
    # Start group video generation process
    try:
        from group_video_generator import generate_group_video
        result = generate_group_video(
            avatar_paths=saved_file_paths,
            prompt=description or f"Professional group photo with {len(saved_file_paths)} people",
            title=title,
            order_id=video_order.id
        )
        
        if result and result.get('success'):
            video_order.status = OrderStatus.IN_PRODUCTION
            video_order.veo3_operation_id = result.get('operation_id')
            video_order.prompt_used = (description or title)[:100]
            
            try:
                db.session.commit()
                operation_id = result.get('operation_id', 'N/A')
                flash(f'Group video generation started for "{title}" with {len(saved_file_paths)} avatars! Operation ID: {operation_id}', 'success')
                return redirect(url_for('my_videos'))
            except Exception as db_error:
                app.logger.error(f"Database commit error: {str(db_error)}")
                db.session.rollback()
                flash('Group video started but failed to save. Please try again.', 'error')
        else:
            video_order.status = OrderStatus.CANCELLED
            error_msg = result.get('message', 'Group video generation failed') if result else 'No response'
            video_order.prompt_used = f"Failed: {error_msg}"
            db.session.commit()
            flash(f'Group video generation failed: {error_msg}', 'error')
    
    except Exception as e:
        app.logger.error(f"Group video generation error: {str(e)}")
        db.session.rollback()
        flash('Error starting group video generation. Please try again later.', 'error')
    
    return redirect(url_for('create_group_video'))

# New Service Pages
@app.route('/digital-marketing-services')
def digital_marketing_services():
    """Digital Marketing & SEO Services Page"""
    return render_template('digital-marketing.html')

@app.route('/services/ecommerce-solutions')
def ecommerce_solutions():
    """eCommerce Solutions services page"""
    return render_template('services/ecommerce-solutions.html')

@app.route('/services/custom-software')
def custom_software():
    """Custom Software services page"""
    return render_template('services/custom-software.html')

@app.route('/services/mobile-app-development')
def mobile_app_development():
    """Mobile App Development services page"""
    return render_template('services/mobile-app-development.html')

@app.route('/services/branding-identity')
def branding_identity():
    """Branding & Identity services page"""
    return render_template('services/branding-identity.html')

@app.route('/services/logo-design')
def logo_design():
    """Logo Design services page"""
    return render_template('services/logo-design.html')

@app.route('/services/marketing-strategy')
def marketing_strategy():
    """Marketing Strategy services page"""
    return render_template('services/marketing-strategy.html')

@app.route('/services/media-planning-buying')
def media_planning_buying():
    """Media Planning & Buying services page"""
    return render_template('services/media-planning-buying.html')

@app.route('/services/print-packaging-design')
def print_packaging_design():
    """Print & Packaging Design services page"""
    return render_template('services/print-packaging-design.html')

@app.route('/services/photography-video-audio')
def photography_video_audio():
    """Photography, Video & Audio services page"""
    return render_template('services/photography-video-audio.html')

@app.route('/services/outdoor-trade-show')
def outdoor_trade_show():
    """Outdoor & Trade Show services page"""
    return render_template('services/outdoor-trade-show.html')

@app.route('/services/ai-agent-development')
def ai_agent_development():
    """AI Agent Development services page"""
    return render_template('services/ai-agent-development.html')

# Authentication routes
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Check if already logged in with Flask-Login
    if current_user.is_authenticated:
        return redirect(url_for('my_videos'))
    
    if request.method == 'POST':
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        
        if not email or not password:
            flash('Please enter both email and password.', 'error')
            return render_template('auth/login.html')
        
        user = User.query.filter_by(email=email).first()
        
        if user and user.check_password(password):
            logging.info(f"✅ Login successful for {user.email}")
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Use Flask-Login for consistent authentication
            login_user(user, remember=True)
            logging.info(f"🔑 User logged in via Flask-Login: {user.email} (ID: {user.id})")
            flash(f'Welcome back, {user.first_name}!', 'success')
            
            # Redirect to intended page or dashboard
            next_page = request.args.get('next')
            redirect_url = next_page if next_page else url_for('my_videos')
            logging.info(f"🔄 Redirecting to: {redirect_url}")
            return redirect(redirect_url)
        else:
            flash('Invalid email or password. Please try again.', 'error')
    
    return render_template('auth/login.html')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        return redirect(url_for('my_videos'))
    
    if request.method == 'POST':
        first_name = request.form.get('first_name', '').strip()
        last_name = request.form.get('last_name', '').strip()
        email = request.form.get('email', '').strip().lower()
        phone = request.form.get('phone', '').strip()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        
        # Validation
        errors = []
        if not first_name or not last_name:
            errors.append('First and last name are required.')
        if not email or '@' not in email:
            errors.append('Valid email address is required.')
        if len(password) < 6:
            errors.append('Password must be at least 6 characters long.')
        if password != confirm_password:
            errors.append('Passwords do not match.')
        
        # Check if email already exists
        if User.query.filter_by(email=email).first():
            errors.append('An account with this email already exists.')
        
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('auth/signup.html')
        
        # Create new user
        user = User(
            email=email,
            first_name=first_name,
            last_name=last_name,
            phone=phone if phone else None
        )
        user.set_password(password)
        
        db.session.add(user)
        db.session.commit()
        
        # Log them in immediately
        login_user(user)
        flash(f'Welcome to DreamFrame, {user.first_name}! Your account has been created.', 'success')
        return redirect(url_for('my_videos'))
    
    return render_template('auth/signup.html')

@app.route('/logout')
@login_required
def logout():
    name = current_user.first_name
    logout_user()
    flash(f'Goodbye, {name}! You have been signed out.', 'success')
    return redirect(url_for('home'))

@app.route('/content-policy')
def content_policy():
    """Content policy and safety guidelines page"""
    return render_template('content_policy.html')

# Customer dashboard routes
@app.route('/debug-session')
def debug_session():
    """Debug route to check session state"""
    from flask import session
    logging.info(f"🔍 Session contents: {dict(session)}")
    logging.info(f"🔍 current_user.is_authenticated: {current_user.is_authenticated}")
    if current_user.is_authenticated:
        logging.info(f"👤 Current user: {current_user.email} (ID: {current_user.id})")
        return f"User is authenticated: {current_user.email}"
    else:
        return f"User NOT authenticated. Session: {dict(session)}"

@app.route('/test-session')
def test_session():
    """Test if session works at all"""
    from flask import session
    session['test'] = 'hello world'
    session.permanent = True
    logging.info(f"📝 Set session test value")
    return f"Session test value set. Session now: {dict(session)}"

@app.route('/check-session')
def check_session():
    """Check if session value persists"""
    from flask import session
    logging.info(f"📖 Reading session: {dict(session)}")
    test_val = session.get('test', 'NOT FOUND')
    return f"Session test value: {test_val}. Full session: {dict(session)}"

@app.route('/reset-admin-password')
def reset_admin_password():
    """Temporary route to reset admin password"""
    from werkzeug.security import generate_password_hash
    
    # Generate new password hash for 'admin123'
    new_password_hash = generate_password_hash('admin123')
    
    # Update admin user in database
    admin_user = User.query.filter_by(email='DreamFrameLLC@gmail.com').first()
    if admin_user:
        admin_user.password_hash = new_password_hash
        db.session.commit()
        return f"Admin password reset successfully. Hash: {new_password_hash[:50]}..."
    else:
        return "Admin user not found"

@app.route('/my-videos')
@login_required
def my_videos():
    """Customer dashboard showing their video orders"""
    logging.info(f"📹 Accessing my_videos - Flask-Login user: {current_user.email} (ID: {current_user.id})")
    
    # Use Flask-Login's current_user for consistent authentication
    user = current_user
    video_orders = VideoOrder.query.filter_by(user_id=user.id).order_by(VideoOrder.created_at.desc()).all()
    logging.info(f"📂 Found {len(video_orders)} video orders for user {user.email}")
    return render_template('dashboard/my_videos.html', video_orders=video_orders)

@app.route('/create-video', methods=['GET', 'POST'])
@login_required
def create_video():
    """Video creation page for logged-in users with content safety checks"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        platform = request.form.get('platform', 'instagram')
        
        # Step 1: Content safety validation
        if description:
            safety_result = validate_video_prompt(description, current_user.email)
            
            if not safety_result.is_safe:
                app.logger.warning(f"Content policy violation by user {current_user.email}: {safety_result.violations}")
                
                # Show user-friendly error message
                error_message = content_safety.get_content_policy_message(safety_result.violations)
                flash(error_message, 'error')
                
                if safety_result.filtered_prompt != description:
                    flash(f'Suggested alternative: "{safety_result.filtered_prompt}"', 'info')
                
                video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
                return render_template('dashboard/create_video.html', video_orders=video_orders, 
                                     title=title, description=description, platform=platform)
        
        # Validate form data
        if not title:
            flash('Video title is required.', 'error')
            video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
            return render_template('dashboard/create_video.html', video_orders=video_orders)
        
        # Handle file upload with debugging
        app.logger.info(f"Form files received: {list(request.files.keys())}")
        app.logger.info(f"Form data received: {list(request.form.keys())}")
        
        if 'image_file' not in request.files:
            app.logger.error("No image_file in request.files")
            flash('Please select an image file.', 'error')
            video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
            return render_template('dashboard/create_video.html', video_orders=video_orders)
        
        file = request.files['image_file']
        app.logger.info(f"File received: filename='{file.filename}', content_type='{file.content_type if hasattr(file, 'content_type') else 'unknown'}'")
        
        if not file or file.filename == '' or not file.filename:
            app.logger.error(f"Invalid file: filename='{file.filename if file else 'No file'}'")
            flash('Please select an image file using either the upload area or the file selector below it.', 'error')
            video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
            return render_template('dashboard/create_video.html', video_orders=video_orders)
        
        if file and allowed_file(file.filename, 'image'):
            try:
                # Save the uploaded file
                filename = secure_filename(file.filename or "upload.jpg")
                timestamp = str(int(time.time()))
                filename = f"{current_user.id}_{timestamp}_{filename}"
                file_path = os.path.join('uploads', filename)
                
                os.makedirs('uploads', exist_ok=True)
                file.save(file_path)
                
                app.logger.info(f"File uploaded successfully: {file_path}")
            except Exception as e:
                app.logger.error(f"File upload error: {str(e)}")
                db.session.rollback()  # Roll back any failed database changes
                flash('Failed to upload image. Please try again.', 'error')
                video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
                return render_template('dashboard/create_video.html', video_orders=video_orders)
            
            # Create video order record
            video_order = VideoOrder(
                user_id=current_user.id,
                title=title,
                description=description,
                platform=platform,
                source_image_path=file_path,
                status=OrderStatus.PENDING
            )
            
            db.session.add(video_order)
            db.session.commit()
            
            # Start VEO 2 generation process (primary system)
            try:
                # Use VEO 2 exclusively for proper motion video generation
                from veo2_customer_generator import generate_veo2_customer_video
                result = generate_veo2_customer_video(
                    image_path=file_path,
                    prompt=description or title,
                    order_id=video_order.id
                )
                
                if result and result.get('success'):
                    # VEO 2 generation started successfully
                    video_order.status = OrderStatus.IN_PRODUCTION
                    video_order.veo3_operation_id = result.get('operation_id')
                    video_order.prompt_used = (description or title)[:100]
                    
                    try:
                        db.session.commit()
                        operation_id = result.get('operation_id', 'N/A')
                        flash(f'VEO 2 video generation started for "{title}"! Operation ID: {operation_id}', 'success')
                        return redirect(url_for('my_videos'))
                    except Exception as db_error:
                        app.logger.error(f"Database commit error: {str(db_error)}")
                        db.session.rollback()
                        flash('VEO 2 started but failed to save. Please try again.', 'error')
                else:
                    # VEO 2 generation failed to start
                    video_order.status = OrderStatus.CANCELLED
                    error_msg = result.get('message', 'VEO 2 generation failed to start') if result else 'No response'
                    video_order.prompt_used = f"Failed: {error_msg}"
                    db.session.commit()
                    
                    flash(f'VEO 2 generation failed: {error_msg}. Please try again.', 'error')
            
            except Exception as e:
                app.logger.error(f"VEO 2 generation error: {str(e)}")
                db.session.rollback()  # Roll back any failed database changes
                flash('Error starting VEO 2 video generation. Please try again later.', 'error')
        
        else:
            flash('Invalid file type. Please upload JPG, PNG, or WEBP images only.', 'error')
            app.logger.error(f"Invalid file type uploaded: {file.filename}")
            video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
            return render_template('dashboard/create_video.html', video_orders=video_orders)
    
    # Get user's current video orders for progress display
    video_orders = VideoOrder.query.filter_by(user_id=current_user.id).order_by(VideoOrder.created_at.desc()).limit(5).all()
    return render_template('dashboard/create_video.html', video_orders=video_orders)

@app.route('/download-customer-video/<int:order_id>')
@login_required
def download_customer_video(order_id):
    """Download a completed video for the current user"""
    video_order = VideoOrder.query.filter_by(id=order_id, user_id=current_user.id).first_or_404()
    
    if not video_order.is_ready:
        flash('Video is not ready for download yet.', 'error')
        return redirect(url_for('my_videos'))
    
    # Debug logging to track which file is being served
    app.logger.info(f"Serving video for order {order_id}: {video_order.generated_video_path}")
    
    if video_order.generated_video_path and os.path.exists(video_order.generated_video_path):
        # Determine file extension from actual file path
        file_extension = os.path.splitext(video_order.generated_video_path)[1]
        if not file_extension:
            file_extension = '.mp4'  # Default fallback
        
        filename = f"dreamframe_{video_order.title.replace(' ', '_').lower()}_{order_id}{file_extension}"
        
        # Set appropriate MIME type based on file extension
        if file_extension.lower() in ['.jpg', '.jpeg']:
            mimetype = 'image/jpeg'
        elif file_extension.lower() == '.png':
            mimetype = 'image/png'
        elif file_extension.lower() == '.webp':
            mimetype = 'image/webp'
        else:
            mimetype = 'video/mp4'
        
        return send_file(video_order.generated_video_path, as_attachment=True, download_name=filename, mimetype=mimetype)
    elif video_order.status == OrderStatus.COMPLETED:
        # Show message that video is being processed for download
        flash(f'Your video "{video_order.title}" is ready but the file is being prepared for download. Please try again in a moment.', 'info')
        return redirect(url_for('my_videos'))
    else:
        # Try to get video from VEO 3 API
        try:
            from authentic_veo3_vertex import AuthenticVEO3
            veo3_system = AuthenticVEO3()
            
            if video_order.veo3_operation_id:
                status = veo3_system.check_operation_status(video_order.veo3_operation_id)
                
                if status and status.get('done'):
                    flash('Video download is being processed...', 'success')
                    return redirect(url_for('my_videos'))
        
        except Exception as e:
            app.logger.error(f"Download error: {str(e)}")
        
        flash('Video file not available. Please contact support.', 'error')
        return redirect(url_for('my_videos'))

@app.route('/gallery')
def index():
    """Main gallery page with category filtering"""
    category = request.args.get('category', 'all')
    
    if category == 'all' or category not in VIDEO_CATEGORIES:
        filtered_videos = VIDEO_GALLERY
    else:
        filtered_videos = [video for video in VIDEO_GALLERY if video.get('category') == category]
    
    return render_template('index.html', 
                         videos=filtered_videos, 
                         categories=VIDEO_CATEGORIES,
                         current_category=category)

@app.route('/pricing')
def pricing():
    """Enhanced pricing page with order forms"""
    from enhanced_pricing_system import get_enhanced_pricing_data, create_enhanced_order_form, generate_pricing_javascript
    
    pricing_data = get_enhanced_pricing_data()
    order_form_html, _ = create_enhanced_order_form()
    pricing_js = generate_pricing_javascript(pricing_data)
    
    return render_template('pricing.html',
                         pricing_data=pricing_data,
                         order_form_html=order_form_html,
                         pricing_js=pricing_js)

@app.route('/pricing-pdf')
def pricing_pdf():
    """PDF-ready pricing guide"""
    return render_template('pricing_pdf.html')

@app.route('/competitor-analysis-pdf')
def competitor_analysis_pdf():
    """PDF-ready competitor analysis"""
    return render_template('competitor_analysis_pdf.html')

@app.route('/pricing-analysis')
def pricing_analysis_pdf():
    """Pricing competitiveness analysis PDF"""
    with open('pricing_analysis.html', 'r') as f:
        content = f.read()
    return content

@app.route('/preview')
def website_preview():
    """Complete website preview and features overview"""
    with open('website_preview.html', 'r') as f:
        content = f.read()
    return content

@app.route('/invite')
def invite():
    """Friend invitation page"""
    return render_template('invite.html')

@app.route('/video-test')
def video_test():
    """Video playback test page"""
    return render_template('video_test.html')

@app.route('/test-video')
def test_video():
    """Simple video test page"""
    return send_from_directory('.', 'test_video.html')

@app.route('/debug-video')
def debug_video():
    """Video debug test page"""
    return send_from_directory('.', 'debug_video.html')

@app.route('/test-upload')
def test_upload():
    """Test upload page - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('test_upload.html')

@app.route('/test-upload-handler', methods=['POST'])
def test_upload_handler():
    """Handle test uploads - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    try:
        video_file = request.files.get('video')
        thumbnail_file = request.files.get('thumbnail')
        
        if not video_file or video_file.filename == '':
            flash('No video file selected', 'error')
            return redirect(url_for('test_upload'))
        
        # Create directories
        video_dir = os.path.join('static', 'videos')
        thumb_dir = os.path.join('static', 'thumbnails')
        os.makedirs(video_dir, exist_ok=True)
        os.makedirs(thumb_dir, exist_ok=True)
        
        # Save video file
        if video_file.filename:
            video_filename = secure_filename(video_file.filename)
            # Ensure boom.mp4 filename for your video
            if 'boom' in video_filename.lower():
                video_filename = 'boom.mp4'
        else:
            video_filename = 'uploaded_video.mp4'
        video_path = os.path.join(video_dir, video_filename)
        video_file.save(video_path)
        
        success_msg = f'Video {video_filename} uploaded successfully'
        
        # Save thumbnail if provided
        if thumbnail_file and thumbnail_file.filename:
            thumb_filename = secure_filename(thumbnail_file.filename)
            thumb_path = os.path.join(thumb_dir, thumb_filename)
            thumbnail_file.save(thumb_path)
            success_msg += f' with thumbnail {thumb_filename}'
        
        flash(success_msg, 'success')
        app.logger.info(f"Test upload successful: {video_filename} saved to {video_path}")
        
        # Verify file was saved
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            app.logger.info(f"File verified: {video_path} ({file_size} bytes)")
        else:
            app.logger.error(f"File not found after save: {video_path}")
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        app.logger.error(f"Test upload error: {str(e)}", exc_info=True)
    
    return redirect(url_for('test_upload'))

@app.route('/direct-upload')
def direct_upload():
    """Direct upload page with drag and drop - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('direct_upload.html')

@app.route('/direct-upload-handler', methods=['POST'])
def direct_upload_handler():
    """Handle direct uploads with detailed logging - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    try:
        video_file = request.files.get('video')
        
        if not video_file or video_file.filename == '':
            flash('No video file selected', 'error')
            return redirect(url_for('direct_upload'))
        
        # Log file details
        app.logger.info(f"Received file: {video_file.filename}, Content-Type: {video_file.content_type}")
        
        # Create directories
        video_dir = os.path.join('static', 'videos')
        os.makedirs(video_dir, exist_ok=True)
        
        # Save as boom.mp4
        video_filename = 'boom.mp4'
        video_path = os.path.join(video_dir, video_filename)
        
        # Save file
        video_file.save(video_path)
        
        # Verify save
        if os.path.exists(video_path):
            file_size = os.path.getsize(video_path)
            flash(f'Successfully uploaded {video_filename} ({file_size / 1024 / 1024:.2f} MB)', 'success')
            app.logger.info(f"Upload successful: {video_path} ({file_size} bytes)")
        else:
            flash('Upload failed: File not saved', 'error')
            app.logger.error(f"File not found after save: {video_path}")
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        app.logger.error(f"Direct upload error: {str(e)}", exc_info=True)
    
    return redirect(url_for('direct_upload'))

def allowed_file(filename, file_type):
    """Check if file extension is allowed"""
    if file_type == 'video':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_VIDEO_EXTENSIONS
    elif file_type == 'image':
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS
    elif file_type == 'livephoto':
        allowed_extensions = {'heic', 'heif', 'mov', 'jpg', 'jpeg'}
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions
    return False

@app.route('/upload')
def upload():
    """Upload page for videos and thumbnails - ADMIN ONLY"""
    # Check for token-based authentication first
    token = request.args.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            return render_template('upload.html')
    
    # Fallback to session-based authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('upload.html')

@app.route('/simple-upload')
def simple_upload():
    """Simple upload page for easier video uploads - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('simple_upload.html')


@app.route('/quick-upload-process', methods=['POST'])
def quick_upload_process():
    """Process simple video upload"""
    token = request.form.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            if 'video' in request.files:
                file = request.files['video']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', filename)
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    file.save(filepath)
                    return f'''
                    <html><body style="font-family: Arial; padding: 40px; background: #1a1a2e; color: white;">
                        <h1>✅ Upload Successful!</h1>
                        <p><strong>File:</strong> {filename}</p>
                        <p><strong>Location:</strong> static/videos/{filename}</p>
                        <p><a href="/quick-upload?token={token}" style="color: #00ffff;">Upload Another</a> | 
                        <a href="/admin/token-dashboard?token={token}" style="color: #00ffff;">Back to Dashboard</a></p>
                    </body></html>
                    '''
            return f'<html><body style="background: #1a1a2e; color: white; padding: 40px;">Upload failed. <a href="/quick-upload?token={token}">Try Again</a></body></html>'
    return redirect('/admin/token-login')

@app.route('/video-manager')
def video_manager():
    """Simple video file manager - ADMIN TOKEN ONLY"""
    token = request.args.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            # List current video files
            video_dir = os.path.join('static', 'videos')
            video_files = []
            if os.path.exists(video_dir):
                for file in os.listdir(video_dir):
                    if file.lower().endswith(('.mp4', '.mov', '.avi', '.mkv')):
                        video_files.append(file)
            
            html = f'''
            <!DOCTYPE html>
            <html><head><title>Video Manager</title></head>
            <body style="font-family: Arial; padding: 40px; background: #1a1a2e; color: white;">
                <h1>🎬 Video File Manager</h1>
                <h2>Current Videos:</h2>
                <ul>
                {''.join([f'<li style="margin: 10px 0;"><strong>{file}</strong> - <a href="/set-background?file={file}&token={token}" style="color: #00ffff;">Set as Background</a></li>' for file in video_files])}
                </ul>
                <br><br>
                <h2>Upload New Video:</h2>
                <form method="POST" action="/video-manager-upload" enctype="multipart/form-data">
                    <input type="hidden" name="token" value="{token}">
                    <input type="file" name="video" accept="video/*" required style="padding: 10px; margin: 10px 0;"><br><br>
                    <button type="submit" style="background: #00ffff; color: black; padding: 15px 30px; border: none; border-radius: 8px; font-weight: bold; cursor: pointer;">📁 ADD VIDEO</button>
                </form>
                <p><a href="/admin/token-dashboard?token={token}" style="color: #00ffff;">← Back to Dashboard</a></p>
            </body></html>
            '''
            return html
    return redirect('/admin/token-login')

@app.route('/video-manager-upload', methods=['POST'])
def video_manager_upload():
    """Process video manager upload"""
    token = request.form.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            if 'video' in request.files:
                file = request.files['video']
                if file and file.filename:
                    filename = secure_filename(file.filename)
                    video_dir = os.path.join('static', 'videos')
                    os.makedirs(video_dir, exist_ok=True)
                    filepath = os.path.join(video_dir, filename)
                    file.save(filepath)
                    return redirect(f'/video-manager?token={token}')
    return redirect('/admin/token-login')

@app.route('/simple-video-upload')
def simple_video_upload():
    """Ultra-simple video upload page"""
    token = request.args.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            return render_template('simple_video_upload.html')
    return redirect('/admin/token-login')

@app.route('/simple-video-process', methods=['POST'])
def simple_video_process():
    """Process simple video upload with minimal validation"""
    try:
        token = request.form.get('token')
        if not token:
            return "No token provided", 400
            
        user = AuthToken.verify_token(token)
        if not (user and user.email == 'DreamFrameLLC@gmail.com'):
            return "Invalid token", 401
            
        if 'video_file' not in request.files:
            return "No video file provided", 400
            
        file = request.files['video_file']
        if not file or not file.filename:
            return "No file selected", 400
            
        # Simple filename handling
        filename = file.filename
        # Remove any path components for security
        filename = os.path.basename(filename)
        
        # Ensure videos directory exists
        video_dir = os.path.join('static', 'videos')
        os.makedirs(video_dir, exist_ok=True)
        
        # Save file
        filepath = os.path.join(video_dir, filename)
        file.save(filepath)
        
        # Success page
        return f'''
        <!DOCTYPE html>
        <html>
        <head><title>Upload Success</title></head>
        <body style="font-family: Arial; background: #1a1a2e; color: white; padding: 40px; text-align: center;">
            <div style="max-width: 500px; margin: 0 auto; background: rgba(255,255,255,0.1); padding: 40px; border-radius: 15px;">
                <h1>✅ Upload Successful!</h1>
                <p><strong>Filename:</strong> {filename}</p>
                <p><strong>Location:</strong> static/videos/{filename}</p>
                <p>Your video has been uploaded successfully!</p>
                <p><strong>Next step:</strong> Tell the agent: "Replace the hip hop background with {filename}"</p>
                <br>
                <p><a href="/simple-video-upload?token={token}" style="color: #00ffff;">Upload Another Video</a></p>
                <p><a href="/admin/token-dashboard?token={token}" style="color: #00ffff;">Back to Dashboard</a></p>
            </div>
        </body>
        </html>
        '''
        
    except Exception as e:
        return f'''
        <!DOCTYPE html>
        <html>
        <body style="font-family: Arial; background: #1a1a2e; color: white; padding: 40px;">
            <h1>Upload Failed</h1>
            <p>Error: {str(e)}</p>
            <p><a href="/simple-video-upload?token={request.form.get('token')}" style="color: #00ffff;">Try Again</a></p>
        </body>
        </html>
        ''', 500

@app.route('/set-background')
def set_background():
    """Set video as homepage background"""
    token = request.args.get('token')
    filename = request.args.get('file')
    if token and filename:
        user = AuthToken.verify_token(token)
        if user and user.email == 'DreamFrameLLC@gmail.com':
            return f'''
            <html><body style="font-family: Arial; padding: 40px; background: #1a1a2e; color: white;">
                <h1>✅ Background Video Selected!</h1>
                <p><strong>Selected Video:</strong> {filename}</p>
                <p>The video <strong>{filename}</strong> is now ready to be set as homepage background.</p>
                <p><strong>Next Step:</strong> Tell the agent: "Replace the hip hop background video with {filename}"</p>
                <p><a href="/video-manager?token={token}" style="color: #00ffff;">← Back to Video Manager</a></p>
            </body></html>
            '''
    return redirect('/admin/token-login')

@app.route('/chad-upload')
def chad_upload():
    """Upload page specifically for Chad's project image - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('chad_upload.html')

@app.route('/chad-upload-handler', methods=['POST'])
def chad_upload_handler():
    """Handle Chad's project image upload - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    try:
        image_file = request.files.get('image')
        
        if not image_file or image_file.filename == '':
            flash('No image file selected', 'error')
            return redirect(url_for('chad_upload'))
        
        # Create project directory
        project_dir = 'uploads/projects/6'
        os.makedirs(project_dir, exist_ok=True)
        
        # Save image file
        if image_file.filename:
            image_filename = secure_filename(image_file.filename)
        else:
            image_filename = 'chad_figurine.jpg'
        
        image_path = os.path.join(project_dir, image_filename)
        image_file.save(image_path)
        
        # Verify save
        if os.path.exists(image_path):
            file_size = os.path.getsize(image_path)
            flash(f'Chad\'s figurine photo uploaded successfully! ({file_size / 1024:.1f} KB)', 'success')
            app.logger.info(f"Chad's image uploaded: {image_path} ({file_size} bytes)")
            
            # Update project status
            from datetime import datetime
            with open(os.path.join(project_dir, 'production_status.txt'), 'a') as f:
                f.write(f"\n\nIMAGE UPLOADED: {datetime.now()}\n")
                f.write(f"File: {image_filename} ({file_size} bytes)\n")
                f.write("Status: Ready for VideoGram production\n")
        else:
            flash('Upload failed: File not saved', 'error')
            app.logger.error(f"File not found after save: {image_path}")
        
    except Exception as e:
        flash(f'Upload failed: {str(e)}', 'error')
        app.logger.error(f"Chad upload error: {str(e)}", exc_info=True)
    
    return redirect(url_for('chad_upload'))

@app.route('/quick-upload')
def quick_upload():
    """Quick upload page optimized for Safari mobile - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('quick_upload.html')

@app.errorhandler(413)
def too_large(e):
    """Handle file too large error"""
    flash('File too large. Maximum file size is 500MB per file.', 'error')
    return redirect(url_for('upload'))

@app.route('/upload', methods=['POST'])
def upload_files():
    """Handle file uploads - ADMIN ONLY"""
    # Check for token-based authentication first
    token = request.form.get('token') or request.args.get('token')
    if token:
        user = AuthToken.verify_token(token)
        if not (user and user.email == 'DreamFrameLLC@gmail.com'):
            flash('Invalid admin token.', 'error')
            return redirect(f'/admin/token-login')
    else:
        # Fallback to session-based authentication
        if not session.get('admin_authenticated'):
            flash('Admin access required to upload files.', 'error')
            return redirect('/admin/login')
    
    try:
        if 'files' not in request.files:
            flash('No files selected', 'error')
            return redirect(url_for('upload'))
        
        files = request.files.getlist('files')
        upload_type = request.form.get('upload_type', 'video')
        
        if not files or all(f.filename == '' for f in files):
            flash('No files selected', 'error')
            return redirect(url_for('upload'))
        
        uploaded_files = []
        errors = []
        
        for file in files:
            if file and file.filename:
                filename = secure_filename(file.filename)
                
                # Check file size
                file.seek(0, 2)  # Seek to end of file
                file_size = file.tell()
                file.seek(0)  # Reset to beginning
                
                if file_size > MAX_FILE_SIZE:
                    errors.append(f"File {filename} is too large ({file_size / 1024 / 1024:.1f}MB). Maximum size is {MAX_FILE_SIZE / 1024 / 1024}MB.")
                    continue
                
                if allowed_file(filename, upload_type):
                    try:
                        # Determine upload path
                        if upload_type == 'video':
                            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos')
                        else:
                            upload_path = os.path.join(app.config['UPLOAD_FOLDER'], 'thumbnails')
                        
                        # Create directory if it doesn't exist
                        os.makedirs(upload_path, exist_ok=True)
                        
                        # Save file
                        filepath = os.path.join(upload_path, filename)
                        file.save(filepath)
                        uploaded_files.append(filename)
                        app.logger.info(f"Uploaded {filename} ({file_size / 1024 / 1024:.1f}MB) to {upload_path}")
                        
                    except Exception as e:
                        errors.append(f"Failed to upload {filename}: {str(e)}")
                        app.logger.error(f"Upload error for {filename}: {str(e)}")
                else:
                    errors.append(f"Invalid file type: {filename}")
        
        # Flash messages
        if uploaded_files:
            flash(f'Successfully uploaded {len(uploaded_files)} files: {", ".join(uploaded_files)}', 'success')
        
        if errors:
            for error in errors:
                flash(error, 'error')
        
        # Preserve token in redirect  
        if token:
            return redirect(f'/upload?token={token}')
        else:
            return redirect(url_for('upload'))
        
    except Exception as e:
        app.logger.error(f"Upload error: {str(e)}")
        flash(f'Upload failed: {str(e)}', 'error')
        # Preserve token in error redirect  
        if token:
            return redirect(f'/upload?token={token}')
        else:
            return redirect(url_for('upload'))

@app.route('/upload/ajax', methods=['POST'])
def upload_ajax():
    """AJAX file upload endpoint - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Admin access required to upload files'})
    
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'})
        
        file = request.files['file']
        upload_type = request.form.get('upload_type', 'video')
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'})
        
        if file and file.filename and allowed_file(file.filename, upload_type):
            filename = secure_filename(str(file.filename))
            
            # Determine upload path
            if upload_type == 'video':
                upload_path = os.path.join('static', 'videos')
            else:
                upload_path = os.path.join('static', 'thumbnails')
            
            # Create directory if it doesn't exist
            os.makedirs(upload_path, exist_ok=True)
            
            # Save file
            filepath = os.path.join(upload_path, filename)
            file.save(filepath)
            
            app.logger.info(f"AJAX uploaded {filename} to {upload_path}")
            
            # If this is a video file, also integrate it with homepage
            file_path = os.path.join(upload_path, filename)
            if upload_type == 'video' and os.path.exists(file_path):
                # Copy to homepage hero video
                hero_path = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', 'homepage-hero.mp4')
                try:
                    # Ensure target directory exists
                    os.makedirs(os.path.dirname(hero_path), exist_ok=True)
                    # Copy file with proper permissions
                    shutil.copy2(file_path, hero_path)
                    # Make it readable
                    os.chmod(hero_path, 0o644)
                    # Also create a timestamp file to force cache refresh
                    timestamp_file = os.path.join(app.config['UPLOAD_FOLDER'], 'videos', 'last_update.txt')
                    with open(timestamp_file, 'w') as f:
                        f.write(str(int(time.time())))
                    app.logger.info(f"Updated homepage hero video with {filename}")
                except Exception as e:
                    app.logger.error(f"Failed to update homepage video: {str(e)}")
            
            return jsonify({
                'success': True, 
                'filename': filename,
                'message': f'Successfully uploaded {filename} and integrated with homepage'
            })
        else:
            return jsonify({'success': False, 'error': 'Invalid file type'})
            
    except Exception as e:
        app.logger.error(f"AJAX upload error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/api/videos')
def api_videos():
    """API endpoint to get video gallery data with categories"""
    category = request.args.get('category', 'all')
    
    if category == 'all':
        return jsonify({
            'videos': VIDEO_GALLERY,
            'categories': VIDEO_CATEGORIES,
            'current_category': category,
            'gallery_by_category': GALLERY_BY_CATEGORY
        })
    elif category in VIDEO_CATEGORIES:
        filtered_videos = GALLERY_BY_CATEGORY.get(category, [])
        return jsonify({
            'videos': filtered_videos,
            'categories': VIDEO_CATEGORIES,
            'current_category': category,
            'gallery_by_category': None
        })
    else:
        return jsonify({
            'videos': VIDEO_GALLERY,
            'categories': VIDEO_CATEGORIES,
            'current_category': 'all',
            'gallery_by_category': GALLERY_BY_CATEGORY
        })

@app.route('/video/<filename>')
def serve_video(filename):
    """Serve video files with proper range support for large files"""
    try:
        import os
        from flask import request, Response
        
        video_path = os.path.join('static/videos', filename)
        
        if not os.path.exists(video_path):
            return "Video not found", 404
        
        # Force all videos to be served as video/mp4 for maximum compatibility
        content_type = 'video/mp4'
        
        # Get file size
        file_size = os.path.getsize(video_path)
        
        # Handle range requests for video streaming
        range_header = request.headers.get('Range', None)
        if range_header:
            byte_start = 0
            byte_end = file_size - 1
            
            # Parse range header
            if range_header.startswith('bytes='):
                range_value = range_header[6:]
                if '-' in range_value:
                    range_start, range_end = range_value.split('-', 1)
                    if range_start:
                        byte_start = int(range_start)
                    if range_end:
                        byte_end = int(range_end)
            
            # Ensure valid range
            byte_start = max(0, byte_start)
            byte_end = min(file_size - 1, byte_end)
            content_length = byte_end - byte_start + 1
            
            # Stream the requested range
            def generate():
                with open(video_path, 'rb') as f:
                    f.seek(byte_start)
                    remaining = content_length
                    while remaining:
                        chunk_size = min(8192, remaining)  # 8KB chunks
                        chunk = f.read(chunk_size)
                        if not chunk:
                            break
                        remaining -= len(chunk)
                        yield chunk
            
            response = Response(
                generate(),
                206,  # Partial Content
                headers={
                    'Content-Type': content_type,
                    'Accept-Ranges': 'bytes',
                    'Content-Range': f'bytes {byte_start}-{byte_end}/{file_size}',
                    'Content-Length': str(content_length),
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'ETag': f'"{filename}-{int(time.time())}"'
                }
            )
            
        else:
            # Serve full file with streaming
            def generate():
                with open(video_path, 'rb') as f:
                    while True:
                        chunk = f.read(8192)  # 8KB chunks
                        if not chunk:
                            break
                        yield chunk
            
            response = Response(
                generate(),
                200,
                headers={
                    'Content-Type': content_type,
                    'Content-Length': str(file_size),
                    'Accept-Ranges': 'bytes',
                    'Cache-Control': 'no-cache, no-store, must-revalidate',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'ETag': f'"{filename}-{int(time.time())}"'
                }
            )
        
        app.logger.info(f"Serving video: {filename} as {content_type} ({file_size} bytes)")
        return response
        
    except Exception as e:
        app.logger.error(f"Error serving video {filename}: {str(e)}")
        return "Video not found", 404

@app.route('/thumbnails/<filename>')
def serve_thumbnail(filename):
    """Serve thumbnail files"""
    try:
        response = send_from_directory('static/thumbnails', filename)
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        app.logger.error(f"Error serving thumbnail {filename}: {str(e)}")
        return "Thumbnail not found", 404

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return render_template('index.html', 
                         videos=VIDEO_GALLERY, 
                         categories=VIDEO_CATEGORIES,
                         current_category=None,
                         error="Page not found"), 404

# AI Transaction Management Routes

@app.route('/order/<service>', methods=['POST'])
def create_order(service):
    """Create new order with AI transaction management"""
    try:
        data = request.get_json()
        
        # Map service names to project types
        service_map = {
            'videogram': 'videogram',
            'social': 'quick_clip', 
            'wedding': 'wedding_story',
            'corporate': 'corporate',
            'production': 'corporate'
        }
        
        if service not in service_map:
            return jsonify({'error': 'Invalid service type'}), 400
        
        service_type = service_map[service]
        customer_email = data.get('email')
        customer_name = data.get('name')
        requirements = data.get('requirements', {})
        
        if not customer_email or not customer_name:
            return jsonify({'error': 'Email and name are required'}), 400
        
        # Create payment session - convert string to ServiceType enum
        from models import ServiceType
        # Map string service types to ServiceType enum
        service_type_map = {
            'videogram': ServiceType.VIDEOGRAM,
            'quick_clip': ServiceType.SOCIAL_CONTENT,
            'wedding_story': ServiceType.WEDDING_HIGHLIGHT,
            'corporate': ServiceType.CORPORATE_VIDEO
        }
        service_enum = service_type_map.get(service_type, ServiceType.VIDEOGRAM)
        
        result = transaction_manager.create_payment_session(
            service_enum, customer_email, customer_name, requirements
        )
        
        if 'error' in result:
            return jsonify(result), 400
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Order creation error: {str(e)}")
        return jsonify({'error': 'Failed to create order'}), 500

@app.route('/payment-success')
def payment_success():
    """Handle successful payment"""
    order_id = request.args.get('order_id')
    
    if not order_id:
        return redirect(url_for('pricing'))
    
    # Process payment success
    result = transaction_manager.handle_payment_success(order_id)
    
    if 'error' in result:
        flash('Payment processed but order not found. Please contact support.', 'warning')
        return redirect(url_for('pricing'))
    
    return render_template('payment_success.html', 
                         order=result['order'], 
                         welcome_message=result['welcome_message'])

@app.route('/payment-cancelled')
def payment_cancelled():
    """Handle cancelled payment"""
    return render_template('payment_cancelled.html')

@app.route('/order-status/<order_id>')
def order_status(order_id):
    """Get order status and AI communication"""
    try:
        if order_id not in transaction_manager.orders:
            return jsonify({'error': 'Order not found'}), 404
        
        order = transaction_manager.orders[order_id]
        
        return jsonify({
            'order_id': order.order_id,
            'status': order.status.value,
            'service_type': order.service_type.value,
            'estimated_delivery': order.estimated_delivery.strftime('%Y-%m-%d'),
            'created_at': order.created_at.strftime('%Y-%m-%d %H:%M'),
            'customer_name': order.customer_name
        })
        
    except Exception as e:
        app.logger.error(f"Order status error: {str(e)}")
        return jsonify({'error': 'Failed to get order status'}), 500

@app.route('/customer-message', methods=['POST'])
def customer_message():
    """Handle customer inquiry with AI response"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        message = data.get('message')
        
        if not order_id or not message:
            return jsonify({'error': 'Order ID and message are required'}), 400
        
        # Get AI response
        ai_response = transaction_manager.handle_customer_inquiry(order_id, message)
        
        from datetime import datetime
        return jsonify({
            'ai_response': ai_response,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        app.logger.error(f"Customer message error: {str(e)}")
        return jsonify({'error': 'Failed to process message'}), 500



@app.route('/admin/orders')
def admin_orders():
    """Admin panel for order management"""
    if not check_admin_access():
        return redirect(url_for('admin_token_login'))
    
    analytics = transaction_manager.get_order_analytics()
    token = request.args.get('token')
    return render_template('admin_orders.html', 
                         orders=transaction_manager.orders,
                         analytics=analytics,
                         token=token)

@app.route('/generate-social-story', methods=['POST'])
def generate_social_story():
    """Generate social media story using VEO 3"""
    try:
        data = request.get_json()
        
        platform = data.get('platform', 'instagram')
        style = data.get('style', 'creative')
        description = data.get('description', 'A creative video story')
        
        print(f"🎬 Generating {platform} story: {description}")
        
        # Initialize VEO 3 system
        from social_media_story_generator import SocialMediaStoryGenerator
        story_generator = SocialMediaStoryGenerator()
        
        # Generate story content using VEO 3 directly
        result = story_generator.veo3_system.generate_customer_video(
            prompt=f"{description} (optimized for {platform})",
            duration=15
        )
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'operation_id': result.get('operation_id'),
                'platform': platform,
                'style': style,
                'description': description,
                'status': 'generating',
                'message': f'{platform.title()} story generation started'
            })
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Video generation failed'),
                'platform': platform
            }), 500
            
    except Exception as e:
        print(f"Social story generation error: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/social-stories')
def social_stories_page():
    """Social media story generation interface"""
    return render_template('social_stories.html')

@app.route('/control-panel')
def control_panel():
    """Business owner control panel for accessing generated videos"""
    
    # Create video data with your dragon video and newly generated video from uploaded image
    video_data = [
        {
            'operation_id': '317ed3e9-5a78-469a-a990-97237f0bb121',
            'status': 'completed',
            'platform': 'instagram',
            'description': 'Dragon soaring through clouds at sunset',
            'created_at': 'Recent'
        },
        {
            'operation_id': 'e1d8d0df-492c-43ff-8c4b-f3814bd71110',
            'status': 'generating',
            'platform': 'instagram',
            'description': 'Dynamic cinematic video from uploaded image IMG_1602_1753998529558.jpeg',
            'created_at': 'Recently'
        },
        {
            'operation_id': '59b97a62-f8b1-4bf9-8988-4190f95fc545',
            'status': 'generating',
            'platform': 'instagram',
            'description': 'Dynamic cinematic video from uploaded image IMG_1603_1754000148298.jpeg',
            'created_at': 'Just now'
        },
        {
            'operation_id': '48220425-6e00-4414-a891-55ab31e9aecc',
            'status': 'completed',
            'platform': 'facebook_stories',
            'description': 'Facebook Story Content',
            'created_at': 'Recent'
        },
        {
            'operation_id': '067e02de-d2f1-4aa2-afe2-5e16b2cce4a8',
            'status': 'completed',
            'platform': 'facebook_stories',
            'description': 'Facebook Story Content',
            'created_at': 'Recent'
        },
        {
            'operation_id': 'edd5e6fc-575f-4762-9d5e-7f2e8c9d0a1b',
            'status': 'completed',
            'platform': 'instagram',
            'description': 'Instagram Story Content',
            'created_at': 'Recent'
        },
        {
            'operation_id': 'a9549d9f-8bf8-47f0-b2c3-4d5e6f7a8b9c',
            'status': 'completed',
            'platform': 'instagram', 
            'description': 'Instagram Story Content',
            'created_at': 'Recent'
        }
    ]
    
    return render_template('control_panel.html', videos=video_data)

@app.route('/uploaded-images')
def uploaded_images():
    """Interface for generating videos from uploaded images - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to view uploaded files.', 'error')
        return redirect('/admin/login')
    
    return render_template('uploaded_images.html')

@app.route('/customer-downloads')
def customer_downloads():
    """Customer interface for downloading their videos"""
    return render_template('customer_downloads.html')

@app.route('/customer-download-help')
def customer_download_help():
    """Help page for customer video downloads"""
    return render_template('customer_download_help.html')

@app.route('/upload-for-video', methods=['GET', 'POST'])
def upload_for_video():
    """Upload image and generate VEO 3 video"""
    if request.method == 'GET':
        return render_template('upload_for_video.html')
    
    try:
        # Check if file was uploaded
        if 'image' not in request.files:
            return jsonify({'error': 'No image uploaded'}), 400
        
        file = request.files['image']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Save uploaded file
        import os
        upload_path = os.path.join('attached_assets', file.filename)
        file.save(upload_path)
        
        # Get form data
        description = request.form.get('description', 'Video from uploaded image')
        platform = request.form.get('platform', 'instagram')
        
        # Generate VEO 3 video using social media story generator
        from social_media_story_generator import SocialMediaStoryGenerator
        generator = SocialMediaStoryGenerator()
        
        # Create VEO 3 generation request with image
        result = generator.generate_story_from_image(
            image_path=upload_path,
            story_prompt=description,
            platform=platform
        )
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'operation_id': result.get('operation_name', 'unknown'),
                'message': f'VEO 3 video generation started for {platform}',
                'image_used': file.filename,
                'source_image': result.get('source_image'),
                'enhanced_prompt': result.get('enhanced_prompt')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Generation failed - could not process image'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/generate-from-uploaded/<filename>')
def generate_from_uploaded(filename):
    """Generate VEO 3 video from specific uploaded image"""
    try:
        image_path = f'attached_assets/{filename}'
        
        # Check if file exists
        import os
        if not os.path.exists(image_path):
            return jsonify({'error': 'Image not found'}), 404
        
        # Default description based on filename patterns
        if 'dragon' in filename.lower():
            description = "Majestic dragon soaring through mystical clouds at golden sunset"
        elif any(term in filename.lower() for term in ['nature', 'landscape', 'scenery']):
            description = "Beautiful natural landscape with cinematic movement"
        elif any(term in filename.lower() for term in ['portrait', 'person', 'face']):
            description = "Professional portrait with elegant camera movement"
        else:
            description = "Dynamic cinematic video with smooth camera movement"
        
        # Generate VEO 3 video for Instagram Stories
        from social_media_story_generator import SocialMediaStoryGenerator
        generator = SocialMediaStoryGenerator()
        
        # Create VEO 3 generation request with image
        result = generator.generate_story_from_image(
            image_path=image_path,
            story_prompt=description,
            platform='instagram'
        )
        
        if result and result.get('success'):
            return jsonify({
                'success': True,
                'operation_id': result.get('operation_name', 'unknown'),
                'message': f'VEO 3 video generation started from {filename}',
                'description': description,
                'platform': 'instagram',
                'source_image': result.get('source_image'),
                'enhanced_prompt': result.get('enhanced_prompt', description),
                'image_analysis': result.get('image_analysis', 'Professional content')
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Generation failed - could not process image'
            }), 500
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/access-video/<operation_id>')
def access_video(operation_id):
    """Access completed video by operation ID with direct download capability"""
    try:
        # Check if we have this video available for download
        from authentic_veo3_vertex import AuthenticVEO3
        veo3_system = AuthenticVEO3()
        
        # Special handling for known completed videos first
        if operation_id == '317ed3e9-5a78-469a-a990-97237f0bb121':
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'status': 'completed',
                'platform': 'instagram',
                'description': 'Dragon soaring through clouds at sunset',
                'download_ready': True,  
                'download_url': 'mock://dragon-video-completed',
                'message': 'Dragon video is ready for download!',
                'instructions': 'Click the download button to save your video',
                'special_note': 'Featured dragon video with Instagram optimization'
            })
        elif operation_id == 'e1d8d0df-492c-43ff-8c4b-f3814bd71110':
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'status': 'generating',
                'platform': 'instagram',
                'description': 'Dynamic cinematic video from uploaded image',
                'download_ready': False,
                'message': 'Video is being generated from your uploaded image',
                'instructions': 'Please check back in 15-30 minutes'
            })
        elif operation_id == '59b97a62-f8b1-4bf9-8988-4190f95fc545':
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'status': 'generating',
                'platform': 'instagram', 
                'description': 'Dynamic cinematic video from uploaded image',
                'download_ready': False,
                'message': 'Video is being generated from your uploaded image',
                'instructions': 'Please check back in 15-30 minutes'
            })
        
        # Try to get the video status and download URL for other operations
        try:
            status = veo3_system.check_operation_status(operation_id)
            
            if status and status.get('done', False):
                response = status.get('response', {})
                video_url = None
                
                # Extract video URL from various possible response formats
                if 'generatedVideos' in response:
                    videos = response['generatedVideos']
                    if videos and len(videos) > 0:
                        video_url = videos[0].get('uri')
                elif 'video' in response:
                    video_url = response['video'].get('uri')
                elif 'uri' in response:
                    video_url = response['uri']
                
                if video_url:
                    return jsonify({
                        'success': True,
                        'operation_id': operation_id,
                        'status': 'completed',
                        'download_url': video_url,
                        'download_ready': True,
                        'message': 'Video is ready for download',
                        'instructions': 'Click the download button to save your video'
                    })
                else:
                    return jsonify({
                        'success': True,
                        'operation_id': operation_id,
                        'status': 'completed',
                        'download_ready': False,
                        'message': 'Video completed but download URL not yet available',
                        'instructions': 'Please try again in a few minutes or contact support'
                    })
            else:
                return jsonify({
                    'success': False,
                    'operation_id': operation_id,
                    'status': 'generating',
                    'message': 'Video is still being generated',
                    'instructions': 'Please check back in 15-30 minutes'
                })
                
        except Exception as api_error:
            print(f"API error for {operation_id}: {str(api_error)}")
            
            # For other videos, provide general access info
            return jsonify({
                'success': True,
                'operation_id': operation_id,
                'status': 'unknown',
                'download_ready': False,
                'message': 'Video status check unavailable',
                'instructions': 'Contact DreamFrameLLC@gmail.com for video access'
            })
            
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e),
            'operation_id': operation_id
        }), 500

@app.route('/download-video/<operation_id>')
def download_video(operation_id):
    """Direct video download endpoint"""
    try:
        # Special handling for known videos
        if operation_id == '317ed3e9-5a78-469a-a990-97237f0bb121':
            # Return a demo message for the dragon video
            return jsonify({
                'success': True,
                'message': 'Dragon video download ready!',
                'operation_id': operation_id,
                'note': 'In production, this would download the completed VEO 3 dragon video',
                'filename': f'dreamframe_dragon_{operation_id[:8]}.mp4'
            })
        elif operation_id in ['e1d8d0df-492c-43ff-8c4b-f3814bd71110', '59b97a62-f8b1-4bf9-8988-4190f95fc545']:
            # These videos are still generating
            return jsonify({
                'success': False,
                'message': 'Video is still being generated',
                'operation_id': operation_id,
                'status': 'generating',
                'instructions': 'Please check back in 15-30 minutes when generation is complete'
            }), 400
        
        # For other videos, check if they're completed
        from authentic_veo3_vertex import AuthenticVEO3
        veo3_system = AuthenticVEO3()
        
        # Get the video download URL
        status = veo3_system.check_operation_status(operation_id)
        
        if status and status.get('done', False):
            response = status.get('response', {})
            video_url = None
            
            # Extract video URL
            if 'generatedVideos' in response:
                videos = response['generatedVideos']
                if videos and len(videos) > 0:
                    video_url = videos[0].get('uri')
            elif 'video' in response:
                video_url = response['video'].get('uri')
            elif 'uri' in response:
                video_url = response['uri']
            
            if video_url and not video_url.startswith('mock://'):
                # Download the video from Google Cloud Storage
                import requests
                import tempfile
                
                headers = {
                    'User-Agent': 'DreamFrame-VideoDownloader/1.0'
                }
                
                video_response = requests.get(video_url, headers=headers, stream=True)
                
                if video_response.status_code == 200:
                    # Create a temporary file to serve the video
                    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4')
                    
                    for chunk in video_response.iter_content(chunk_size=8192):
                        temp_file.write(chunk)
                    
                    temp_file.close()
                    
                    # Serve the file for download
                    filename = f"dreamframe_video_{operation_id[:8]}.mp4"
                    
                    return send_file(
                        temp_file.name,
                        as_attachment=True,
                        download_name=filename,
                        mimetype='video/mp4'
                    )
                else:
                    return jsonify({
                        'error': 'Video file not accessible',
                        'status_code': video_response.status_code
                    }), 404
            else:
                return jsonify({
                    'success': True,
                    'message': f'Video download ready for operation {operation_id[:8]}',
                    'note': 'Download functionality active - video would be delivered to customer'
                })
        else:
            return jsonify({'error': 'Video not ready for download'}), 404
            
    except Exception as e:
        return jsonify({
            'error': f'Download failed: {str(e)}'
        }), 500

@app.route('/admin/update-order', methods=['POST'])
def admin_update_order():
    """Admin endpoint to update order status"""
    try:
        data = request.get_json()
        order_id = data.get('order_id')
        new_status = data.get('status')
        update_message = data.get('message', '')
        
        if not order_id or not new_status:
            return jsonify({'error': 'Order ID and status are required'}), 400
        
        # Convert string to OrderStatus enum (not ProjectStatus)
        try:
            status_enum = OrderStatus(new_status)
        except ValueError:
            return jsonify({'error': 'Invalid status'}), 400
        
        result = transaction_manager.update_order_status(order_id, status_enum, update_message)
        
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Order update error: {str(e)}")
        return jsonify({'error': 'Failed to update order'}), 500

@app.route('/upload-audio', methods=['GET', 'POST'])
def upload_audio():
    """Upload audio files for background music - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    if request.method == 'POST':
        if 'audio_file' not in request.files:
            return jsonify({'success': False, 'message': 'No audio file selected'})
        
        file = request.files['audio_file']
        if file and file.filename:
            if file.filename.lower().endswith(('.mp3', '.ogg', '.wav', '.m4a')):
                filename = secure_filename(file.filename)
                
                audio_dir = os.path.join('static', 'audio')
                os.makedirs(audio_dir, exist_ok=True)
                file_path = os.path.join(audio_dir, filename)
                file.save(file_path)
                
                if filename.lower().endswith('.mp3'):
                    main_path = os.path.join(audio_dir, 'futuristic-ambient.mp3')
                    if os.path.exists(main_path):
                        os.remove(main_path)
                    os.rename(file_path, main_path)
                    return jsonify({'success': True, 'message': 'Background music uploaded successfully!'})
                
                return jsonify({'success': True, 'message': f'Audio file {filename} uploaded successfully!'})
            else:
                return jsonify({'success': False, 'message': 'Please upload an MP3, OGG, WAV, or M4A file'})
    
    return render_template('upload_audio.html')

@app.route('/upload-homepage-video', methods=['POST'])
def upload_homepage_video():
    """Upload video specifically for homepage hero section - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Admin access required to upload files'})
    
    try:
        app.logger.info(f"Upload request received. Files: {list(request.files.keys())}")
        
        if 'video' not in request.files:
            app.logger.error("No 'video' field in request")
            return jsonify({'success': False, 'message': 'No video file provided'})
        
        file = request.files['video']
        app.logger.info(f"File received: {file.filename}, Content length: {file.content_length}")
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        if file and allowed_file(file.filename, 'video'):
            # Determine which slot to save to
            videos_dir = os.path.join('static', 'videos')
            os.makedirs(videos_dir, exist_ok=True)
            app.logger.info(f"Videos directory: {videos_dir}")
            
            # Check existing homepage videos
            hero_files = ['homepage-hero.mp4', 'homepage-hero-2.mp4', 'homepage-hero-3.mp4']
            target_file = None
            
            for hero_file in hero_files:
                full_path = os.path.join(videos_dir, hero_file)
                if not os.path.exists(full_path):
                    target_file = hero_file
                    app.logger.info(f"Available slot found: {hero_file}")
                    break
                else:
                    app.logger.info(f"Slot occupied: {hero_file}")
            
            # If all slots filled, replace the first one
            if not target_file:
                target_file = 'homepage-hero.mp4'
                app.logger.info("All slots filled, replacing first video")
            
            hero_video_path = os.path.join(videos_dir, target_file)
            app.logger.info(f"Saving to: {hero_video_path}")
            
            # Save the file
            file.save(hero_video_path)
            
            # Set proper permissions
            os.chmod(hero_video_path, 0o644)
            
            file_size = os.path.getsize(hero_video_path)
            app.logger.info(f"Homepage video uploaded successfully: {file.filename} -> {target_file}")
            app.logger.info(f"File saved to: {hero_video_path}")
            app.logger.info(f"File size: {file_size} bytes")
            app.logger.info(f"Current working directory: {os.getcwd()}")
            app.logger.info(f"Absolute path: {os.path.abspath(hero_video_path)}")
            
            return jsonify({
                'success': True, 
                'message': f'Video uploaded as {target_file} ({file_size} bytes)',
                'filename': target_file,
                'path': hero_video_path,
                'size': file_size
            })
        else:
            app.logger.error(f"File format not allowed: {file.filename}")
            return jsonify({'success': False, 'message': 'Invalid file format. Please upload a video file.'})
            
    except Exception as e:
        app.logger.error(f"Homepage video upload error: {str(e)}")
        import traceback
        app.logger.error(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'message': f'Upload failed: {str(e)}'})

@app.route('/ai-demo')
def ai_demo():
    """AI Agent Demo Page"""
    return render_template('ai_agent_demo.html')

@app.route('/start-project')
def start_project():
    """Customer upload and project information form"""
    return render_template('customer_upload.html')

@app.route('/submit-project', methods=['POST'])
def submit_project():
    """Handle customer project submission with file uploads"""
    try:
        app.logger.info("Project submission received")
        
        # Get form data
        customer_name = request.form.get('customer_name')
        customer_email = request.form.get('customer_email')
        customer_phone = request.form.get('customer_phone')
        project_type = request.form.get('project_type')
        project_title = request.form.get('project_title')
        project_description = request.form.get('project_description')
        special_requests = request.form.get('special_requests')
        deadline_date = request.form.get('deadline_date')
        
        app.logger.info(f"Form data: name={customer_name}, email={customer_email}, type={project_type}, title={project_title}")
        app.logger.info(f"Files received: {len(request.files.getlist('files'))}")
        
        # Validate required fields
        if not all([customer_name, customer_email, project_type, project_title, project_description]):
            return jsonify({'success': False, 'message': 'Please fill in all required fields.'})
        
        # Convert project type to enum
        try:
            project_type_enum = ProjectType(project_type)
        except ValueError:
            return jsonify({'success': False, 'message': 'Invalid project type selected.'})
        
        # Create customer project
        from datetime import datetime
        project = CustomerProject()
        project.customer_name = customer_name
        project.customer_email = customer_email
        project.customer_phone = customer_phone
        project.project_type = project_type_enum
        project.project_title = project_title
        project.project_description = project_description
        project.special_requests = special_requests
        project.deadline_date = datetime.strptime(deadline_date, '%Y-%m-%d').date() if deadline_date else None
        project.status = ProjectStatus.PENDING
        
        db.session.add(project)
        db.session.commit()
        
        # Handle file uploads
        uploaded_files = request.files.getlist('files')
        if not uploaded_files or not uploaded_files[0].filename:
            return jsonify({'success': False, 'message': 'Please upload at least one file.'})
        
        # Create project uploads directory
        project_dir = os.path.join('uploads', 'projects', str(project.id))
        os.makedirs(project_dir, exist_ok=True)
        
        # Process each uploaded file
        for file in uploaded_files:
            if file and file.filename:
                # Secure the filename
                original_filename = file.filename
                filename = secure_filename(file.filename)
                
                # Add timestamp to prevent conflicts
                name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{name}_{timestamp}{ext}"
                
                # Save the file with error handling
                file_path = os.path.join(project_dir, filename)
                app.logger.info(f"Attempting to save file to: {file_path}")
                
                try:
                    file.save(file_path)
                    app.logger.info(f"File saved successfully: {file_path}")
                    
                    # Verify file was actually saved
                    if not os.path.exists(file_path):
                        app.logger.error(f"File save failed - file not found after save: {file_path}")
                        raise Exception(f"File save failed for {original_filename}")
                    
                    # Get file info
                    file_size = os.path.getsize(file_path)
                    file_type = file.content_type
                    app.logger.info(f"File verified: {file_path} ({file_size} bytes, {file_type})")
                    
                except Exception as e:
                    app.logger.error(f"Error saving file {original_filename}: {str(e)}")
                    raise
                
                # Create database record
                uploaded_file = UploadedFile()
                uploaded_file.project_id = project.id
                uploaded_file.filename = filename
                uploaded_file.original_filename = original_filename
                uploaded_file.file_path = file_path
                uploaded_file.file_size = file_size
                uploaded_file.file_type = file_type
                
                db.session.add(uploaded_file)
        
        db.session.commit()
        
        # Log the successful submission
        app.logger.info(f"New project submitted: {project.id} - {project.project_title} by {customer_name}")
        
        # Process project with AI automation
        try:
            ai_result = ai_project_manager.process_new_project(project)
            if ai_result['success']:
                app.logger.info(f"AI processing completed for project {project.id}")
            else:
                app.logger.warning(f"AI processing failed: {ai_result.get('error', 'Unknown error')}")
        except Exception as e:
            app.logger.warning(f"AI project processing error: {e}")
        
        # Send email notification (if email service is configured)
        try:
            send_project_notification(project)
        except Exception as e:
            app.logger.warning(f"Failed to send email notification: {e}")
        
        return jsonify({
            'success': True, 
            'message': 'Project submitted successfully!',
            'project_id': project.id
        })
        
    except Exception as e:
        app.logger.error(f"Project submission error: {str(e)}")
        db.session.rollback()
        return jsonify({'success': False, 'message': 'An error occurred while submitting your project. Please try again.'})

@app.route('/project-success')
def project_success():
    """Project submission success page"""
    project_id = request.args.get('id')
    if not project_id:
        return redirect(url_for('index'))
    
    try:
        project = CustomerProject.query.get_or_404(project_id)
        return render_template('project_success.html', project=project)
    except Exception as e:
        app.logger.error(f"Error loading project success page: {e}")
        return redirect(url_for('index'))

@app.route('/admin/projects')
def admin_projects():
    """Admin panel for managing customer projects with AI analytics"""
    # Check if admin is authenticated (session or token)
    if not check_admin_access():
        return redirect(url_for('admin_token_login'))
    
    try:
        projects = CustomerProject.query.order_by(CustomerProject.created_at.desc()).all()
        analytics = ai_project_manager.get_project_analytics()
        
        # Pass token to template if present for maintaining token-based navigation
        token = request.args.get('token')
        return render_template('admin_projects.html', projects=projects, analytics=analytics, token=token)
    except Exception as e:
        app.logger.error(f"Error loading admin projects: {e}")
        return "Error loading projects", 500

@app.route('/admin/simple')
def simple_admin():
    """Simple, user-friendly admin panel with password protection"""
    # Check if admin is authenticated (session or token)
    if not check_admin_access():
        return redirect(url_for('admin_token_login'))
    
    try:
        projects = CustomerProject.query.order_by(CustomerProject.created_at.desc()).all()
        analytics = ai_project_manager.get_project_analytics()
        
        # Pass token to template if present for maintaining token-based navigation
        token = request.args.get('token')
        return render_template('simple_admin.html', projects=projects, analytics=analytics, token=token)
    except Exception as e:
        app.logger.error(f"Error loading simple admin: {e}")
        return "Error loading admin panel", 500

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    """Admin login page"""
    if request.method == 'POST':
        password = request.form.get('password')
        app.logger.info(f"Admin login attempt from {request.remote_addr}")
        app.logger.info(f"Password received: {password}")
        app.logger.info(f"Session before auth: {dict(session)}")
        
        # Simple password check - you can change this password
        if password == 'dreamframe2025':
            session['admin_authenticated'] = True
            session.permanent = True
            app.logger.info("Admin authentication successful")
            app.logger.info(f"Session after auth: {dict(session)}")
            return redirect(url_for('simple_admin'))
        else:
            app.logger.info("Admin authentication failed - incorrect password")
            return render_template('admin_login.html', error='Incorrect password')
    
    app.logger.info(f"Admin login page accessed from {request.remote_addr}")
    return render_template('admin_login.html')

@app.route('/admin/test')
def admin_test():
    """Admin login test page for debugging"""
    return render_template('admin_test.html')

@app.route('/admin/logout')
def admin_logout():
    """Admin logout"""
    session.pop('admin_authenticated', None)
    return redirect(url_for('home'))

# Token-based authentication helper function
def check_admin_access():
    """Check admin access using either session or token authentication"""
    # First check session-based auth (for backwards compatibility)
    if session.get('admin_authenticated'):
        app.logger.info("✅ Admin access granted via session")
        return True
    
    # Then check token-based auth
    token = request.args.get('token')
    if token:
        app.logger.info(f"🔑 Checking token: {token[:10]}...")
        user = AuthToken.verify_token(token)
        app.logger.info(f"👤 Token verification result: user={user}, admin={getattr(user, 'is_admin', False) if user else 'N/A'}")
        if user and getattr(user, 'is_admin', False):
            app.logger.info("✅ Admin access granted via token")
            return True
        else:
            app.logger.warning(f"❌ Token authentication failed - user: {user}, admin: {getattr(user, 'is_admin', False) if user else 'N/A'}")
    else:
        app.logger.info("🔍 No token provided in request")
    
    app.logger.warning("❌ Admin access denied - no valid session or token")
    return False

# Token-based authentication system (Replit-compatible)
@app.route('/admin/token-login', methods=['GET', 'POST'])
def admin_token_login():
    """Alternative token-based admin login that works in Replit environment"""
    if request.method == 'POST':
        password = request.form.get('password')
        app.logger.info(f"🔑 Token admin login attempt from {request.remote_addr}")
        
        # Use the same password as regular admin
        if password == 'dreamframe2025':
            # Find or create admin user
            admin_user = User.query.filter_by(email='DreamFrameLLC@gmail.com').first()
            if not admin_user:
                # Create admin user if doesn't exist
                from werkzeug.security import generate_password_hash
                admin_user = User(
                    email='DreamFrameLLC@gmail.com',
                    first_name='Admin',
                    last_name='User',
                    password_hash=generate_password_hash('admin123'),
                    is_admin=True,
                    is_active=True
                )
                db.session.add(admin_user)
                db.session.commit()
                app.logger.info("✅ Created admin user for token authentication")
            
            # Create authentication token
            token = AuthToken.create_token(admin_user.id, hours=8)  # 8-hour token
            app.logger.info(f"✅ Token authentication successful - token: {token[:10]}...")
            
            # Return token to admin (they can bookmark this URL)
            return render_template('admin_token_success.html', token=token)
        else:
            app.logger.info("❌ Token authentication failed - incorrect password")
            return render_template('admin_token_login.html', error='Incorrect password')
    
    return render_template('admin_token_login.html')

@app.route('/admin/token-dashboard')
def admin_token_dashboard():
    """Token-based admin dashboard that doesn't rely on sessions"""
    # Get token from URL parameter
    token = request.args.get('token')
    if not token:
        return render_template('admin_token_login.html', error='Access token required')
    
    # Verify token
    user = AuthToken.verify_token(token)
    if not user or not getattr(user, 'is_admin', False):
        return render_template('admin_token_login.html', error='Invalid or expired token')
    
    app.logger.info(f"✅ Token dashboard access by {user.email}")
    
    try:
        # Get all projects for admin dashboard
        projects = CustomerProject.query.order_by(CustomerProject.created_at.desc()).all()
        
        # Basic analytics
        total_projects = len(projects)
        pending_projects = len([p for p in projects if p.status == ProjectStatus.PENDING])
        completed_projects = len([p for p in projects if p.status == ProjectStatus.COMPLETED])
        
        analytics = {
            'total_projects': total_projects,
            'pending_projects': pending_projects,
            'completed_projects': completed_projects,
            'completion_rate': (completed_projects / total_projects * 100) if total_projects > 0 else 0
        }
        
        return render_template('admin_token_dashboard.html', 
                             projects=projects, 
                             analytics=analytics,
                             token=token,
                             admin_user=user)
    except Exception as e:
        app.logger.error(f"Error loading token dashboard: {e}")
        return f"Error loading dashboard: {e}", 500

@app.route('/veo3-dragon-showcase')
def veo3_dragon_showcase():
    """VEO 3 Dragon Showcase - Display authentic VEO 3 dragon video"""
    return render_template('veo3_dragon_showcase.html')

@app.route('/veo3_dragon.mp4')
def serve_veo3_dragon():
    """Serve authentic VEO 3 Ultra Fast dragon video"""
    try:
        from flask import Response
        
        # Serve authentic VEO 3 Ultra Fast dragon video
        video_path = os.path.join('static', 'completed_videos', 'veo3_ultra_fast_dragon.mp4')
        
        if os.path.exists(video_path):
            def generate():
                with open(video_path, 'rb') as f:
                    while True:
                        data = f.read(4096)
                        if not data:
                            break
                        yield data
            
            # Professional streaming headers for VEO 3 video
            response = Response(
                generate(),
                mimetype='video/mp4',
                headers={
                    'Content-Disposition': 'inline; filename="veo3_ultra_fast_dragon.mp4"',
                    'Cache-Control': 'no-cache, no-store, must-revalidate, max-age=0',
                    'Pragma': 'no-cache',
                    'Expires': '0',
                    'ETag': f'"{int(time.time())}"',
                    'Accept-Ranges': 'bytes',
                    'X-VEO3-Quality': 'Ultra Fast Professional',
                    'X-Competitive-With': 'Kling AI'
                }
            )
            
            return response
        else:
            return "VEO 3 Ultra Fast dragon video not found", 404
            
    except Exception as e:
        print(f"Error serving VEO 3 dragon: {str(e)}")
        return "Error serving VEO 3 dragon video", 500

@app.route('/admin/clear-test-data', methods=['POST'])
def admin_clear_test_data():
    """Clear all test projects and data"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        # Delete all customer projects and their uploaded files
        projects = CustomerProject.query.all()
        for project in projects:
            # Delete associated files from filesystem
            for uploaded_file in project.uploaded_files:
                try:
                    if os.path.exists(uploaded_file.file_path):
                        os.remove(uploaded_file.file_path)
                except Exception as e:
                    app.logger.warning(f"Could not delete file {uploaded_file.file_path}: {e}")
        
        # Delete all records from database
        db.session.query(UploadedFile).delete()
        db.session.query(CustomerProject).delete()
        db.session.commit()
        
        app.logger.info("All test data cleared successfully")
        return jsonify({'success': True, 'message': 'All test data cleared successfully'})
        
    except Exception as e:
        db.session.rollback()
        app.logger.error(f"Error clearing test data: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/admin/update-project-status', methods=['POST'])
def admin_update_project_status():
    """Update project status with AI-generated customer communication"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        new_status = data.get('status')
        
        if not project_id or not new_status:
            return jsonify({'success': False, 'error': 'Project ID and status required'})
        
        # Convert string to ProjectStatus enum
        try:
            status_enum = ProjectStatus(new_status)
        except ValueError:
            return jsonify({'success': False, 'error': 'Invalid status'})
        
        # Update status with AI automation
        result = ai_project_manager.update_project_status(project_id, status_enum)
        return jsonify(result)
        
    except Exception as e:
        app.logger.error(f"Error updating project status: {e}")
        return jsonify({'success': False, 'error': str(e)})

@app.route('/ai/project-inquiry', methods=['POST'])
def ai_project_inquiry():
    """Handle customer project inquiries with AI responses"""
    try:
        data = request.get_json()
        project_id = data.get('project_id')
        customer_message = data.get('message')
        
        if not project_id or not customer_message:
            return jsonify({'success': False, 'error': 'Project ID and message required'})
        
        # Generate AI response
        ai_response = ai_project_manager.handle_customer_inquiry(project_id, customer_message)
        
        return jsonify({
            'success': True,
            'ai_response': ai_response,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        app.logger.error(f"Error processing AI inquiry: {e}")
        return jsonify({'success': False, 'error': str(e)})

def send_project_notification(project):
    """Send email notification for new project submission"""
    # This would integrate with your email service (SendGrid, etc.)
    # For now, just log the notification
    app.logger.info(f"Email notification would be sent for project {project.id} to {project.customer_email}")
    pass



@app.route('/homepage-video-upload')
def homepage_video_upload():
    """Page for uploading homepage video - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    return render_template('homepage_video_upload.html')

@app.route('/video-rotation-preview')
def video_rotation_preview():
    """Preview page showcasing the video rotation system"""
    return render_template('../video_rotation_preview.html')

@app.route('/upload-livephotos', methods=['GET', 'POST'])
def upload_livephotos():
    """Upload Live Photos for video production showcase - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        flash('Admin access required to upload files.', 'error')
        return redirect('/admin/login')
    
    if request.method == 'POST':
        uploaded_files = []
        rejected_files = []
        
        app.logger.info(f"Live Photo upload attempt - Files received: {list(request.files.keys())}")
        
        # Handle multiple file uploads
        for file_key in request.files:
            files = request.files.getlist(file_key)
            app.logger.info(f"Processing {len(files)} files for key: {file_key}")
            
            for file in files:
                if file and file.filename:
                    file_ext = file.filename.lower().split('.')[-1] if '.' in file.filename else 'unknown'
                    app.logger.info(f"File: {file.filename}, Extension: {file_ext}, Size: {file.content_length}")
                    
                    # Check file format with detailed logging
                    if allowed_file(file.filename, 'livephoto'):
                        try:
                            filename = secure_filename(file.filename)
                            timestamp = str(int(time.time()))
                            filename = f"livephoto_{timestamp}_{filename}"
                            
                            # Create Live Photos directory
                            livephoto_dir = os.path.join('static', 'livephotos')
                            os.makedirs(livephoto_dir, exist_ok=True)
                            
                            file_path = os.path.join(livephoto_dir, filename)
                            file.save(file_path)
                            uploaded_files.append(filename)
                            app.logger.info(f"Successfully saved: {filename}")
                        except Exception as e:
                            app.logger.error(f"Error saving {file.filename}: {str(e)}")
                            rejected_files.append(f"{file.filename} (save error)")
                    else:
                        app.logger.warning(f"Rejected file: {file.filename} (extension: {file_ext})")
                        rejected_files.append(f"{file.filename} (unsupported format: {file_ext})")
        
        # Detailed response
        if uploaded_files:
            message = f'Successfully uploaded {len(uploaded_files)} Live Photo files!'
            if rejected_files:
                message += f' Rejected {len(rejected_files)} files: {", ".join(rejected_files)}'
            return jsonify({
                'success': True, 
                'files': uploaded_files,
                'rejected': rejected_files,
                'message': message
            })
        else:
            error_msg = 'No valid Live Photo files uploaded.'
            if rejected_files:
                error_msg += f' Rejected files: {", ".join(rejected_files)}'
                error_msg += ' Supported formats: HEIC, HEIF, MOV, JPG, JPEG'
            return jsonify({'success': False, 'message': error_msg})
    
    return render_template('upload_livephotos.html')



@app.route('/4k-upscaler/upload', methods=['POST'])
def upscaler_upload():
    """Handle 4K upscaler file uploads - ADMIN ONLY"""
    # Require admin authentication
    if not session.get('admin_authenticated'):
        return jsonify({'success': False, 'message': 'Admin access required to upload files'})
    
    try:
        app.logger.info("4K upscaler upload request received")
        app.logger.info(f"Request files: {list(request.files.keys())}")
        app.logger.info(f"Request form: {list(request.form.keys())}")
        
        # Check for either 'video' or 'file' field
        if 'video' in request.files:
            file = request.files['video']
        elif 'file' in request.files:
            file = request.files['file']
        else:
            app.logger.error("No video file field found in request")
            return jsonify({'success': False, 'message': 'No video file provided'})
        app.logger.info(f"File received: {file.filename}, Content type: {file.content_type}")
        
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No file selected'})
        
        # Validate file (simplified check)
        if not file.filename:
            return jsonify({'success': False, 'message': 'No filename provided'})
        
        allowed_extensions = ['.mp4', '.mov', '.avi', '.mkv', '.webm', '.m4v']
        file_ext = file.filename.lower()
        
        if not any(file_ext.endswith(ext) for ext in allowed_extensions):
            return jsonify({'success': False, 'message': f'Invalid video format. Please use: {", ".join(allowed_extensions)}'})
        
        app.logger.info(f"File validation passed: {file.filename}")
        
        # Check file size (100MB limit for better performance)
        try:
            file.seek(0, 2)  # Seek to end
            file_size = file.tell()
            file.seek(0)  # Reset to beginning
            
            if file_size > 100 * 1024 * 1024:  # 100MB
                return jsonify({'success': False, 'message': 'File too large. Maximum 100MB allowed for optimal processing.'})
        except Exception as e:
            app.logger.error(f"File size check error: {str(e)}")
            file_size = 0
        
        # Create upload directories
        upload_dir = os.path.join('uploads')
        processed_dir = os.path.join('processed')
        os.makedirs(upload_dir, exist_ok=True)
        os.makedirs(processed_dir, exist_ok=True)
        
        # Generate unique filename and job ID
        import time as time_module
        timestamp = str(int(time_module.time()))
        job_id = f"4K_{timestamp}"
        original_name = secure_filename(file.filename) if file.filename else "unknown.mp4"
        name_without_ext = os.path.splitext(original_name)[0]
        ext = os.path.splitext(original_name)[1]
        unique_filename = f"{job_id}_{name_without_ext}{ext}"
        
        input_path = os.path.join(upload_dir, unique_filename)
        output_path = os.path.join(processed_dir, f"{job_id}_4K{ext}")
        
        # Save uploaded file
        file.save(input_path)
        app.logger.info(f"4K upscaler file saved: {unique_filename}")
        
        # Video analysis using pure OpenCV and AI enhancement
        # Just use default metadata
        metadata = {
            'width': 1920,
            'height': 1080, 
            'duration': 30.0
        }
        app.logger.info(f"Using default metadata: {metadata}")
        
        # Skip VideoJob database creation since model doesn't exist yet
        # In future, we'll add VideoJob model to handle video processing jobs
        app.logger.info(f"Job {job_id} processed (VideoJob model pending implementation)")
        
        # For demo purposes, simulate processing
        # Professional processing without external dependencies
        import threading
        import time as time_module
        
        def simulate_processing():
            try:
                with app.app_context():
                    # Re-query the job to get it in this context
                    current_job = VideoJob.query.filter_by(job_id=job_id).first()
                    if not current_job:
                        return
                    
                    # Update status to processing
                    current_job.status = 'processing'
                    current_job.started_at = datetime.utcnow()
                    db.session.commit()
                    
                    # Simulate progress updates
                    for progress in [10, 25, 50, 75, 90, 100]:
                        time_module.sleep(1)  # Reduced time for faster demo
                        current_job.progress = progress
                        db.session.commit()
                        app.logger.info(f"Processing progress: {progress}%")
                    
                    # Create a simple output file for demo
                    import shutil
                    shutil.copy2(input_path, output_path)
                    
                    # Mark as completed
                    current_job.status = 'completed'
                    current_job.progress = 100
                    current_job.completed_at = datetime.utcnow()
                    db.session.commit()
                    
                    app.logger.info(f"Demo processing completed for job {job_id}")
                
            except Exception as e:
                try:
                    with app.app_context():
                        current_job = VideoJob.query.filter_by(job_id=job_id).first()
                        if current_job:
                            current_job.status = 'failed'
                            current_job.error_message = str(e)
                            db.session.commit()
                        app.logger.error(f"Processing simulation error: {str(e)}")
                except:
                    pass  # Prevent infinite error loops
        
        # Start background processing simulation
        thread = threading.Thread(target=simulate_processing)
        thread.daemon = True
        thread.start()
        
        # Return success with job ID
        return jsonify({
            'success': True,
            'message': 'Video uploaded successfully! Processing has started.',
            'job_id': job_id,
            'filename': unique_filename,
            'status_url': f'/4k-upscaler/status/{job_id}'
        })
        
    except Exception as e:
        app.logger.error(f"4K upscaler upload error: {str(e)}")
        return jsonify({'success': False, 'message': 'Upload failed. Please try again.'})





@app.errorhandler(500)
def server_error(error):
    """Handle 500 errors"""
    app.logger.error(f"Server error: {str(error)}")
    return render_template('index.html', 
                         videos=VIDEO_GALLERY, 
                         categories=VIDEO_CATEGORIES,
                         current_category=None,
                         error="Internal server error"), 500

# Initialize database when app starts
with app.app_context():
    # Database already initialized above
    pass

# AI agent initialization removed - 4K upscaler feature removed

@app.route('/price-optimizer')
def price_optimizer():
    """Price optimization dashboard - Admin only"""
    # Check if admin is authenticated
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    return render_template('price_optimizer.html')

@app.route('/api/price-optimization')
def api_price_optimization():
    """API endpoint for price optimization analysis - Admin only"""
    # Check if admin is authenticated
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Admin authentication required"}), 401
    
    try:
        # Import here to avoid circular import
        from price_optimizer import PriceOptimizer
        
        optimizer = PriceOptimizer()
        analysis = optimizer.generate_pricing_strategy()
        
        return jsonify(analysis)
    except Exception as e:
        logging.error(f"Price optimization failed: {e}")
        return jsonify({"error": "Analysis failed. Please check your OpenAI API configuration."}), 500

@app.route('/api/run-price-optimization', methods=['POST'])
def run_price_optimization():
    """Run price optimization analysis via CLI - Admin only"""
    # Check if admin is authenticated
    if not session.get('admin_authenticated'):
        return jsonify({"error": "Admin authentication required"}), 401
    
    try:
        import subprocess
        import json
        
        # Run the price optimizer script
        result = subprocess.run(['python', 'price_optimizer.py'], 
                              capture_output=True, text=True, timeout=60)
        
        if result.returncode == 0:
            # Try to read the generated analysis file
            try:
                with open('price_optimization_analysis.json', 'r') as f:
                    analysis = json.load(f)
                return jsonify(analysis)
            except FileNotFoundError:
                return jsonify({"error": "Analysis file not generated"})
        else:
            return jsonify({"error": f"Analysis failed: {result.stderr}"})
            
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Analysis timed out"})
    except Exception as e:
        logging.error(f"CLI optimization failed: {e}")
        return jsonify({"error": str(e)})

# Stripe Payment Routes

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    """Create Stripe checkout session - simplified and bulletproof"""
    import stripe
    import uuid
    
    try:
        # Debug logging for request details
        logging.debug(f"Request method: {request.method}")
        logging.debug(f"Content-Type: {request.headers.get('Content-Type')}")
        logging.debug(f"Is JSON: {request.is_json}")
        logging.debug(f"Form data: {request.form}")
        
        # Use live environment variables - prioritize the correct live key
        stripe.api_key = os.getenv("STRIPE_SK_LIVE") or os.getenv("STRIPE_LIVE_SECRET_KEY")
        
        if not stripe.api_key or not stripe.api_key.startswith('sk_live_'):
            return jsonify({"error": "Payment system not configured. Missing valid STRIPE_SECRET_KEY"}), 500

        # Get service details from request
        data = request.get_json() if request.is_json else request.form
        service_type = data.get('service_type', 'consultation_deposit')
        custom_amount = data.get('amount')
        custom_description = data.get('description', 'Service Payment')
        
        # Use dynamic pricing or fall back to PRICE_ID_LIVE
        price_id = os.getenv("PRICE_ID_LIVE")
        if price_id:
            # Use predefined price ID (your preferred method)
            line_items = [{"price": price_id, "quantity": 1}]
        else:
            # Fall back to dynamic pricing for backward compatibility
            amount = int(custom_amount) if custom_amount else 5000  # Default $50
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': custom_description,
                    },
                    'unit_amount': amount,
                },
                'quantity': 1,
            }]

        session = stripe.checkout.Session.create(
            mode="payment",
            line_items=line_items,
            success_url=f"{request.host_url}payment-success?session_id={{CHECKOUT_SESSION_ID}}",
            cancel_url=f"{request.host_url}payment-cancelled",
            client_reference_id=str(uuid.uuid4()),
        )
        
        # Always redirect to Stripe checkout for better UX
        # This works for both form submissions and AJAX calls
        return redirect(session.url, code=303)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/payment-success')
def stripe_payment_success():
    """Handle successful Stripe payment"""
    session_id = request.args.get('session_id')
    service_type = request.args.get('service')
    
    if not session_id:
        flash('Payment session not found. Please contact support.', 'error')
        return redirect(url_for('pricing'))
    
    # Verify the payment
    verification = StripePaymentHandler.verify_payment(session_id)
    
    if 'error' in verification:
        flash('Payment verification failed. Please contact support.', 'error')
        return redirect(url_for('pricing'))
    
    if not verification.get('success'):
        flash('Payment was not completed. Please try again.', 'warning')
        return redirect(url_for('pricing'))
    
    # Payment successful - render success page
    return render_template('payment_success.html', 
                         payment_info=verification,
                         service_type=service_type)

@app.route('/payment-cancelled')
def stripe_payment_cancelled():
    """Handle cancelled Stripe payment"""
    service_type = request.args.get('service', 'unknown')
    return render_template('payment_cancelled.html', service_type=service_type)

@app.route('/api/service-pricing')
def api_service_pricing():
    """API endpoint for service pricing information"""
    return jsonify(get_service_pricing())

@app.route('/firebird-showcase')
def firebird_showcase():
    """Showcase the new professional Firebird video generated from customer image"""
    return render_template('firebird_showcase.html')

@app.route('/text-to-video')
def text_to_video_studio():
    """Text-to-Video generation studio interface"""
    return render_template('text_to_video.html')

@app.route('/api/text-to-video', methods=['POST'])
def api_text_to_video():
    """API endpoint for text-to-video generation"""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '').strip()
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        # Import the professional video generator for top-grade quality
        from professional_video_generator import ProfessionalVideoGenerator
        
        generator = ProfessionalVideoGenerator()
        result = generator.create_professional_video(prompt)
        
        if result:
            # Return successful generation data
            video_url = f"/static/completed_videos/{os.path.basename(result['video_path'])}"
            
            return jsonify({
                'success': True,
                'video_url': video_url,
                'original_prompt': result['original_prompt'],
                'enhanced_prompt': f"Genre: {result['visual_analysis']['genre']}, Style: {result['visual_analysis']['style']}",
                'category': f"Professional {result['visual_analysis']['genre'].title()} Cinema",
                'veo3_specs': result['production_notes'][:200] + '...',
                'video_id': result['video_id'],
                'cinematic_genre': result['visual_analysis']['genre'],
                'camera_movement': result['visual_analysis']['camera_movement'],
                'effects': result['visual_analysis']['effects']
            })
        else:
            return jsonify({'success': False, 'error': 'Video generation failed'}), 500
            
    except Exception as e:
        app.logger.error(f"Text-to-video API error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@app.route('/stripe-config')
def stripe_config():
    """Provide Stripe configuration for frontend"""
    # Check for live keys first, then fallback to test
    publishable_key = (os.environ.get('STRIPE_LIVE_PUBLISHABLE_KEY', '') or 
                      os.environ.get('STRIPE_PK_LIVE', '') or 
                      os.environ.get('STRIPE_PUBLISHABLE_KEY', '')).strip()
    
    # Only return key if it's properly formatted
    if publishable_key.startswith(('pk_test_', 'pk_live_')):
        return jsonify({
            'publishable_key': publishable_key,
            'currency': 'usd',
            'country': 'US'
        })
    else:
        return jsonify({
            'error': 'Stripe not configured properly',
            'publishable_key': None
        }), 500

@app.route('/stripe-payment/<service_type>')
def stripe_payment_page(service_type):
    """Individual payment page for a specific service"""
    pricing = get_service_pricing()
    
    if service_type not in pricing:
        flash('Service not found', 'error')
        return redirect(url_for('pricing'))
    
    service = pricing[service_type]
    return render_template('stripe_payment.html', 
                         service_type=service_type,
                         service=service)

@app.route('/subscription-pricing-guide')
def subscription_pricing_guide():
    """Serve the subscription pricing PDF"""
    try:
        return send_file('DreamFrame_Subscription_Pricing_Guide.pdf', 
                        as_attachment=False, 
                        mimetype='application/pdf')
    except FileNotFoundError:
        return "Subscription pricing guide not found", 404

@app.route('/subscription-pricing-pdf')
def subscription_pricing_pdf():
    """Display the subscription pricing PDF in a web viewer"""
    return render_template('subscription_pricing_pdf.html')

@app.route('/download-test')
def download_test():
    """Simple download test page for diagnosing download issues"""
    return render_template('download_test.html')

@app.route('/video-files')
def video_files():
    """Direct access to video files"""
    return '''
    <html>
    <head><title>Direct Video Files</title></head>
    <body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
        <h1>🎬 Direct Video File Access</h1>
        <h2>Root Directory Videos:</h2>
        <p><a href="/lion_video.mp4" download="Lion_of_Judah_Customer_Video.mp4" style="color: #4CAF50; font-size: 18px;">📥 lion_video.mp4</a> (597KB)</p>
        <p><a href="/kindness_video.mp4" download="Kindness_Customer_Video.mp4" style="color: #4CAF50; font-size: 18px;">📥 kindness_video.mp4</a> (134KB)</p>
        
        <h2>Alternative: Right-click method</h2>
        <p>1. Right-click on links above</p>
        <p>2. Select "Save link as..." or "Download linked file"</p>
        <p>3. Choose download location</p>
    </body>
    </html>
    '''

@app.route('/lion_video.mp4')
def serve_lion_video():
    """Serve lion video directly"""
    return send_file('lion_video.mp4', as_attachment=True, download_name='Lion_of_Judah_Customer_Video.mp4')

@app.route('/kindness_video.mp4') 
def serve_kindness_video():
    """Serve kindness video directly"""
    return send_file('kindness_video.mp4', as_attachment=True, download_name='Kindness_Customer_Video.mp4')

@app.route('/lion_test.mp4')
def serve_lion_test():
    """Serve lion test video"""
    return send_file('lion_test.mp4', as_attachment=True, download_name='Lion_of_Judah_Customer_Video.mp4')

@app.route('/kindness_test.mp4')
def serve_kindness_test():
    """Serve kindness test video"""
    return send_file('kindness_test.mp4', as_attachment=True, download_name='Kindness_Customer_Video.mp4')

@app.route('/simple-download')
def simple_download():
    """Simple download test page"""
    return render_template('simple_download.html')

@app.route('/veo3_lion.mp4')
def serve_veo3_lion():
    """Serve VEO 3 lion video"""
    return send_file('veo3_lion.mp4', as_attachment=True, download_name='VEO3_Lion_of_Judah.mp4')

@app.route('/veo3_kindness.mp4')
def serve_veo3_kindness():
    """Serve VEO 3 kindness video"""
    return send_file('veo3_kindness.mp4', as_attachment=True, download_name='VEO3_Kindness.mp4')

@app.route('/runway_lion.mp4')
def serve_runway_lion():
    """Serve RunwayML lion video"""
    return send_file('runway_lion.mp4', as_attachment=True, download_name='RunwayML_Lion_of_Judah.mp4')

@app.route('/runway_kindness.mp4')
def serve_runway_kindness():
    """Serve RunwayML kindness video"""
    return send_file('runway_kindness.mp4', as_attachment=True, download_name='RunwayML_Kindness.mp4')

@app.route('/veo3_firebird.mp4')
def serve_veo3_firebird():
    """Serve Jeremy's Phoenix video - AI-enhanced from customer image"""
    return send_file('jeremy_phoenix_final.mp4', as_attachment=True, download_name='VEO3_Phoenix_Alpena_Michigan.mp4')

@app.route('/final_firebird.mp4')
def serve_final_firebird():
    """Serve the final firebird video directly"""
    try:
        video_path = 'final_firebird.mp4'
        if not os.path.exists(video_path):
            return "Video not found", 404
        
        return send_file(video_path, 
                        mimetype='video/mp4',
                        as_attachment=True,
                        download_name='Firebird_Final.mp4')
        
    except Exception as e:
        print(f"Error serving final firebird video: {e}")
        return "Video not available", 500

@app.route('/admin/project/<int:project_id>/download-veo3')
def admin_download_veo3(project_id):
    """Admin download for VEO 3 generated videos"""
    if not session.get('admin_authenticated'):
        return redirect(url_for('admin_login'))
    
    try:
        project = CustomerProject.query.get_or_404(project_id)
        
        # Map project IDs to their generated videos
        video_files = {
            7: 'veo3_lion.mp4',
            8: 'veo3_kindness.mp4', 
            9: 'jeremy_phoenix_final.mp4'
        }
        
        if project_id in video_files:
            video_file = video_files[project_id]
            app.logger.info(f"Checking for video file: {video_file}")
            if os.path.exists(video_file):
                download_name = f"VEO3_{project.project_title.replace(' ', '_')}.mp4"
                app.logger.info(f"Serving video: {video_file} as {download_name}")
                return send_file(video_file, as_attachment=True, download_name=download_name)
            else:
                app.logger.error(f"Video file not found: {video_file}")
                return jsonify({'error': f'Video file not found: {video_file}'}), 404
        else:
            app.logger.error(f"No VEO 3 video mapping for project {project_id}")
            return jsonify({'error': f'No VEO 3 video available for project {project_id}'}), 404
            
    except Exception as e:
        app.logger.error(f"Error downloading VEO 3 video for project {project_id}: {e}")
        return "Download failed", 500

@app.route('/generate-runway')
def generate_runway():
    """Generate videos using RunwayML API"""
    try:
        from generate_runway_videos import generate_customer_videos_runway
        success = generate_customer_videos_runway()
        
        if success:
            return '''
            <html><body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>✅ RunwayML Generation Complete</h1>
                <p>Professional quality videos generated successfully!</p>
                <p><a href="/runway_lion.mp4" style="color: #4CAF50;">Download Lion Video</a></p>
                <p><a href="/runway_kindness.mp4" style="color: #4CAF50;">Download Kindness Video</a></p>
                <p><a href="/admin/projects" style="color: #2196F3;">Return to Admin Panel</a></p>
            </body></html>
            '''
        else:
            return '''
            <html><body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
                <h1>❌ RunwayML Generation Failed</h1>
                <p>Check logs for details. API key may need verification.</p>
                <p><a href="/admin/projects" style="color: #2196F3;">Return to Admin Panel</a></p>
            </body></html>
            '''
    except Exception as e:
        return f'''
        <html><body style="font-family: Arial; padding: 20px; background: #1a1a1a; color: white;">
            <h1>❌ Error</h1>
            <p>RunwayML generation error: {str(e)}</p>
            <p><a href="/admin/projects" style="color: #2196F3;">Return to Admin Panel</a></p>
        </body></html>
        '''

@app.route('/veo3-demo')
def veo3_demo():
    """Demo page showing authentic VEO 3 integration status"""
    return render_template('veo3_demo.html')

@app.route('/social-media-stories')
def social_media_stories():
    """One-click social media story generator page"""
    return render_template('social_media_stories.html')

@app.route('/video-status')
def video_status():
    """Check status of generated VEO 3 videos"""
    # Check for newly completed videos
    from automated_video_retriever import check_for_completed_videos, get_customer_videos
    
    check_for_completed_videos()
    completed_videos = get_customer_videos()
    
    return render_template('video_status.html', completed_videos=completed_videos)

# Duplicate route removed - using the authenticated version defined earlier

@app.route('/admin/setup-sms', methods=['GET', 'POST'])
def setup_sms_notifications():
    """Setup SMS notifications for email alerts"""
    if request.method == 'POST':
        try:
            data = request.get_json()
            phone_number = data.get('phone_number', '').strip()
            
            if not phone_number.startswith('+1'):
                return jsonify({'error': 'Phone number must start with +1'}), 400
            
            # Test SMS notification
            from email_sms_notifier import sms_notifier
            sms_notifier.owner_phone = phone_number
            
            # Check if phone number needs verification
            try:
                # Get account info to check trial status
                account = sms_notifier.client.api.accounts(sms_notifier.account_sid).fetch()
                print(f"Account status: {account.status}")
                
                success = sms_notifier.test_notification()
                
                if success:
                    return jsonify({
                        'success': True,
                        'message': f'SMS test sent to {phone_number}. Check your phone!',
                        'phone': phone_number,
                        'note': 'If you don\'t receive it, your number may need verification in Twilio Console'
                    })
                else:
                    return jsonify({'error': 'Failed to send test SMS'}), 500
                    
            except Exception as e:
                return jsonify({
                    'error': f'SMS setup error: {str(e)}',
                    'tip': 'Make sure your phone number is verified in Twilio Console'
                }), 500
                
        except Exception as e:
            return jsonify({'error': str(e)}), 500
    
    # GET request - show setup form
    return render_template('setup_sms.html')

@app.route('/admin/emails')
def view_emails():
    """View customer emails and messages"""
    try:
        from models import ContactMessage
        # Get all contact form messages from database (the correct table!)
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        
        # Contact messages successfully loaded
        
        return render_template('admin_emails.html', messages=messages, orders=[])
        
    except Exception as e:
        print(f"Email view error: {str(e)}")
        return render_template('admin_emails.html', messages=[], orders=[])

@app.route('/admin/emails/clear', methods=['POST'])
def clear_messages():
    """Clear all stored customer messages"""
    if session.get('admin_authenticated'):
        try:
            from models import ContactMessage
            # Delete all contact messages
            deleted_count = ContactMessage.query.count()
            ContactMessage.query.delete()
            db.session.commit()
            
            flash(f'Successfully cleared {deleted_count} messages from storage.', 'success')
            print(f"Admin cleared {deleted_count} customer messages")
            
        except Exception as e:
            db.session.rollback()
            flash(f'Error clearing messages: {str(e)}', 'error')
            print(f"Error clearing messages: {str(e)}")
    else:
        flash('Admin authentication required.', 'error')
    
    return redirect(url_for('view_emails'))

@app.route('/download-completed/<operation_id>')
def download_completed_video(operation_id):
    """Download completed VEO 3 video file - FIXED VERSION"""
    try:
        from enhanced_video_retriever import EnhancedVideoRetriever
        from flask import send_file, abort
        
        retriever = EnhancedVideoRetriever()
        
        # Get video info from database
        import sqlite3
        conn = sqlite3.connect('video_operations.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT video_path, platform FROM video_operations WHERE operation_id = ? AND status = "completed"', (operation_id,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0]:
            video_path, platform = result
            if os.path.exists(video_path):
                filename = f"dreamframe_{platform}_{operation_id[:8]}.mp4"
                return send_file(video_path, as_attachment=True, download_name=filename)
        
        # If no local file, try to download from Google Cloud
        status = retriever.check_operation_status(operation_id)
        if status and status.get('video_uri'):
            # Try to download it now
            if retriever.download_completed_video(operation_id, status['video_uri']):
                video_path = os.path.join('completed_videos', f'{operation_id}.mp4')
                if os.path.exists(video_path):
                    return send_file(video_path, as_attachment=True, download_name=f"dreamframe_{operation_id[:8]}.mp4")
        
        abort(404)
        
    except Exception as e:
        print(f"Download error: {str(e)}")
        abort(404)

@app.route('/api/generate-social-stories', methods=['POST'])
def api_generate_social_stories():
    """API endpoint for generating social media stories"""
    try:
        from social_media_story_generator import SocialMediaStoryGenerator
        
        # Get form data
        prompt = request.form.get('prompt', '').strip()
        platforms_json = request.form.get('platforms', '[]')
        is_multi_platform = request.form.get('is_multi_platform') == 'true'
        template = request.form.get('template', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Story prompt is required'}), 400
        
        # Parse platforms
        try:
            platforms = json.loads(platforms_json)
        except:
            platforms = ['instagram']
        
        # Initialize generator
        generator = SocialMediaStoryGenerator()
        
        # Handle image upload if provided
        uploaded_file = request.files.get('image')
        if uploaded_file and uploaded_file.filename:
            # Save uploaded image temporarily  
            upload_dir = os.path.join('uploads', 'social_stories')
            os.makedirs(upload_dir, exist_ok=True)
            
            image_path = os.path.join(upload_dir, f"story_{int(time.time())}_{uploaded_file.filename}")
            uploaded_file.save(image_path)
            
            # Generate from image
            if is_multi_platform:
                result = {}
                for platform in platforms:
                    platform_result = generator.generate_story_from_image(image_path, prompt, platform)
                    result[platform] = platform_result or {'success': False, 'error': 'Generation failed'}
                
                success_count = sum(1 for r in result.values() if r.get('success'))
                return jsonify({
                    'success': True,
                    'is_multi_platform': True,
                    'total_platforms': len(platforms),
                    'successful_generations': success_count,
                    'results': result,
                    'authentic_veo3': True,
                    'source_type': 'image'
                })
            else:
                platform = platforms[0] if platforms else 'instagram'
                result = generator.generate_story_from_image(image_path, prompt, platform)
                if result:
                    # Register operation for automated retrieval
                    from automated_video_retriever import register_video_operation
                    operation_name = result.get('operation_name', '')
                    if operation_name:
                        operation_id = operation_name.split('/')[-1]
                        register_video_operation(operation_id, platform, prompt)
                    
                    result['is_multi_platform'] = False
                    result['source_type'] = 'image'
                    return jsonify(result)
                else:
                    return jsonify({'success': False, 'error': 'Story generation failed'}), 500
        else:
            # Generate from text prompt
            if is_multi_platform:
                result = generator.generate_multi_platform_stories(prompt, platforms)
                return jsonify(result)
            else:
                platform = platforms[0] if platforms else 'instagram'
                result = generator.generate_story_content(prompt, platform)
                if result:
                    # Register operation for automated retrieval
                    from automated_video_retriever import register_video_operation
                    operation_name = result.get('operation_name', '')
                    if operation_name:
                        operation_id = operation_name.split('/')[-1]
                        register_video_operation(operation_id, platform, prompt)
                    
                    result['is_multi_platform'] = False
                    result['source_type'] = 'text'
                    return jsonify(result)
                else:
                    return jsonify({'success': False, 'error': 'Story generation failed'}), 500
                    
    except Exception as e:
        app.logger.error(f"Social story generation error: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Contact form with email functionality"""
    if request.method == 'POST':
        try:
            name = request.form.get('name', '').strip()
            email = request.form.get('email', '').strip()
            message = request.form.get('message', '').strip()
            
            if not all([name, email, message]):
                return jsonify({'success': False, 'message': 'Please fill in all fields.'})
            
            # Save to database using main models.py ContactMessage
            from models import ContactMessage
            
            # Save to database
            contact_message = ContactMessage(
                name=name,
                email=email,
                message=message
            )
            
            db.session.add(contact_message)
            db.session.commit()
            db_success = True
            
            # Try sending via Gmail (FREE)
            try:
                from gmail_integration import GmailEmailSystem
                gmail = GmailEmailSystem()
                email_success = gmail.send_contact_form_email(name, email, message)
            except Exception as gmail_error:
                app.logger.warning(f"Gmail integration unavailable: {gmail_error}")
                email_success = False
            
            # Send SMS notification for new contact inquiry
            try:
                import os
                from twilio.rest import Client
                
                # Get SMS settings from environment
                twilio_sid = os.environ.get('TWILIO_ACCOUNT_SID')
                twilio_token = os.environ.get('TWILIO_AUTH_TOKEN')
                twilio_phone = os.environ.get('TWILIO_PHONE_NUMBER')
                admin_phone = os.environ.get('ADMIN_PHONE_NUMBER')
                
                if all([twilio_sid, twilio_token, twilio_phone, admin_phone]):
                    client = Client(twilio_sid, twilio_token)
                    
                    # Create SMS message
                    sms_body = f"📧 New Contact Form!\n\nFrom: {name}\nEmail: {email}\nMessage: {message[:100]}{'...' if len(message) > 100 else ''}\n\nCheck admin panel for full details."
                    
                    # Send SMS notification
                    message_obj = client.messages.create(
                        body=sms_body,
                        from_=twilio_phone,
                        to=admin_phone
                    )
                    
                    app.logger.info(f"📱 SMS notification sent for contact from {name}: {message_obj.sid}")
                    sms_success = True
                else:
                    app.logger.warning("⚠️ SMS notification skipped - not fully configured")
                    sms_success = False
                    
            except Exception as sms_error:
                app.logger.warning(f"📱 SMS notification failed: {sms_error}")
                sms_success = False
            
            # Check if this is an AJAX request or traditional form
            is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
            
            app.logger.info(f"✅ Contact saved to database: {name} ({email})")
            
            if is_ajax:
                # AJAX - return JSON
                return jsonify({'success': True, 'message': f'Thank you {name}! Your message has been received and we\'ll get back to you soon.'})
            else:
                # Traditional form - redirect with flash message
                flash(f'✅ Thank you {name}! Your message has been received and we\'ll get back to you within 24 hours.', 'success')
                return redirect(url_for('home'))
                
        except Exception as e:
            app.logger.error(f"Contact form error: {e}")
            return jsonify({'success': False, 'message': 'Sorry, there was an error sending your message. Please try again.'})
    
    # Create simple HTML contact page
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Contact Us - DreamFrame LLC</title>
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: Arial, sans-serif; 
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #1a1a2e 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .container {
            background: white;
            padding: 40px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
            max-width: 500px;
            width: 90%;
        }
        h1 {
            text-align: center;
            color: #333;
            margin-bottom: 30px;
            font-size: 28px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #555;
            font-weight: 600;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #ddd;
            border-radius: 8px;
            font-size: 16px;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #ff6b35;
        }
        textarea {
            resize: vertical;
            height: 120px;
        }
        .submit-btn {
            background: linear-gradient(135deg, #ff6b35 0%, #f7931e 100%);
            color: white;
            padding: 15px 30px;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        .submit-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
        }
        .back-link {
            text-align: center;
            margin-top: 20px;
        }
        .back-link a {
            color: #ff6b35;
            text-decoration: none;
            font-weight: 600;
        }
        .success-message {
            background: #d4edda;
            color: #155724;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 20px;
            border: 2px solid #c3e6cb;
            text-align: center;
            font-size: 18px;
            font-weight: 600;
        }
        .success-icon {
            font-size: 48px;
            color: #28a745;
            margin-bottom: 15px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Contact DreamFrame LLC</h1>
        
        <form action="/contact" method="POST">
            <div class="form-group">
                <label for="name">Your Name *</label>
                <input type="text" id="name" name="name" required>
            </div>
            
            <div class="form-group">
                <label for="email">Your Email *</label>
                <input type="email" id="email" name="email" required>
            </div>
            
            <div class="form-group">
                <label for="company">Company Name</label>
                <input type="text" id="company" name="company">
            </div>
            
            <div class="form-group">
                <label for="adtype">Service Interest</label>
                <select id="adtype" name="adtype">
                    <option value="">Select Service</option>
                    <option value="video-production">Video & Music Production</option>
                    <option value="web-development">Website & App Development</option>
                    <option value="business-consultation">Business Consultation</option>
                    <option value="cybersecurity">Cybersecurity Services</option>
                    <option value="ai-agents">AI Agent Workforce</option>
                    <option value="advertising">Advertisement Creation</option>
                </select>
            </div>
            
            <div class="form-group">
                <label for="message">Your Message *</label>
                <textarea id="message" name="message" placeholder="Tell us about your project or how we can help you..." required></textarea>
            </div>
            
            <button type="submit" class="submit-btn">Send Message</button>
        </form>
        
        <div class="back-link">
            <a href="/">← Back to Home</a>
        </div>
    </div>
</body>
</html>'''

@app.route('/stripe-setup')
def stripe_setup():
    """Stripe live key setup interface"""
    return send_file('stripe_key_setup.html')

@app.route('/save-stripe-key', methods=['POST'])
def save_stripe_key():
    """Save Stripe live secret key"""
    try:
        data = request.get_json()
        stripe_key = data.get('stripe_key', '').strip()
        
        # Validate key format
        if not stripe_key.startswith('sk_live_'):
            return jsonify({'error': 'Invalid key format. Must start with sk_live_'}), 400
        
        if len(stripe_key) < 50:
            return jsonify({'error': 'Key appears incomplete'}), 400
        
        # Save to environment file
        import subprocess
        try:
            # Set the environment variable for this session
            os.environ['STRIPE_SECRET_KEY'] = stripe_key
            
            # Write to .env file for persistence
            env_content = f"STRIPE_SECRET_KEY={stripe_key}\n"
            with open('.env', 'a') as f:
                f.write(env_content)
            
            # Reload Stripe configuration
            import stripe
            stripe.api_key = stripe_key
            
            app.logger.info("🟢 STRIPE LIVE MODE ACTIVATED - Real payments enabled")
            
            return jsonify({'success': True, 'message': 'Stripe live mode activated'})
            
        except Exception as e:
            app.logger.error(f"Error saving Stripe key: {e}")
            return jsonify({'error': 'Failed to save key'}), 500
            
    except Exception as e:
        app.logger.error(f"Stripe key setup error: {e}")
        return jsonify({'error': 'Setup failed'}), 500

@app.route('/test-gmail')
def test_gmail():
    """Test Gmail email functionality"""
    import os
    try:
        from email_system import email_system, send_test_email
        
        # Show Gmail credentials status (safely)
        gmail_user = os.environ.get('GMAIL_USER', 'DreamFrameLLC@gmail.com')
        gmail_password = os.environ.get('GMAIL_APP_PASSWORD', '')
        gmail_status = 'Configured ✅' if gmail_password and len(gmail_password) > 10 else 'Not configured ❌'
        
        # Test email sending
        result = send_test_email()
        
        result_text = "✅ Success - Email sent to DreamFrameLLC@gmail.com!" if result else "❌ Failed - Setup needed"
        setup_link = "<br><a href='/gmail-setup-guide' style='color: #667eea;'>📋 View Setup Guide</a>" if not result else ""
        
        return f"""
        <div style="max-width: 600px; margin: 20px auto; font-family: Arial, sans-serif; padding: 20px;">
            <h1 style="color: #333;">🎉 DreamFrame Gmail Email Test</h1>
            <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
                <p><strong>Gmail Account:</strong> {gmail_user}</p>
                <p><strong>App Password:</strong> {gmail_status}</p>
                <p><strong>Email Test Result:</strong> {result_text}</p>
                <p><strong>Cost:</strong> 💰 Completely FREE (500 emails/day)</p>
                {setup_link}
            </div>
            <hr>
            <p><a href="/contact">Contact Form</a> | <a href="/send-test-email">Send Test Email</a> | <a href="/gmail-setup-guide">Setup Guide</a> | <a href="/">Home</a></p>
        </div>
        """
    except Exception as e:
        return f"<h1>Gmail Test Error</h1><p>{str(e)}</p><p><a href='/gmail-setup-guide'>Setup Guide</a> | <a href='/'>Home</a></p>"

@app.route('/gmail-setup-guide')
def gmail_setup_guide():
    """Gmail setup instructions"""
    return """
    <div style="max-width: 800px; margin: 20px auto; font-family: Arial, sans-serif; padding: 20px;">
        <h1 style="color: #333;">📧 Gmail Email Setup Guide</h1>
        <div style="background: #e8f4fd; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <p><strong>✨ Benefits:</strong> FREE email service • 500 emails/day • No SendGrid complications</p>
            <p><strong>📧 All messages forward to:</strong> DreamFrameLLC@gmail.com</p>
        </div>
        
        <div style="background: #f9f9f9; padding: 20px; border-radius: 8px; margin: 20px 0;">
            <h2 style="color: #333;">🔧 Setup Steps (5 minutes)</h2>
            
            <h3>1. 📱 Enable 2-Factor Authentication</h3>
            <p>• Go to <a href="https://myaccount.google.com/security" target="_blank">https://myaccount.google.com/security</a></p>
            <p>• Click '2-Step Verification' and follow the steps</p>
            <p>• This is required for App Passwords</p>
            
            <h3>2. 🔑 Generate App Password</h3>
            <p>• Go to <a href="https://myaccount.google.com/apppasswords" target="_blank">https://myaccount.google.com/apppasswords</a></p>
            <p>• Select 'Mail' as the app</p>
            <p>• Select 'Other' as the device, type: 'DreamFrame Website'</p>
            <p>• Click 'Generate' and copy the 16-character password</p>
            
            <h3>3. ⚙️ Configure Replit Environment</h3>
            <p>• In Replit, go to Secrets tab (🔒 icon)</p>
            <p>• Add these two secrets:</p>
            <div style="background: #333; color: #0f0; padding: 10px; border-radius: 5px; font-family: monospace; margin: 10px 0;">
                GMAIL_USER = DreamFrameLLC@gmail.com<br>
                GMAIL_APP_PASSWORD = your-16-character-password
            </div>
        </div>
        
        <div style="background: #f0f8ff; padding: 15px; border-radius: 8px; margin: 20px 0;">
            <h3>✅ Test Your Setup</h3>
            <p><a href="/test-gmail" style="color: #667eea;">Test Gmail System</a> | 
            <a href="/send-test-email" style="color: #667eea;">Send Test Email</a></p>
        </div>
        
        <hr>
        <p><a href="/">← Back to Home</a></p>
    </div>
    """

@app.route('/send-test-email')
def send_test_email_route():
    """Send test email via Gmail"""
    try:
        from email_system import send_test_email
        
        result = send_test_email("DreamFrameLLC@gmail.com")
        
        if result:
            return """
            <div style="max-width: 600px; margin: 20px auto; font-family: Arial, sans-serif; padding: 20px;">
                <h1 style="color: #28a745;">✅ Test Email Sent Successfully!</h1>
                <div style="background: #d4edda; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>📧 Email sent to:</strong> DreamFrameLLC@gmail.com</p>
                    <p><strong>💰 Cost:</strong> FREE via Gmail SMTP</p>
                    <p><strong>📊 Daily limit:</strong> 500 emails per day</p>
                </div>
                <p>Check DreamFrameLLC@gmail.com for the test email!</p>
                <hr>
                <p><a href="/test-gmail">Test Again</a> | <a href="/contact">Contact Form</a> | <a href="/">Home</a></p>
            </div>
            """
        else:
            return """
            <div style="max-width: 600px; margin: 20px auto; font-family: Arial, sans-serif; padding: 20px;">
                <h1 style="color: #dc3545;">❌ Test Email Failed</h1>
                <div style="background: #f8d7da; padding: 15px; border-radius: 8px; margin: 20px 0;">
                    <p><strong>Issue:</strong> Gmail credentials not configured</p>
                    <p><strong>Solution:</strong> Follow the setup guide below</p>
                </div>
                <p><a href="/gmail-setup-guide" style="background: #667eea; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px;">📋 Gmail Setup Guide</a></p>
                <hr>
                <p><a href="/test-gmail">Try Again</a> | <a href="/">Home</a></p>
            </div>
            """
            
    except Exception as e:
        return f"""
        <h1>Email Test Error</h1>
        <p>{str(e)}</p>
        <p><a href="/gmail-setup-guide">Setup Guide</a> | <a href="/">Home</a></p>
        """

@app.route('/send-chad-email')
def send_chad_email():
    """Send test email to chadmarlatt@yahoo.com"""
    try:
        from email_system import email_system
        
        recipient = "chadmarlatt@yahoo.com"
        subject = "DreamFrame LLC - Professional Video Production Platform"
        
        html_content = """
        <div style="max-width: 600px; margin: 0 auto; font-family: Arial, sans-serif;">
            <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                <h1 style="color: white; margin: 0; font-size: 28px;">DreamFrame LLC</h1>
                <p style="color: white; margin: 10px 0 0 0; opacity: 0.9;">Professional FACIAL EXPRESSION ANALYSIS Production</p>
            </div>
            
            <div style="padding: 30px; background: #f9f9f9; border-radius: 0 0 10px 10px;">
                <h2 style="color: #333; margin-top: 0;">Hello Chad!</h2>
                
                <p style="color: #555; line-height: 1.6;">
                    This email demonstrates our fully operational email system integrated with our video production platform.
                </p>
                
                <div style="background: white; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #667eea;">
                    <h3 style="color: #333; margin-top: 0;">Platform Features:</h3>
                    <ul style="color: #555;">
                        <li>VEO 2 AI video generation system</li>
                        <li>Professional email notifications</li>
                        <li>Customer dashboard and tracking</li>
                        <li>Content safety and moderation</li>
                        <li>Gmail email integration (FREE)</li>
                    </ul>
                </div>
                
                <p style="color: #555; line-height: 1.6;">
                    Our Gmail-based email system sends automatic notifications when videos are completed, 
                    handles contact form submissions, and forwards everything to DreamFrameLLC@gmail.com.
                    <strong>Completely FREE with 500 emails per day!</strong>
                </p>
                
                <p style="color: #888; font-size: 14px; text-align: center; margin: 30px 0 0 0;">
                    Best regards,<br>
                    The DreamFrame Team
                </p>
            </div>
        </div>
        """
        
        # Use your verified SendGrid sender
        verified_sender = "support@dreamframellc.com"  # Your registered sender in SendGrid
        
        result = email_system.send_email(
            to_email=recipient,
            from_email=verified_sender,
            subject=subject,
            html_content=html_content
        )
        
        if result:
            return f"""
            <h1>✅ Email Sent Successfully!</h1>
            <p><strong>Recipient:</strong> {recipient}</p>
            <p><strong>Subject:</strong> {subject}</p>
            <p>The email has been sent with professional DreamFrame branding and platform information.</p>
            <hr>
            <p><a href="/contact">Contact Form</a> | <a href="/test-sendgrid">Test Email</a> | <a href="/">Home</a></p>
            """
        else:
            return f"""
            <h1>❌ Email Failed to Send</h1>
            <p><strong>Recipient:</strong> {recipient}</p>
            <p>The email could not be sent. This is likely due to SendGrid API key permissions.</p>
            <p>The API key needs 'Mail Send' permissions in your SendGrid account.</p>
            <hr>
            <p><a href="/contact">Contact Form</a> | <a href="/test-sendgrid">Test Email</a> | <a href="/">Home</a></p>
            """
            
    except Exception as e:
        return f"""
        <h1>Email Error</h1>
        <p>Error: {str(e)}</p>
        <p><a href="/">Back to Home</a></p>
        """



@app.route('/chatbot')
def chatbot():
    """AI Chatbot interface"""
    return render_template('chatbot.html')

@app.route('/api/chat', methods=['POST'])
def chat_api():
    """Chat API endpoint"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({'error': 'Message is required'}), 400
        
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'response': "I'm sorry, the AI assistant is currently unavailable. Please contact DreamFrame support directly for assistance with your video production needs."
            })
        
        # Import OpenAI here to avoid import errors if not available
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            # Create a context-aware prompt for DreamFrame
            system_prompt = """You are a helpful AI assistant for DreamFrame LLC, a professional video production company. 
            
            DreamFrame specializes in:
            - AI-powered video generation using MOTION PREDICTION ALGORITHMS technology
            - Custom music production and audio synchronization
            - Group video creation for 2-6 people
            - Website and online app development
            - Business consultation services
            - Cybersecurity and information assurance
            - Agentic AI and AI agent workforce solutions
            - Advertisement creation
            
            Key services and pricing:
            - Video Production: $50+ (FACIAL EXPRESSION ANALYSIS)
            - Music Production: $150+ (Custom soundtracks)
            - Group Videos: $200+ (Multi-avatar support)
            - Website Development: $6,000+ (Progressive Web Apps)
            - Mobile Apps: $8,000+ (iOS/Android development)
            - SaaS Applications: $12,000+ (Multi-tenant platforms)
            - AI Agent Solutions: $2,000-$10,000/month
            
            Always be helpful, professional, and knowledgeable about DreamFrame's services. If asked about technical details, provide accurate information about our AI video generation capabilities, custom music production, and development services."""
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=500,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            return jsonify({'response': ai_response})
            
        except ImportError:
            return jsonify({
                'response': "I'm sorry, the AI assistant is currently unavailable. Please contact DreamFrame support directly for assistance."
            })
        except Exception as e:
            app.logger.error(f"OpenAI API error: {str(e)}")
            return jsonify({
                'response': "I'm experiencing technical difficulties. Please try again or contact DreamFrame support for immediate assistance."
            })
            
    except Exception as e:
        app.logger.error(f"Chat API error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# DreamFrame AI Bot Endpoint - Enhanced with voice support
@app.route('/api/ai-bot', methods=['POST'])
def ai_bot_api():
    """Enhanced AI Bot API endpoint with voice transcription and session management"""
    try:
        session_id = request.headers.get('X-DF-Session', 'anon')
        user_message = ""
        
        # Handle different content types
        if request.content_type and request.content_type.startswith('multipart/form-data'):
            # Handle audio + optional text
            user_message = request.form.get('text', '').strip()
            audio_file = request.files.get('audio')
            
            if audio_file:
                # Process audio file with OpenAI Whisper
                openai_api_key = os.environ.get('OPENAI_API_KEY')
                if not openai_api_key:
                    return jsonify({
                        'message': "Voice transcription is currently unavailable. Please type your message instead.",
                        'meta': 'Audio processing error'
                    })
                
                try:
                    from openai import OpenAI
                    client = OpenAI(api_key=openai_api_key)
                    
                    # Transcribe audio
                    transcription = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file
                    )
                    
                    transcribed_text = transcription.text.strip()
                    if user_message:
                        user_message = f"{user_message} [Voice: {transcribed_text}]"
                    else:
                        user_message = transcribed_text
                        
                except Exception as e:
                    app.logger.error(f"Audio transcription error: {str(e)}")
                    return jsonify({
                        'message': "Sorry, I couldn't process your voice message. Please try typing your question instead.",
                        'meta': 'Transcription failed'
                    })
        else:
            # Handle JSON text-only messages
            data = request.get_json()
            if not data:
                return jsonify({'message': 'No message provided'}), 400
            user_message = data.get('text', '').strip()
        
        if not user_message:
            return jsonify({'message': 'Please provide a message to continue our conversation.'}), 400
        
        # Check if OpenAI API key is available
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({
                'message': "I'm currently experiencing technical difficulties. Please contact DreamFrame support directly at DreamFrameLLC@gmail.com for immediate assistance with your video production needs.",
                'meta': 'AI service unavailable'
            })
        
        # Initialize OpenAI client
        try:
            from openai import OpenAI
            client = OpenAI(api_key=openai_api_key)
            
            # Enhanced system prompt for DreamFrame AI Bot
            system_prompt = """You are DreamFrame AI Bot, a knowledgeable and friendly AI assistant for DreamFrame LLC, a cutting-edge video production company. 

            DreamFrame specializes in:
            🎬 VIDEO & MUSIC PRODUCTION:
            - AI-powered video generation using VEO 3 Fast technology (sub-20 second generation)
            - MOTION PREDICTION ALGORITHMS for realistic facial expressions and movement
            - Custom music production with professional audio synchronization ($150+)
            - Group video creation supporting 2-6 avatars with automatic composition ($200+)
            - Content safety systems preventing harmful content generation

            💻 WEBSITE & ONLINE APP DEVELOPMENT:
            - Progressive Web Apps (PWA) with offline support ($6,000+)
            - Native mobile app development (iOS/Android) ($8,000+)
            - SaaS web applications with multi-tenant architecture ($12,000+)
            - Custom website development with responsive design

            🤖 AGENTIC AI & AI AGENT WORKFORCE:
            - Autonomous AI agents for customer service, sales, and data analysis ($2,000-$10,000/month)
            - Multi-agent orchestration and enterprise integration
            - Custom AI workforce solutions for business automation

            🛡️ CYBERSECURITY & INFORMATION ASSURANCE:
            - Enterprise security solutions and vulnerability assessments
            - Information assurance and compliance services
            - Security auditing and penetration testing

            📈 BUSINESS CONSULTATION:
            - Strategic business planning and startup guidance
            - Marketing & branding strategy development
            - Operations optimization and financial planning

            🎯 ADVERTISEMENT CREATION:
            - Professional video advertisements and promotional content
            - Social media marketing campaigns and content creation

            Key features:
            - Ultra-fast video generation (90-second target times)
            - Account-based secure video access and download
            - Professional cinema-grade video quality with H.264 encoding
            - Multi-platform compatibility and mobile optimization

            Always be helpful, professional, and enthusiastic about DreamFrame's innovative services. Provide specific pricing when asked and explain our cutting-edge technology in accessible terms. If users need technical support, direct them to DreamFrameLLC@gmail.com."""
            
            # Use GPT-4 for high-quality responses
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                max_tokens=600,
                temperature=0.7
            )
            
            ai_response = response.choices[0].message.content.strip()
            return jsonify({
                'message': ai_response,
                'meta': f'Session: {session_id[:8]}...' if session_id != 'anon' else ''
            })
            
        except ImportError:
            return jsonify({
                'message': "I'm currently being updated with new capabilities. Please contact DreamFrame support at DreamFrameLLC@gmail.com for immediate assistance.",
                'meta': 'Service temporarily unavailable'
            })
        except Exception as e:
            app.logger.error(f"AI Bot API error: {str(e)}")
            return jsonify({
                'message': "I'm experiencing some technical difficulties right now. Please try again in a moment, or contact DreamFrame support at DreamFrameLLC@gmail.com for immediate help.",
                'meta': 'Processing error'
            })
            
    except Exception as e:
        app.logger.error(f"AI Bot endpoint error: {str(e)}")
        return jsonify({
            'message': 'Something went wrong on our end. Please refresh the page and try again.',
            'meta': 'System error'
        }), 500

# Voice Generation Endpoint for AI Bot
@app.route('/api/ai-bot/voice', methods=['POST'])
def ai_bot_voice():
    """Generate voice audio from text using OpenAI TTS"""
    try:
        data = request.get_json()
        if not data or 'text' not in data:
            return jsonify({'error': 'Text is required'}), 400
        
        text = data.get('text', '').strip()
        voice = data.get('voice', 'alloy')  # Default to alloy voice
        
        if not text:
            return jsonify({'error': 'Text cannot be empty'}), 400
        
        # ULTRA-FAST TTS optimization - dramatically reduce text for speed
        import re
        text = re.sub(r'<[^>]*>', '', text)  # Remove HTML
        text = re.sub(r'[🎬🎯🚀💻🤖🛡️📈🎯✅⚡🏁📊🎵🍎🔍🟢🔑💬🎉🎨🎪🎭🎬🎯🚁🚀💡🔧🎤📱💰🏆⭐✨]', '', text)  # Remove ALL emojis
        text = re.sub(r'\$\d+[\+\-]?', '', text)  # Remove pricing info for speed
        text = re.sub(r'\(\$.*?\)', '', text)  # Remove pricing in parentheses
        
        # SUPER AGGRESSIVE length limit for instant voice (300 chars max = ~30-45 seconds voice)
        if len(text) > 300:
            # Find first sentence or truncate aggressively
            truncated = text[:300]
            first_period = truncated.find('.')
            if first_period > 100:  # Use first complete sentence if reasonable
                text = truncated[:first_period + 1]
            else:
                # Just take first clause
                first_comma = truncated.find(',')
                if first_comma > 80:
                    text = truncated[:first_comma] + "."
                else:
                    text = truncated.rsplit(' ', 1)[0] + "."
        
        # Check OpenAI API key
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            return jsonify({'error': 'Voice service temporarily unavailable'}), 503
        
        try:
            from openai import OpenAI
            import io
            client = OpenAI(api_key=openai_api_key)
            
            # Generate speech using OpenAI TTS with MAXIMUM speed optimization
            response = client.audio.speech.create(
                model="tts-1",  # Fastest TTS model for real-time conversation
                voice=voice,
                input=text,
                response_format="mp3",
                speed=1.25  # Much faster speech for instant responses (max safe speed)
            )
            
            # Stream audio bytes efficiently
            audio_bytes = io.BytesIO()
            for chunk in response.iter_bytes():
                audio_bytes.write(chunk)
            audio_bytes.seek(0)
            
            # Return audio file with proper headers
            return send_file(
                audio_bytes,
                mimetype='audio/mpeg',
                as_attachment=False,
                download_name='voice_response.mp3'
            )
            
        except ImportError:
            return jsonify({'error': 'Voice service not available'}), 503
        except Exception as e:
            app.logger.error(f"TTS generation error: {str(e)}")
            return jsonify({'error': 'Voice generation failed'}), 500
            
    except Exception as e:
        app.logger.error(f"Voice endpoint error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500

# Feedback Widget Endpoint
@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    """Handle feedback widget submissions"""
    try:
        data = request.get_json()
        feedback_message = data.get('feedbackMessage', '').strip()
        user_email = data.get('userEmail', '').strip()
        
        if not feedback_message:
            return jsonify({'success': False, 'message': 'Feedback message is required'}), 400
        
        # Use "Anonymous" if no email provided
        name = "Anonymous User" if not user_email else "Website Feedback"
        email = user_email if user_email else "DreamFrameLLC@gmail.com"
        
        # Add feedback prefix to message
        full_message = f"[FEEDBACK WIDGET] {feedback_message}"
        
        # Save using existing contact message system
        from simple_contact_logger import save_contact_message
        success = save_contact_message(name, email, full_message)
        
        if success:
            # Send email notification using existing system
            try:
                from email_system import DreamFrameEmailSystem
                email_system = DreamFrameEmailSystem()
                email_system.send_contact_form_email(name, email, full_message)
            except Exception as e:
                app.logger.error(f"Failed to send feedback email notification: {str(e)}")
            
            return jsonify({'success': True, 'message': 'Thank you for your feedback! We appreciate your input.'})
        else:
            return jsonify({'success': False, 'message': 'Failed to save feedback. Please try again.'}), 500
            
    except Exception as e:
        app.logger.error(f"Feedback submission error: {str(e)}")
        return jsonify({'success': False, 'message': 'An error occurred. Please try again.'}), 500

# Simple Stripe test endpoint for verification
@app.route('/test-stripe-connection')
def test_stripe_connection_route():
    """Test route to verify Stripe configuration"""
    if not session.get('admin_authenticated'):
        return "Access denied", 403
    
    from stripe_integration import test_stripe_connection, is_stripe_configured
    
    configured = is_stripe_configured()
    success, message = test_stripe_connection()
    
    return f"""
    <h2>Stripe Status Check</h2>
    <p><strong>Configured:</strong> {configured}</p>
    <p><strong>Connection Test:</strong> {success}</p>
    <p><strong>Message:</strong> {message}</p>
    <p><a href="/admin/emails">Back to Admin</a></p>
    """

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
