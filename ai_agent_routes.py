"""
AI Agent Routes for DreamFrame LLC
API endpoints for AI-powered customer service automation
"""

from flask import Blueprint, request, jsonify
from ai_email_agent import email_agent
from ai_transaction_manager import AITransactionManager
import json

ai_bp = Blueprint('ai_agent', __name__, url_prefix='/ai')

@ai_bp.route('/process-email', methods=['POST'])
def process_email():
    """Process incoming email and generate AI response"""
    
    try:
        data = request.get_json()
        
        from_email = data.get('from_email')
        subject = data.get('subject', '')
        content = data.get('content', '')
        
        if not from_email or not content:
            return jsonify({
                "error": "Missing required fields: from_email, content"
            }), 400
        
        # Send SMS notification
        from email_sms_notifier import notify_email_received
        notify_email_received(from_email, subject, content)
        
        # Process email with AI agent
        result = email_agent.process_incoming_email(from_email, subject, content)
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to process email: {str(e)}"
        }), 500

@ai_bp.route('/classify-intent', methods=['POST'])
def classify_intent():
    """Classify email intent for debugging/testing"""
    
    try:
        data = request.get_json()
        
        email_content = data.get('content', '')
        subject = data.get('subject', '')
        
        intent = email_agent.classify_email_intent(email_content, subject)
        
        return jsonify({
            "intent_type": intent.intent_type,
            "service_type": intent.service_type.value if intent.service_type else None,
            "customer_name": intent.customer_name,
            "customer_email": intent.customer_email,
            "urgency": intent.urgency,
            "requirements": intent.requirements,
            "extracted_info": intent.extracted_info
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to classify intent: {str(e)}"
        }), 500

@ai_bp.route('/generate-response', methods=['POST'])
def generate_response():
    """Generate AI response for given intent and email"""
    
    try:
        data = request.get_json()
        
        # Reconstruct intent from request
        from ai_email_agent import EmailIntent
        from models import ServiceType
        
        intent = EmailIntent(
            intent_type=data.get('intent_type', 'general_inquiry'),
            service_type=ServiceType(data['service_type']) if data.get('service_type') else None,
            customer_name=data.get('customer_name'),
            customer_email=data.get('customer_email'),
            urgency=data.get('urgency', 'normal'),
            requirements=data.get('requirements', {}),
            extracted_info=data.get('extracted_info', {})
        )
        
        email_content = data.get('email_content', '')
        
        response = email_agent.generate_ai_response(intent, email_content)
        
        return jsonify({
            "ai_response": response
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate response: {str(e)}"
        }), 500

@ai_bp.route('/follow-ups', methods=['GET'])
def get_follow_ups():
    """Get automated follow-up emails to send"""
    
    try:
        follow_ups = email_agent.generate_follow_up_emails()
        
        return jsonify({
            "follow_ups": follow_ups,
            "count": len(follow_ups)
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to generate follow-ups: {str(e)}"
        }), 500

@ai_bp.route('/send-follow-up', methods=['POST'])
def send_follow_up():
    """Send a specific follow-up email"""
    
    try:
        data = request.get_json()
        
        to_email = data.get('to_email')
        subject = data.get('subject')
        content = data.get('content')
        customer_name = data.get('customer_name')
        
        if not all([to_email, subject, content]):
            return jsonify({
                "error": "Missing required fields: to_email, subject, content"
            }), 400
        
        email_sent = email_agent.send_email_response(
            to_email=to_email,
            subject=subject,
            content=content,
            customer_name=customer_name
        )
        
        return jsonify({
            "email_sent": email_sent,
            "message": "Follow-up email sent successfully" if email_sent else "Failed to send email"
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to send follow-up: {str(e)}"
        }), 500

@ai_bp.route('/order-analytics', methods=['GET'])
def get_order_analytics():
    """Get AI-generated business analytics"""
    
    try:
        transaction_manager = AITransactionManager()
        analytics = transaction_manager.get_order_analytics()
        
        return jsonify(analytics)
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to get analytics: {str(e)}"
        }), 500

@ai_bp.route('/customer-inquiry', methods=['POST'])
def handle_customer_inquiry():
    """Handle customer inquiry with AI response"""
    
    try:
        data = request.get_json()
        
        order_id = data.get('order_id')
        customer_message = data.get('message')
        
        if not order_id or not customer_message:
            return jsonify({
                "error": "Missing required fields: order_id, message"
            }), 400
        
        transaction_manager = AITransactionManager()
        ai_response = transaction_manager.handle_customer_inquiry(order_id, customer_message)
        
        return jsonify({
            "ai_response": ai_response
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Failed to handle inquiry: {str(e)}"
        }), 500

@ai_bp.route('/webhook/email', methods=['POST'])
def email_webhook():
    """Webhook endpoint for incoming emails from email providers"""
    
    try:
        data = request.get_json()
        
        # Parse email data (format depends on email provider)
        from_email = data.get('from', {}).get('email')
        subject = data.get('subject', '')
        content = data.get('text', '') or data.get('html', '')
        
        if from_email and content:
            # Send SMS notification
            from email_sms_notifier import notify_email_received
            notify_email_received(from_email, subject, content)
            
            result = email_agent.process_incoming_email(from_email, subject, content)
            return jsonify(result)
        else:
            return jsonify({"error": "Invalid email data"}), 400
        
    except Exception as e:
        return jsonify({
            "error": f"Webhook processing failed: {str(e)}"
        }), 500

@ai_bp.route('/test-email', methods=['POST'])
def test_email():
    """Test endpoint for email processing"""
    
    try:
        data = request.get_json()
        
        # Sample email for testing
        sample_emails = {
            "new_order": {
                "from_email": "john@example.com",
                "subject": "Wedding Video Quote",
                "content": "Hi, I need a wedding highlight video for my wedding next month. Can you provide a quote? My name is John Smith and the wedding is on July 15th."
            },
            "pricing_request": {
                "from_email": "sarah@example.com", 
                "subject": "Video Production Pricing",
                "content": "Hello, I'm interested in your video production services. Could you send me your pricing information? I'm particularly interested in social media content creation."
            },
            "order_inquiry": {
                "from_email": "mike@example.com",
                "subject": "Order Status Check",
                "content": "Hi, I placed an order #ORD123456 last week and wanted to check on the status. When will it be ready?"
            }
        }
        
        test_type = data.get('test_type', 'new_order')
        test_email = sample_emails.get(test_type, sample_emails['new_order'])
        
        # Send SMS notification for test
        from email_sms_notifier import notify_email_received
        notify_email_received(test_email['from_email'], test_email['subject'], test_email['content'])
        
        result = email_agent.process_incoming_email(
            test_email['from_email'],
            test_email['subject'], 
            test_email['content']
        )
        
        return jsonify({
            "test_email": test_email,
            "result": result
        })
        
    except Exception as e:
        return jsonify({
            "error": f"Test failed: {str(e)}"
        }), 500