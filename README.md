# PyBalance - A Fault-Tolerant Application Layer Load Balancer

A production-ready, fault-tolerant application layer (Layer 7) load balancer built in Python. PyBalance distributes HTTP traffic across multiple backend servers with intelligent routing, health monitoring, and high-performance async I/O.

## Features

- **7 Routing Algorithms**: Round Robin, Weighted Round Robin, IP Hash, Least Connections, Random, URL Hash, Consistent Hash
- **Health Monitoring**: Automatic TCP health checks with failover and recovery
- **High Performance**: Async I/O for thousands of concurrent connections
- **Fault Tolerance**: Automatic dead server detection and recovery
- **Observability**: Metrics endpoint (`/metrics`) with JSON output
- **Optional C++ Extension**: 2-3x speedup for large transfers

## Quick Start

### Prerequisites

- Python 3.7+
- Docker Desktop

### Installation

```bash
git clone https://github.com/bkodzo/pybalance.git
cd pybalance
```

### Running

**1. Start backend servers:**
```bash
./scripts/start.sh
```

**2. Start load balancer:**
```bash
python3 -m src.main
```

**3. Test it:**
```bash
curl http://localhost:8080
curl http://localhost:8080/metrics | python3 -m json.tool
```

**4. Stop everything:**
```bash
./scripts/stop.sh
```

## Configuration

Edit `src/config.py`:

```python
BACKEND_SERVERS = [
    {"host": "localhost", "port": 5003, "weight": 1},
    {"host": "localhost", "port": 5001, "weight": 1},
    {"host": "localhost", "port": 5002, "weight": 1},
]

ROUTING_ALGORITHM = RoutingAlgorithm.ROUND_ROBIN
```

Available algorithms: `ROUND_ROBIN`, `WEIGHTED_ROUND_ROBIN`, `IP_HASH`, `LEAST_CONNECTIONS`, `RANDOM`, `URL_HASH`, `CONSISTENT_HASH`

## Project Structure

```
pybalance/
├── src/              # Core application code
├── tests/            # Test files
├── scripts/          # Utility scripts
├── docs/             # Documentation
└── test_backends/    # Backend test files
```

## Testing

```bash
./scripts/test_algorithms.sh    # Test routing algorithms
./scripts/test_now.sh           # Quick verification
./scripts/demo.sh               # Full demonstration
python3 tests/load_test.py      # Load testing
```

## Documentation

- [Architecture](docs/ARCHITECTURE.md) - Design decisions and rationale
- [Routing Algorithms](docs/ROUTING_ALGORITHMS.md) - Algorithm explanations
- [Code Structure](docs/CODE_STRUCTURE.md) - Code navigation guide
- [Load Testing](docs/LOAD_TESTING.md) - Testing guide
- [Build C++ Extension](docs/BUILD_CPP.md) - C++ extension build guide

## License

MIT License - see [LICENSE](LICENSE) file for details.
