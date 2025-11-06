#!/usr/bin/env python3
"""
Test Stripe integration for DreamFrame LLC
"""
import os
import stripe
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_stripe_keys():
    """Test Stripe API keys and connection"""
    # Get keys from environment
    secret_key = (os.environ.get('STRIPE_SK_LIVE', '') or 
                 os.environ.get('STRIPE_SECRET_KEY_LIVE', '') or 
                 os.environ.get('STRIPE_SECRET_KEY', '')).strip()
    # Try the new key first, fallback to old one
    publishable_key = (os.environ.get('STRIPE_PK_LIVE', '') or 
                      os.environ.get('STRIPE_PUBLISHABLE_KEY', '')).strip()
    
    logger.info("Testing Stripe configuration...")
    logger.info(f"Secret key format: {secret_key[:12]}...{secret_key[-4:] if len(secret_key) > 16 else 'invalid'}")
    logger.info(f"Publishable key format: {publishable_key[:12]}...{publishable_key[-4:] if len(publishable_key) > 16 else 'invalid'}")
    
    if not secret_key:
        logger.error("❌ STRIPE_SECRET_KEY not found")
        return False
    
    if not publishable_key:
        logger.error("❌ STRIPE_PUBLISHABLE_KEY not found")
        return False
    
    # Validate key formats
    if not secret_key.startswith(('sk_test_', 'sk_live_')):
        logger.error("❌ Secret key has invalid format")
        return False
    
    if not publishable_key.startswith(('pk_test_', 'pk_live_')):
        logger.error("❌ Publishable key has invalid format")
        return False
    
    # Test Stripe connection
    stripe.api_key = secret_key
    
    try:
        # Test with a simple API call
        products = stripe.Product.list(limit=1)
        logger.info("✅ Stripe connection successful")
        logger.info(f"Found {len(products.data)} existing products")
        return True
        
    except stripe.error.AuthenticationError as e:
        logger.error(f"❌ Authentication failed: {e}")
        return False
    except stripe.error.StripeError as e:
        logger.error(f"❌ Stripe error: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ Unexpected error: {e}")
        return False

def create_test_payment_session():
    """Create a test payment session"""
    try:
        # Create a test checkout session
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': 'DreamFrame Test - VideoGram',
                        'description': 'Test payment for VideoGram service',
                    },
                    'unit_amount': 5000,  # $50 in cents
                },
                'quantity': 1,
            }],
            mode='payment',
            success_url='http://localhost:5000/payment-success',
            cancel_url='http://localhost:5000/payment-cancelled',
        )
        
        logger.info("✅ Test payment session created successfully")
        logger.info(f"Session ID: {session.id}")
        logger.info(f"Payment URL: {session.url}")
        return session
        
    except stripe.error.StripeError as e:
        logger.error(f"❌ Failed to create payment session: {e}")
        return None

if __name__ == "__main__":
    logger.info("DreamFrame LLC - Stripe Integration Test")
    logger.info("=" * 50)
    
    # Test keys and connection
    if test_stripe_keys():
        logger.info("\n" + "=" * 50)
        logger.info("Testing payment session creation...")
        create_test_payment_session()
        
        logger.info("\n" + "=" * 50)
        logger.info("✅ Stripe setup test completed successfully!")
        logger.info("Your Stripe integration is ready for payments.")
    else:
        logger.error("\n❌ Stripe setup test failed!")
        logger.error("Please check your API keys and try again.")