from flask import Blueprint, request, jsonify, render_template, flash, redirect, url_for
import os
import logging
from datetime import datetime
from veo3_generator import VEO3VideoGenerator
from models import CustomerProject, db
from werkzeug.utils import secure_filename

veo3_bp = Blueprint('veo3', __name__)
veo3_generator = VEO3VideoGenerator()

@veo3_bp.route('/veo3/generate', methods=['POST'])
def generate_veo3_video():
    """
    Generate video using VEO 3 from customer project
    """
    try:
        project_id = request.form.get('project_id')
        service_type = request.form.get('service_type', 'videogram')
        
        if not project_id:
            return jsonify({'error': 'Project ID required'}), 400
        
        # Get customer project
        project = CustomerProject.query.get(project_id)
        if not project:
            return jsonify({'error': 'Project not found'}), 404
        
        # Find uploaded image
        image_path = None
        project_dir = f"uploads/projects/{project_id}"
        
        if os.path.exists(project_dir):
            for file in os.listdir(project_dir):
                if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                    image_path = os.path.join(project_dir, file)
                    break
        
        if not image_path:
            return jsonify({'error': 'No image found for project'}), 400
        
        # Generate video based on service type
        if service_type == 'videogram':
            result = veo3_generator.generate_videogram(
                image_path=image_path,
                customer_name=project.customer_name.split()[0],  # First name
                project_description=project.project_description or 'Professional VideoGram'
            )
        elif service_type == 'family_memory':
            result = veo3_generator.generate_family_memory(
                image_path=image_path,
                memory_description=project.project_description or 'Family memory video',
                duration=30
            )
        else:
            return jsonify({'error': 'Unsupported service type'}), 400
        
        if result['success']:
            # Update project status
            project.status = 'COMPLETED'
            project.completion_date = datetime.now()
            db.session.commit()
            
            # Log successful generation
            logging.info(f"VEO 3 video generated for project {project_id}: {result['video_path']}")
            
            return jsonify({
                'success': True,
                'video_path': result['video_path'],
                'thumbnail_path': result['thumbnail_path'],
                'duration': result['duration'],
                'resolution': result['resolution'],
                'file_size': result['file_size'],
                'cost': veo3_generator.get_generation_cost(result['duration']),
                'model': 'VEO-3'
            })
        else:
            logging.error(f"VEO 3 generation failed for project {project_id}: {result.get('error')}")
            return jsonify({
                'success': False,
                'error': result.get('error'),
                'fallback_available': True
            }), 500
            
    except Exception as e:
        logging.error(f"VEO 3 route error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@veo3_bp.route('/veo3/studio')
def veo3_studio():
    """
    VEO 3 Video Studio interface for advanced video generation
    """
    # Get pending projects for VEO 3 processing
    pending_projects = CustomerProject.query.filter_by(status='IN_PROGRESS').all()
    
    return render_template('veo3_studio.html', 
                         pending_projects=pending_projects,
                         api_valid=veo3_generator.validate_api_key())

@veo3_bp.route('/veo3/batch-generate', methods=['POST'])
def batch_generate():
    """
    Batch process multiple projects with VEO 3
    """
    try:
        json_data = request.get_json() or {}
        project_ids = json_data.get('project_ids', [])
        service_type = json_data.get('service_type', 'videogram')
        
        results = []
        total_cost = 0
        
        for project_id in project_ids:
            # Process each project
            project = CustomerProject.query.get(project_id)
            if not project:
                continue
                
            # Find image
            image_path = None
            project_dir = f"uploads/projects/{project_id}"
            
            if os.path.exists(project_dir):
                for file in os.listdir(project_dir):
                    if file.lower().endswith(('.jpg', '.jpeg', '.png')):
                        image_path = os.path.join(project_dir, file)
                        break
            
            if not image_path:
                results.append({
                    'project_id': project_id,
                    'success': False,
                    'error': 'No image found'
                })
                continue
            
            # Generate video
            if service_type == 'videogram':
                result = veo3_generator.generate_videogram(
                    image_path=image_path,
                    customer_name=project.customer_name.split()[0],
                    project_description=project.project_details
                )
            else:
                result = veo3_generator.generate_family_memory(
                    image_path=image_path,
                    memory_description=project.project_details,
                    duration=30
                )
            
            if result['success']:
                project.status = 'COMPLETED'
                project.completion_date = datetime.now()
                db.session.commit()
                
                cost = veo3_generator.get_generation_cost(result['duration'])
                total_cost += cost
                
                results.append({
                    'project_id': project_id,
                    'success': True,
                    'video_path': result['video_path'],
                    'cost': cost
                })
            else:
                results.append({
                    'project_id': project_id,
                    'success': False,
                    'error': result.get('error')
                })
        
        return jsonify({
            'success': True,
            'processed': len(results),
            'total_cost': total_cost,
            'results': results
        })
        
    except Exception as e:
        logging.error(f"Batch generation error: {e}")
        return jsonify({'error': 'Batch processing failed'}), 500

@veo3_bp.route('/veo3/preview/<project_id>')
def preview_generation(project_id):
    """
    Preview what VEO 3 will generate for a project
    """
    project = CustomerProject.query.get(project_id)
    if not project:
        return jsonify({'error': 'Project not found'}), 404
    
    # Estimate generation cost
    if project.service_type == 'videogram':
        duration = 5
    elif project.service_type == 'family_memory':
        duration = 30
    else:
        duration = 15
    
    cost = veo3_generator.get_generation_cost(duration)
    
    return jsonify({
        'project_id': project_id,
        'customer_name': project.customer_name,
        'service_type': project.service_type,
        'estimated_duration': duration,
        'estimated_cost': cost,
        'project_details': project.project_details
    })