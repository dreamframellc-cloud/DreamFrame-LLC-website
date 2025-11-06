#!/usr/bin/env python3
"""
Daily Payment System Health Check Scheduler for DreamFrame LLC
Automated daily testing with intelligent scheduling and failure recovery
"""

import os
import sys
import time
import schedule
import logging
import threading
import datetime
from payment_health_monitor import PaymentHealthMonitor, HealthCheckResult
from typing import List

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('daily_scheduler.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class DailyPaymentScheduler:
    """Daily payment system health check scheduler"""
    
    def __init__(self):
        self.monitor = PaymentHealthMonitor()
        self.last_run_status = None
        self.consecutive_failures = 0
        self.running = False
        
    def run_daily_check(self):
        """Run the daily payment system health check"""
        logger.info("🔄 Starting scheduled daily payment health check...")
        
        try:
            # Run health checks
            results = self.monitor.run_health_checks()
            
            # Analyze results
            failed_tests = [r for r in results if r.status == 'FAIL']
            warning_tests = [r for r in results if r.status == 'WARNING']
            
            # Update status tracking
            if failed_tests:
                self.last_run_status = 'FAILED'
                self.consecutive_failures += 1
                logger.error(f"🚨 Daily check FAILED - {len(failed_tests)} critical failures!")
                
                # Send critical alerts
                self._send_critical_alerts(failed_tests)
                
                # If multiple consecutive failures, escalate
                if self.consecutive_failures >= 3:
                    self._escalate_alerts()
                    
            elif warning_tests:
                self.last_run_status = 'WARNING'
                self.consecutive_failures = 0  # Reset failure count
                logger.warning(f"⚠️ Daily check completed with {len(warning_tests)} warnings")
                
                # Send warning notifications
                self._send_warning_notifications(warning_tests)
                
            else:
                self.last_run_status = 'SUCCESS'
                self.consecutive_failures = 0  # Reset failure count
                logger.info("✅ Daily payment system check: ALL SYSTEMS OPERATIONAL")
            
            # Send alerts and save results
            self.monitor.send_alerts(results)
            self.monitor.save_results(results)
            
            # Log summary
            self._log_daily_summary(results)
            
        except Exception as e:
            logger.error(f"❌ Daily check failed with exception: {e}")
            self.last_run_status = 'ERROR'
            self.consecutive_failures += 1
    
    def _send_critical_alerts(self, failed_tests: List[HealthCheckResult]):
        """Send critical alerts for failed tests"""
        logger.error("🚨 CRITICAL PAYMENT SYSTEM ALERT 🚨")
        logger.error(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.error(f"Failed Tests: {len(failed_tests)}")
        
        for test in failed_tests:
            logger.error(f"❌ {test.test_name}")
            logger.error(f"   Details: {test.details}")
            if test.error:
                logger.error(f"   Error: {test.error}")
    
    def _send_warning_notifications(self, warning_tests: List[HealthCheckResult]):
        """Send warning notifications"""
        logger.warning("⚠️ Payment System Warning Notification")
        logger.warning(f"Time: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.warning(f"Warning Tests: {len(warning_tests)}")
        
        for test in warning_tests:
            logger.warning(f"⚠️ {test.test_name}: {test.details}")
    
    def _escalate_alerts(self):
        """Escalate alerts for consecutive failures"""
        logger.error("🔥 PAYMENT SYSTEM ESCALATION 🔥")
        logger.error(f"CRITICAL: {self.consecutive_failures} consecutive daily check failures!")
        logger.error("Immediate attention required - payment system may be compromised")
        logger.error("Recommended actions:")
        logger.error("1. Check Stripe API connectivity")
        logger.error("2. Verify environment variables")
        logger.error("3. Review server logs")
        logger.error("4. Test payment flow manually")
    
    def _log_daily_summary(self, results: List[HealthCheckResult]):
        """Log daily summary statistics"""
        passed = len([r for r in results if r.status == 'PASS'])
        failed = len([r for r in results if r.status == 'FAIL'])
        warnings = len([r for r in results if r.status == 'WARNING'])
        
        logger.info("📊 Daily Payment Health Summary:")
        logger.info(f"   ✅ Passed: {passed}")
        logger.info(f"   ❌ Failed: {failed}")
        logger.info(f"   ⚠️ Warnings: {warnings}")
        logger.info(f"   🔄 Consecutive Failures: {self.consecutive_failures}")
        
        # Calculate uptime percentage
        if passed + failed + warnings > 0:
            uptime = (passed / (passed + failed + warnings)) * 100
            logger.info(f"   📈 System Health: {uptime:.1f}%")
    
    def run_immediate_check(self):
        """Run an immediate health check (for testing)"""
        logger.info("🚀 Running immediate payment health check...")
        self.run_daily_check()
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        logger.info("🕐 Starting daily payment system scheduler...")
        
        # Schedule daily check at 8:00 AM
        schedule.every().day.at("08:00").do(self.run_daily_check)
        
        # Schedule backup check at 8:00 PM
        schedule.every().day.at("20:00").do(self.run_daily_check)
        
        self.running = True
        
        logger.info("⏰ Scheduled daily checks:")
        logger.info("   📅 8:00 AM - Primary daily health check")
        logger.info("   📅 8:00 PM - Backup daily health check")
        
        # Run initial check
        logger.info("🔄 Running initial health check...")
        self.run_daily_check()
        
        # Start scheduler loop
        while self.running:
            schedule.run_pending()
            time.sleep(60)  # Check every minute
    
    def stop_scheduler(self):
        """Stop the scheduler"""
        logger.info("🛑 Stopping daily payment scheduler...")
        self.running = False
    
    def get_status(self):
        """Get current scheduler status"""
        return {
            'running': self.running,
            'last_run_status': self.last_run_status,
            'consecutive_failures': self.consecutive_failures,
            'next_scheduled_run': schedule.next_run()
        }

def main():
    """Main function to run the scheduler"""
    logger.info("🚀 DreamFrame Daily Payment System Monitor Starting...")
    
    scheduler = DailyPaymentScheduler()
    
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--immediate':
            # Run immediate check
            scheduler.run_immediate_check()
        else:
            # Start daily scheduler
            scheduler.start_scheduler()
            
    except KeyboardInterrupt:
        logger.info("⏹️ Scheduler stopped by user")
        scheduler.stop_scheduler()
    except Exception as e:
        logger.error(f"❌ Scheduler error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()