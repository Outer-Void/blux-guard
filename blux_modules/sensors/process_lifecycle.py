"""
Enhanced process lifecycle sensor: track start/stop of processes with security analysis
"""

import os
import time
import threading
import psutil  # Requires: pip install psutil
from datetime import datetime
from collections import defaultdict, deque
import logging

class ProcessSensor:
    def __init__(self, check_interval=2, max_history=1000):
        self.check_interval = check_interval
        self.process_history = deque(maxlen=max_history)
        self.known_processes = set()
        self.suspicious_processes = {"nc", "netcat", "nmap", "john", "hydra"}
        self.process_creation_times = {}
        self.logger = logging.getLogger('blux.sensors.process')
        self._monitoring = False
    
    def list_processes(self):
        """List all running processes with security analysis"""
        try:
            current_processes = {}
            new_processes = []
            terminated_processes = []
            
            for proc in psutil.process_iter(['pid', 'name', 'create_time', 'cmdline', 'username']):
                try:
                    process_info = proc.info
                    pid = process_info['pid']
                    
                    current_processes[pid] = process_info
                    
                    # Detect new processes
                    if pid not in self.known_processes and pid in self.process_creation_times:
                        new_processes.append(process_info)
                        self._analyze_new_process(process_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied):
                    continue
            
            # Detect terminated processes
            current_pids = set(current_processes.keys())
            previous_pids = set(self.process_creation_times.keys())
            terminated_pids = previous_pids - current_pids
            
            for pid in terminated_pids:
                if pid in self.process_creation_times:
                    terminated_processes.append({
                        'pid': pid,
                        'name': self.process_creation_times[pid].get('name', 'unknown'),
                        'lifetime': time.time() - self.process_creation_times[pid]['create_time']
                    })
                    del self.process_creation_times[pid]
            
            # Update known processes
            self.known_processes = set(current_processes.keys())
            
            # Log process activity
            if new_processes:
                self.logger.info(f"Detected {len(new_processes)} new processes")
            if terminated_processes:
                self.logger.info(f"Detected {len(terminated_processes)} terminated processes")
            
            result = {
                'total_processes': len(current_processes),
                'new_processes': new_processes,
                'terminated_processes': terminated_processes,
                'sample_processes': list(current_processes.values())[:10],  # Sample for performance
                'timestamp': datetime.now()
            }
            
            self.process_history.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Process listing error: {e}")
            return {'total_processes': 0, 'new_processes': [], 'terminated_processes': [], 'sample_processes': []}
    
    def _analyze_new_process(self, process_info):
        """Analyze new process for security concerns"""
        security_analysis = {
            'suspicious': False,
            'issues': [],
            'risk_level': 'low'
        }
        
        process_name = process_info['name'].lower() if process_info['name'] else ''
        cmdline = ' '.join(process_info['cmdline']) if process_info['cmdline'] else ''
        
        # Check for known suspicious process names
        if any(suspicious in process_name for suspicious in self.suspicious_processes):
            security_analysis['suspicious'] = True
            security_analysis['issues'].append('suspicious_name')
            security_analysis['risk_level'] = 'high'
            self.logger.warning(f"Suspicious process detected: {process_name} (PID: {process_info['pid']})")
        
        # Check for processes running from unusual locations
        if cmdline and ('/tmp/' in cmdline or '/var/tmp/' in cmdline):
            security_analysis['suspicious'] = True
            security_analysis['issues'].append('temp_location')
            security_analysis['risk_level'] = 'medium'
            self.logger.warning(f"Process running from temp location: {process_name}")
        
        # Check for hidden or disguised processes
        if process_name.startswith('.') or ' ' in process_name:
            security_analysis['issues'].append('unusual_naming')
        
        # Store process creation time for lifetime analysis
        self.process_creation_times[process_info['pid']] = {
            'name': process_info['name'],
            'create_time': process_info.get('create_time', time.time()),
            'security_analysis': security_analysis
        }
        
        return security_analysis
    
    def get_process_statistics(self):
        """Get process lifecycle statistics"""
        current_info = self.list_processes()
        
        stats = {
            'total_running': current_info['total_processes'],
            'recently_started': len(current_info['new_processes']),
            'recently_terminated': len(current_info['terminated_processes']),
            'suspicious_processes': len([p for p in current_info['new_processes'] 
                                       if self._analyze_new_process(p)['suspicious']]),
            'timestamp': datetime.now()
        }
        
        return stats
    
    def find_process_by_name(self, name_pattern):
        """Find processes by name pattern"""
        current_info = self.list_processes()
        matching = []
        
        for process in current_info['sample_processes']:
            if (process['name'] and name_pattern.lower() in process['name'].lower()) or \
               (process['cmdline'] and any(name_pattern.lower() in str(arg).lower() 
                                         for arg in process['cmdline'])):
                matching.append(process)
        
        return matching
    
    def start_monitoring(self):
        """Start continuous process monitoring"""
        self._monitoring = True
        self.logger.info("Process monitoring started")
        
        # Initial scan to populate known processes
        self.list_processes()
        
        def monitor():
            while self._monitoring:
                self.list_processes()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("Process monitoring stopped")
