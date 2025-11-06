"""
Admin panel functionality for DreamFrame LLC
"""
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from models import db, Order, CustomerMessage, OrderRevision, VideoAsset, PricingTier, AdminSettings, OrderStatus, ServiceType
from datetime import datetime, timedelta
import os
import json
import glob
from payment_health_monitor import PaymentHealthMonitor
from daily_payment_scheduler import DailyPaymentScheduler

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/')
def dashboard():
    """Admin dashboard with key metrics"""
    # Get key metrics
    total_orders = Order.query.count()
    pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).count()
    in_progress = Order.query.filter(Order.status.in_([OrderStatus.PAID, OrderStatus.IN_PRODUCTION, OrderStatus.REVIEW])).count()
    completed_orders = Order.query.filter_by(status=OrderStatus.COMPLETED).count()
    
    # Revenue calculation (completed orders)
    completed_revenue = db.session.query(db.func.sum(Order.amount)).filter_by(status=OrderStatus.COMPLETED).scalar() or 0
    pending_revenue = db.session.query(db.func.sum(Order.amount)).filter(Order.status.in_([OrderStatus.PAID, OrderStatus.IN_PRODUCTION, OrderStatus.REVIEW])).scalar() or 0
    
    # Recent orders
    recent_orders = Order.query.order_by(Order.created_at.desc()).limit(10).all()
    
    # Unread messages count
    unread_messages = CustomerMessage.query.filter_by(read_by_admin=False, is_from_customer=True).count()
    
    return render_template('admin/dashboard.html',
                         total_orders=total_orders,
                         pending_orders=pending_orders,
                         in_progress=in_progress,
                         completed_orders=completed_orders,
                         completed_revenue=completed_revenue,
                         pending_revenue=pending_revenue,
                         recent_orders=recent_orders,
                         unread_messages=unread_messages)

@admin_bp.route('/orders')
def orders():
    """View and manage all orders"""
    status_filter = request.args.get('status')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    query = Order.query
    if status_filter:
        query = query.filter_by(status=OrderStatus(status_filter))
    
    orders = query.order_by(Order.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/orders.html', orders=orders, status_filter=status_filter)

@admin_bp.route('/orders/<int:order_id>')
def order_detail(order_id):
    """Detailed view of a specific order"""
    order = Order.query.get_or_404(order_id)
    messages = CustomerMessage.query.filter_by(order_id=order_id).order_by(CustomerMessage.created_at.asc()).all()
    revisions = OrderRevision.query.filter_by(order_id=order_id).order_by(OrderRevision.created_at.desc()).all()
    
    return render_template('admin/order_detail.html', order=order, messages=messages, revisions=revisions)

@admin_bp.route('/orders/<int:order_id>/update_status', methods=['POST'])
def update_order_status(order_id):
    """Update order status"""
    order = Order.query.get_or_404(order_id)
    new_status = request.form.get('status')
    notes = request.form.get('notes', '')
    
    if new_status:
        old_status = order.status
        order.status = OrderStatus(new_status)
        order.updated_at = datetime.utcnow()
        
        # Note: delivered_at attribute doesn't exist in Order model
        # This would need to be added to the model if needed
        
        # Create status update message
        if notes:
            message = CustomerMessage()
            message.order_id = order.order_id  # Use order.order_id instead of order_id
            message.message_text = f"Status updated to {new_status}: {notes}"  # Use message_text to match database
            message.is_from_customer = False
            message.read_by_admin = True
            db.session.add(message)
        
        db.session.commit()
        flash(f'Order status updated to {new_status.replace("_", " ").title()}', 'success')
    
    return redirect(url_for('admin.order_detail', order_id=order_id))

@admin_bp.route('/messages')
def messages():
    """View customer contact form messages"""
    unread_only = request.args.get('unread', False, type=bool)
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Import ContactMessage for contact form submissions
    from models import ContactMessage
    
    query = ContactMessage.query
    if unread_only:
        query = query.filter_by(status='new')  # ContactMessage uses 'status' field, not 'read_by_admin'
    
    messages = query.order_by(ContactMessage.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/messages.html', messages=messages, unread_only=unread_only)

@admin_bp.route('/messages/<int:message_id>/mark_read', methods=['POST'])
def mark_message_read(message_id):
    """Mark contact message as read"""
    from models import ContactMessage
    message = ContactMessage.query.get_or_404(message_id)
    message.status = 'read'  # ContactMessage uses 'status' field
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/messages/<int:message_id>/delete', methods=['POST'])
def delete_message(message_id):
    """Delete contact message"""
    from models import ContactMessage
    message = ContactMessage.query.get_or_404(message_id)
    db.session.delete(message)
    db.session.commit()
    
    return jsonify({'success': True})

@admin_bp.route('/download-contact-guide')
def download_contact_guide():
    """Download the Contact Form System Guide PDF"""
    from flask import send_file
    import os
    
    pdf_path = os.path.join('static', 'DreamFrame_Contact_System_Guide.pdf')
    if os.path.exists(pdf_path):
        return send_file(pdf_path, 
                        as_attachment=True, 
                        download_name="DreamFrame_Contact_System_Guide.pdf",
                        mimetype='application/pdf')
    else:
        flash('Contact guide PDF not found.', 'error')
        return redirect(url_for('admin.messages'))

@admin_bp.route('/gallery')
def gallery():
    """Manage video gallery"""
    videos = VideoAsset.query.order_by(VideoAsset.created_at.desc()).all()
    return render_template('admin/gallery.html', videos=videos)

@admin_bp.route('/gallery/add', methods=['GET', 'POST'])
def add_video():
    """Add new video to gallery"""
    if request.method == 'POST':
        # Handle video upload and database entry
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        video_file = request.form.get('video_file')
        thumbnail = request.form.get('thumbnail')
        duration = request.form.get('duration')
        
        if title and video_file:
            video_id = title.lower().replace(' ', '_').replace('-', '_')
            
            # Create VideoAsset with proper attributes (based on model)
            video_asset = VideoAsset()
            video_asset.filename = video_file
            video_asset.file_path = f"static/videos/{video_file}"
            video_asset.asset_type = 'gallery'
            video_asset.order_id = 'GALLERY_ASSET'  # Placeholder for gallery assets
            
            db.session.add(video_asset)
            db.session.commit()
            
            flash('Video added successfully', 'success')
            return redirect(url_for('admin.gallery'))
    
    return render_template('admin/add_video.html')

@admin_bp.route('/pricing')
def pricing():
    """Manage pricing tiers"""
    tiers = PricingTier.query.order_by(PricingTier.price.asc()).all()  # Use 'price' not 'base_price'
    return render_template('admin/pricing.html', tiers=tiers)

@admin_bp.route('/pricing/<int:tier_id>/edit', methods=['GET', 'POST'])
def edit_pricing(tier_id):
    """Edit pricing tier"""
    tier = PricingTier.query.get_or_404(tier_id)
    
    if request.method == 'POST':
        tier.tier_name = request.form.get('tier_name')
        tier.base_price = int(float(request.form.get('base_price', 0)) * 100)  # Convert to cents
        tier.delivery_days = int(request.form.get('delivery_days', 7))
        tier.active = 'active' in request.form
        
        # Handle features (JSON array)
        features_text = request.form.get('features', '')
        if features_text:
            tier.features = [f.strip() for f in features_text.split('\n') if f.strip()]
        
        db.session.commit()
        flash('Pricing tier updated successfully', 'success')
        return redirect(url_for('admin.pricing'))
    
    return render_template('admin/edit_pricing.html', tier=tier)

@admin_bp.route('/settings')
def settings():
    """System settings"""
    settings = AdminSettings.query.all()
    return render_template('admin/settings.html', settings=settings)

@admin_bp.route('/settings/update', methods=['POST'])
def update_settings():
    """Update system settings"""
    for key, value in request.form.items():
        if key.startswith('setting_'):
            setting_key = key.replace('setting_', '')
            setting = AdminSettings.query.filter_by(setting_key=setting_key).first()
            
            if setting:
                setting.setting_value = value
                setting.updated_at = datetime.utcnow()
    
    db.session.commit()
    flash('Settings updated successfully', 'success')
    return redirect(url_for('admin.settings'))

@admin_bp.route('/analytics')
def analytics():
    """Business analytics dashboard"""
    # Revenue analytics
    thirty_days_ago = datetime.utcnow() - timedelta(days=30)
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    
    revenue_30_days = db.session.query(db.func.sum(Order.amount)).filter(
        Order.status == OrderStatus.COMPLETED,
        Order.created_at >= thirty_days_ago  # Use created_at instead of delivered_at
    ).scalar() or 0
    
    revenue_7_days = db.session.query(db.func.sum(Order.amount)).filter(
        Order.status == OrderStatus.COMPLETED,
        Order.created_at >= seven_days_ago  # Use created_at instead of delivered_at
    ).scalar() or 0
    
    # Order analytics
    orders_by_service = db.session.query(
        Order.service_type,
        db.func.count(Order.id).label('count'),
        db.func.sum(Order.amount).label('revenue')
    ).group_by(Order.service_type).all()
    
    # Monthly trends
    monthly_data = db.session.query(
        db.func.date_trunc('month', Order.created_at).label('month'),
        db.func.count(Order.id).label('orders'),
        db.func.sum(Order.amount).label('revenue')
    ).filter(Order.created_at >= datetime.utcnow() - timedelta(days=365)).group_by('month').all()
    
    return render_template('admin/analytics.html',
                         revenue_30_days=revenue_30_days,
                         revenue_7_days=revenue_7_days,
                         orders_by_service=orders_by_service,
                         monthly_data=monthly_data)

@admin_bp.route('/ai-health-reports')
def ai_health_reports():
    """AI Payment System Health Reports Dashboard"""
    # Get all health report files
    report_files = glob.glob('payment_health_*.json')
    report_files.sort(reverse=True)  # Most recent first
    
    reports = []
    for file_path in report_files[:30]:  # Show last 30 reports
        try:
            with open(file_path, 'r') as f:
                report_data = json.load(f)
                # Extract timestamp from filename
                timestamp = file_path.replace('payment_health_', '').replace('.json', '')
                report_data['filename'] = file_path
                report_data['timestamp_formatted'] = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
                reports.append(report_data)
        except Exception as e:
            print(f"Error loading report {file_path}: {e}")
    
    # Get current scheduler status
    try:
        scheduler = DailyPaymentScheduler()
        scheduler_status = scheduler.get_status()
    except Exception as e:
        scheduler_status = {'error': str(e)}
    
    return render_template('admin/ai_health_reports.html', 
                         reports=reports, 
                         scheduler_status=scheduler_status)

@admin_bp.route('/ai-health-reports/<filename>')
def view_health_report(filename):
    """View detailed health report"""
    try:
        with open(filename, 'r') as f:
            report_data = json.load(f)
        
        # Extract timestamp from filename
        timestamp = filename.replace('payment_health_', '').replace('.json', '')
        report_data['timestamp_formatted'] = datetime.strptime(timestamp, '%Y%m%d_%H%M%S').strftime('%Y-%m-%d %H:%M:%S')
        
        return render_template('admin/health_report_detail.html', report=report_data)
    except Exception as e:
        flash(f'Error loading report: {str(e)}', 'error')
        return redirect(url_for('admin.ai_health_reports'))

@admin_bp.route('/ai-health-reports/run-check', methods=['POST'])
def run_manual_health_check():
    """Run manual health check"""
    try:
        scheduler = DailyPaymentScheduler()
        scheduler.run_immediate_check()
        flash('Manual health check completed successfully!', 'success')
    except Exception as e:
        flash(f'Error running health check: {str(e)}', 'error')
    
    return redirect(url_for('admin.ai_health_reports'))