"""
Subscription Routes for DreamFrame LLC
Handles subscription management, checkout, and billing
"""

from flask import Blueprint, render_template, request, jsonify, redirect, url_for, session
import logging
from stripe_subscriptions import subscription_manager
from subscription_plans import SUBSCRIPTION_PLANS, ADDON_SERVICES

subscription_bp = Blueprint('subscription', __name__, url_prefix='/subscription')

@subscription_bp.route('/plans')
def subscription_plans():
    """Display subscription pricing plans"""
    return render_template('subscription_pricing.html', 
                         plans=SUBSCRIPTION_PLANS, 
                         addons=ADDON_SERVICES)

@subscription_bp.route('/create-checkout', methods=['POST'])
def create_checkout():
    """Create Stripe checkout session for subscription"""
    try:
        data = request.get_json()
        plan_id = data.get('plan_id')
        billing_cycle = data.get('billing_cycle', 'monthly')
        customer_email = data.get('customer_email')
        
        if not plan_id:
            return jsonify({'success': False, 'error': 'Plan ID required'}), 400
        
        # Create subscription checkout
        result = subscription_manager.create_subscription_checkout(
            plan_id=plan_id,
            billing_cycle=billing_cycle,
            customer_email=customer_email
        )
        
        if result['success']:
            # Store checkout info in session
            session['checkout_session_id'] = result['session_id']
            session['plan_id'] = plan_id
            session['billing_cycle'] = billing_cycle
            
            logging.info(f"Created subscription checkout: {result['session_id']}")
            return jsonify(result)
        else:
            logging.error(f"Checkout creation failed: {result['error']}")
            return jsonify(result), 500
            
    except Exception as e:
        logging.error(f"Subscription checkout error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@subscription_bp.route('/success')
def subscription_success():
    """Handle successful subscription payment"""
    try:
        session_id = request.args.get('session_id')
        
        if not session_id:
            return redirect(url_for('subscription.subscription_plans'))
        
        # Verify payment and get subscription details
        result = subscription_manager.verify_subscription_payment(session_id)
        
        if result['success']:
            # Store subscription info in session
            session['subscription_id'] = result['subscription_id']
            session['customer_id'] = result['customer_id']
            session['plan_id'] = result['plan_id']
            
            logging.info(f"Subscription activated: {result['subscription_id']}")
            
            return render_template('subscription_success.html', 
                                 subscription=result)
        else:
            logging.error(f"Payment verification failed: {result['error']}")
            return render_template('subscription_error.html', 
                                 error=result['error'])
            
    except Exception as e:
        logging.error(f"Subscription success error: {e}")
        return render_template('subscription_error.html', 
                             error='An error occurred processing your subscription')

@subscription_bp.route('/cancelled')
def subscription_cancelled():
    """Handle cancelled subscription payment"""
    return render_template('subscription_cancelled.html')

@subscription_bp.route('/dashboard')
def subscription_dashboard():
    """Customer subscription dashboard"""
    try:
        subscription_id = session.get('subscription_id')
        customer_id = session.get('customer_id')
        plan_id = session.get('plan_id')
        
        if not subscription_id:
            return redirect(url_for('subscription.subscription_plans'))
        
        # Get customer usage and plan details
        plan = SUBSCRIPTION_PLANS.get(plan_id, {})
        
        return render_template('subscription_dashboard.html',
                             subscription_id=subscription_id,
                             plan=plan,
                             plan_id=plan_id)
        
    except Exception as e:
        logging.error(f"Dashboard error: {e}")
        return render_template('subscription_error.html',
                             error='Error loading dashboard')

@subscription_bp.route('/cancel', methods=['POST'])
def cancel_subscription():
    """Cancel subscription"""
    try:
        subscription_id = session.get('subscription_id')
        
        if not subscription_id:
            return jsonify({'success': False, 'error': 'No active subscription'}), 400
        
        result = subscription_manager.cancel_subscription(subscription_id)
        
        if result['success']:
            logging.info(f"Subscription cancelled: {subscription_id}")
            return jsonify(result)
        else:
            logging.error(f"Cancellation failed: {result['error']}")
            return jsonify(result), 500
            
    except Exception as e:
        logging.error(f"Cancellation error: {e}")
        return jsonify({'success': False, 'error': 'Internal server error'}), 500

@subscription_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    """Handle Stripe webhooks for subscription events"""
    try:
        payload = request.get_data(as_text=True)
        sig_header = request.headers.get('Stripe-Signature')
        
        # TODO: Verify webhook signature and handle events
        # This would include subscription updates, cancellations, etc.
        
        logging.info("Received Stripe webhook")
        return jsonify({'status': 'success'})
        
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return jsonify({'error': str(e)}), 500