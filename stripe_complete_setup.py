#!/usr/bin/env python3
"""
Complete Stripe Setup for DreamFrame LLC
This script sets up all Stripe products, webhooks, and configurations
"""

import os
import stripe
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StripeSetupManager:
    def __init__(self):
        """Initialize Stripe with API key"""
        self.secret_key = os.environ.get('STRIPE_SECRET_KEY', '').strip()
        if not self.secret_key:
            raise ValueError("STRIPE_SECRET_KEY not found in environment")
        
        stripe.api_key = self.secret_key
        logger.info("Stripe API initialized")
    
    def create_products_and_prices(self) -> Dict[str, Any]:
        """Create all DreamFrame LLC products and prices in Stripe"""
        
        services = {
            'videogram': {
                'name': 'VideoGram',
                'description': '5-second promotional video showcase perfect for social media',
                'price': 5000,  # $50.00 in cents
                'metadata': {'service_type': 'videogram', 'duration': '5-seconds'}
            },
            'quick_clips': {
                'name': 'Quick Clips',
                'description': 'Short social media video content with professional editing',
                'price': 7500,  # $75.00 in cents
                'metadata': {'service_type': 'quick_clips', 'duration': 'short-form'}
            },
            'family_memories': {
                'name': 'Family Memories',
                'description': 'Personal family video storytelling with emotional depth',
                'price': 20000,  # $200.00 in cents
                'metadata': {'service_type': 'family_memories', 'category': 'personal'}
            },
            'military_tributes': {
                'name': 'Military Tributes',
                'description': 'Honor military service with professional tribute videos',
                'price': 30000,  # $300.00 in cents
                'metadata': {'service_type': 'military_tributes', 'category': 'tribute'}
            },
            'wedding_stories': {
                'name': 'Wedding Stories',
                'description': 'Professional wedding video highlights and storytelling',
                'price': 50000,  # $500.00 in cents
                'metadata': {'service_type': 'wedding_stories', 'category': 'wedding'}
            },
            'corporate_productions': {
                'name': 'Corporate Productions',
                'description': 'Full-scale commercial video production and marketing content',
                'price': 100000,  # $1000.00 in cents
                'metadata': {'service_type': 'corporate_productions', 'category': 'commercial'}
            }
        }
        
        created_products = {}
        
        for service_key, service_data in services.items():
            try:
                # Create product
                product = stripe.Product.create(
                    name=service_data['name'],
                    description=service_data['description'],
                    metadata=service_data['metadata']
                )
                
                # Create price for the product
                price = stripe.Price.create(
                    unit_amount=service_data['price'],
                    currency='usd',
                    product=product.id,
                    metadata=service_data['metadata']
                )
                
                created_products[service_key] = {
                    'product_id': product.id,
                    'price_id': price.id,
                    'amount': service_data['price']
                }
                
                logger.info(f"✓ Created {service_data['name']} - Product: {product.id}, Price: {price.id}")
                
            except stripe.error.StripeError as e:
                logger.error(f"✗ Error creating {service_data['name']}: {e}")
        
        return created_products
    
    def setup_webhook(self) -> str:
        """Set up webhook endpoint for payment confirmations"""
        
        # Get domain for webhook URL
        domain = os.environ.get('REPLIT_DEV_DOMAIN')
        if not domain:
            domains = os.environ.get('REPLIT_DOMAINS', '').split(',')
            domain = domains[0] if domains else 'your-app.replit.app'
        
        webhook_url = f"https://{domain}/stripe-webhook"
        
        try:
            webhook = stripe.WebhookEndpoint.create(
                url=webhook_url,
                enabled_events=[
                    'checkout.session.completed',
                    'payment_intent.succeeded',
                    'payment_intent.payment_failed',
                    'customer.created',
                    'invoice.payment_succeeded'
                ],
                description='DreamFrame LLC Payment Webhook'
            )
            
            logger.info(f"✓ Webhook created: {webhook_url}")
            logger.info(f"Webhook ID: {webhook.id}")
            logger.info(f"⚠️  Save webhook secret: {webhook.secret}")
            
            return webhook.secret
            
        except stripe.error.StripeError as e:
            logger.error(f"✗ Error creating webhook: {e}")
            return ""
    
    def test_payment_flow(self) -> bool:
        """Test payment session creation"""
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'DreamFrame Test Payment',
                            'description': 'Test payment session for VideoGram service',
                        },
                        'unit_amount': 5000,
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://your-domain.replit.app/payment-success',
                cancel_url='https://your-domain.replit.app/payment-cancelled',
                metadata={'test': 'true', 'service_type': 'videogram'}
            )
            
            logger.info(f"✓ Test payment session created: {session.id}")
            return True
            
        except stripe.error.StripeError as e:
            logger.error(f"✗ Payment test failed: {e}")
            return False
    
    def generate_config_file(self, products: Dict[str, Any], webhook_secret: str):
        """Generate configuration file with Stripe IDs"""
        config = {
            'stripe_products': products,
            'webhook_secret': webhook_secret,
            'setup_complete': True
        }
        
        config_content = f"""# DreamFrame LLC - Stripe Configuration
# Generated automatically - do not edit manually

STRIPE_PRODUCTS = {products}

STRIPE_WEBHOOK_SECRET = "{webhook_secret}"

# Service pricing for display (in dollars)
SERVICE_PRICING = {{
"""
        
        for service_key, service_data in products.items():
            price_dollars = service_data['amount'] / 100
            config_content += f"    '{service_key}': {price_dollars},\n"
        
        config_content += "}\n"
        
        with open('stripe_config.py', 'w') as f:
            f.write(config_content)
        
        logger.info("✓ Configuration file generated: stripe_config.py")

def main():
    """Run complete Stripe setup"""
    logger.info("DreamFrame LLC - Complete Stripe Setup")
    logger.info("=" * 50)
    
    try:
        setup_manager = StripeSetupManager()
        
        # Create products and prices
        logger.info("Creating Stripe products and prices...")
        products = setup_manager.create_products_and_prices()
        
        if products:
            logger.info(f"✓ Successfully created {len(products)} products")
            
            # Setup webhook
            logger.info("\nSetting up webhook...")
            webhook_secret = setup_manager.setup_webhook()
            
            # Test payment flow
            logger.info("\nTesting payment flow...")
            payment_test = setup_manager.test_payment_flow()
            
            # Generate config file
            logger.info("\nGenerating configuration...")
            setup_manager.generate_config_file(products, webhook_secret)
            
            # Summary
            logger.info("\n" + "=" * 50)
            logger.info("✅ Stripe setup completed successfully!")
            logger.info("\nSetup Summary:")
            logger.info(f"- Products created: {len(products)}")
            logger.info(f"- Webhook configured: {'Yes' if webhook_secret else 'No'}")
            logger.info(f"- Payment test: {'Passed' if payment_test else 'Failed'}")
            
            logger.info("\nNext steps:")
            logger.info("1. Update your frontend with the publishable key")
            logger.info("2. Test payments with Stripe test cards")
            logger.info("3. Configure webhook secret in environment variables")
            logger.info("4. Switch to live keys when ready for production")
            
        else:
            logger.error("❌ No products were created successfully")
            
    except Exception as e:
        logger.error(f"❌ Setup failed: {e}")
        raise

if __name__ == "__main__":
    main()