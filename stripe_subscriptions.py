"""
Stripe Subscription Management for DreamFrame
Handles subscription creation, management, and billing
"""

import os
import stripe
import logging
from datetime import datetime, timedelta
from subscription_plans import SUBSCRIPTION_PLANS, get_plan_by_id
from models import db, CustomerProject

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

class SubscriptionManager:
    """Manages Stripe subscriptions for DreamFrame customers"""
    
    def __init__(self):
        self.domain = self._get_domain()
    
    def _get_domain(self):
        """Get the current domain for redirect URLs"""
        if os.environ.get('REPLIT_DEPLOYMENT'):
            return os.environ.get('REPLIT_DEV_DOMAIN')
        else:
            domains = os.environ.get('REPLIT_DOMAINS', 'localhost:5000')
            return domains.split(',')[0]
    
    def create_subscription_checkout(self, plan_id, billing_cycle='monthly', customer_email=None):
        """
        Create Stripe checkout session for subscription
        
        Args:
            plan_id: ID of the subscription plan (starter, professional, enterprise)
            billing_cycle: 'monthly' or 'annual'
            customer_email: Optional customer email for pre-filling
        
        Returns:
            Checkout session object with URL for redirect
        """
        try:
            plan = get_plan_by_id(plan_id)
            if not plan:
                raise ValueError(f"Invalid plan ID: {plan_id}")
            
            # Get the appropriate price ID
            if billing_cycle == 'annual':
                price_id = plan['stripe_annual_price_id']
                price = plan['annual_price']
            else:
                price_id = plan['stripe_monthly_price_id']
                price = plan['monthly_price']
            
            # Create checkout session
            session_params = {
                'payment_method_types': ['card'],
                'line_items': [{
                    'price': price_id,
                    'quantity': 1,
                }],
                'mode': 'subscription',
                'success_url': f'https://{self.domain}/subscription/success?session_id={{CHECKOUT_SESSION_ID}}',
                'cancel_url': f'https://{self.domain}/subscription/cancelled',
                'automatic_tax': {'enabled': True},
                'billing_address_collection': 'required',
                'metadata': {
                    'plan_id': plan_id,
                    'billing_cycle': billing_cycle,
                    'plan_name': plan['name']
                }
            }
            
            # Add customer email if provided
            if customer_email:
                session_params['customer_email'] = customer_email
            
            checkout_session = stripe.checkout.Session.create(**session_params)
            
            logging.info(f"Created subscription checkout for {plan['name']} ({billing_cycle}): {checkout_session.id}")
            
            return {
                'success': True,
                'checkout_url': checkout_session.url,
                'session_id': checkout_session.id,
                'plan': plan['name'],
                'price': price,
                'billing_cycle': billing_cycle
            }
            
        except Exception as e:
            logging.error(f"Subscription checkout error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def verify_subscription_payment(self, session_id):
        """
        Verify successful subscription payment and retrieve customer info
        
        Args:
            session_id: Stripe checkout session ID
        
        Returns:
            Dictionary with subscription details and customer info
        """
        try:
            # Retrieve the checkout session
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status != 'paid':
                return {
                    'success': False,
                    'error': 'Payment not completed'
                }
            
            # Get subscription details
            subscription = stripe.Subscription.retrieve(session.subscription)
            customer = stripe.Customer.retrieve(session.customer)
            
            plan_id = session.metadata.get('plan_id')
            plan = get_plan_by_id(plan_id)
            
            return {
                'success': True,
                'subscription_id': subscription.id,
                'customer_id': customer.id,
                'customer_email': customer.email,
                'plan_id': plan_id,
                'plan_name': plan['name'] if plan else 'Unknown',
                'status': subscription.status,
                'current_period_start': datetime.fromtimestamp(subscription.current_period_start),
                'current_period_end': datetime.fromtimestamp(subscription.current_period_end),
                'billing_cycle': session.metadata.get('billing_cycle', 'monthly')
            }
            
        except Exception as e:
            logging.error(f"Subscription verification error: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_customer_usage(self, customer_email, current_period_start):
        """
        Get customer's usage for current billing period
        
        Args:
            customer_email: Customer's email address
            current_period_start: Start of current billing period
        
        Returns:
            Dictionary with usage counts by service type
        """
        try:
            # Query projects created in current billing period
            projects = CustomerProject.query.filter(
                CustomerProject.customer_email == customer_email,
                CustomerProject.created_at >= current_period_start,
                CustomerProject.status == 'COMPLETED'
            ).all()
            
            usage = {
                'videograms': 0,
                'quick_clips': 0,
                'family_memories': 0,
                'military_tributes': 0,
                'wedding_stories': 0,
                'corporate_productions': 0
            }
            
            # Count projects by type
            for project in projects:
                project_type = project.project_type.lower()
                if project_type == 'videogram':
                    usage['videograms'] += 1
                elif project_type == 'quick_clip':
                    usage['quick_clips'] += 1
                elif project_type == 'family_memory':
                    usage['family_memories'] += 1
                elif project_type == 'military_tribute':
                    usage['military_tributes'] += 1
                elif project_type == 'wedding_story':
                    usage['wedding_stories'] += 1
                elif project_type == 'corporate_production':
                    usage['corporate_productions'] += 1
            
            return usage
            
        except Exception as e:
            logging.error(f"Usage tracking error: {e}")
            return {}
    
    def check_usage_limits(self, customer_email, plan_id, service_type):
        """
        Check if customer can create a new project based on their plan limits
        
        Args:
            customer_email: Customer's email address
            plan_id: Customer's subscription plan ID
            service_type: Type of service being requested
        
        Returns:
            Boolean indicating if request is within limits
        """
        try:
            plan = get_plan_by_id(plan_id)
            if not plan:
                return False
            
            # Get current period usage (simplified - in production would get from subscription)
            current_period_start = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            usage = self.get_customer_usage(customer_email, current_period_start)
            
            # Check limits
            limits = plan['limits']
            service_key = service_type.lower().replace(' ', '_')
            
            if service_key in limits and service_key in usage:
                return usage[service_key] < limits[service_key]
            
            return False
            
        except Exception as e:
            logging.error(f"Limit checking error: {e}")
            return False
    
    def cancel_subscription(self, subscription_id):
        """
        Cancel a subscription at the end of the current billing period
        
        Args:
            subscription_id: Stripe subscription ID
        
        Returns:
            Dictionary with cancellation status
        """
        try:
            subscription = stripe.Subscription.modify(
                subscription_id,
                cancel_at_period_end=True
            )
            
            return {
                'success': True,
                'message': 'Subscription will cancel at the end of the current billing period',
                'cancels_at': datetime.fromtimestamp(subscription.current_period_end)
            }
            
        except Exception as e:
            logging.error(f"Subscription cancellation error: {e}")
            return {
                'success': False,
                'error': str(e)
            }

# Global subscription manager instance
subscription_manager = SubscriptionManager()