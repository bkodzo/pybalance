# PyBalance Code Structure

This document explains the codebase structure and how to navigate it.

## Directory Structure

```
LoadBalancer/
│
├── src/                     # Core application source code
│   ├── __init__.py         # Package initialization
│   ├── main.py             # Entry point, orchestrates all components
│   ├── router.py           # Request routing and algorithm implementation
│   ├── proxy.py            # Async proxy engine for request forwarding
│   ├── health_monitor.py   # Background health checking
│   ├── metrics.py          # Metrics collection and reporting
│   ├── config.py          # Centralized configuration
│   └── proxy_cpp.cpp      # C++ extension for high-performance operations
│
├── tests/                  # Test files
│   ├── load_test.py        # Load testing script
│   └── test_load_balancer.py # Unit tests
│
├── scripts/                # Utility scripts
│   ├── start.sh            # Start Docker backends
│   ├── stop.sh             # Stop Docker backends
│   ├── test_algorithms.sh  # Test routing algorithm distribution
│   ├── test_now.sh         # Quick verification test
│   ├── demo.sh             # Full demonstration
│   └── clean_start.sh      # Kill all processes for fresh start
│
├── docs/                   # Documentation
│   ├── ARCHITECTURE.md      # Design decisions and rationale
│   ├── CODE_STRUCTURE.md   # This file
│   ├── CONTRIBUTING.md     # Contribution guidelines
│   ├── ROUTING_ALGORITHMS.md # Algorithm explanations
│   ├── LOAD_TESTING.md     # Testing guide
│   └── BUILD_CPP.md        # C++ extension build guide
│
├── test_backends/          # Backend test files
│   ├── backend1/           # HTML files for backend 1
│   ├── backend2/           # HTML files for backend 2
│   └── backend3/           # HTML files for backend 3
│
├── README.md               # Main documentation
├── LICENSE                 # MIT License
├── requirements.txt        # Python dependencies
├── docker-compose.yml      # Docker Compose configuration
├── setup.py                # Build script for C++ extension
└── Makefile               # Build commands
```

## Core Modules Explained

### main.py

**Purpose**: Entry point and orchestrator.

**Key Components**:
- `LoadBalancer` class: Main orchestrator
- Initializes Router, HealthMonitor, ProxyEngine, Metrics
- Handles graceful shutdown (SIGINT, SIGTERM)
- Sets up async server

**Entry Point**:
```python
if __name__ == "__main__":
    asyncio.run(main())
```

**Flow**:
1. Create LoadBalancer instance
2. Setup servers from config
3. Start health monitor
4. Start async server
5. Serve forever

### router.py

**Purpose**: Request routing and server selection.

**Key Classes**:
- `RoutingAlgorithm`: Enum of available algorithms
- `Server`: Represents a backend server
- `Router`: Main routing logic

**Key Methods**:
- `select_server()`: Selects server based on algorithm
- `add_server()`: Adds backend to pool
- `get_alive_servers()`: Returns only healthy servers
- Algorithm implementations: `_round_robin()`, `_random()`, etc.

**Thread Safety**:
- Uses `threading.Lock` for all operations
- Prevents race conditions between health monitor and proxy engine

### proxy.py

**Purpose**: Async request forwarding.

**Key Components**:
- `ProxyEngine` class: Handles client connections
- Async I/O using `asyncio`
- Optional C++ extension for performance

**Key Methods**:
- `handle_client()`: Main request handler (async)
- `_proxy_request()`: Forwards request to backend
- `_handle_metrics()`: Serves metrics endpoint

**Flow**:
1. Accept client connection
2. Read request data
3. Parse HTTP headers
4. Select backend via router
5. Forward request to backend
6. Stream response back to client
7. Close connection

**Error Handling**:
- Timeouts: 504 Gateway Timeout
- Connection failures: 502 Bad Gateway
- No backends: 503 Service Unavailable

### health_monitor.py

**Purpose**: Background health monitoring.

**Key Components**:
- `HealthMonitor` class: Runs in background thread
- Periodic TCP health checks
- Updates server status in router

**Key Methods**:
- `start()`: Start monitoring thread
- `stop()`: Stop monitoring thread
- `_monitor_loop()`: Main monitoring loop
- `_check_server_health()`: TCP connect check

**Flow**:
1. Start background thread
2. Every N seconds (configurable):
   - Check each server via TCP connect
   - Update server status (alive/dead)
   - Log status changes
3. Continue until stopped

### metrics.py

**Purpose**: Metrics collection and reporting.

**Key Components**:
- `Metrics` class: Thread-safe metrics tracking
- Tracks requests, errors, connections
- Provides JSON endpoint

**Key Methods**:
- `record_request()`: Increment request count
- `record_error()`: Increment error count
- `increment_connections()`: Track active connections
- `get_metrics()`: Return JSON metrics

**Metrics Tracked**:
- Total requests
- Requests per backend
- Total errors
- Errors per backend
- Active connections
- Uptime
- Requests per second

### config.py

**Purpose**: Centralized configuration.

**Settings**:
- `LISTEN_HOST`, `LISTEN_PORT`: Load balancer address
- `BACKEND_SERVERS`: List of backend servers
- `ROUTING_ALGORITHM`: Algorithm to use
- `HEALTH_CHECK_INTERVAL`: Health check frequency
- `HEALTH_CHECK_TIMEOUT`: Health check timeout
- `LOG_LEVEL`: Logging verbosity

**Usage**:
```python
import config
# Access settings
config.LISTEN_PORT
config.BACKEND_SERVERS
```

## Data Flow

### Request Flow

```
Client Request
    ↓
main.py (async server accepts)
    ↓
proxy.py (handle_client)
    ↓
router.py (select_server)
    ↓
proxy.py (forward to backend)
    ↓
Backend Server
    ↓
proxy.py (stream response)
    ↓
Client Response
```

### Health Check Flow

```
health_monitor.py (background thread)
    ↓
Every N seconds:
    ↓
For each server:
    ↓
TCP connect check
    ↓
Update router.py (server.is_alive)
    ↓
Log status changes
```

## Key Design Patterns

### 1. Separation of Concerns

Each module has a single, clear responsibility:
- `router.py`: Routing logic only
- `proxy.py`: Request forwarding only
- `health_monitor.py`: Health checking only
- `metrics.py`: Metrics only

### 2. Dependency Injection

Components receive dependencies via constructor:
```python
def __init__(self, router: Router, metrics: Metrics):
    self.router = router
    self.metrics = metrics
```

### 3. Thread Safety

Shared state protected with locks:
```python
with self.lock:
    # Critical section
    # Update shared state
```

### 4. Graceful Degradation

C++ extension is optional:
```python
try:
    import proxy_cpp
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    # Fall back to pure Python
```

## Adding New Features

### Adding a Routing Algorithm

1. Add to `RoutingAlgorithm` enum in `router.py`
2. Implement algorithm method: `_new_algorithm()`
3. Add case in `select_server()`
4. Update documentation

### Adding a New Endpoint

1. Add check in `proxy.py` `handle_client()`
2. Implement handler method
3. Return appropriate response

### Adding Metrics

1. Add tracking in `metrics.py`
2. Update `get_metrics()` to include new metric
3. Update documentation

## Testing Structure

### Unit Tests

- `test_load_balancer.py`: Unit tests for components
- Test individual functions and classes

### Integration Tests

- `test_running.py`: Test full system
- `test_algorithms.sh`: Test routing algorithms
- `load_test.py`: Performance testing

### Manual Testing

- `test_now.sh`: Quick verification
- `demo.sh`: Full demonstration
- `test_scenarios.sh`: Various scenarios

## Performance Considerations

### Critical Paths

1. **Request Handling**: `proxy.py` `handle_client()`
   - Optimized with async I/O
   - C++ extension for byte operations

2. **Server Selection**: `router.py` `select_server()`
   - Fast algorithm implementations
   - Minimal lock contention

3. **Health Checks**: `health_monitor.py`
   - Runs in background, doesn't block requests
   - Fast TCP connect checks

### Optimization Opportunities

1. **Connection Pooling**: Reuse backend connections
2. **Caching**: Cache parsed headers
3. **Zero-Copy**: Use C++ extension for large transfers
4. **Batch Operations**: Batch health checks if needed

## Code Quality

### Documentation

- Docstrings for all classes and methods
- Comments explain "why", not "what"
- First-person comments ("I parse...")

### Error Handling

- Appropriate HTTP status codes
- Graceful error handling
- Comprehensive logging

### Type Hints

- Used where appropriate
- Improves code clarity
- Helps with IDE support

---


