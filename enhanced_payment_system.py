"""
Enhanced Payment System for DreamFrame LLC
Integrates with Stripe and database models
"""
import os
import stripe
from datetime import datetime, timedelta
from models import db, Order, PricingTier, ServiceType, OrderStatus
from flask import current_app
import uuid

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class PaymentProcessor:
    def __init__(self):
        self.stripe_key = os.environ.get('STRIPE_SECRET_KEY')
        if not self.stripe_key:
            current_app.logger.warning("Stripe secret key not found")
    
    def create_checkout_session(self, service_type: ServiceType, customer_email: str, 
                              customer_name: str, requirements: dict = None):
        """Create Stripe checkout session for a service"""
        try:
            # Get pricing for service type
            pricing_tier = PricingTier.query.filter_by(
                service_type=service_type, 
                active=True
            ).first()
            
            if not pricing_tier:
                raise ValueError(f"No active pricing found for {service_type.value}")
            
            # Create order in database
            order_id = f"DF-{datetime.now().strftime('%Y%m%d')}-{str(uuid.uuid4())[:8].upper()}"
            
            order = Order()
            order.order_id = order_id
            order.customer_email = customer_email
            order.customer_name = customer_name
            order.service_type = service_type
            order.amount = pricing_tier.base_price
            order.requirements = requirements or {}
            order.estimated_delivery = datetime.utcnow() + timedelta(days=pricing_tier.delivery_days)
            
            db.session.add(order)
            db.session.flush()  # Get the ID
            
            # Create Stripe checkout session
            domain = os.environ.get('REPLIT_DEV_DOMAIN', 'localhost:5000')
            protocol = 'https' if 'replit' in domain else 'http'
            
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': pricing_tier.tier_name,
                            'description': f"Video production service - {service_type.value.replace('_', ' ').title()}",
                        },
                        'unit_amount': pricing_tier.base_price,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url=f'{protocol}://{domain}/payment/success?session_id={{CHECKOUT_SESSION_ID}}&order_id={order.id}',
                cancel_url=f'{protocol}://{domain}/payment/cancelled?order_id={order.id}',
                customer_email=customer_email,
                metadata={
                    'order_id': str(order.id),
                    'service_type': service_type.value
                }
            )
            
            # Update order with Stripe session ID
            order.stripe_session_id = checkout_session.id
            db.session.commit()
            
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'order_id': order.id,
                'session_id': checkout_session.id
            }
            
        except Exception as e:
            db.session.rollback()
            current_app.logger.error(f"Payment session creation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_payment_success(self, session_id: str, order_id: int):
        """Process successful payment"""
        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                # Update order status
                order = Order.query.get(order_id)
                if order:
                    order.status = OrderStatus.PAID
                    order.stripe_payment_intent_id = session.payment_intent
                    order.updated_at = datetime.utcnow()
                    
                    db.session.commit()
                    
                    return {
                        'success': True,
                        'order': order,
                        'message': 'Payment processed successfully'
                    }
            
            return {
                'success': False,
                'error': 'Payment not completed'
            }
            
        except Exception as e:
            current_app.logger.error(f"Payment success handling error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def cancel_order(self, order_id: int):
        """Cancel an order"""
        try:
            order = Order.query.get(order_id)
            if order:
                order.status = OrderStatus.CANCELLED
                order.updated_at = datetime.utcnow()
                db.session.commit()
                
                return {
                    'success': True,
                    'message': 'Order cancelled successfully'
                }
            
            return {
                'success': False,
                'error': 'Order not found'
            }
            
        except Exception as e:
            current_app.logger.error(f"Order cancellation error: {str(e)}")
            return {
                'success': False,
                'error': str(e)
            }

# Global instance
payment_processor = PaymentProcessor()