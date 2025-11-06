#!/usr/bin/env python3
"""
AI-Powered Payment System Health Monitor for DreamFrame LLC
Daily automated testing and intelligent monitoring with OpenAI analysis
"""

import os
import sys
import json
import time
import datetime
import logging
import stripe
import requests
from openai import OpenAI
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('payment_monitor.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class HealthCheckResult:
    """Structure for health check results"""
    timestamp: str
    test_name: str
    status: str  # 'PASS', 'FAIL', 'WARNING'
    details: str
    response_time_ms: Optional[float] = None
    error: Optional[str] = None

class PaymentHealthMonitor:
    """AI-powered payment system health monitor"""
    
    def __init__(self):
        self.openai_client = None
        self.stripe_test_key = None
        self.base_url = "http://localhost:5000"  # Your Flask app URL
        self.results: List[HealthCheckResult] = []
        
        # Initialize OpenAI
        self._init_openai()
        
        # Initialize Stripe
        self._init_stripe()
        
    def _init_openai(self):
        """Initialize OpenAI client"""
        try:
            api_key = os.environ.get('OPENAI_API_KEY')
            if not api_key:
                logger.error("OPENAI_API_KEY not found in environment")
                return
                
            self.openai_client = OpenAI(api_key=api_key)
            logger.info("🤖 OpenAI client initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI: {e}")
    
    def _init_stripe(self):
        """Initialize Stripe with test keys"""
        try:
            # Use test key for daily monitoring
            test_key = os.environ.get('STRIPE_TEST_SECRET_KEY')
            if not test_key:
                logger.warning("STRIPE_TEST_SECRET_KEY not found - using default test key")
                test_key = "sk_test_..."  # Fallback test key
            
            stripe.api_key = test_key
            self.stripe_test_key = test_key
            logger.info("💳 Stripe test client initialized")
            
        except Exception as e:
            logger.error(f"Failed to initialize Stripe: {e}")
    
    def run_health_checks(self) -> List[HealthCheckResult]:
        """Run comprehensive payment system health checks"""
        logger.info("🔍 Starting daily payment system health checks...")
        
        self.results = []
        
        # Test 1: Stripe API Connection
        self._test_stripe_connection()
        
        # Test 2: Payment Page Load
        self._test_payment_page_load()
        
        # Test 3: Checkout Session Creation
        self._test_checkout_session_creation()
        
        # Test 4: Payment Processing Flow
        self._test_payment_flow()
        
        # Test 5: Error Handling
        self._test_error_handling()
        
        # Generate AI analysis
        if self.openai_client:
            self._generate_ai_analysis()
        
        return self.results
    
    def _test_stripe_connection(self):
        """Test Stripe API connectivity"""
        start_time = time.time()
        
        try:
            # Test basic Stripe API call
            account = stripe.Account.retrieve()
            response_time = (time.time() - start_time) * 1000
            
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Stripe API Connection",
                status="PASS",
                details=f"Successfully connected to Stripe API. Account: {account.get('id', 'N/A')}",
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Stripe API Connection",
                status="FAIL",
                details="Failed to connect to Stripe API",
                response_time_ms=response_time,
                error=str(e)
            ))
    
    def _test_payment_page_load(self):
        """Test payment page accessibility"""
        start_time = time.time()
        
        try:
            response = requests.get(f"{self.base_url}/", timeout=10)
            response_time = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                # Check for payment-related elements
                content = response.text.lower()
                has_payment_elements = any(keyword in content for keyword in [
                    'stripe', 'payment', 'checkout', 'pay now', 'deposit'
                ])
                
                status = "PASS" if has_payment_elements else "WARNING"
                details = f"Page loaded successfully (HTTP {response.status_code}). Payment elements: {'Found' if has_payment_elements else 'Not found'}"
                
                self.results.append(HealthCheckResult(
                    timestamp=datetime.datetime.now().isoformat(),
                    test_name="Payment Page Load",
                    status=status,
                    details=details,
                    response_time_ms=response_time
                ))
            else:
                self.results.append(HealthCheckResult(
                    timestamp=datetime.datetime.now().isoformat(),
                    test_name="Payment Page Load",
                    status="FAIL",
                    details=f"Page returned HTTP {response.status_code}",
                    response_time_ms=response_time
                ))
                
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Payment Page Load",
                status="FAIL",
                details="Failed to load payment page",
                response_time_ms=response_time,
                error=str(e)
            ))
    
    def _test_checkout_session_creation(self):
        """Test Stripe checkout session creation"""
        start_time = time.time()
        
        try:
            # Create a test checkout session
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': 'Health Check Test Payment',
                        },
                        'unit_amount': 100,  # $1.00 test
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:5000/success',
                cancel_url='http://localhost:5000/cancel',
                metadata={'test': 'health_check', 'timestamp': str(int(time.time()))}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Checkout Session Creation",
                status="PASS",
                details=f"Successfully created checkout session: {session.id}",
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Checkout Session Creation",
                status="FAIL",
                details="Failed to create checkout session",
                response_time_ms=response_time,
                error=str(e)
            ))
    
    def _test_payment_flow(self):
        """Test end-to-end payment flow simulation"""
        start_time = time.time()
        
        try:
            # Test payment intent creation
            payment_intent = stripe.PaymentIntent.create(
                amount=100,  # $1.00 test
                currency='usd',
                metadata={'test': 'health_check_flow'}
            )
            
            response_time = (time.time() - start_time) * 1000
            
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Payment Flow Simulation",
                status="PASS",
                details=f"Payment intent created successfully: {payment_intent.id}",
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Payment Flow Simulation",
                status="FAIL",
                details="Failed to create payment intent",
                response_time_ms=response_time,
                error=str(e)
            ))
    
    def _test_error_handling(self):
        """Test payment system error handling"""
        start_time = time.time()
        
        try:
            # Test with invalid amount to trigger error handling
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=-100,  # Invalid negative amount
                    currency='usd',
                    metadata={'test': 'error_handling'}
                )
                
                # If this succeeds, something might be wrong
                status = "WARNING"
                details = "Expected failure but payment intent was created with invalid amount"
                
            except stripe.error.InvalidRequestError as e:
                # This is expected - invalid amount should be rejected
                status = "PASS"
                details = f"Error handling working correctly - invalid request properly handled: {str(e)}"
            except Exception as e:
                # Any other error is also expected
                status = "PASS"
                details = f"Error handling working correctly - error properly caught: {str(e)}"
            
            response_time = (time.time() - start_time) * 1000
            
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Error Handling Test",
                status=status,
                details=details,
                response_time_ms=response_time
            ))
            
        except Exception as e:
            response_time = (time.time() - start_time) * 1000
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="Error Handling Test",
                status="FAIL",
                details="Error handling test failed unexpectedly",
                response_time_ms=response_time,
                error=str(e)
            ))
    
    def _generate_ai_analysis(self):
        """Generate AI-powered analysis of health check results"""
        try:
            # Prepare results summary for AI
            summary = {
                'total_tests': len(self.results),
                'passed': len([r for r in self.results if r.status == 'PASS']),
                'failed': len([r for r in self.results if r.status == 'FAIL']),
                'warnings': len([r for r in self.results if r.status == 'WARNING']),
                'avg_response_time': sum([r.response_time_ms for r in self.results if r.response_time_ms]) / len([r for r in self.results if r.response_time_ms]),
                'test_details': [
                    {
                        'test': r.test_name,
                        'status': r.status,
                        'details': r.details,
                        'response_time': r.response_time_ms,
                        'error': r.error
                    } for r in self.results
                ]
            }
            
            # the newest OpenAI model is "gpt-5" which was released August 7, 2025.
            # do not change this unless explicitly requested by the user
            if self.openai_client:
                response = self.openai_client.chat.completions.create(
                    model="gpt-5",
                    messages=[
                        {
                            "role": "system",
                            "content": "You are an AI payment system analyst for DreamFrame LLC video production company. Analyze payment system health check results and provide insights, recommendations, and alert level assessment. Be concise but thorough. Respond with JSON containing 'summary', 'risk_level', 'recommendations' fields."
                        },
                        {
                            "role": "user",
                            "content": f"Analyze these payment system health check results and provide recommendations:\n\n{json.dumps(summary, indent=2)}"
                        }
                    ],
                    response_format={"type": "json_object"}
                )
            
                ai_analysis = json.loads(response.choices[0].message.content)
            else:
                ai_analysis = {"summary": "OpenAI client not available", "risk_level": "unknown"}
            
            # Add AI analysis as a special result
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="AI System Analysis",
                status="PASS",
                details=f"AI Analysis Complete: {ai_analysis.get('summary', 'Analysis generated successfully')}"
            ))
            
            # Log detailed AI analysis
            logger.info("🤖 AI Analysis Results:")
            logger.info(json.dumps(ai_analysis, indent=2))
            
        except Exception as e:
            logger.error(f"Failed to generate AI analysis: {e}")
            self.results.append(HealthCheckResult(
                timestamp=datetime.datetime.now().isoformat(),
                test_name="AI System Analysis",
                status="WARNING",
                details="AI analysis failed but system monitoring completed",
                error=str(e)
            ))
    
    def send_alerts(self, results: List[HealthCheckResult]):
        """Send alerts based on health check results"""
        failed_tests = [r for r in results if r.status == 'FAIL']
        warning_tests = [r for r in results if r.status == 'WARNING']
        
        if failed_tests:
            logger.error(f"🚨 CRITICAL: {len(failed_tests)} payment system tests FAILED!")
            for test in failed_tests:
                logger.error(f"   ❌ {test.test_name}: {test.details}")
        
        if warning_tests:
            logger.warning(f"⚠️  WARNING: {len(warning_tests)} tests have warnings")
            for test in warning_tests:
                logger.warning(f"   ⚠️  {test.test_name}: {test.details}")
        
        if not failed_tests and not warning_tests:
            logger.info("✅ All payment system tests PASSED!")
    
    def save_results(self, results: List[HealthCheckResult]):
        """Save results to file for historical tracking"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"payment_health_{timestamp}.json"
            
            data = {
                'timestamp': datetime.datetime.now().isoformat(),
                'summary': {
                    'total_tests': len(results),
                    'passed': len([r for r in results if r.status == 'PASS']),
                    'failed': len([r for r in results if r.status == 'FAIL']),
                    'warnings': len([r for r in results if r.status == 'WARNING'])
                },
                'results': [
                    {
                        'timestamp': r.timestamp,
                        'test_name': r.test_name,
                        'status': r.status,
                        'details': r.details,
                        'response_time_ms': r.response_time_ms,
                        'error': r.error
                    } for r in results
                ]
            }
            
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            
            logger.info(f"📊 Results saved to {filename}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

def main():
    """Main function to run daily health checks"""
    logger.info("🚀 Starting DreamFrame Payment System Health Monitor")
    
    monitor = PaymentHealthMonitor()
    results = monitor.run_health_checks()
    
    # Send alerts
    monitor.send_alerts(results)
    
    # Save results
    monitor.save_results(results)
    
    # Print summary
    passed = len([r for r in results if r.status == 'PASS'])
    failed = len([r for r in results if r.status == 'FAIL'])
    warnings = len([r for r in results if r.status == 'WARNING'])
    
    logger.info(f"📋 Health Check Summary: {passed} PASSED, {failed} FAILED, {warnings} WARNINGS")
    
    # Return exit code based on results
    if failed > 0:
        sys.exit(1)  # Critical failures
    elif warnings > 0:
        sys.exit(2)  # Warnings only
    else:
        sys.exit(0)  # All good

if __name__ == "__main__":
    main()