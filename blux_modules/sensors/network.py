"""
Enhanced network sensor: tracks flows and remote connections with threat detection
"""

import time
import threading
import socket
from datetime import datetime
from collections import defaultdict, deque
import logging
import psutil  # Requires: pip install psutil

class NetworkSensor:
    def __init__(self, check_interval=5, max_history=1000):
        self.check_interval = check_interval
        self.connection_history = deque(maxlen=max_history)
        self.suspicious_ips = {"8.8.8.8", "1.1.1.1"}  # Example suspicious IPs
        self.port_scan_threshold = 10  # Connections per minute
        self.connection_rates = defaultdict(list)
        self.logger = logging.getLogger('blux.sensors.network')
        self._monitoring = False
    
    def scan_network_flows(self):
        """Scan active network connections with security analysis"""
        try:
            connections = []
            suspicious_flows = []
            
            # Use psutil to get real network connections
            for conn in psutil.net_connections(kind='inet'):
                if conn.status == 'ESTABLISHED':
                    flow = {
                        'src_ip': conn.laddr.ip if conn.laddr else 'unknown',
                        'src_port': conn.laddr.port if conn.laddr else 0,
                        'dst_ip': conn.raddr.ip if conn.raddr else 'unknown',
                        'dst_port': conn.raddr.port if conn.raddr else 0,
                        'pid': conn.pid or 'unknown',
                        'timestamp': datetime.now()
                    }
                    
                    connections.append(flow)
                    
                    # Security analysis
                    if self._is_suspicious_flow(flow):
                        suspicious_flows.append(flow)
                        self.logger.warning(f"Suspicious network flow: {flow}")
            
            # Log connection statistics
            unique_ips = len(set(flow['dst_ip'] for flow in connections))
            self.logger.info(f"Found {len(connections)} established connections to {unique_ips} unique IPs")
            
            # Update connection rates for anomaly detection
            self._update_connection_rates(connections)
            
            result = {
                'total_connections': len(connections),
                'suspicious_flows': suspicious_flows,
                'sample_connections': connections[:10],  # Return sample for performance
                'timestamp': datetime.now()
            }
            
            self.connection_history.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"Network scan error: {e}")
            return {'total_connections': 0, 'suspicious_flows': [], 'sample_connections': []}
    
    def _is_suspicious_flow(self, flow):
        """Determine if a network flow is suspicious"""
        # Check against known suspicious IPs
        if flow['dst_ip'] in self.suspicious_ips:
            return True
        
        # Check for unusual destination ports
        suspicious_ports = {22, 23, 3389, 5900}  # SSH, Telnet, RDP, VNC
        if flow['dst_port'] in suspicious_ports:
            return True
        
        # Check for connections to private IPs from unexpected processes
        if flow['dst_ip'].startswith('10.') or flow['dst_ip'].startswith('192.168.'):
            # Add additional logic for internal network monitoring
            pass
            
        return False
    
    def _update_connection_rates(self, connections):
        """Update connection rates for anomaly detection"""
        current_time = time.time()
        
        for flow in connections:
            dst_ip = flow['dst_ip']
            self.connection_rates[dst_ip].append(current_time)
            
            # Remove old entries (older than 1 minute)
            self.connection_rates[dst_ip] = [
                ts for ts in self.connection_rates[dst_ip] 
                if current_time - ts < 60
            ]
            
            # Check for port scanning behavior
            if len(self.connection_rates[dst_ip]) > self.port_scan_threshold:
                self.logger.warning(f"Possible port scanning detected from {dst_ip}")
    
    def get_network_statistics(self):
        """Get comprehensive network statistics"""
        flows = self.scan_network_flows()
        
        stats = {
            'total_connections': flows['total_connections'],
            'suspicious_connections': len(flows['suspicious_flows']),
            'unique_destinations': len(set(f['dst_ip'] for f in flows['sample_connections'])),
            'common_ports': self._get_common_ports(flows['sample_connections']),
            'timestamp': datetime.now()
        }
        
        return stats
    
    def _get_common_ports(self, connections):
        """Get most common destination ports"""
        from collections import Counter
        ports = [conn['dst_port'] for conn in connections if conn['dst_port'] > 0]
        return Counter(ports).most_common(5)
    
    def start_monitoring(self):
        """Start continuous network monitoring"""
        self._monitoring = True
        self.logger.info("Network monitoring started")
        
        def monitor():
            while self._monitoring:
                self.scan_network_flows()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("Network monitoring stopped")
