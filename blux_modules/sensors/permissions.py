"""
Enhanced permissions sensor: track changes in file or app permissions with security analysis
"""

import os
import time
import threading
import stat
from pathlib import Path
from datetime import datetime
import logging

class PermissionSensor:
    def __init__(self, watch_paths=None, check_interval=30):
        self.watch_paths = watch_paths or ["/tmp", "/usr/bin", "/etc"]
        self.check_interval = check_interval
        self.permission_history = {}
        self.suspicious_permissions = {
            'world_writable': 0o002,  # Files writable by anyone
            'setuid': stat.S_ISUID,   # SetUID files
            'setgid': stat.S_ISGID,   # SetGID files
        }
        self.logger = logging.getLogger('blux.sensors.permissions')
        self._monitoring = False
    
    def check_permissions(self, path=None):
        """Check permissions for specified path or all watch paths"""
        results = []
        
        paths_to_check = [path] if path else self.watch_paths
        
        for check_path in paths_to_check:
            if not os.path.exists(check_path):
                self.logger.warning(f"Watch path does not exist: {check_path}")
                continue
                
            try:
                if os.path.isfile(check_path):
                    results.extend(self._analyze_file_permissions(check_path))
                else:
                    # Scan directory (limit depth and count for performance)
                    for root, dirs, files in os.walk(check_path):
                        for file in files[:50]:  # Limit files per directory
                            full_path = os.path.join(root, file)
                            results.extend(self._analyze_file_permissions(full_path))
                        break  # Only top level for performance
                        
            except PermissionError as e:
                self.logger.error(f"Permission denied: {check_path} - {e}")
            except Exception as e:
                self.logger.error(f"Error scanning {check_path}: {e}")
        
        # Log summary
        suspicious_count = len([r for r in results if r.get('suspicious', False)])
        self.logger.info(f"Permission scan: {len(results)} files, {suspicious_count} suspicious")
        
        return results
    
    def _analyze_file_permissions(self, file_path):
        """Analyze file permissions for security issues"""
        try:
            file_stat = os.stat(file_path)
            permissions = file_stat.st_mode
            current_perms = oct(permissions)[-3:]
            
            analysis = {
                'path': file_path,
                'permissions': current_perms,
                'numeric_perms': permissions,
                'owner': file_stat.st_uid,
                'group': file_stat.st_gid,
                'size': file_stat.st_size,
                'timestamp': datetime.now(),
                'suspicious': False,
                'issues': []
            }
            
            # Check for suspicious permission patterns
            if permissions & self.suspicious_permissions['world_writable']:
                analysis['suspicious'] = True
                analysis['issues'].append('world_writable')
                self.logger.warning(f"World-writable file: {file_path} ({current_perms})")
            
            if permissions & self.suspicious_permissions['setuid']:
                analysis['suspicious'] = True
                analysis['issues'].append('setuid')
                self.logger.warning(f"SetUID file: {file_path} ({current_perms})")
            
            if permissions & self.suspicious_permissions['setgid']:
                analysis['suspicious'] = True
                analysis['issues'].append('setgid')
                self.logger.warning(f"SetGID file: {file_path} ({current_perms})")
            
            # Track permission changes
            self._track_permission_changes(file_path, analysis)
            
            return [analysis]
            
        except Exception as e:
            self.logger.error(f"Error analyzing {file_path}: {e}")
            return []
    
    def _track_permission_changes(self, file_path, current_analysis):
        """Track changes in file permissions over time"""
        file_key = file_path
        
        if file_key in self.permission_history:
            previous = self.permission_history[file_key]
            if previous['permissions'] != current_analysis['permissions']:
                self.logger.warning(
                    f"Permission change detected: {file_path} "
                    f"from {previous['permissions']} to {current_analysis['permissions']}"
                )
        
        self.permission_history[file_key] = current_analysis
    
    def find_suspicious_permissions(self):
        """Find files with suspicious permissions"""
        all_results = self.check_permissions()
        return [result for result in all_results if result['suspicious']]
    
    def start_monitoring(self):
        """Start continuous permission monitoring"""
        self._monitoring = True
        self.logger.info("Permission monitoring started")
        
        def monitor():
            while self._monitoring:
                self.check_permissions()
                time.sleep(self.check_interval)
        
        thread = threading.Thread(target=monitor, daemon=True)
        thread.start()
        return thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.logger.info("Permission monitoring stopped")
