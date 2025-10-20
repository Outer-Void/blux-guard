"""
Enhanced filesystem sensor: monitor file creation/modification with integrity checking
"""

import os
import time
import hashlib
import threading
from pathlib import Path
from datetime import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

class FileSystemSensor(FileSystemEventHandler):
    def __init__(self, watch_dirs=None, scan_interval=30):
        self.watch_dirs = watch_dirs or ["/tmp", "/home/test"]
        self.scan_interval = scan_interval
        self.file_hashes = {}
        self.suspicious_extensions = {'.exe', '.bat', '.sh', '.py'}
        self.logger = logging.getLogger('blux.sensors.filesystem')
        self.observer = Observer()
        self._monitoring = False
        
    def on_created(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            self._analyze_file(file_path)
    
    def on_modified(self, event):
        if not event.is_directory:
            file_path = Path(event.src_path)
            if file_path.exists():
                self._analyze_file(file_path)
    
    def _analyze_file(self, file_path):
        """Analyze file for potential threats"""
        try:
            stats = file_path.stat()
            file_info = {
                'path': str(file_path),
                'size': stats.st_size,
                'modified': datetime.fromtimestamp(stats.st_mtime),
                'extension': file_path.suffix.lower()
            }
            
            # Check for suspicious characteristics
            if file_info['extension'] in self.suspicious_extensions:
                self.logger.warning(f"Suspicious file created: {file_path}")
            
            # Calculate file hash for integrity monitoring
            file_hash = self._calculate_file_hash(file_path)
            if str(file_path) in self.file_hashes:
                if self.file_hashes[str(file_path)] != file_hash:
                    self.logger.warning(f"File modified: {file_path}")
            
            self.file_hashes[str(file_path)] = file_hash
            self.logger.info(f"File activity: {file_path}")
            
        except Exception as e:
            self.logger.error(f"File analysis error: {e}")
    
    def _calculate_file_hash(self, file_path):
        """Calculate SHA-256 hash of file"""
        try:
            hasher = hashlib.sha256()
            with open(file_path, 'rb') as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception:
            return "unknown"
    
    def scan_filesystem(self):
        """Perform full filesystem scan"""
        all_files = []
        for watch_dir in self.watch_dirs:
            if os.path.exists(watch_dir):
                for root, dirs, files in os.walk(watch_dir):
                    for file in files[:100]:  # Limit for performance
                        full_path = os.path.join(root, file)
                        all_files.append(full_path)
        
        self.logger.info(f"Scanned {len(all_files)} files in watch directories")
        return all_files[:20]  # Return sample for demo
    
    def start_monitoring(self):
        """Start filesystem monitoring"""
        self._monitoring = True
        
        # Start watchdog observer
        for directory in self.watch_dirs:
            if os.path.exists(directory):
                self.observer.schedule(self, directory, recursive=True)
        
        self.observer.start()
        self.logger.info("Filesystem monitoring started")
        
        # Background scanning thread
        def background_scan():
            while self._monitoring:
                self.scan_filesystem()
                time.sleep(self.scan_interval)
        
        scan_thread = threading.Thread(target=background_scan, daemon=True)
        scan_thread.start()
        
        return self.observer, scan_thread
    
    def stop_monitoring(self):
        """Stop monitoring"""
        self._monitoring = False
        self.observer.stop()
        self.observer.join()
        self.logger.info("Filesystem monitoring stopped")
