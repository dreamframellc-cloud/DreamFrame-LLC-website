// DreamFrame LLC - Stripe Frontend Configuration
// This file configures Stripe payments on the frontend

class DreamFrameStripeHandler {
    constructor() {
        // Initialize Stripe with publishable key
        // Note: The publishable key will be loaded from environment
        this.stripe = null;
        this.elements = null;
        this.card = null;
        
        this.initializeStripe();
    }
    
    async initializeStripe() {
        try {
            // Get publishable key from backend
            const response = await fetch('/stripe-config');
            const config = await response.json();
            
            if (config.publishable_key) {
                this.stripe = Stripe(config.publishable_key);
                this.setupElements();
                console.log('✅ Stripe initialized successfully');
            } else {
                throw new Error('Publishable key not found');
            }
        } catch (error) {
            console.error('❌ Stripe initialization failed:', error);
            this.showError('Payment system temporarily unavailable');
        }
    }
    
    setupElements() {
        // Create Stripe Elements
        this.elements = this.stripe.elements();
        
        // Create card element with custom styling
        this.card = this.elements.create('card', {
            style: {
                base: {
                    fontSize: '16px',
                    color: '#ffffff',
                    backgroundColor: 'rgba(255, 255, 255, 0.1)',
                    '::placeholder': {
                        color: 'rgba(255, 255, 255, 0.7)',
                    },
                },
                invalid: {
                    color: '#fa755a',
                    iconColor: '#fa755a'
                }
            }
        });
        
        // Mount card element
        const cardElement = document.getElementById('card-element');
        if (cardElement) {
            this.card.mount('#card-element');
            this.setupCardEvents();
        }
    }
    
    setupCardEvents() {
        this.card.on('change', (event) => {
            const displayError = document.getElementById('card-errors');
            if (event.error) {
                displayError.textContent = event.error.message;
                displayError.style.display = 'block';
            } else {
                displayError.textContent = '';
                displayError.style.display = 'none';
            }
        });
    }
    
    async createPaymentSession(serviceType, customerData) {
        try {
            const response = await fetch('/create-payment-session', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    service_type: serviceType,
                    customer_email: customerData.email,
                    customer_name: customerData.name,
                    requirements: customerData.requirements || {}
                })
            });
            
            const session = await response.json();
            
            if (session.error) {
                throw new Error(session.error);
            }
            
            // Redirect to Stripe Checkout
            const result = await this.stripe.redirectToCheckout({
                sessionId: session.session_id
            });
            
            if (result.error) {
                this.showError(result.error.message);
            }
            
        } catch (error) {
            console.error('Payment session creation failed:', error);
            this.showError('Failed to create payment session');
        }
    }
    
    showError(message) {
        const errorElement = document.getElementById('payment-errors') || 
                           document.getElementById('card-errors');
        
        if (errorElement) {
            errorElement.textContent = message;
            errorElement.style.display = 'block';
            errorElement.style.color = '#fa755a';
            errorElement.style.marginTop = '10px';
        } else {
            alert(message);
        }
    }
    
    // Service-specific payment methods
    async payForVideoGram(customerData) {
        return this.createPaymentSession('videogram', customerData);
    }
    
    async payForQuickClips(customerData) {
        return this.createPaymentSession('quick_clips', customerData);
    }
    
    async payForFamilyMemories(customerData) {
        return this.createPaymentSession('family_memories', customerData);
    }
    
    async payForMilitaryTributes(customerData) {
        return this.createPaymentSession('military_tributes', customerData);
    }
    
    async payForWeddingStories(customerData) {
        return this.createPaymentSession('wedding_stories', customerData);
    }
    
    async payForCorporateProductions(customerData) {
        return this.createPaymentSession('corporate_productions', customerData);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    window.dreamFrameStripe = new DreamFrameStripeHandler();
});

// Export for use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DreamFrameStripeHandler;
}