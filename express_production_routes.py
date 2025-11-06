"""
Express Production Routes
Fast-track video production endpoints for rapid turnaround
"""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
from datetime import datetime, timedelta
import os
import json
from fast_turnaround_system import FastTurnaroundManager, TurnaroundPriority, AutomationLevel
from app import app
import logging

# Create blueprint
express_bp = Blueprint('express', __name__, url_prefix='/express')

# Initialize fast turnaround manager
turnaround_manager = FastTurnaroundManager()

@express_bp.route('/dashboard')
def express_dashboard():
    """Express production dashboard for monitoring fast turnaround projects"""
    try:
        # Get current production queue status
        capacity = turnaround_manager.estimate_capacity(24)
        
        # Mock current projects for demonstration
        current_projects = [
            {
                "id": "EXP-001",
                "type": "videogram",
                "priority": "rush",
                "status": "in_production",
                "estimated_completion": (datetime.now() + timedelta(minutes=10)).isoformat(),
                "progress": 75
            },
            {
                "id": "EXP-002", 
                "type": "quick_clip",
                "priority": "express",
                "status": "queued",
                "estimated_completion": (datetime.now() + timedelta(minutes=45)).isoformat(),
                "progress": 0
            }
        ]
        
        return render_template('express_dashboard.html', 
                             capacity=capacity,
                             projects=current_projects,
                             turnaround_manager=turnaround_manager)
        
    except Exception as e:
        app.logger.error(f"Error loading express dashboard: {e}")
        return "Error loading dashboard", 500

@express_bp.route('/calculate-turnaround', methods=['POST'])
def calculate_turnaround():
    """Calculate turnaround time for a project"""
    try:
        data = request.get_json()
        
        project_type = data.get('project_type', 'quick_clip')
        priority = TurnaroundPriority(data.get('priority', 'standard'))
        complexity = int(data.get('complexity_score', 1))
        
        turnaround_info = turnaround_manager.calculate_turnaround_time(
            project_type, priority, complexity
        )
        
        return jsonify({
            'success': True,
            'turnaround': turnaround_info
        })
        
    except Exception as e:
        app.logger.error(f"Error calculating turnaround: {e}")
        return jsonify({'error': 'Failed to calculate turnaround'}), 500

@express_bp.route('/create-ultra-order', methods=['POST'])
def create_ultra_order():
    """Create ultra-fast production order with 3-minute turnaround"""
    try:
        data = request.get_json()
        
        project_type = data.get('project_type', 'videogram')
        priority = TurnaroundPriority(data.get('priority', 'ultra'))
        
        # Calculate turnaround
        turnaround_info = turnaround_manager.calculate_turnaround_time(
            project_type, priority, data.get('complexity_score', 1)
        )
        
        # Generate automation script
        project_data = {
            'id': f"EXP-{int(datetime.now().timestamp())}",
            'type': project_type,
            'priority': priority.value,
            'estimated_minutes': turnaround_info['estimated_minutes']
        }
        
        automation_script = turnaround_manager.generate_automation_script(project_data)
        
        # Create express pipeline
        express_pipeline = turnaround_manager.create_express_pipeline(project_type)
        
        order = {
            'order_id': project_data['id'],
            'project_type': project_type,
            'priority': priority.value,
            'turnaround_info': turnaround_info,
            'automation_script': automation_script,
            'express_pipeline': express_pipeline,
            'created_at': datetime.now().isoformat(),
            'status': 'created'
        }
        
        return jsonify({
            'success': True,
            'order': order,
            'estimated_delivery': turnaround_info['delivery_time'],
            'can_rush': turnaround_info['can_rush']
        })
        
    except Exception as e:
        app.logger.error(f"Error creating express order: {e}")
        return jsonify({'error': 'Failed to create express order'}), 500

@express_bp.route('/rush-pricing')
def rush_pricing():
    """Get rush pricing information"""
    try:
        # Rush pricing multipliers
        rush_multipliers = {
            'videogram': {
                'rush': 2.0,      # 2x for rush (2-4 hours)
                'express': 1.5,   # 1.5x for express (same day)
                'standard': 1.0,  # Standard pricing
                'bulk': 0.8       # 20% discount for bulk
            },
            'quick_clip': {
                'rush': 2.5,
                'express': 1.8,
                'standard': 1.0,
                'bulk': 0.75
            },
            'family_memory': {
                'rush': 3.0,
                'express': 2.0,
                'standard': 1.0,
                'bulk': 0.7
            }
        }
        
        # Base pricing (from existing pricing system)
        base_pricing = {
            'videogram': 50,
            'quick_clip': 75, 
            'family_memory': 200,
            'military_tribute': 300,
            'wedding_story': 500
        }
        
        rush_pricing_info = {}
        for service, base_price in base_pricing.items():
            if service in rush_multipliers:
                multipliers = rush_multipliers[service]
                rush_pricing_info[service] = {
                    'base_price': base_price,
                    'rush_price': int(base_price * multipliers['rush']),
                    'express_price': int(base_price * multipliers['express']),
                    'standard_price': base_price,
                    'bulk_price': int(base_price * multipliers['bulk']),
                    'rush_savings_hours': 'Delivered in 2-4 hours',
                    'express_savings_hours': 'Same-day delivery'
                }
        
        return jsonify({
            'success': True,
            'rush_pricing': rush_pricing_info,
            'pricing_notes': {
                'rush': 'Premium pricing for 2-4 hour delivery',
                'express': 'Premium pricing for same-day delivery',
                'standard': 'Standard pricing for 1-2 day delivery',
                'bulk': 'Discount pricing for 3-5 day delivery'
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error getting rush pricing: {e}")
        return jsonify({'error': 'Failed to get pricing'}), 500

@express_bp.route('/automation-status/<project_id>')
def automation_status(project_id):
    """Get automation status for a project"""
    try:
        # Mock automation status tracking
        status = {
            'project_id': project_id,
            'current_step': 'ai_video_editing',
            'completed_steps': [
                'ai_content_analysis',
                'auto_frame_extraction'
            ],
            'remaining_steps': [
                'auto_music_sync',
                'brand_overlay_application', 
                'quality_validation',
                'final_render'
            ],
            'progress_percentage': 45,
            'estimated_completion': (datetime.now() + timedelta(minutes=12)).isoformat(),
            'automation_level': 'full_auto',
            'quality_score': 0.92
        }
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        app.logger.error(f"Error getting automation status: {e}")
        return jsonify({'error': 'Failed to get status'}), 500

@express_bp.route('/queue-optimization')
def queue_optimization():
    """Get optimized production queue"""
    try:
        # Mock current queue
        current_queue = [
            {
                'id': 'PRJ-001',
                'type': 'videogram',
                'priority': 'rush',
                'estimated_minutes': 15,
                'automation_level': 'full_auto'
            },
            {
                'id': 'PRJ-002',
                'type': 'quick_clip', 
                'priority': 'express',
                'estimated_minutes': 30,
                'automation_level': 'assisted'
            },
            {
                'id': 'PRJ-003',
                'type': 'videogram',
                'priority': 'standard',
                'estimated_minutes': 15,
                'automation_level': 'full_auto'
            }
        ]
        
        optimized_queue = turnaround_manager.optimize_production_queue(current_queue)
        
        return jsonify({
            'success': True,
            'original_queue': current_queue,
            'optimized_queue': optimized_queue,
            'optimization_benefits': {
                'time_savings': '25% reduction in total completion time',
                'batch_opportunities': 2,
                'efficiency_gain': '30% through automation batching'
            }
        })
        
    except Exception as e:
        app.logger.error(f"Error optimizing queue: {e}")
        return jsonify({'error': 'Failed to optimize queue'}), 500

# Register main app routes
@app.route('/fast-turnaround')
def fast_turnaround_page():
    """Fast turnaround service page"""
    try:
        # Get capacity and pricing info
        capacity = turnaround_manager.estimate_capacity(24)
        
        return render_template('fast_turnaround.html',
                             capacity=capacity,
                             turnaround_manager=turnaround_manager)
        
    except Exception as e:
        app.logger.error(f"Error loading fast turnaround page: {e}")
        return "Error loading page", 500

@app.route('/express-quote', methods=['POST'])
def express_quote():
    """Generate instant quote for express service"""
    try:
        data = request.get_json()
        
        project_type = data.get('project_type', 'videogram')
        priority = TurnaroundPriority(data.get('priority', 'express'))
        complexity = int(data.get('complexity_score', 1))
        
        # Calculate turnaround and pricing
        turnaround_info = turnaround_manager.calculate_turnaround_time(
            project_type, priority, complexity
        )
        
        # Get rush pricing multipliers
        base_prices = {'videogram': 50, 'quick_clip': 75, 'family_memory': 200}
        multipliers = {'rush': 2.0, 'express': 1.5, 'standard': 1.0}
        
        base_price = base_prices.get(project_type, 75)
        multiplier = multipliers.get(priority.value, 1.0)
        express_price = int(base_price * multiplier)
        
        quote = {
            'project_type': project_type,
            'priority': priority.value,
            'base_price': base_price,
            'express_price': express_price,
            'price_difference': express_price - base_price,
            'turnaround_info': turnaround_info,
            'savings': f"Save {turnaround_info['estimated_hours']} hours",
            'quote_valid_until': (datetime.now() + timedelta(hours=1)).isoformat()
        }
        
        return jsonify({
            'success': True,
            'quote': quote
        })
        
    except Exception as e:
        app.logger.error(f"Error generating express quote: {e}")
        return jsonify({'error': 'Failed to generate quote'}), 500