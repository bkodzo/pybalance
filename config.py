"""
Configuration settings for PyBalance.
"""

from router import RoutingAlgorithm


# Load balancer settings
LISTEN_HOST = "0.0.0.0"
LISTEN_PORT = 8080

# Backend servers
BACKEND_SERVERS = [
    {"host": "localhost", "port": 5003, "weight": 5},
    {"host": "localhost", "port": 5001, "weight": 1},
    {"host": "localhost", "port": 5002, "weight": 1},
]

# Routing algorithm
ROUTING_ALGORITHM = RoutingAlgorithm.RANDOM

# Health check settings
HEALTH_CHECK_INTERVAL = 5  # seconds
HEALTH_CHECK_TIMEOUT = 2   # seconds

# Logging
LOG_LEVEL = "INFO"

