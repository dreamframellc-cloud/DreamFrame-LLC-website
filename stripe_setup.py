#!/usr/bin/env python3
"""
Stripe Setup Script for DreamFrame LLC
Creates products and prices in Stripe for all service types
"""
import os
import stripe
from models import ServiceType

# Initialize Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_stripe_products():
    """Create Stripe products and prices for all service types"""
    
    services = {
        ServiceType.VIDEOGRAM: {
            'name': 'VideoGram - Quick Clips',
            'description': '5-second promotional videos perfect for social media',
            'price': 3500,  # $35 in cents
        },
        ServiceType.SOCIAL_CONTENT: {
            'name': 'Social Media Content',
            'description': 'Custom social media videos and content creation',
            'price': 15000,  # $150 in cents
        },
        ServiceType.WEDDING_HIGHLIGHT: {
            'name': 'Wedding Highlight Video',
            'description': 'Professional wedding highlight reel',
            'price': 50000,  # $500 in cents
        },
        ServiceType.CORPORATE_VIDEO: {
            'name': 'Corporate Video Production',
            'description': 'Professional corporate video content',
            'price': 100000,  # $1000 in cents
        },
        ServiceType.FULL_PRODUCTION: {
            'name': 'Full Video Production',
            'description': 'Complete video production service',
            'price': 200000,  # $2000 in cents
        }
    }
    
    created_products = {}
    
    for service_type, service_data in services.items():
        try:
            # Create product
            product = stripe.Product.create(
                name=service_data['name'],
                description=service_data['description'],
                metadata={
                    'service_type': service_type.value,
                    'company': 'DreamFrame LLC'
                }
            )
            
            # Create price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=service_data['price'],
                currency='usd',
                metadata={
                    'service_type': service_type.value
                }
            )
            
            created_products[service_type] = {
                'product_id': product.id,
                'price_id': price.id,
                'amount': service_data['price']
            }
            
            print(f"✓ Created {service_data['name']}")
            print(f"  Product ID: {product.id}")
            print(f"  Price ID: {price.id}")
            print(f"  Amount: ${service_data['price']/100}")
            print()
            
        except stripe.error.StripeError as e:
            print(f"✗ Error creating {service_data['name']}: {e}")
            
    return created_products

def list_existing_products():
    """List existing Stripe products"""
    try:
        products = stripe.Product.list(limit=20)
        print("Existing Stripe Products:")
        for product in products:
            prices = stripe.Price.list(product=product.id)
            print(f"- {product.name} (ID: {product.id})")
            for price in prices:
                print(f"  Price: ${price.unit_amount/100} (ID: {price.id})")
        print()
    except stripe.error.StripeError as e:
        print(f"Error listing products: {e}")

if __name__ == "__main__":
    print("DreamFrame LLC - Stripe Setup")
    print("=" * 40)
    
    # Check if Stripe key is available
    if not stripe.api_key:
        print("❌ STRIPE_SECRET_KEY not found in environment variables")
        exit(1)
    
    print("✓ Stripe API key found")
    print()
    
    # List existing products first
    list_existing_products()
    
    # Create new products
    print("Creating DreamFrame LLC products...")
    created = create_stripe_products()
    
    print(f"Successfully created {len(created)} products in Stripe!")
    print("\nNext steps:")
    print("1. Update your pricing page with the new Stripe price IDs")
    print("2. Test payment flow with Stripe test cards")
    print("3. Configure webhooks for payment confirmation")