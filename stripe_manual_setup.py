#!/usr/bin/env python3
"""
Manual Stripe Setup Instructions for DreamFrame LLC
Since there's an issue with the API key, this provides manual setup steps
"""

def generate_manual_setup_guide():
    """Generate comprehensive manual setup guide"""
    
    setup_guide = """
# DreamFrame LLC - Manual Stripe Setup Guide

## Issue Detected
Your Stripe secret key appears to be corrupted or incorrectly formatted in the environment.
The key should be exactly as provided by Stripe without any modifications.

## Step 1: Verify Your Stripe Keys
1. Go to https://dashboard.stripe.com
2. Navigate to Developers → API keys
3. Copy your keys EXACTLY as shown:
   - Secret key: starts with `sk_test_` or `sk_live_`
   - Publishable key: starts with `pk_test_` or `pk_live_`

## Step 2: Update Environment Variables
In your Replit Secrets, make sure:
- STRIPE_SECRET_KEY = your complete secret key (no extra characters)
- STRIPE_PUBLISHABLE_KEY = your complete publishable key (no extra characters)

## Step 3: Manual Product Creation
Once your keys are working, create these products in your Stripe Dashboard:

### VideoGram Service
- Name: VideoGram
- Description: 5-second promotional video showcase
- Price: $50.00 USD

### Quick Clips Service  
- Name: Quick Clips
- Description: Short social media video content
- Price: $75.00 USD

### Family Memories Service
- Name: Family Memories
- Description: Personal family video storytelling
- Price: $200.00 USD

### Military Tributes Service
- Name: Military Tributes
- Description: Honor military service with tribute videos
- Price: $300.00 USD

### Wedding Stories Service
- Name: Wedding Stories
- Description: Professional wedding video highlights
- Price: $500.00 USD

### Corporate Productions Service
- Name: Corporate Productions
- Description: Full-scale commercial video production
- Price: $1000.00 USD

## Step 4: Configure Webhooks
1. Go to Developers → Webhooks in your Stripe Dashboard
2. Add endpoint: https://your-replit-url.replit.app/stripe-webhook
3. Select events:
   - checkout.session.completed
   - payment_intent.succeeded
   - payment_intent.payment_failed
4. Save the webhook secret for later use

## Step 5: Test Your Setup
After fixing the API keys, run:
```bash
python stripe_test.py
```

This should show all green checkmarks if everything is configured correctly.

## Current Integration Status
✅ Payment pages created and configured
✅ Stripe integration code implemented
✅ Webhook handling ready
❌ API keys need to be fixed
❌ Products need to be created in Stripe Dashboard

## Next Steps
1. Fix the API key formatting issue
2. Create products manually in Stripe Dashboard
3. Test payment flow
4. Deploy and verify webhook functionality
"""
    
    print(setup_guide)
    
    # Also save to file
    with open('STRIPE_MANUAL_SETUP.md', 'w') as f:
        f.write(setup_guide)
    
    print("\n" + "="*50)
    print("✅ Manual setup guide created: STRIPE_MANUAL_SETUP.md")
    print("Follow the steps above to complete your Stripe setup.")

if __name__ == "__main__":
    generate_manual_setup_guide()