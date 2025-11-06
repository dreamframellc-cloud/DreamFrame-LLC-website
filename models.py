from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import enum
import secrets

db = SQLAlchemy()

# Database-backed authentication tokens for Replit compatibility
class AuthToken(db.Model):
    __tablename__ = 'auth_tokens'
    
    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(128), unique=True, nullable=False, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    user = db.relationship('User', backref='auth_tokens')
    
    @classmethod
    def create_token(cls, user_id, hours=24):
        """Create a new authentication token for a user"""
        from datetime import timedelta
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=hours)
        
        auth_token = cls(
            token=token,
            user_id=user_id,
            expires_at=expires_at
        )
        db.session.add(auth_token)
        db.session.commit()
        return token
    
    @classmethod
    def verify_token(cls, token):
        """Verify a token and return the associated user"""
        auth_token = cls.query.filter_by(
            token=token,
            is_active=True
        ).first()
        
        if auth_token and auth_token.expires_at > datetime.utcnow():
            return auth_token.user
        elif auth_token:
            # Token expired, deactivate it
            auth_token.is_active = False
            db.session.commit()
        
        return None

class ProjectType(enum.Enum):
    VIDEOGRAM = "videogram"
    QUICK_CLIP = "quick_clip"
    FAMILY_MEMORY = "family_memory"
    MILITARY_TRIBUTE = "military_tribute"
    WEDDING_STORY = "wedding_story"
    CORPORATE = "corporate"

class ProjectStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    DELIVERED = "delivered"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    PAID = "paid"
    IN_PRODUCTION = "in_production"
    REVIEW = "review"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class ServiceType(enum.Enum):
    VIDEOGRAM = "videogram"
    SOCIAL_CONTENT = "social_content"
    FLASH_PROMOTION = "flash_promotion"
    WEDDING_HIGHLIGHT = "wedding_highlight"
    CORPORATE_VIDEO = "corporate_video"
    FULL_PRODUCTION = "full_production"

class User(UserMixin, db.Model):
    """Customer user accounts for the platform"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Account Info
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    
    # Profile Info
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    phone = db.Column(db.String(20))
    
    # Account Status
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    email_verified = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    # Relationships
    video_orders = db.relationship('VideoOrder', backref='customer', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Set password hash"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_id(self):
        """Flask-Login method to get user ID for session storage"""
        return str(self.id)
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def __repr__(self):
        return f'<User {self.email}>'

class VideoOrder(db.Model):
    """Customer video generation orders"""
    id = db.Column(db.Integer, primary_key=True)
    
    # Customer
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Order Details
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    platform = db.Column(db.String(50), default='instagram')  # instagram, tiktok, youtube, etc.
    
    # VEO 3 Integration
    veo3_operation_id = db.Column(db.String(100), unique=True, index=True)  # Google VEO 3 operation ID
    source_image_path = db.Column(db.String(500))  # Path to uploaded image
    generated_video_path = db.Column(db.String(500))  # Path to completed video
    
    # Status
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime)
    
    # Generation Details
    prompt_used = db.Column(db.Text)  # AI prompt used for generation
    generation_settings = db.Column(db.Text)  # JSON settings
    
    @property
    def is_ready(self):
        """Check if video is ready for download"""
        return self.status == OrderStatus.COMPLETED and self.generated_video_path
    
    @property
    def is_generating(self):
        """Check if video is currently being generated"""
        return self.status == OrderStatus.IN_PRODUCTION
    
    def __repr__(self):
        return f'<VideoOrder {self.id}: {self.title}>'

class CustomerProject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Link to user account (optional for backward compatibility)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    # Customer Information (kept for legacy support)
    customer_name = db.Column(db.String(100), nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_phone = db.Column(db.String(20))
    
    # Project Details
    project_type = db.Column(db.Enum(ProjectType), nullable=False)
    project_title = db.Column(db.String(200), nullable=False)
    project_description = db.Column(db.Text, nullable=False)
    special_requests = db.Column(db.Text)
    deadline_date = db.Column(db.Date)
    budget_range = db.Column(db.String(50))
    
    # Project Status
    status = db.Column(db.Enum(ProjectStatus), default=ProjectStatus.PENDING)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # File tracking
    uploaded_files = db.relationship('UploadedFile', backref='project', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<CustomerProject {self.id}: {self.project_title}>'

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('customer_project.id'), nullable=False)
    
    # File Information
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.Integer)
    file_type = db.Column(db.String(50))
    
    # Upload metadata
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)
    description = db.Column(db.String(500))  # Customer can describe each file
    
    def __repr__(self):
        return f'<UploadedFile {self.filename}>'

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Order Information
    order_id = db.Column(db.String(50), unique=True, nullable=False)
    customer_email = db.Column(db.String(120), nullable=False)
    customer_name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING)
    amount = db.Column(db.Integer, nullable=False)  # in cents
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    estimated_delivery = db.Column(db.DateTime)
    
    # Payment and AI Integration
    stripe_payment_intent_id = db.Column(db.String(200))
    ai_thread_id = db.Column(db.String(200))
    requirements = db.Column(db.Text)  # JSON string of requirements
    
    def __repr__(self):
        return f'<Order {self.order_id}: {self.service_type.value}>'

class CustomerMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('order.order_id'), nullable=False)
    
    # Message Information
    message_text = db.Column(db.Text, nullable=False)
    is_from_customer = db.Column(db.Boolean, default=True)
    read_by_admin = db.Column(db.Boolean, default=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<CustomerMessage {self.id}: Order {self.order_id}>'

class OrderRevision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('order.order_id'), nullable=False)
    
    # Revision Information
    revision_number = db.Column(db.Integer, default=1)
    revision_notes = db.Column(db.Text)
    status = db.Column(db.String(50), default='pending')
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<OrderRevision {self.revision_number}: Order {self.order_id}>'

class VideoAsset(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(50), db.ForeignKey('order.order_id'), nullable=False)
    
    # Asset Information
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    asset_type = db.Column(db.String(50))  # 'raw', 'processed', 'final'
    file_size = db.Column(db.Integer)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<VideoAsset {self.filename}: Order {self.order_id}>'

class ContactMessage(db.Model):
    __tablename__ = 'contact_messages'
    __table_args__ = {'extend_existing': True}
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(255), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(50), default='new')
    
    def __repr__(self):
        return f'<ContactMessage {self.id}: {self.name} ({self.email})>'

class PricingTier(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Tier Information
    name = db.Column(db.String(100), nullable=False)
    service_type = db.Column(db.Enum(ServiceType), nullable=False)
    price = db.Column(db.Integer, nullable=False)  # in cents
    description = db.Column(db.Text)
    
    # Features
    features = db.Column(db.Text)  # JSON string of features
    is_active = db.Column(db.Boolean, default=True)
    
    def __repr__(self):
        return f'<PricingTier {self.name}: ${self.price/100}>'

class AdminSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Settings
    setting_key = db.Column(db.String(100), unique=True, nullable=False)
    setting_value = db.Column(db.Text)
    setting_type = db.Column(db.String(50), default='string')  # 'string', 'int', 'bool', 'json'
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<AdminSettings {self.setting_key}: {self.setting_value}>'

class VideoJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    
    # Job Information
    job_id = db.Column(db.String(100), unique=True, nullable=False)
    project_id = db.Column(db.Integer, db.ForeignKey('customer_project.id'), nullable=True)
    
    # Processing Details
    status = db.Column(db.String(50), default='pending')  # pending, processing, completed, failed
    input_file_path = db.Column(db.String(500))
    output_file_path = db.Column(db.String(500))
    processing_type = db.Column(db.String(100))  # veo3, runway, upscaling, etc.
    
    # Progress Tracking
    progress_percentage = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<VideoJob {self.job_id}: {self.status}>'

def init_database(app):
    """Initialize database with tables"""
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")