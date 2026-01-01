"""
Metrics tracking for PyBalance.
Tracks request statistics and server health.
"""

import threading
import time
from typing import Dict, List
from collections import defaultdict
from .router import Router, Server


class Metrics:
    """Tracks metrics for the load balancer."""
    
    def __init__(self, router: Router):
        self.router = router
        self.requests_total = 0
        self.requests_per_server: Dict[str, int] = defaultdict(int)
        self.errors_total = 0
        self.errors_per_server: Dict[str, int] = defaultdict(int)
        self.start_time = time.time()
        self.active_connections = 0
        self.lock = threading.Lock()
    
    def record_request(self, server: Server):
        """Record a successful request to a server."""
        with self.lock:
            self.requests_total += 1
            server_key = f"{server.host}:{server.port}"
            self.requests_per_server[server_key] += 1
    
    def record_error(self, server: Server = None):
        """Record an error."""
        with self.lock:
            self.errors_total += 1
            if server:
                server_key = f"{server.host}:{server.port}"
                self.errors_per_server[server_key] += 1
    
    def increment_connections(self):
        """Increment active connection count."""
        with self.lock:
            self.active_connections += 1
    
    def decrement_connections(self):
        """Decrement active connection count."""
        with self.lock:
            self.active_connections = max(0, self.active_connections - 1)
    
    def get_stats(self) -> Dict:
        """Get current statistics."""
        with self.router.lock:
            servers = self.router.servers.copy()
        
        uptime = time.time() - self.start_time
        
        with self.lock:
            backend_stats = []
            for server in servers:
                server_key = f"{server.host}:{server.port}"
                backend_stats.append({
                    "host": server.host,
                    "port": server.port,
                    "status": "alive" if server.is_alive else "dead",
                    "weight": server.weight,
                    "requests": self.requests_per_server.get(server_key, 0),
                    "errors": self.errors_per_server.get(server_key, 0)
                })
        
        return {
            "uptime_seconds": int(uptime),
            "requests_total": self.requests_total,
            "errors_total": self.errors_total,
            "active_connections": self.active_connections,
            "requests_per_second": round(self.requests_total / uptime, 2) if uptime > 0 else 0,
            "routing_algorithm": self.router.algorithm.value,
            "backends": backend_stats
        }

