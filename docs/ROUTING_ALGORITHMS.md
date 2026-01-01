# Routing Algorithms in PyBalance

PyBalance supports multiple routing algorithms, each optimized for different use cases.

## Available Algorithms

### 1. Round Robin
**Algorithm:** `ROUND_ROBIN`

**How it works:**
- Cycles through servers sequentially
- Request 1 → Server A, Request 2 → Server B, Request 3 → Server C, repeat

**Best for:**
- Servers with equal capacity
- Simple, predictable distribution
- General purpose load balancing

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.ROUND_ROBIN
```

### 2. Weighted Round Robin
**Algorithm:** `WEIGHTED_ROUND_ROBIN`

**How it works:**
- Distributes requests based on server weights
- Server with weight=4 gets 4x more requests than weight=1
- Automatically balances over time

**Best for:**
- Servers with different capacities
- Mixed hardware (powerful + weak servers)
- When you want proportional distribution

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.WEIGHTED_ROUND_ROBIN

BACKEND_SERVERS = [
    {"host": "localhost", "port": 5003, "weight": 4},  # Powerful server
    {"host": "localhost", "port": 5001, "weight": 1},  # Weak server
    {"host": "localhost", "port": 5002, "weight": 1},  # Weak server
]
```

### 3. IP Hash
**Algorithm:** `IP_HASH`

**How it works:**
- Hashes client IP address
- Same IP always hits same server
- Ensures session affinity

**Best for:**
- Stateful applications
- Session-based caching
- When you need sticky sessions

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.IP_HASH
```

**Note:** If a server dies, its clients are redistributed (may lose sessions).

### 4. Least Connections
**Algorithm:** `LEAST_CONNECTIONS`

**How it works:**
- Routes to server with fewest active connections
- Dynamically adapts to current load
- Tracks connections in real-time

**Best for:**
- Long-lived connections
- Servers with varying response times
- When connection duration varies significantly
- WebSocket connections

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.LEAST_CONNECTIONS
```

**How it works internally:**
- Tracks active connections per server
- Increments on request start
- Decrements on request completion
- Always selects server with minimum connections

### 5. Random
**Algorithm:** `RANDOM`

**How it works:**
- Randomly selects a server for each request
- Simple and fast
- Good for testing

**Best for:**
- Testing and development
- When distribution doesn't matter
- Simple scenarios

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.RANDOM
```

### 6. URL Hash
**Algorithm:** `URL_HASH`

**How it works:**
- Hashes the URL path
- Same URL always hits same server
- Useful for caching scenarios

**Best for:**
- Content caching (CDN-like behavior)
- When you want URL-based routing
- Cache efficiency

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.URL_HASH
```

**Use case:**
- `/images/photo.jpg` always goes to Server A
- `/images/logo.png` always goes to Server B
- Each server caches its URLs, improving hit rate

### 7. Consistent Hash
**Algorithm:** `CONSISTENT_HASH`

**How it works:**
- Uses consistent hashing algorithm
- Better distribution than simple hash
- Handles server additions/removals better
- Minimal redistribution when servers change

**Best for:**
- Distributed systems
- When servers are frequently added/removed
- Cache clusters
- Better than IP_HASH for dynamic environments

**Example:**
```python
ROUTING_ALGORITHM = RoutingAlgorithm.CONSISTENT_HASH
```

**Advantages over IP_HASH:**
- Better hash distribution
- Less disruption when servers change
- More even load distribution

## Algorithm Comparison

| Algorithm | Complexity | Best For | Session Affinity | Dynamic Load |
|-----------|-----------|----------|------------------|--------------|
| Round Robin | Low | Equal servers | No | No |
| Weighted RR | Medium | Mixed capacity | No | No |
| IP Hash | Low | Stateful apps | Yes | No |
| Least Connections | Medium | Long connections | No | Yes |
| Random | Low | Testing | No | No |
| URL Hash | Low | Caching | Yes (by URL) | No |
| Consistent Hash | Medium | Distributed systems | Yes | Better |

## When to Use Each

### Use Round Robin when:
- All servers are equal
- You want simple, predictable behavior
- Request duration is similar

### Use Weighted Round Robin when:
- Servers have different capacities
- You want proportional distribution
- Hardware is mixed

### Use IP Hash when:
- You need session affinity
- Stateful applications
- Simple sticky sessions

### Use Least Connections when:
- Connections are long-lived
- Response times vary
- WebSocket connections
- Real-time load balancing needed

### Use Random when:
- Testing
- Distribution doesn't matter
- Simple scenarios

### Use URL Hash when:
- Content caching is important
- CDN-like behavior needed
- Cache hit rate matters

### Use Consistent Hash when:
- Servers change frequently
- Distributed cache systems
- Better than IP_HASH for dynamic environments

## Configuration

Edit `config.py`:

```python
from router import RoutingAlgorithm

ROUTING_ALGORITHM = RoutingAlgorithm.LEAST_CONNECTIONS  # Change this
```

## Testing Different Algorithms

1. Change algorithm in `config.py`
2. Restart load balancer
3. Run load test: `python3 load_test.py concurrent 100 10`
4. Check metrics: `curl http://localhost:8080/metrics`
5. Observe distribution in metrics output

## Performance Notes

- **Round Robin / Weighted RR**: O(1) - fastest
- **IP Hash / URL Hash**: O(1) - very fast
- **Random**: O(1) - very fast
- **Least Connections**: O(n) where n=servers - still very fast
- **Consistent Hash**: O(n log n) - slightly slower but still fast

All algorithms are efficient enough for production use.

