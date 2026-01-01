"""
Module C: The Proxy Engine
Handles the actual proxying of requests and responses.
"""

import asyncio
import logging
import time
from typing import Optional, Tuple
from .router import Router, Server

# Try to import C++ extension for performance boost
try:
    import proxy_cpp
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False

logger = logging.getLogger(__name__)

if CPP_AVAILABLE:
    logger.info("C++ extension loaded - using high-performance byte operations")
else:
    logger.debug("C++ extension not available - using pure Python implementation")


class ProxyEngine:
    """Handles proxying requests to backend servers."""
    
    def __init__(self, router: Router, metrics=None):
        self.router = router
        self.metrics = metrics
    
    async def handle_client(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        """Handle a client connection by proxying to backend."""
        client_addr = writer.get_extra_info('peername')
        client_ip = client_addr[0] if client_addr else None
        
        if self.metrics:
            self.metrics.increment_connections()
        
        try:
            request_data = await asyncio.wait_for(reader.read(8192), timeout=10.0)
            
            if not request_data:
                return
            
            request_str = request_data.decode('utf-8', errors='ignore')
            if request_str.startswith('GET /metrics'):
                await self._handle_metrics(writer)
                return
            
            url_path = None
            if CPP_AVAILABLE:
                try:
                    method, path = proxy_cpp.parse_http_header(list(request_data))
                    url_path = path
                except Exception:
                    pass
            
            if not url_path and request_str:
                for line in request_str.split('\n'):
                    if line.startswith('GET ') or line.startswith('POST ') or line.startswith('PUT '):
                        parts = line.split()
                        if len(parts) > 1:
                            url_path = parts[1].split('?')[0]
                        break
            
            if client_ip and request_str:
                for line in request_str.split('\n'):
                    if line.startswith('X-Forwarded-For:'):
                        client_ip = line.split(':', 1)[1].strip()
                        break
            
            backend = self.router.select_server(client_ip, url_path)
            
            if backend and self.router.algorithm.value == "least_connections":
                self.router.increment_connections(backend.host, backend.port)
            
            if not backend:
                logger.error("No healthy backend servers available")
                writer.write(b"HTTP/1.1 503 Service Unavailable\r\n\r\n")
                await writer.drain()
                return
            
            logger.info(f"Proxying request from {client_ip} to {backend.host}:{backend.port}")
            
            request_start_time = time.time()
            success = await self._proxy_request(request_data, backend, reader, writer)
            request_duration = time.time() - request_start_time
            
            if backend and self.router.algorithm.value == "least_connections":
                self.router.decrement_connections(backend.host, backend.port)
            
            if backend and success:
                self.router.record_response_time(backend.host, backend.port, request_duration)
            
            if self.metrics:
                if success:
                    self.metrics.record_request(backend)
                else:
                    self.metrics.record_error(backend)
            
        except asyncio.TimeoutError:
            logger.warning(f"Request timeout from {client_ip}")
            if self.metrics:
                self.metrics.record_error()
        except Exception as e:
            logger.error(f"Error handling client {client_ip}: {e}")
            if self.metrics:
                self.metrics.record_error()
        finally:
            if self.metrics:
                self.metrics.decrement_connections()
            writer.close()
            await writer.wait_closed()
    
    async def _handle_metrics(self, writer: asyncio.StreamWriter):
        """Handle /metrics endpoint request."""
        import json
        
        if not self.metrics:
            writer.write(b"HTTP/1.1 503 Service Unavailable\r\n\r\n")
            await writer.drain()
            return
        
        stats = self.metrics.get_stats()
        json_data = json.dumps(stats, indent=2)
        
        response = f"HTTP/1.1 200 OK\r\n"
        response += f"Content-Type: application/json\r\n"
        response += f"Content-Length: {len(json_data)}\r\n"
        response += f"\r\n{json_data}"
        
        writer.write(response.encode())
        await writer.drain()
    
    async def _proxy_request(
        self,
        request_data: bytes,
        backend: Server,
        client_reader: asyncio.StreamReader,
        client_writer: asyncio.StreamWriter
    ) -> bool:
        """Proxy request to backend and response back to client. Returns True if successful."""
        backend_reader = None
        backend_writer = None
        success = False
        
        try:
            backend_reader, backend_writer = await asyncio.wait_for(
                asyncio.open_connection(backend.host, backend.port),
                timeout=5.0
            )
            
            if CPP_AVAILABLE and len(request_data) > 4096:
                try:
                    optimized_data = bytes(proxy_cpp.fast_copy(list(request_data)))
                    backend_writer.write(optimized_data)
                except Exception:
                    backend_writer.write(request_data)
            else:
                backend_writer.write(request_data)
            await backend_writer.drain()
            
            while True:
                chunk = await asyncio.wait_for(
                    backend_reader.read(4096),
                    timeout=30.0
                )
                
                if not chunk:
                    break
                
                if CPP_AVAILABLE and len(chunk) > 1024:
                    try:
                        optimized_chunk = bytes(proxy_cpp.fast_copy(list(chunk)))
                        client_writer.write(optimized_chunk)
                    except Exception:
                        client_writer.write(chunk)
                else:
                    client_writer.write(chunk)
                await client_writer.drain()
            
            success = True
        
        except asyncio.TimeoutError:
            logger.warning(f"Backend {backend.host}:{backend.port} timeout")
            if not client_writer.is_closing():
                client_writer.write(b"HTTP/1.1 504 Gateway Timeout\r\n\r\n")
                await client_writer.drain()
        except Exception as e:
            logger.error(f"Error proxying to {backend.host}:{backend.port}: {e}")
            if not client_writer.is_closing():
                client_writer.write(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
                await client_writer.drain()
        finally:
            if backend_writer:
                backend_writer.close()
                await backend_writer.wait_closed()
        
        return success

