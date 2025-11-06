#!/usr/bin/env python3
"""
Test script for DreamFrame Payment Health Monitor
Quick test to verify the AI monitoring system is working
"""

import sys
import logging
from daily_payment_scheduler import DailyPaymentScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_payment_monitor():
    """Test the payment monitoring system"""
    print("🤖 Testing DreamFrame AI Payment Monitor...")
    print("=" * 50)
    
    try:
        # Create scheduler instance
        scheduler = DailyPaymentScheduler()
        
        # Run immediate health check
        print("🔍 Running payment system health check...")
        scheduler.run_immediate_check()
        
        print("\n✅ Payment monitor test completed!")
        print("Check the logs above for detailed results.")
        
        # Show status
        status = scheduler.get_status()
        print(f"\n📊 Monitor Status:")
        print(f"   Last Run: {status['last_run_status']}")
        print(f"   Consecutive Failures: {status['consecutive_failures']}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_payment_monitor()
    sys.exit(0 if success else 1)