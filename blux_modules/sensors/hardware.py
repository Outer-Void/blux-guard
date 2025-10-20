"""
Enhanced hardware sensors: charging, BT pairing, USB attach with security analysis
"""

import time
import threading
from datetime import datetime
import logging
import platform

class HardwareSensor:
    def __init__(self, check_interval=10):
        self.check_interval = check_interval
        self.bt_whitelist = {"BT-Headset-1", "BT-Keyboard-1"}
        self.usb_whitelist = {"Known-USB-1"}
        self.history = []
        self.logger = logging.getLogger('blux.sensors.hardware')
        self._monitoring = False
    
    def get_charging_status(self):
        """Get charging status with security context"""
        try:
            # Platform-specific implementation would go here
            status = True  # Simulated
            power_source = "AC" if status else "Battery"
            
            event = {
                'type': 'charging',
                'status': status,
                'power_source': power_source,
                'timestamp': datetime.now(),
                'risk_level': 'low' if status else 'medium'  # Battery mode might be riskier
            }
            
            self.history.append(event)
            self.logger.info(f"Charging status: {power_source}")
            return event
            
        except Exception as e:
            self.logger.error(f"Charging status error: {e}")
            return None
    
    def get_bluetooth_devices(self):
        """Get paired Bluetooth devices with security analysis"""
        try:
            # Simulated - in production, use platform-specific APIs
            devices = ["BT-Headset-1", "Suspicious-Device"]
            
            security_analysis = []
            for device in devices:
                is_whitelisted = device in self.bt_whitelist
                risk = "low" if is_whitelisted else "high"
                
                if not is_whitelisted:
                    self.logger.warning(f"Unknown Bluetooth device: {device}")
                
                security_analysis.append({
                    'device': device,
                    'whitelisted': is_whitelisted,
                    'risk_level': risk,
                    'timestamp': datetime.now()
                })
            
            event = {
                'type': 'bluetooth',
                'devices': security_analysis,
                'unknown_devices': [d for d in devices if d not in self.bt_whitelist]
            }
            
            self.history.append(event)
            return event
            
        except Exception as e:
            self.logger.error(f"Bluetooth scan error: {e}")
            return None
    
    def get_usb_devices(self):
        """Get attached USB devices with security analysis"""
        try:
            # Simulated - in production, use platform-specific APIs
            usb_devices = ["Known-USB-1", "Unknown-USB-Device"]
            
            security_analysis = []
            for device in usb_devices:
                is_whitelisted = device in self.usb_whitelist
                risk = "low" if is_whitelisted else "high"
                
                if not is_whitelisted:
                    self.logger.warning(f"Unknown USB device: {device}")
                
                security_analysis.append({
                    'device': device,
                    'whitelisted': is_whitelisted,
                    'risk_level': risk,
                    'timestamp': datetime.now()
                })
            
            event = {
                'type': 'usb',
                'devices': security_analysis,
                'unknown_devices': [d for d in usb_devices if d not in self.usb_whitelist]
            }
            
            self.history.append(event)
            return event
            
        except Exception as e:
            self.logger.error(f"USB scan error: {e}")
            return None
    
    def perform_security_scan(self):
        """Perform complete hardware security scan"""
        results = {
            'charging': self.get_charging_status(),
            'bluetooth': self.get_bluetooth_devices(),
            'usb': self.get_usb_devices(),
            'timestamp': datetime.now(),
            'system': platform.system()
        }
        
        # Calculate overall risk
        risks = []
        if results['bluetooth']:
            risks.extend([d['risk_level'] for d in results['bluetooth']['devices']])
        if results['usb']:
            risks.extend([d['risk_level'] for d in results['usb']['devices']])
        
        overall_risk = "high" if "high" in risks else "medium" if "medium" in risks else "low"
        results['overall_risk'] = overall_risk
        
        return results
    
    def start_monitoring(self):
        """Start continuous hardware monitoring"""
        self._monitoring = True
        self.logger.info("Hardware monitoring started")
        
        def monitor():
            while self._monitoring:
                self.perform_security_scan()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("Hardware monitoring stopped")
