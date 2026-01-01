"""
PyBalance - A Fault-Tolerant Application Layer Load Balancer
Main entry point.
"""

import asyncio
import logging
import signal
import sys
from router import Router, RoutingAlgorithm
from health_monitor import HealthMonitor
from proxy import ProxyEngine
from metrics import Metrics
import config


logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LoadBalancer:
    """Main load balancer orchestrator."""
    
    def __init__(self):
        self.router = Router(algorithm=config.ROUTING_ALGORITHM)
        self.metrics = Metrics(self.router)
        self.health_monitor = HealthMonitor(
            self.router,
            check_interval=config.HEALTH_CHECK_INTERVAL,
            timeout=config.HEALTH_CHECK_TIMEOUT
        )
        self.proxy_engine = ProxyEngine(self.router, self.metrics)
        self.server = None
    
    def setup_servers(self):
        """Add backend servers to router."""
        for server_config in config.BACKEND_SERVERS:
            self.router.add_server(
                server_config["host"],
                server_config["port"],
                server_config.get("weight", 1)
            )
            logger.info(f"Added backend server: {server_config['host']}:{server_config['port']}")
    
    async def start(self):
        """Start the load balancer."""
        self.setup_servers()
        self.health_monitor.start()
        
        self.server = await asyncio.start_server(
            self.proxy_engine.handle_client,
            config.LISTEN_HOST,
            config.LISTEN_PORT
        )
        
        addr = self.server.sockets[0].getsockname()
        logger.info(f"PyBalance listening on {addr[0]}:{addr[1]}")
        logger.info(f"Routing algorithm: {config.ROUTING_ALGORITHM.value}")
        logger.info(f"Backend servers: {len(config.BACKEND_SERVERS)}")
        logger.info(f"Metrics endpoint: http://{addr[0]}:{addr[1]}/metrics")
        
        async with self.server:
            await self.server.serve_forever()
    
    def stop(self):
        """Stop the load balancer."""
        logger.info("Shutting down PyBalance...")
        self.health_monitor.stop()
        if self.server:
            self.server.close()


    async def main():
    """Main entry point."""
    lb = LoadBalancer()
    
    def signal_handler(sig, frame):
        logger.info("Received shutdown signal")
        lb.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        await lb.start()
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
        lb.stop()


if __name__ == "__main__":
    asyncio.run(main())

