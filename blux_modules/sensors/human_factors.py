"""
Enhanced human factors: unlock patterns, presence windows with behavioral analysis
"""

import time
import threading
from datetime import datetime, timedelta
import logging

class HumanFactorsSensor:
    def __init__(self, check_interval=5):
        self.check_interval = check_interval
        self.presence_log = []
        self.unlock_attempts = []
        self.working_hours = (8, 18)  # 8 AM to 6 PM
        self.logger = logging.getLogger('blux.sensors.human_factors')
        self._monitoring = False
    
    def get_screen_status(self):
        """Get screen lock status with security context"""
        try:
            # Simulated - in production, use platform-specific APIs
            locked = False  # Simulated status
            current_time = datetime.now()
            
            event = {
                'type': 'screen_status',
                'locked': locked,
                'timestamp': current_time,
                'risk_level': 'high' if not locked and not self._is_working_hours() else 'low'
            }
            
            if not locked and not self._is_working_hours():
                self.logger.warning("Screen unlocked outside working hours")
            
            return event
            
        except Exception as e:
            self.logger.error(f"Screen status error: {e}")
            return None
    
    def get_user_presence(self):
        """Detect user presence with behavioral analysis"""
        try:
            # Simulated - in production, use sensors/webcam/etc.
            present = True  # Simulated
            
            current_time = datetime.now()
            presence_event = {
                'type': 'presence',
                'present': present,
                'timestamp': current_time
            }
            
            self.presence_log.append(presence_event)
            
            # Analyze presence patterns
            self._analyze_presence_patterns()
            
            return presence_event
            
        except Exception as e:
            self.logger.error(f"Presence detection error: {e}")
            return None
    
    def _is_working_hours(self):
        """Check if current time is within working hours"""
        current_hour = datetime.now().hour
        return self.working_hours[0] <= current_hour < self.working_hours[1]
    
    def _analyze_presence_patterns(self):
        """Analyze user presence patterns for anomalies"""
        if len(self.presence_log) < 10:  # Need sufficient data
            return
        
        # Check for unusual activity hours
        recent_logs = self.presence_log[-10:]
        unusual_hours = sum(1 for log in recent_logs 
                          if not self._is_working_hours() and log['present'])
        
        if unusual_hours > 5:  # More than 5 presence events outside working hours
            self.logger.warning("Unusual activity pattern detected outside working hours")
    
    def record_unlock_attempt(self, success=True, method="password"):
        """Record screen unlock attempts"""
        attempt = {
            'success': success,
            'method': method,
            'timestamp': datetime.now()
        }
        self.unlock_attempts.append(attempt)
        
        if not success:
            self.logger.warning(f"Failed unlock attempt using {method}")
    
    def get_security_status(self):
        """Get comprehensive human factors security status"""
        screen_status = self.get_screen_status()
        presence_status = self.get_user_presence()
        
        status = {
            'screen_locked': screen_status['locked'] if screen_status else True,
            'user_present': presence_status['present'] if presence_status else False,
            'working_hours': self._is_working_hours(),
            'recent_unlock_attempts': len([a for a in self.unlock_attempts 
                                         if datetime.now() - a['timestamp'] < timedelta(hours=1)]),
            'timestamp': datetime.now()
        }
        
        # Calculate risk score
        risk_factors = []
        if not status['screen_locked']:
            risk_factors.append(2)
        if status['recent_unlock_attempts'] > 3:
            risk_factors.append(3)
        if not status['working_hours'] and status['user_present']:
            risk_factors.append(1)
        
        status['risk_score'] = sum(risk_factors)
        status['risk_level'] = 'high' if status['risk_score'] >= 3 else 'medium' if status['risk_score'] >= 1 else 'low'
        
        return status
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self._monitoring = True
        self.logger.info("Human factors monitoring started")
        
        def monitor():
            while self._monitoring:
                self.get_security_status()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("Human factors monitoring stopped")
