"""
AI Transaction Manager for DreamFrame LLC
Handles payment processing, order management, and customer communication
"""
import os
import json
import stripe
from datetime import datetime, timedelta
from openai import OpenAI
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum

# Initialize services
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')
openai_client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY'))

# Import enums and models from models to maintain consistency
from models import OrderStatus, ServiceType, Order

class AITransactionManager:
    def __init__(self):
        self.orders = {}  # In production, use a database
        self.service_pricing = {
            ServiceType.VIDEOGRAM: 5000,  # $50
            ServiceType.SOCIAL_CONTENT: 15000,  # $150
            ServiceType.WEDDING_HIGHLIGHT: 50000,  # $500
            ServiceType.CORPORATE_VIDEO: 100000,  # $1000
            ServiceType.FULL_PRODUCTION: 200000,  # $2000+
        }
        
    def create_payment_session(self, service_type: ServiceType, customer_email: str, 
                             customer_name: str, requirements: Dict) -> Dict:
        """Create Stripe checkout session for a service"""
        try:
            amount = self.service_pricing[service_type]
            
            # Create order
            order_id = f"DF_{int(datetime.now().timestamp())}"
            estimated_delivery = datetime.now() + timedelta(days=self._get_delivery_days(service_type))
            
            # For now, store in memory. In production, create database record
            order_data = {
                'order_id': order_id,
                'customer_email': customer_email,
                'customer_name': customer_name,
                'service_type': service_type,
                'status': OrderStatus.PENDING,
                'amount': amount,
                'created_at': datetime.now(),
                'estimated_delivery': estimated_delivery,
                'requirements': requirements
            }
            
            # Create Stripe checkout session
            domain = os.environ.get('REPLIT_DEV_DOMAIN') if os.environ.get('REPLIT_DEPLOYMENT') != '' else os.environ.get('REPLIT_DOMAINS', 'localhost:5000').split(',')[0]
            
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': f'DreamFrame LLC - {service_type.value.replace("_", " ").title()}',
                            'description': self._get_service_description(service_type),
                        },
                        'unit_amount': amount,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'https://{domain}/payment-success?order_id={order_id}',
                cancel_url=f'https://{domain}/payment-cancelled',
                customer_email=customer_email,
                metadata={
                    'order_id': order_id,
                    'service_type': service_type.value,
                    'customer_name': customer_name
                }
            )
            
            order_data['payment_intent_id'] = session.payment_intent
            self.orders[order_id] = order_data
            
            return {
                'checkout_url': session.url,
                'order_id': order_id,
                'amount': amount / 100,  # Convert to dollars
                'estimated_delivery': estimated_delivery.strftime('%Y-%m-%d')
            }
            
        except Exception as e:
            return {'error': str(e)}
    
    def handle_payment_success(self, order_id: str) -> Dict:
        """Process successful payment and initialize AI communication"""
        if order_id not in self.orders:
            return {'error': 'Order not found'}
        
        order = self.orders[order_id]
        order['status'] = OrderStatus.PAID
        
        # Initialize AI communication thread
        ai_response = self._create_ai_thread(order)
        order['ai_thread_id'] = ai_response.get('thread_id')
        
        # Send welcome message
        welcome_message = self._generate_welcome_message(order)
        
        return {
            'success': True,
            'order': {
                'id': order['order_id'],
                'status': order['status'].value,
                'estimated_delivery': order['estimated_delivery'].strftime('%Y-%m-%d'),
                'ai_thread_id': order['ai_thread_id']
            },
            'welcome_message': welcome_message
        }
    
    def _create_ai_thread(self, order: Dict) -> Dict:
        """Create AI conversation thread for customer communication"""
        try:
            # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
            # do not change this unless explicitly requested by the user
            system_prompt = f"""You are an AI assistant for DreamFrame LLC, a veteran-owned video production company.
            
            You're managing order {order['order_id']} for {order['customer_name']}.
            Service: {order['service_type'].value.replace('_', ' ').title()}
            Estimated delivery: {order['estimated_delivery'].strftime('%Y-%m-%d')}
            
            Your role:
            1. Provide updates on production progress
            2. Collect additional requirements if needed
            3. Schedule review sessions
            4. Handle customer questions professionally
            5. Maintain the veteran-owned business values of excellence and service
            
            Customer requirements: {json.dumps(order['requirements'])}
            
            Always be professional, helpful, and maintain DreamFrame's reputation for quality."""
            
            # Create a conversation thread (simulated - in production use a proper threading system)
            thread_id = f"thread_{order['order_id']}"
            
            return {'thread_id': thread_id, 'system_prompt': system_prompt}
            
        except Exception as e:
            return {'error': str(e)}
    
    def _generate_welcome_message(self, order: Dict) -> str:
        """Generate personalized welcome message using AI"""
        try:
            prompt = f"""Create a professional welcome message for {order['customer_name']} who just ordered a {order['service_type'].value.replace('_', ' ')} from DreamFrame LLC.

            Order details:
            - Service: {order['service_type'].value.replace('_', ' ').title()}
            - Estimated delivery: {order['estimated_delivery'].strftime('%B %d, %Y')}
            - Requirements: {json.dumps(order['requirements'])}
            
            The message should:
            1. Thank them for choosing DreamFrame LLC
            2. Confirm their order and estimated delivery
            3. Outline next steps
            4. Mention our veteran-owned heritage
            5. Be warm but professional
            
            Keep it concise (2-3 paragraphs)."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=300,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "Welcome to DreamFrame LLC! Thank you for your order."
            
        except Exception as e:
            delivery_date = order.get('estimated_delivery', 'soon')
            if hasattr(delivery_date, 'strftime'):
                date_str = delivery_date.strftime('%B %d, %Y')
            else:
                date_str = 'soon'
            return f"Welcome to DreamFrame LLC! Your order {order['order_id']} has been received and we'll begin production soon. Expected delivery: {date_str}"
    
    def update_order_status(self, order_id: str, new_status: OrderStatus, update_message: Optional[str] = None) -> Dict:
        """Update order status and notify customer via AI"""
        if order_id not in self.orders:
            return {'error': 'Order not found'}
        
        order = self.orders[order_id]
        old_status = order['status']
        order['status'] = new_status
        
        # Generate AI update message
        ai_message = self._generate_status_update(order, old_status, update_message or "")
        
        return {
            'success': True,
            'order_id': order_id,
            'old_status': old_status.value,
            'new_status': new_status.value,
            'ai_message': ai_message
        }
    
    def _generate_status_update(self, order: Dict, old_status: OrderStatus, custom_message: Optional[str] = None) -> str:
        """Generate AI-powered status update message"""
        try:
            prompt = f"""Create a professional status update message for DreamFrame LLC customer {order['customer_name']}.

            Order: {order['order_id']}
            Status changed from: {old_status.value} to: {order['status'].value}
            Service: {order['service_type'].value.replace('_', ' ').title()}
            
            {f'Additional context: {custom_message}' if custom_message else ''}
            
            Create a message that:
            1. Clearly communicates the status change
            2. Provides relevant next steps
            3. Maintains professional DreamFrame tone
            4. Includes estimated timeline if relevant
            
            Keep it brief and actionable."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.7
            )
            
            return response.choices[0].message.content or f"Order {order['order_id']} status updated to {order['status'].value}"
            
        except Exception as e:
            return f"Order {order['order_id']} status updated to {order['status'].value}"
    
    def handle_customer_inquiry(self, order_id: str, customer_message: str) -> str:
        """Process customer inquiry using AI"""
        if order_id not in self.orders:
            return "I'm sorry, I couldn't find that order. Please check your order ID."
        
        order = self.orders[order_id]
        
        try:
            prompt = f"""You are responding to a customer inquiry for DreamFrame LLC.

            Customer: {order['customer_name']}
            Order: {order['order_id']}
            Service: {order['service_type'].value.replace('_', ' ').title()}
            Current Status: {order['status'].value}
            Estimated Delivery: {order['estimated_delivery'].strftime('%B %d, %Y')}
            
            Customer message: "{customer_message or 'General inquiry'}"
            
            Provide a helpful, professional response that:
            1. Addresses their specific question
            2. Provides relevant order information
            3. Offers next steps if appropriate
            4. Maintains DreamFrame's veteran-owned business values
            
            Be concise and actionable."""
            
            response = openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=250,
                temperature=0.7
            )
            
            return response.choices[0].message.content or "Thank you for your message. Our team will respond shortly."
            
        except Exception as e:
            return "Thank you for your message. Our team will respond shortly. For urgent matters, please contact support directly."
    
    def get_order_analytics(self) -> Dict:
        """Generate business analytics using AI"""
        if not self.orders:
            return {'total_orders': 0, 'total_revenue': 0, 'insights': 'No orders yet.'}
        
        total_orders = len(self.orders)
        total_revenue = sum(order['amount'] for order in self.orders.values() if order['status'] != OrderStatus.CANCELLED)
        
        # Service type distribution
        service_counts = {}
        for order in self.orders.values():
            service_counts[order['service_type'].value] = service_counts.get(order['service_type'].value, 0) + 1
        
        # Status distribution
        status_counts = {}
        for order in self.orders.values():
            status_counts[order['status'].value] = status_counts.get(order['status'].value, 0) + 1
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue / 100,  # Convert to dollars
            'service_distribution': service_counts,
            'status_distribution': status_counts,
            'average_order_value': (total_revenue / total_orders) / 100 if total_orders > 0 else 0
        }
    
    def _get_delivery_days(self, service_type: ServiceType) -> int:
        """Get estimated delivery days for service type"""
        delivery_map = {
            ServiceType.VIDEOGRAM: 3,
            ServiceType.SOCIAL_CONTENT: 5,
            ServiceType.WEDDING_HIGHLIGHT: 14,
            ServiceType.CORPORATE_VIDEO: 21,
            ServiceType.FULL_PRODUCTION: 30,
        }
        return delivery_map.get(service_type, 7)
    
    def _get_service_description(self, service_type: ServiceType) -> str:
        """Get service description for Stripe"""
        descriptions = {
            ServiceType.VIDEOGRAM: "Quick personalized video message (30-60 seconds)",
            ServiceType.SOCIAL_CONTENT: "Social media video package (3-5 videos)",
            ServiceType.WEDDING_HIGHLIGHT: "Wedding highlight reel (3-5 minutes)",
            ServiceType.CORPORATE_VIDEO: "Professional corporate video production",
            ServiceType.FULL_PRODUCTION: "Complete video production package",
        }
        return descriptions.get(service_type, "Professional video production service")

# Global instance
transaction_manager = AITransactionManager()