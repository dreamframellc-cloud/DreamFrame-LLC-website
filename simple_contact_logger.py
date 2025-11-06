#!/usr/bin/env python3
"""
Simple contact form logger - No external email service required
Saves all customer messages to database and logs for manual follow-up
"""

import os
import json
from datetime import datetime
from models import db
from sqlalchemy import Column, Integer, String, Text, DateTime
from app import app

class ContactMessage(db.Model):
    """Store customer contact messages"""
    __tablename__ = 'contact_messages'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(20), default='new')  # new, responded, closed
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'message': self.message,
            'created_at': self.created_at.isoformat(),
            'status': self.status
        }

def save_contact_message(name: str, email: str, message: str) -> bool:
    """Save contact message to database and log file"""
    try:
        # Save to database
        contact = ContactMessage(
            name=name,
            email=email,
            message=message
        )
        
        with app.app_context():
            db.session.add(contact)
            db.session.commit()
        
        # Also save to JSON log file for backup
        log_entry = {
            'timestamp': datetime.utcnow().isoformat(),
            'name': name,
            'email': email,
            'message': message
        }
        
        log_file = 'customer_messages.json'
        
        # Read existing messages
        messages = []
        if os.path.exists(log_file):
            with open(log_file, 'r') as f:
                messages = json.load(f)
        
        # Add new message
        messages.append(log_entry)
        
        # Save updated messages
        with open(log_file, 'w') as f:
            json.dump(messages, f, indent=2)
        
        print(f"✅ Contact message saved: {name} ({email})")
        return True
        
    except Exception as e:
        print(f"❌ Error saving contact message: {e}")
        return False

def get_all_messages():
    """Get all contact messages from database"""
    try:
        with app.app_context():
            messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
            return [msg.to_dict() for msg in messages]
    except Exception as e:
        print(f"Error retrieving messages: {e}")
        return []

def mark_message_responded(message_id: int):
    """Mark a message as responded to"""
    try:
        with app.app_context():
            message = ContactMessage.query.get(message_id)
            if message:
                message.status = 'responded'
                db.session.commit()
                return True
    except Exception as e:
        print(f"Error updating message status: {e}")
    return False

if __name__ == "__main__":
    # Create database table
    with app.app_context():
        db.create_all()
        print("✅ Contact messages table created")
    
    # Test saving a message
    test_result = save_contact_message(
        name="Test Customer",
        email="test@example.com",
        message="This is a test message without email services"
    )
    
    if test_result:
        print("✅ Message logging system working!")
        
        # Show all messages
        messages = get_all_messages()
        print(f"📨 Total messages: {len(messages)}")
        for msg in messages[-3:]:  # Show last 3
            print(f"  - {msg['name']} ({msg['email']}): {msg['message'][:50]}...")