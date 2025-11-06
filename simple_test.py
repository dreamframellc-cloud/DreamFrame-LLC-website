#!/usr/bin/env python3
"""
Simple test to verify 4K upscaler database functionality
"""

from app import app, db
from models import VideoJob
from datetime import datetime

def test_database():
    """Test VideoJob database operations"""
    
    with app.app_context():
        print("Testing VideoJob database model...")
        
        # Create a test job
        test_job = VideoJob(
            job_id="TEST_123456",
            original_filename="test_video.mp4",
            input_file_path="/uploads/test_video.mp4",
            output_file_path="/processed/test_video_4k.mp4",
            status="pending",
            progress=0,
            original_width=1920,
            original_height=1080,
            duration=30.0,
            file_size=10485760,  # 10MB
            service_tier="standard",
            amount=4900,  # $49
            customer_email="test@example.com",
            customer_name="Test User",
            created_at=datetime.utcnow()
        )
        
        try:
            # Add to database
            db.session.add(test_job)
            db.session.commit()
            print("✓ Test job created successfully")
            
            # Query the job
            found_job = VideoJob.query.filter_by(job_id="TEST_123456").first()
            if found_job:
                print("✓ Job found in database")
                print(f"  Job ID: {found_job.job_id}")
                print(f"  Status: {found_job.status}")
                print(f"  Filename: {found_job.original_filename}")
                
                # Test to_dict method
                job_dict = found_job.to_dict()
                print("✓ Job serialization works")
                print(f"  Dict keys: {list(job_dict.keys())}")
            else:
                print("✗ Job not found in database")
            
            # Cleanup
            db.session.delete(test_job)
            db.session.commit()
            print("✓ Test job cleaned up")
            
        except Exception as e:
            print(f"✗ Database test failed: {e}")
            db.session.rollback()

if __name__ == '__main__':
    test_database()