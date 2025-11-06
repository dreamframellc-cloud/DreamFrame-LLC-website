"""
DreamFrame Subscription Plans Configuration
Defines monthly and annual subscription tiers with Stripe integration
"""

# Subscription Plans Configuration
SUBSCRIPTION_PLANS = {
    'starter': {
        'name': 'Starter Plan',
        'monthly_price': 29,
        'annual_price': 290,  # 2 months free
        'stripe_monthly_price_id': 'price_1QWUBsD8xhexjD1TDEMO_starter_monthly',
        'stripe_annual_price_id': 'price_1QWUBsD8xhexjD1TDEMO_starter_annual',
        'features': [
            '3 VideoGrams per month',
            '1 Quick Clip per month',
            'Standard quality (1080p)',
            'Email support',
            '48-hour turnaround'
        ],
        'limits': {
            'videograms': 3,
            'quick_clips': 1,
            'family_memories': 0,
            'military_tributes': 0,
            'wedding_stories': 0,
            'corporate_productions': 0
        }
    },
    'professional': {
        'name': 'Professional Plan',
        'monthly_price': 79,
        'annual_price': 790,  # 2 months free
        'stripe_monthly_price_id': 'price_1QWUBsD8xhexjD1TDEMO_professional_monthly',
        'stripe_annual_price_id': 'price_1QWUBsD8xhexjD1TDEMO_professional_annual',
        'features': [
            '10 VideoGrams per month',
            '5 Quick Clips per month',
            '2 Family Memories per month',
            '4K quality available',
            'Priority support',
            '24-hour turnaround',
            'Custom music library access'
        ],
        'limits': {
            'videograms': 10,
            'quick_clips': 5,
            'family_memories': 2,
            'military_tributes': 1,
            'wedding_stories': 0,
            'corporate_productions': 0
        }
    },
    'enterprise': {
        'name': 'Enterprise Plan',
        'monthly_price': 199,
        'annual_price': 1990,  # 2 months free
        'stripe_monthly_price_id': 'price_1QWUBsD8xhexjD1TDEMO_enterprise_monthly',
        'stripe_annual_price_id': 'price_1QWUBsD8xhexjD1TDEMO_enterprise_annual',
        'features': [
            'Unlimited VideoGrams',
            'Unlimited Quick Clips',
            '10 Family Memories per month',
            '5 Military Tributes per month',
            '3 Wedding Stories per month',
            '2 Corporate Productions per month',
            '4K quality with VEO 3 AI',
            'Dedicated account manager',
            '12-hour turnaround',
            'Custom branding options',
            'API access',
            'White-label solutions'
        ],
        'limits': {
            'videograms': 999999,  # Unlimited
            'quick_clips': 999999,  # Unlimited
            'family_memories': 10,
            'military_tributes': 5,
            'wedding_stories': 3,
            'corporate_productions': 2
        }
    }
}

# Add-on services for all plans
ADDON_SERVICES = {
    'extra_videogram': {
        'name': 'Extra VideoGram',
        'price': 15,
        'description': 'Additional 5-second promotional video'
    },
    'extra_quick_clip': {
        'name': 'Extra Quick Clip',
        'price': 25,
        'description': 'Additional 15-second quick clip'
    },
    'extra_family_memory': {
        'name': 'Extra Family Memory',
        'price': 65,
        'description': 'Additional 30-second family memory video'
    },
    'rush_delivery': {
        'name': 'Rush Delivery',
        'price': 50,
        'description': '6-hour expedited delivery'
    },
    'custom_music': {
        'name': 'Custom Music',
        'price': 35,
        'description': 'Professional music composition'
    },
    'voiceover': {
        'name': 'Professional Voiceover',
        'price': 35,
        'description': 'Custom narration recording'
    }
}

def get_plan_by_id(plan_id):
    """Get subscription plan details by ID"""
    return SUBSCRIPTION_PLANS.get(plan_id)

def get_plan_limits(plan_id):
    """Get usage limits for a subscription plan"""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    return plan['limits'] if plan else {}

def calculate_annual_savings(plan_id):
    """Calculate savings when choosing annual over monthly"""
    plan = SUBSCRIPTION_PLANS.get(plan_id)
    if not plan:
        return 0
    
    monthly_total = plan['monthly_price'] * 12
    annual_price = plan['annual_price']
    return monthly_total - annual_price