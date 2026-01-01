"""
Module B: The Health Monitor
Continuously checks backend server health in the background.
"""

import socket
import threading
import time
import logging
from typing import List
from router import Router, Server


logger = logging.getLogger(__name__)


class HealthMonitor:
    """Monitors backend server health and updates router accordingly."""
    
    def __init__(self, router: Router, check_interval: int = 5, timeout: int = 2):
        self.router = router
        self.check_interval = check_interval  # seconds
        self.timeout = timeout  # seconds
        self.running = False
        self.thread = None
    
    def start(self):
        """Start the health monitoring thread."""
        if self.running:
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        logger.info("Health monitor started")
    
    def stop(self):
        """Stop the health monitoring thread."""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        logger.info("Health monitor stopped")
    
    def _monitor_loop(self):
        """Main monitoring loop running in background thread."""
        while self.running:
            try:
                with self.router.lock:
                    servers = self.router.servers.copy()
                
                for server in servers:
                    is_alive = self._check_server_health(server)
                    
                    if is_alive and not server.is_alive:
                        self.router.mark_server_alive(server.host, server.port)
                        logger.info(f"Server {server.host}:{server.port} is now ALIVE")
                    elif not is_alive and server.is_alive:
                        self.router.mark_server_dead(server.host, server.port)
                        logger.warning(f"Server {server.host}:{server.port} is now DEAD")
                
            except Exception as e:
                logger.error(f"Error in health monitor loop: {e}")
            
            time.sleep(self.check_interval)
    
    def _check_server_health(self, server: Server) -> bool:
        """Check if a server is healthy using TCP connect."""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            result = sock.connect_ex((server.host, server.port))
            sock.close()
            return result == 0
        except Exception as e:
            logger.debug(f"Health check failed for {server.host}:{server.port}: {e}")
            return False

