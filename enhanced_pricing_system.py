"""
Enhanced Pricing System with Order Form Integration
"""
from flask import render_template, request, jsonify, flash, redirect, url_for
from models import PricingTier, ServiceType
import json

def get_enhanced_pricing_data():
    """Get pricing data from database with enhanced features"""
    try:
        pricing_tiers = PricingTier.query.filter_by(active=True).order_by(PricingTier.base_price.asc()).all()
        
        pricing_data = {}
        for tier in pricing_tiers:
            service_key = tier.service_type.value
            pricing_data[service_key] = {
                'id': tier.id,
                'name': tier.tier_name,
                'price': tier.base_price / 100,  # Convert cents to dollars
                'features': tier.features or [],
                'delivery_days': tier.delivery_days,
                'service_type': tier.service_type.value,
                'stripe_price_id': tier.stripe_price_id,
                'popular': service_key in ['videogram', 'social_content']  # Mark popular services
            }
        
        return pricing_data
    except Exception as e:
        # Fallback to static pricing if database fails
        return {
            'videogram': {
                'name': 'VideoGram Basic',
                'price': 50,
                'features': ['30-60 second video', 'Basic transitions', '48-hour delivery', 'Music included'],
                'delivery_days': 2,
                'popular': True
            },
            'social_content': {
                'name': 'Social Media Package',
                'price': 150,
                'features': ['3 short videos', 'Custom graphics', 'Social media ready', '72-hour delivery'],
                'delivery_days': 3,
                'popular': True
            },
            'wedding_highlight': {
                'name': 'Wedding Highlight Reel',
                'price': 500,
                'features': ['3-5 minute highlight', 'Professional editing', 'Music licensing', '1 week delivery'],
                'delivery_days': 7
            },
            'corporate_video': {
                'name': 'Corporate Production',
                'price': 1000,
                'features': ['Professional production', 'Script writing', 'Voice over', '2 week delivery'],
                'delivery_days': 14
            },
            'full_production': {
                'name': 'Full Production Service',
                'price': 2000,
                'features': ['Complete production', 'Multiple revisions', 'Premium quality', 'Custom timeline'],
                'delivery_days': 21
            }
        }

def create_enhanced_order_form():
    """Create enhanced order form with dynamic pricing"""
    pricing_data = get_enhanced_pricing_data()
    
    order_form_template = """
    <div class="modal fade" id="orderModal" tabindex="-1">
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Order <span id="selectedService"></span></h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <form id="orderForm">
                        <input type="hidden" id="serviceType" name="service_type">
                        
                        <!-- Customer Information -->
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <label for="customerName" class="form-label">Full Name *</label>
                                <input type="text" class="form-control" id="customerName" name="name" required>
                            </div>
                            <div class="col-md-6">
                                <label for="customerEmail" class="form-label">Email Address *</label>
                                <input type="email" class="form-control" id="customerEmail" name="email" required>
                            </div>
                        </div>
                        
                        <div class="row mb-4">
                            <div class="col-md-6">
                                <label for="customerPhone" class="form-label">Phone Number</label>
                                <input type="tel" class="form-control" id="customerPhone" name="phone">
                            </div>
                            <div class="col-md-6">
                                <label for="timeline" class="form-label">Preferred Timeline</label>
                                <select class="form-select" id="timeline" name="timeline">
                                    <option value="">Select timeline</option>
                                    <option value="asap">ASAP</option>
                                    <option value="1_week">Within 1 week</option>
                                    <option value="2_weeks">Within 2 weeks</option>
                                    <option value="1_month">Within 1 month</option>
                                    <option value="flexible">Flexible</option>
                                </select>
                            </div>
                        </div>
                        
                        <!-- Project Details -->
                        <div class="mb-4">
                            <label for="projectDescription" class="form-label">Project Description *</label>
                            <textarea class="form-control" id="projectDescription" name="message" rows="4" 
                                    placeholder="Tell us about your project, vision, and any specific requirements..." required></textarea>
                        </div>
                        
                        <!-- File Upload -->
                        <div class="mb-4">
                            <label for="fileUpload" class="form-label">Upload Materials (Optional)</label>
                            <input type="file" class="form-control" id="fileUpload" name="files" multiple 
                                   accept="video/*,image/*,.pdf,.doc,.docx">
                            <div class="form-text">Upload photos, videos, or documents related to your project</div>
                        </div>
                        
                        <!-- Additional Services -->
                        <div class="mb-4">
                            <label class="form-label">Additional Services</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="rushDelivery" name="rush_delivery">
                                <label class="form-check-label" for="rushDelivery">
                                    Rush Delivery (+$100)
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="extraRevisions" name="extra_revisions">
                                <label class="form-check-label" for="extraRevisions">
                                    Extra Revisions (+$50)
                                </label>
                            </div>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="sourceFiles" name="source_files">
                                <label class="form-check-label" for="sourceFiles">
                                    Source Files (+$25)
                                </label>
                            </div>
                        </div>
                        
                        <!-- Order Summary -->
                        <div class="card bg-light mb-4">
                            <div class="card-body">
                                <h6>Order Summary</h6>
                                <div class="d-flex justify-content-between">
                                    <span id="baseServiceName">Service</span>
                                    <span id="baseServicePrice">$0</span>
                                </div>
                                <div id="additionalServices"></div>
                                <hr>
                                <div class="d-flex justify-content-between fw-bold">
                                    <span>Total</span>
                                    <span id="totalPrice">$0</span>
                                </div>
                                <small class="text-muted">Estimated delivery: <span id="estimatedDelivery"></span></small>
                            </div>
                        </div>
                        
                        <!-- Terms and Conditions -->
                        <div class="form-check mb-4">
                            <input class="form-check-input" type="checkbox" id="agreeTerms" required>
                            <label class="form-check-label" for="agreeTerms">
                                I agree to the <a href="#" target="_blank">Terms and Conditions</a> *
                            </label>
                        </div>
                    </form>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                    <button type="button" class="btn btn-primary" id="proceedToPayment">
                        <i class="fas fa-credit-card me-2"></i>Proceed to Payment
                    </button>
                </div>
            </div>
        </div>
    </div>
    """
    
    return order_form_template, pricing_data

def generate_pricing_javascript(pricing_data):
    """Generate JavaScript for dynamic pricing calculations"""
    js_code = f"""
    <script>
    const pricingData = {json.dumps(pricing_data)};
    let currentService = null;
    
    function openOrderModal(serviceType) {{
        currentService = serviceType;
        const service = pricingData[serviceType];
        
        if (!service) {{
            alert('Service not found');
            return;
        }}
        
        document.getElementById('serviceType').value = serviceType;
        document.getElementById('selectedService').textContent = service.name;
        document.getElementById('baseServiceName').textContent = service.name;
        document.getElementById('baseServicePrice').textContent = '$' + service.price;
        
        updateOrderSummary();
        
        const modal = new bootstrap.Modal(document.getElementById('orderModal'));
        modal.show();
    }}
    
    function updateOrderSummary() {{
        if (!currentService) return;
        
        const service = pricingData[currentService];
        let total = service.price;
        let additionalServices = '';
        
        // Calculate additional services
        if (document.getElementById('rushDelivery').checked) {{
            total += 100;
            additionalServices += '<div class="d-flex justify-content-between"><span>Rush Delivery</span><span>+$100</span></div>';
        }}
        
        if (document.getElementById('extraRevisions').checked) {{
            total += 50;
            additionalServices += '<div class="d-flex justify-content-between"><span>Extra Revisions</span><span>+$50</span></div>';
        }}
        
        if (document.getElementById('sourceFiles').checked) {{
            total += 25;
            additionalServices += '<div class="d-flex justify-content-between"><span>Source Files</span><span>+$25</span></div>';
        }}
        
        document.getElementById('additionalServices').innerHTML = additionalServices;
        document.getElementById('totalPrice').textContent = '$' + total;
        
        // Update estimated delivery
        let deliveryDays = service.delivery_days;
        if (document.getElementById('rushDelivery').checked) {{
            deliveryDays = Math.max(1, Math.floor(deliveryDays / 2));
        }}
        
        const deliveryDate = new Date();
        deliveryDate.setDate(deliveryDate.getDate() + deliveryDays);
        document.getElementById('estimatedDelivery').textContent = deliveryDate.toLocaleDateString();
    }}
    
    // Add event listeners for checkboxes
    document.addEventListener('DOMContentLoaded', function() {{
        ['rushDelivery', 'extraRevisions', 'sourceFiles'].forEach(id => {{
            document.getElementById(id).addEventListener('change', updateOrderSummary);
        }});
        
        document.getElementById('proceedToPayment').addEventListener('click', function() {{
            const form = document.getElementById('orderForm');
            if (form.checkValidity()) {{
                submitOrder();
            }} else {{
                form.reportValidity();
            }}
        }});
    }});
    
    function submitOrder() {{
        const formData = new FormData(document.getElementById('orderForm'));
        
        fetch('/create_order/' + currentService, {{
            method: 'POST',
            body: formData
        }})
        .then(response => response.json())
        .then(data => {{
            if (data.success) {{
                // Redirect to Stripe checkout
                window.location.href = data.checkout_url;
            }} else {{
                alert('Error creating order: ' + data.error);
            }}
        }})
        .catch(error => {{
            alert('Error creating order: ' + error);
        }});
    }}
    </script>
    """
    
    return js_code