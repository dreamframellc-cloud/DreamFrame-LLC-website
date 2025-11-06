"""
Setup Stripe Products and Prices for DreamFrame Subscription Plans
Run this script to create the necessary Stripe products and pricing
"""

import os
import stripe
from subscription_plans import SUBSCRIPTION_PLANS

# Configure Stripe
stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_stripe_products_and_prices():
    """Create Stripe products and prices for all subscription plans"""
    
    if not stripe.api_key:
        print("Error: STRIPE_SECRET_KEY environment variable not set")
        return
    
    print("Setting up Stripe products and prices for DreamFrame...")
    
    for plan_id, plan_data in SUBSCRIPTION_PLANS.items():
        try:
            # Create product
            product = stripe.Product.create(
                name=plan_data['name'],
                description=f"DreamFrame {plan_data['name']} - Professional video creation subscription",
                metadata={
                    'plan_id': plan_id,
                    'features': ', '.join(plan_data['features'][:3])  # First 3 features
                }
            )
            
            print(f"Created product: {product.id} - {plan_data['name']}")
            
            # Create monthly price
            monthly_price = stripe.Price.create(
                product=product.id,
                unit_amount=plan_data['monthly_price'] * 100,  # Convert to cents
                currency='usd',
                recurring={'interval': 'month'},
                lookup_key=f"{plan_id}_monthly",
                metadata={
                    'plan_id': plan_id,
                    'billing_cycle': 'monthly'
                }
            )
            
            print(f"Created monthly price: {monthly_price.id} - ${plan_data['monthly_price']}/month")
            
            # Create annual price
            annual_price = stripe.Price.create(
                product=product.id,
                unit_amount=plan_data['annual_price'] * 100,  # Convert to cents
                currency='usd',
                recurring={'interval': 'year'},
                lookup_key=f"{plan_id}_annual",
                metadata={
                    'plan_id': plan_id,
                    'billing_cycle': 'annual'
                }
            )
            
            print(f"Created annual price: {annual_price.id} - ${plan_data['annual_price']}/year")
            
            # Update subscription_plans.py with actual price IDs
            print(f"Update {plan_id} in subscription_plans.py:")
            print(f"  'stripe_monthly_price_id': '{monthly_price.id}',")
            print(f"  'stripe_annual_price_id': '{annual_price.id}',")
            print()
            
        except Exception as e:
            print(f"Error creating {plan_id}: {e}")
            continue
    
    print("Stripe setup complete!")
    print("\nNext steps:")
    print("1. Update subscription_plans.py with the actual Stripe price IDs shown above")
    print("2. Test the subscription flow on your website")
    print("3. Set up webhook endpoints for subscription events")

if __name__ == "__main__":
    create_stripe_products_and_prices()