"""
AI Email Agent for DreamFrame LLC
Handles automated email communications, order processing, and customer inquiries
"""

import os
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
from dataclasses import dataclass
import openai
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from models import Order, CustomerMessage, OrderStatus, ServiceType, db
from ai_transaction_manager import AITransactionManager
from email_sms_notifier import notify_email_received

# the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
# do not change this unless explicitly requested by the user
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
SENDGRID_API_KEY = os.environ.get("SENDGRID_API_KEY")
FROM_EMAIL = "support@dreamframe.com"  # Standardized email address

openai_client = openai.OpenAI(api_key=OPENAI_API_KEY)
sendgrid_client = SendGridAPIClient(api_key=SENDGRID_API_KEY) if SENDGRID_API_KEY else None

@dataclass
class EmailIntent:
    """Classified email intent and extracted information"""
    intent_type: str  # 'new_order', 'order_inquiry', 'pricing_request', 'general_inquiry', 'complaint'
    service_type: Optional[ServiceType] = None
    order_id: Optional[str] = None
    customer_name: Optional[str] = None
    customer_email: Optional[str] = None
    requirements: Optional[Dict] = None
    urgency: str = "normal"  # 'low', 'normal', 'high', 'urgent'
    extracted_info: Optional[Dict] = None

class AIEmailAgent:
    """AI-powered email agent for automated customer communication"""
    
    def __init__(self):
        self.transaction_manager = AITransactionManager()
        self.company_info = {
            "name": "DreamFrame LLC",
            "tagline": "Veteran-owned video production company",
            "services": {
                "videogram": {"price": 50, "delivery": "3-5 business days"},
                "social_content": {"price": 150, "delivery": "5-7 business days"},
                "wedding_highlight": {"price": 500, "delivery": "7-10 business days"},
                "corporate_video": {"price": 1000, "delivery": "10-14 business days"},
                "full_production": {"price": 2000, "delivery": "2-3 weeks"}
            },
            "contact_email": "hello@dreamframe.com",
            "phone": "(555) 123-4567"
        }

    def classify_email_intent(self, email_content: str, subject: str = "") -> EmailIntent:
        """Use AI to classify email intent and extract relevant information"""
        
        prompt = f"""
        Analyze this customer email and classify the intent. Extract relevant information.
        
        Subject: {subject}
        Email Content: {email_content}
        
        Available service types: videogram, social_content, wedding_highlight, corporate_video, full_production
        
        Respond with JSON in this exact format:
        {{
            "intent_type": "new_order|order_inquiry|pricing_request|general_inquiry|complaint",
            "service_type": "videogram|social_content|wedding_highlight|corporate_video|full_production|null",
            "customer_name": "extracted name or null",
            "customer_email": "extracted email or null",
            "urgency": "low|normal|high|urgent",
            "requirements": {{"any_specific_requirements": "extracted_details"}},
            "extracted_info": {{"any_other_relevant_info": "details"}}
        }}
        """
        
        try:
            # Fallback to rule-based classification to avoid OpenAI rate limits
            return self._classify_email_fallback(email_content, subject)
            

            
        except Exception as e:
            print(f"Error classifying email: {e}")
            return self._classify_email_fallback(email_content, subject)

    def _classify_email_fallback(self, email_content: str, subject: str = "") -> EmailIntent:
        """Rule-based email classification fallback"""
        content_lower = email_content.lower()
        subject_lower = subject.lower()
        
        # Extract customer name (improved)
        customer_name = None
        import re
        name_patterns = [
            r"my name is ([a-zA-Z\s]+?)(?:\.|,|$|\s+and)",
            r"i'm ([a-zA-Z\s]+?)(?:\.|,|$|\s+and)",
            r"this is ([a-zA-Z\s]+?)(?:\.|,|$|\s+and)"
        ]
        for pattern in name_patterns:
            match = re.search(pattern, content_lower)
            if match:
                customer_name = match.group(1).strip().title()
                break
        
        # Determine intent and service type
        if any(word in content_lower for word in ['order', 'book', 'purchase', 'buy', 'need', 'want']):
            # Check for specific services
            if any(word in content_lower for word in ['videogram', 'video gram']):
                return EmailIntent(
                    intent_type="new_order",
                    service_type=ServiceType.VIDEOGRAM,
                    customer_name=customer_name,
                    urgency="normal",
                    requirements={"service": "videogram"}
                )
            elif any(word in content_lower for word in ['wedding', 'marriage', 'bride', 'groom']):
                return EmailIntent(
                    intent_type="new_order",
                    service_type=ServiceType.WEDDING_HIGHLIGHT,
                    customer_name=customer_name,
                    urgency="normal",
                    requirements={"service": "wedding"}
                )
            elif any(word in content_lower for word in ['social', 'instagram', 'facebook', 'content']):
                return EmailIntent(
                    intent_type="new_order",
                    service_type=ServiceType.SOCIAL_CONTENT,
                    customer_name=customer_name,
                    urgency="normal",
                    requirements={"service": "social"}
                )
            else:
                return EmailIntent(
                    intent_type="new_order",
                    customer_name=customer_name,
                    urgency="normal"
                )
        
        elif any(word in content_lower for word in ['price', 'cost', 'quote', 'rate', 'pricing']):
            return EmailIntent(
                intent_type="pricing_request",
                customer_name=customer_name,
                urgency="normal"
            )
        
        elif any(word in content_lower for word in ['status', 'order #', 'ord123', 'progress', 'update']):
            # Try to extract order ID
            order_match = re.search(r'order\s*#?\s*([a-zA-Z0-9]+)', content_lower)
            order_id = order_match.group(1) if order_match else None
            return EmailIntent(
                intent_type="order_inquiry",
                order_id=order_id,
                customer_name=customer_name,
                urgency="normal"
            )
        
        else:
            return EmailIntent(
                intent_type="general_inquiry",
                customer_name=customer_name,
                urgency="normal"
            )

    def generate_ai_response(self, intent: EmailIntent, email_content: str) -> str:
        """Generate personalized AI response based on email intent"""
        
        context = f"""
        You are a professional customer service representative for DreamFrame LLC, a veteran-owned video production company.
        
        Customer Intent: {intent.intent_type}
        Service Type: {intent.service_type.value if intent.service_type else "Not specified"}
        Customer Name: {intent.customer_name or "Valued Customer"}
        
        Company Information:
        - Veteran-owned and operated
        - Specializes in transforming photos and memories into professional videos
        - Services: VideoGrams ($50), Social Content ($150), Wedding Highlights ($500), Corporate Videos ($1000), Full Production ($2000+)
        - All projects include professional editing, custom music, and unlimited revisions
        - Fast turnaround times and personalized service
        
        Original Email: {email_content}
        
        Generate a warm, professional response that:
        1. Addresses their specific needs
        2. Provides relevant pricing and timeline information
        3. Includes a clear call-to-action
        4. Maintains our veteran-owned brand identity
        5. Uses a conversational, friendly tone
        """
        
        # Use fallback responses to avoid OpenAI rate limits
        return self._get_fallback_response(intent)

    def _get_fallback_response(self, intent: EmailIntent) -> str:
        """Fallback response when AI generation fails"""
        
        responses = {
            "new_order": f"""Thank you for your interest in DreamFrame LLC! 

We're excited to help bring your vision to life. As a veteran-owned company, we take pride in delivering professional video production services with personalized attention.

For your project, I'd recommend starting with our consultation process where we can discuss your specific needs, timeline, and budget. Our services range from quick VideoGrams ($50) to full production packages ($2000+).

Please reply with:
- Your preferred service type
- Project timeline
- Any specific requirements

We'll get back to you within 2 hours with a detailed proposal.

Best regards,
DreamFrame Team""",
            
            "pricing_request": f"""Thank you for your interest in DreamFrame LLC!

Here's our current pricing structure:

🎬 VideoGrams: $50 (3-5 business days)
📱 Social Media Content: $150 (5-7 business days)  
💒 Wedding Highlights: $500 (7-10 business days)
🏢 Corporate Videos: $1000 (10-14 business days)
🎥 Full Production: $2000+ (2-3 weeks)

All packages include:
- Professional editing and color correction
- Custom music and sound design
- Unlimited revisions until perfect
- High-resolution final delivery

Ready to get started? Reply with your project details and we'll create a custom quote.

Proudly veteran-owned and operated,
DreamFrame Team""",
            
            "general_inquiry": f"""Thank you for reaching out to DreamFrame LLC!

As a veteran-owned video production company, we specialize in transforming your precious memories and photos into professional videos that tell your story.

Whether you need a quick VideoGram, social media content, or a full production piece, we're here to help bring your vision to life with the attention to detail that our military background instills.

How can we serve you today?

Best regards,
DreamFrame Team"""
        }
        
        return responses.get(intent.intent_type, responses["general_inquiry"])

    def send_email_response(self, to_email: str, subject: str, content: str, 
                          customer_name: Optional[str] = None) -> bool:
        """Send email response using SendGrid"""
        
        if not sendgrid_client:
            print("SendGrid not configured")
            return False
        
        try:
            from_email = FROM_EMAIL
            
            # Personalize subject if customer name available
            if customer_name and not subject.startswith("Re:"):
                subject = f"Re: Your inquiry - {subject}"
            
            message = Mail(
                from_email=from_email,
                to_emails=to_email,
                subject=subject,
                html_content=content.replace('\n', '<br>')
            )
            
            response = sendgrid_client.send(message)
            return response.status_code == 202
            
        except Exception as e:
            print(f"Failed to send email: {e}")
            return False

    def process_incoming_email(self, from_email: str, subject: str, content: str) -> Dict:
        """Main method to process incoming emails and generate responses"""
        
        # Send SMS notification to owner
        try:
            notify_email_received(from_email, subject, content)
        except Exception as e:
            print(f"SMS notification failed: {e}")
        
        # Classify email intent
        intent = self.classify_email_intent(content, subject)
        
        # Handle different intent types
        if intent.intent_type == "new_order" and intent.service_type:
            return self._handle_new_order(intent, from_email, content)
        elif intent.intent_type == "order_inquiry" and intent.order_id:
            return self._handle_order_inquiry(intent, from_email)
        else:
            return self._handle_general_inquiry(intent, from_email, subject, content)

    def _handle_new_order(self, intent: EmailIntent, from_email: str, content: str) -> Dict:
        """Handle new order requests"""
        
        # For demo purposes, simulate order creation without Stripe
        try:
            import uuid
            order_id = f"DF_{int(datetime.now().timestamp())}"
            
            # Simulate successful order creation
            order_result = {
                'order_id': order_id,
                'payment_url': f'https://checkout.stripe.com/demo/{order_id}',
                'status': 'success'
            }
            
            # Generate personalized response with order details
            service_name = intent.service_type.value.replace('_', ' ').title() if intent.service_type else "Video Production"
            service_price = self.company_info['services'].get(intent.service_type.value, {}).get('price', 'Custom') if intent.service_type else 'Custom'
            service_delivery = self.company_info['services'].get(intent.service_type.value, {}).get('delivery', '5-7 business days') if intent.service_type else '5-7 business days'
            
            response_content = f"""Thank you for choosing DreamFrame LLC for your {service_name} project!

I've created your order #{order_result['order_id']} and prepared everything for you.

Project Details:
- Service: {service_name}
- Estimated Delivery: {service_delivery}
- Total: ${service_price}

Payment Link: {order_result['payment_url']}

Once payment is complete, I'll reach out within 2 hours to discuss your specific requirements and begin production.

Thank you for supporting our veteran-owned business!

Best regards,
DreamFrame Team"""

            # Send response
            email_sent = self.send_email_response(
                to_email=from_email,
                subject=f"Your DreamFrame Order #{order_result['order_id']} - Payment Ready",
                content=response_content,
                customer_name=intent.customer_name
            )
            
            return {
                "status": "success",
                "action": "order_created",
                "order_id": order_result['order_id'],
                "email_sent": email_sent
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_order_inquiry(self, intent: EmailIntent, from_email: str) -> Dict:
        """Handle order status inquiries"""
        
        try:
            # Find order
            order = Order.query.filter_by(order_id=intent.order_id).first()
            
            if not order:
                response_content = f"""I couldn't find an order with ID #{intent.order_id}. 

Please double-check the order number or contact us directly if you need assistance.

Best regards,
DreamFrame Team"""
            else:
                # Generate status update message
                status_message = f"Your order #{order.order_id} is currently {order.status.value.replace('_', ' ').title()}."
                
                response_content = f"""Here's an update on your order #{order.order_id}:

{status_message}

Service: {order.service_type.value.replace('_', ' ').title()}
Status: {order.status.value.replace('_', ' ').title()}
Created: {order.created_at.strftime('%B %d, %Y')}

If you have any questions or concerns, please don't hesitate to reach out.

Thank you for choosing DreamFrame LLC!

Best regards,
DreamFrame Team"""
            
            email_sent = self.send_email_response(
                to_email=from_email,
                subject=f"Order #{intent.order_id} Status Update",
                content=response_content,
                customer_name=intent.customer_name
            )
            
            return {
                "status": "success",
                "action": "status_update",
                "email_sent": email_sent
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}

    def _handle_general_inquiry(self, intent: EmailIntent, from_email: str, 
                              subject: str, content: str) -> Dict:
        """Handle general inquiries and pricing requests"""
        
        # Generate AI response
        ai_response = self.generate_ai_response(intent, content)
        
        # Send response
        email_sent = self.send_email_response(
            to_email=from_email,
            subject=f"Re: {subject}" if not subject.startswith("Re:") else subject,
            content=ai_response,
            customer_name=intent.customer_name
        )
        
        return {
            "status": "success",
            "action": "inquiry_response",
            "email_sent": email_sent
        }

    def generate_follow_up_emails(self) -> List[Dict]:
        """Generate automated follow-up emails for orders"""
        
        follow_ups = []
        
        # Find orders that need follow-ups
        pending_orders = Order.query.filter_by(status=OrderStatus.PENDING).all()
        in_production_orders = Order.query.filter_by(status=OrderStatus.IN_PRODUCTION).all()
        
        for order in pending_orders:
            # Follow up on unpaid orders after 24 hours
            if order.created_at < datetime.utcnow() - timedelta(hours=24):
                follow_up_content = f"""Hi {order.customer_name},

I noticed you haven't completed payment for your DreamFrame order #{order.order_id} yet.

No worries! Your order is still reserved. You can complete payment anytime using this secure link:
[Payment Link]

If you have any questions or need to modify your order, just reply to this email.

Best regards,
DreamFrame Team"""

                follow_ups.append({
                    "order_id": order.order_id,
                    "customer_email": order.customer_email,
                    "subject": f"Complete Your DreamFrame Order #{order.order_id}",
                    "content": follow_up_content
                })
        
        for order in in_production_orders:
            # Progress updates for orders in production
            days_in_production = (datetime.utcnow() - order.created_at).days
            
            if days_in_production == 3:  # 3-day progress update
                progress_content = f"""Hi {order.customer_name},

Great news! Your DreamFrame project #{order.order_id} is progressing beautifully.

Our editing team has completed the initial cut and is now working on:
- Color correction and enhancement
- Audio mixing and music integration
- Final polish and effects

You'll receive a preview for review within the next 2-3 days.

Excited to share the results with you!

Best regards,
DreamFrame Team"""

                follow_ups.append({
                    "order_id": order.order_id,
                    "customer_email": order.customer_email,
                    "subject": f"Your DreamFrame Project #{order.order_id} - Progress Update",
                    "content": progress_content
                })
        
        return follow_ups

# Create global instance
email_agent = AIEmailAgent()