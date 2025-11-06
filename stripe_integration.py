import os
import stripe
from flask import url_for
import logging
import time
import uuid

# Configure Stripe function to be called from Flask app
def configure_stripe():
    """Initialize Stripe with proper API key from environment"""
    # Use STRIPE_LIVE_SECRET_KEY which contains the actual secret key
    stripe_key = os.environ.get('STRIPE_LIVE_SECRET_KEY', '').strip()
    
    if stripe_key and stripe_key.startswith('sk_live_'):
        stripe.api_key = stripe_key
        logging.info("🟢 STRIPE LIVE MODE ACTIVE - Real payments enabled")
        logging.info(f"🔑 Using live secret key: {stripe_key[:15]}... (length: {len(stripe_key)})")
        return True
    else:
        logging.error(f"🔴 STRIPE SECRET KEY INVALID - Got: {stripe_key[:15] if stripe_key else 'None'}... (length: {len(stripe_key) if stripe_key else 0})")
        return False

# Initialize Stripe configuration
_stripe_configured = configure_stripe()

# Get domain for success/cancel URLs
def get_domain():
    """Get the current domain for Stripe redirects"""
    if os.environ.get('REPLIT_DEPLOYMENT'):
        return f"https://{os.environ.get('REPLIT_DEV_DOMAIN')}"
    else:
        domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
        return f"https://{domains[0]}" if domains and domains[0] else "http://localhost:5000"

def is_stripe_configured():
    """Check if Stripe is properly configured and accessible"""
    return _stripe_configured and hasattr(stripe, 'api_key') and stripe.api_key is not None

def test_stripe_connection():
    """Test Stripe API connection"""
    if not is_stripe_configured():
        return False, "Stripe not configured"
    
    try:
        # Test with a simple API call
        stripe.Account.retrieve()
        return True, "Stripe connection successful"
    except stripe.error.AuthenticationError:
        return False, "Invalid Stripe API key"
    except Exception as e:
        return False, f"Stripe connection error: {str(e)}"

class StripePaymentHandler:
    """Handle Stripe payment processing for DreamFrame LLC services"""
    
    # Service pricing in cents (Stripe uses cents)
    SERVICE_PRICES = {
        'videogram': {
            'name': 'VideoGram',
            'price': 5000,  # $50.00
            'description': '5-second promotional video showcase'
        },
        'quick_clips': {
            'name': 'Quick Clips',
            'price': 7500,  # $75.00
            'description': 'Short social media video content'
        },
        'family_memories': {
            'name': 'Family Memories',
            'price': 20000,  # $200.00
            'description': 'Personal family video storytelling'
        },
        'military_tributes': {
            'name': 'Military Tributes',
            'price': 30000,  # $300.00
            'description': 'Honor military service with tribute videos'
        },
        'wedding_stories': {
            'name': 'Wedding Stories',
            'price': 50000,  # $500.00
            'description': 'Professional wedding video highlights'
        },
        'corporate_productions': {
            'name': 'Corporate Productions',
            'price': 100000,  # $1000.00
            'description': 'Full-scale commercial video production'
        },
        'project_deposit': {
            'name': 'Project Deposit',
            'price': 10000,  # $100.00
            'description': 'Video Production Project Deposit - Reserve your spot in our production queue'
        },
        'consultation_deposit': {
            'name': 'Consultation Deposit',
            'price': 5000,  # $50.00
            'description': 'Video Consultation Deposit - Applied to your final project cost'
        }
    }
    
    @staticmethod
    def create_checkout_session(service_type, customer_email=None, customer_name=None, quantity=1, custom_amount=None, custom_description=None):
        """Create a Stripe checkout session for a service"""
        # Ensure Stripe is configured with live secret key
        stripe_key = os.environ.get('STRIPE_LIVE_SECRET_KEY', '').strip()
        if stripe_key and stripe_key.startswith('sk_live_'):
            stripe.api_key = stripe_key
            logging.info("🟢 CHECKOUT SESSION - LIVE MODE ENFORCED")
            logging.info(f"🔑 Session using live secret key: {stripe_key[:15]}... (length: {len(stripe_key)})")
        else:
            logging.error(f"🔴 CHECKOUT SESSION - SECRET KEY FAILED: {stripe_key[:15] if stripe_key else 'None'}...")
            return {"error": "Payment system not configured. Please contact support."}
        
        # First check if Stripe is properly configured
        if not is_stripe_configured():
            logging.error("🔴 STRIPE NOT CONFIGURED - Cannot create checkout session")
            return {"error": "Payment system not configured. Please contact support."}
        
        try:
            # Handle custom deposit amounts from form data
            if custom_amount and custom_description:
                service = {
                    'name': service_type.replace('_', ' ').title(),
                    'price': int(custom_amount),  # Amount already in cents
                    'description': custom_description
                }
            elif service_type not in StripePaymentHandler.SERVICE_PRICES:
                return {"error": "Invalid service type"}
            else:
                service = StripePaymentHandler.SERVICE_PRICES[service_type]
            
            domain = get_domain()
            
            # Cache-busting parameters to force fresh sessions
            timestamp = int(time.time())
            unique_id = str(uuid.uuid4())
            
            # Create line items
            line_items = [{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': service['name'],
                        'description': service['description'],
                    },
                    'unit_amount': service['price'],
                },
                'quantity': quantity,
            }]
            
            # Session configuration - minimal fields for digital services with cache-busting
            session_config = {
                'payment_method_types': ['card'],
                'line_items': line_items,
                'mode': 'payment',
                'success_url': f"{domain}/payment-success?session_id={{CHECKOUT_SESSION_ID}}&service={service_type}&t={timestamp}",
                'cancel_url': f"{domain}/payment-cancelled?service={service_type}&t={timestamp}",
                'automatic_tax': {'enabled': False},
                'allow_promotion_codes': True,
                'shipping_address_collection': {'allowed_countries': []},  # Disable shipping completely
                'billing_address_collection': 'required',  # Keep billing for payment verification
                'phone_number_collection': {'enabled': False},  # Explicitly disable phone
                'client_reference_id': unique_id,  # Uniqueness guards against reuse
                'metadata': {
                    'service_type': service_type,
                    'company': 'DreamFrame LLC',
                    'timestamp': str(timestamp),
                    'unique_id': unique_id
                }
            }
            
            # Add customer info if provided
            if customer_email:
                session_config['customer_email'] = customer_email
            
            # Create the session
            session = stripe.checkout.Session.create(**session_config)
            
            # Add cache-busting query parameter to Stripe's URL (harmless, busts caches/proxies)
            checkout_url = session.url + f"?v={timestamp}"
            
            logging.info(f"Stripe session created: {session.id} for service: {service_type} with cache-busting timestamp: {timestamp}")
            
            return {
                'session_id': session.id,
                'checkout_url': checkout_url,
                'service': service['name'],
                'amount': service['price'] / 100  # Convert back to dollars for display
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Stripe error: {str(e)}")
            return {"error": f"Payment system error: {str(e)}"}
        except Exception as e:
            logging.error(f"Checkout session error: {str(e)}")
            return {"error": "Failed to create payment session"}
    
    @staticmethod
    def verify_payment(session_id):
        """Verify a completed payment session"""
        try:
            session = stripe.checkout.Session.retrieve(session_id)
            
            if session.payment_status == 'paid':
                return {
                    'success': True,
                    'customer_email': session.customer_details.email if session.customer_details else None,
                    'customer_name': session.customer_details.name if session.customer_details else None,
                    'amount_paid': session.amount_total / 100,  # Convert to dollars
                    'service_type': session.metadata.get('service_type'),
                    'payment_intent': session.payment_intent
                }
            else:
                return {'success': False, 'status': session.payment_status}
                
        except stripe.error.StripeError as e:
            logging.error(f"Payment verification error: {str(e)}")
            return {"error": f"Payment verification failed: {str(e)}"}
    
    @staticmethod
    def create_payment_link(service_type, return_url=None):
        """Create a Stripe payment link for a service"""
        try:
            if service_type not in StripePaymentHandler.SERVICE_PRICES:
                return {"error": "Invalid service type"}
            
            service = StripePaymentHandler.SERVICE_PRICES[service_type]
            
            # Create a price object
            price = stripe.Price.create(
                unit_amount=service['price'],
                currency='usd',
                product_data={
                    'name': service['name'],
                    'description': service['description'],
                },
            )
            
            # Create payment link
            payment_link = stripe.PaymentLink.create(
                line_items=[{
                    'price': price.id,
                    'quantity': 1,
                }],
                after_completion={
                    'type': 'redirect',
                    'redirect': {
                        'url': return_url or f"{get_domain()}/payment-success"
                    }
                }
            )
            
            return {
                'payment_link_url': payment_link.url,
                'service': service['name'],
                'amount': service['price'] / 100
            }
            
        except stripe.error.StripeError as e:
            logging.error(f"Payment link error: {str(e)}")
            return {"error": f"Failed to create payment link: {str(e)}"}

def get_service_pricing():
    """Get all service pricing for display"""
    pricing = {}
    for key, service in StripePaymentHandler.SERVICE_PRICES.items():
        pricing[key] = {
            'name': service['name'],
            'price': service['price'] / 100,  # Convert to dollars
            'description': service['description']
        }
    return pricing