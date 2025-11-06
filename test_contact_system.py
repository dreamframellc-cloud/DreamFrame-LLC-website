#!/usr/bin/env python3
"""
Test the contact form system to identify issues
"""

import sys
import os
from datetime import datetime

def test_contact_imports():
    """Test if all contact form imports work"""
    print("🧪 Testing Contact Form System")
    print("=" * 50)
    
    try:
        # Test database logger import
        from simple_contact_logger import save_contact_message
        print("✅ Database logger import successful")
        
        # Test saving a message
        test_result = save_contact_message(
            name="Test User",
            email="test@example.com", 
            message="This is a test message to verify the contact system works."
        )
        
        if test_result:
            print("✅ Database save successful")
        else:
            print("❌ Database save failed")
            
    except Exception as e:
        print(f"❌ Database logger error: {e}")
    
    try:
        # Test Gmail integration import
        from gmail_integration import GmailEmailSystem
        print("✅ Gmail integration import successful")
        
        # Test Gmail system (without sending)
        gmail = GmailEmailSystem()
        print("✅ Gmail system initialized")
        
    except Exception as e:
        print(f"❌ Gmail integration error: {e}")

def test_flash_messages():
    """Test Flask flash message system"""
    try:
        from flask import Flask, flash
        test_app = Flask(__name__)
        test_app.secret_key = "test"
        
        with test_app.app_context():
            flash("Test message", "success")
            print("✅ Flask flash system working")
            
    except Exception as e:
        print(f"❌ Flask flash error: {e}")

def check_database_messages():
    """Check if any messages are actually being saved"""
    try:
        import sqlite3
        
        # Check if database file exists
        if os.path.exists('contact_messages.db'):
            print("✅ Database file exists")
            
            conn = sqlite3.connect('contact_messages.db')
            cursor = conn.cursor()
            
            cursor.execute("SELECT COUNT(*) FROM contact_messages")
            count = cursor.fetchone()[0]
            
            print(f"📊 Total messages in database: {count}")
            
            if count > 0:
                cursor.execute("SELECT * FROM contact_messages ORDER BY timestamp DESC LIMIT 3")
                recent_messages = cursor.fetchall()
                
                print("\n📧 Recent messages:")
                for msg in recent_messages:
                    print(f"  - {msg[1]} ({msg[2]}): {msg[3][:50]}...")
            
            conn.close()
            
        else:
            print("❌ Database file not found")
            
    except Exception as e:
        print(f"❌ Database check error: {e}")

def create_simple_contact_test():
    """Create a minimal contact form for testing"""
    
    test_html = '''<!DOCTYPE html>
<html>
<head>
    <title>Contact Test</title>
    <style>
        .flash-message { padding: 10px; margin: 10px 0; border-radius: 5px; }
        .success { background: #d4edda; color: #155724; border: 1px solid #c3e6cb; }
        .error { background: #f8d7da; color: #721c24; border: 1px solid #f5c6cb; }
        form { max-width: 500px; margin: 20px auto; padding: 20px; }
        input, textarea { width: 100%; padding: 8px; margin: 5px 0; }
        button { background: #007bff; color: white; padding: 10px 20px; border: none; cursor: pointer; }
    </style>
</head>
<body>
    <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
        <h1>Contact Form Test</h1>
        
        <!-- Flash Messages -->
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="flash-message {{ category }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        
        <form method="POST" action="/contact">
            <div>
                <label>Name:</label>
                <input type="text" name="name" required>
            </div>
            <div>
                <label>Email:</label>
                <input type="email" name="email" required>
            </div>
            <div>
                <label>Message:</label>
                <textarea name="message" rows="4" required></textarea>
            </div>
            <button type="submit">Send Message</button>
        </form>
        
        <hr>
        <p><a href="/">Back to Homepage</a></p>
    </div>
</body>
</html>'''
    
    with open('templates/simple_contact.html', 'w') as f:
        f.write(test_html)
    
    print("✅ Created simple contact form template")

if __name__ == "__main__":
    test_contact_imports()
    print()
    test_flash_messages()
    print()
    check_database_messages()
    print()
    create_simple_contact_test()
    
    print("\n🔧 Recommended fixes:")
    print("1. Make sure simple_contact_logger.py exists and works")
    print("2. Verify Flask flash messages are displaying in template")
    print("3. Check that contact form POST is reaching the /contact route")
    print("4. Test with the simple contact form at /contact")