"""
Module A: The Request Router
Decides which backend server should handle each request.
"""

import hashlib
import threading
import random
import time
from typing import List, Dict, Optional
from enum import Enum


class RoutingAlgorithm(Enum):
    """Available routing algorithms."""
    ROUND_ROBIN = "round_robin"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    IP_HASH = "ip_hash"
    LEAST_CONNECTIONS = "least_connections"
    RANDOM = "random"
    URL_HASH = "url_hash"
    CONSISTENT_HASH = "consistent_hash"


class Server:
    """Represents a backend server."""
    
    def __init__(self, host: str, port: int, weight: int = 1):
        self.host = host
        self.port = port
        self.weight = weight
        self.is_alive = True
        self.current_weight = 0  # For weighted round-robin
        self.active_connections = 0  # For least connections
        self.response_times = []  # For least response time (keep last 10)
        self.avg_response_time = 0.0  # Cached average


class Router:
    """Routes requests to backend servers using various algorithms."""
    
    def __init__(self, algorithm: RoutingAlgorithm = RoutingAlgorithm.ROUND_ROBIN):
        self.algorithm = algorithm
        self.servers: List[Server] = []
        self.current_index = 0
        self.lock = threading.Lock()
    
    def add_server(self, host: str, port: int, weight: int = 1):
        """Add a backend server to the pool."""
        with self.lock:
            self.servers.append(Server(host, port, weight))
    
    def get_alive_servers(self) -> List[Server]:
        """Get list of currently alive servers."""
        with self.lock:
            return [s for s in self.servers if s.is_alive]
    
    def select_server(self, client_ip: Optional[str] = None, url_path: Optional[str] = None) -> Optional[Server]:
        """Select a server based on the routing algorithm."""
        with self.lock:
            alive_servers = [s for s in self.servers if s.is_alive]
            
            if not alive_servers:
                return None
            
            if self.algorithm == RoutingAlgorithm.ROUND_ROBIN:
                return self._round_robin(alive_servers)
            elif self.algorithm == RoutingAlgorithm.WEIGHTED_ROUND_ROBIN:
                return self._weighted_round_robin(alive_servers)
            elif self.algorithm == RoutingAlgorithm.IP_HASH:
                return self._ip_hash(alive_servers, client_ip)
            elif self.algorithm == RoutingAlgorithm.LEAST_CONNECTIONS:
                return self._least_connections(alive_servers)
            elif self.algorithm == RoutingAlgorithm.RANDOM:
                return self._random(alive_servers)
            elif self.algorithm == RoutingAlgorithm.URL_HASH:
                return self._url_hash(alive_servers, url_path)
            elif self.algorithm == RoutingAlgorithm.CONSISTENT_HASH:
                return self._consistent_hash(alive_servers, client_ip or url_path or "")
            else:
                return self._round_robin(alive_servers)
    
    def _round_robin(self, servers: List[Server]) -> Server:
        """Round-robin: cycle through servers sequentially."""
        server = servers[self.current_index % len(servers)]
        self.current_index = (self.current_index + 1) % len(servers)
        return server
    
    def _weighted_round_robin(self, servers: List[Server]) -> Server:
        """Weighted round-robin: distribute based on server weights."""
        max_weight_server = max(servers, key=lambda s: s.current_weight)
        
        total_weight = sum(s.weight for s in servers)
        for server in servers:
            server.current_weight += server.weight
        
        max_weight_server.current_weight -= total_weight
        
        return max_weight_server
    
    def _ip_hash(self, servers: List[Server], client_ip: Optional[str]) -> Server:
        """IP hashing: same client always hits same server."""
        if not client_ip:
            return self._round_robin(servers)
        
        hash_value = int(hashlib.md5(client_ip.encode()).hexdigest(), 16)
        index = hash_value % len(servers)
        return servers[index]
    
    def _least_connections(self, servers: List[Server]) -> Server:
        """Least connections: route to server with fewest active connections."""
        return min(servers, key=lambda s: s.active_connections)
    
    def _random(self, servers: List[Server]) -> Server:
        """Random: randomly select a server."""
        return random.choice(servers)
    
    def _url_hash(self, servers: List[Server], url_path: Optional[str]) -> Server:
        """URL hashing: same URL always hits same server (useful for caching)."""
        if not url_path:
            return self._round_robin(servers)
        
        hash_value = int(hashlib.md5(url_path.encode()).hexdigest(), 16)
        index = hash_value % len(servers)
        return servers[index]
    
    def _consistent_hash(self, servers: List[Server], key: str) -> Server:
        """Consistent hashing: better distribution than simple hash, handles server changes better."""
        if not key:
            return self._round_robin(servers)
        
        hash_value = int(hashlib.md5(key.encode()).hexdigest(), 16)
        
        server_hashes = []
        for server in servers:
            server_key = f"{server.host}:{server.port}"
            server_hash = int(hashlib.md5(server_key.encode()).hexdigest(), 16)
            server_hashes.append((server_hash, server))
        
        server_hashes.sort(key=lambda x: x[0])
        
        for server_hash, server in server_hashes:
            if server_hash >= hash_value:
                return server
        
        return server_hashes[0][1]
    
    def increment_connections(self, host: str, port: int):
        """Increment active connections for a server."""
        with self.lock:
            for server in self.servers:
                if server.host == host and server.port == port:
                    server.active_connections += 1
                    break
    
    def decrement_connections(self, host: str, port: int):
        """Decrement active connections for a server."""
        with self.lock:
            for server in self.servers:
                if server.host == host and server.port == port:
                    server.active_connections = max(0, server.active_connections - 1)
                    break
    
    def record_response_time(self, host: str, port: int, response_time: float):
        """Record response time for a server."""
        with self.lock:
            for server in self.servers:
                if server.host == host and server.port == port:
                    server.response_times.append(response_time)
                    if len(server.response_times) > 10:
                        server.response_times.pop(0)
                    if server.response_times:
                        server.avg_response_time = sum(server.response_times) / len(server.response_times)
                    break
    
    def mark_server_dead(self, host: str, port: int):
        """Mark a server as dead (called by health monitor)."""
        with self.lock:
            for server in self.servers:
                if server.host == host and server.port == port:
                    server.is_alive = False
                    break
    
    def mark_server_alive(self, host: str, port: int):
        """Mark a server as alive (called by health monitor)."""
        with self.lock:
            for server in self.servers:
                if server.host == host and server.port == port:
                    server.is_alive = True
                    break

