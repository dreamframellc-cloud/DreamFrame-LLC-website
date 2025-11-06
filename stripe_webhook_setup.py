#!/usr/bin/env python3
"""
Stripe Webhook Setup for DreamFrame LLC
Creates webhook endpoint for payment confirmations
"""
import os
import stripe

stripe.api_key = os.environ.get('STRIPE_SECRET_KEY')

def create_webhook_endpoint():
    """Create webhook endpoint for payment events"""
    
    # Get the current domain
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
            ],
            description='DreamFrame LLC Payment Webhook'
        )
        
        print(f"✓ Webhook created successfully!")
        print(f"Webhook ID: {webhook.id}")
        print(f"Webhook URL: {webhook_url}")
        print(f"Secret: {webhook.secret}")
        print()
        print("⚠️  IMPORTANT: Save the webhook secret as STRIPE_WEBHOOK_SECRET environment variable")
        
        return webhook
        
    except stripe.error.StripeError as e:
        print(f"Error creating webhook: {e}")
        return None

def list_webhooks():
    """List existing webhooks"""
    try:
        webhooks = stripe.WebhookEndpoint.list()
        print("Existing Webhooks:")
        for webhook in webhooks:
            print(f"- {webhook.url} (ID: {webhook.id})")
            print(f"  Events: {', '.join(webhook.enabled_events)}")
        print()
    except stripe.error.StripeError as e:
        print(f"Error listing webhooks: {e}")

if __name__ == "__main__":
    print("DreamFrame LLC - Stripe Webhook Setup")
    print("=" * 40)
    
    if not stripe.api_key:
        print("❌ STRIPE_SECRET_KEY not found")
        exit(1)
    
    print("✓ Stripe API key found")
    print()
    
    list_webhooks()
    create_webhook_endpoint()