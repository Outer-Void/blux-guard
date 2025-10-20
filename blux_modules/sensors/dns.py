"""
DNS sensor: monitors DNS queries and resolutions with improved detection
"""

import time
import socket
import threading
from collections import deque
from datetime import datetime
import logging

class DNSSensor:
    def __init__(self, watch_interval=5, max_history=1000):
        self.watch_interval = watch_interval
        self.query_history = deque(maxlen=max_history)
        self.suspicious_domains = {"bad.site", "malicious.com", "phishing.net"}
        self.logger = logging.getLogger('blux.sensors.dns')
        self._monitoring = False
        
    def capture_dns_queries(self):
        """Capture and analyze DNS queries"""
        try:
            # Simulate real DNS monitoring - in production, hook into system DNS
            queries = ["example.com", "good.site", "bad.site", "trusted.org"]
            
            suspicious_queries = []
            for query in queries:
                timestamp = datetime.now()
                is_suspicious = query in self.suspicious_domains
                record = {
                    'query': query,
                    'timestamp': timestamp,
                    'suspicious': is_suspicious,
                    'resolved_ip': self._resolve_dns(query) if not is_suspicious else None
                }
                self.query_history.append(record)
                
                if is_suspicious:
                    suspicious_queries.append(record)
                    self.logger.warning(f"Suspicious DNS query detected: {query}")
            
            self.logger.info(f"Captured {len(queries)} DNS queries, {len(suspicious_queries)} suspicious")
            return list(self.query_history)[-10:]  # Return recent queries
            
        except Exception as e:
            self.logger.error(f"DNS capture error: {e}")
            return []
    
    def _resolve_dns(self, domain):
        """Resolve domain to IP address"""
        try:
            return socket.gethostbyname(domain)
        except socket.gaierror:
            return "Unresolvable"
    
    def get_suspicious_activity(self):
        """Get recent suspicious DNS activity"""
        return [q for q in self.query_history if q['suspicious']]
    
    def start_monitoring(self):
        """Start continuous monitoring"""
        self._monitoring = True
        self.logger.info("DNS monitoring started")
        
        def monitor():
            while self._monitoring:
                self.capture_dns_queries()
                time.sleep(self.watch_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("DNS monitoring stopped")
