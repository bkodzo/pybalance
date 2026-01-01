# Load Testing PyBalance

This guide shows you how to test your load balancer under realistic conditions.

## Quick Tests

### Basic Test Script
```bash
./test_scenarios.sh
```

This runs:
- Round-robin verification
- Concurrent requests
- High volume test
- Metrics check

### Python Load Tester (Advanced)

**Install dependencies:**
```bash
pip3 install requests
```

**Run comprehensive tests:**
```bash
python3 load_test.py
```

## Test Scenarios

### 1. Round-Robin Distribution

Verify requests are evenly distributed:
```bash
for i in {1..15}; do
  curl -s http://localhost:8080 | grep "Backend Server"
  sleep 0.1
done
```

**Expected:** Requests cycle through Server 1, 2, 3, 1, 2, 3...

### 2. Concurrent Requests

Simulate multiple users hitting the load balancer simultaneously:
```bash
python3 load_test.py concurrent 100 10
```
- 100 total requests
- 10 concurrent connections

**What to observe:**
- All requests complete successfully
- Even distribution across backends
- Response times remain reasonable

### 3. Sustained Load

Simulate steady traffic over time:
```bash
python3 load_test.py sustained 60 20
```
- Run for 60 seconds
- 20 requests per second

**What to observe:**
- Consistent throughput
- Stable response times
- No errors under sustained load

### 4. Burst Test

Simulate traffic spike (e.g., flash sale):
```bash
python3 load_test.py burst 100
```
- 100 simultaneous requests

**What to observe:**
- Load balancer handles burst gracefully
- All requests complete
- Response times may increase but stay reasonable

### 5. Fault Tolerance Test

Test automatic failover:

**Step 1:** Stop a backend
```bash
docker-compose stop backend1
```

**Step 2:** Wait 6 seconds (health check interval)

**Step 3:** Make requests
```bash
for i in {1..10}; do
  curl -s http://localhost:8080 | grep "Backend Server"
done
```

**Expected:** Only Server 2 and Server 3 receive requests

**Step 4:** Restart backend
```bash
docker-compose start backend1
```

**Step 5:** Wait 6 seconds, then make requests again

**Expected:** Server 1 is back in rotation

### 6. Performance Metrics

Check metrics during/after load:
```bash
curl http://localhost:8080/metrics | python3 -m json.tool
```

**What to check:**
- `requests_total`: Total requests handled
- `requests_per_second`: Throughput
- `backends[].requests`: Distribution per server
- `errors_total`: Should be low/zero

## Using Apache Bench (if available)

Apache Bench provides detailed performance metrics:

```bash
# Install (macOS)
brew install httpd

# Run test
ab -n 1000 -c 10 http://localhost:8080/

# Parameters:
# -n: Total number of requests
# -c: Concurrent requests
```

**Output includes:**
- Requests per second
- Time per request
- Transfer rate
- Connection times

## Real-World Scenarios

### Scenario 1: E-commerce Site (Normal Traffic)
```bash
python3 load_test.py sustained 300 5
```
- 5 requests/second for 5 minutes
- Simulates normal shopping traffic

### Scenario 2: News Site (Traffic Spike)
```bash
python3 load_test.py burst 500
```
- 500 simultaneous requests
- Simulates breaking news traffic spike

### Scenario 3: API Service (Steady Load)
```bash
python3 load_test.py sustained 600 50
```
- 50 requests/second for 10 minutes
- Simulates API with steady usage

### Scenario 4: Gradual Ramp-Up
```bash
# Start with low load, gradually increase
for rate in 5 10 20 30 50; do
  echo "Testing at $rate req/sec..."
  python3 load_test.py sustained 10 $rate
  sleep 2
done
```

## What to Monitor

### During Tests

1. **Load Balancer Logs**
   - Watch for errors
   - Check request distribution
   - Monitor health check messages

2. **Metrics Endpoint**
   ```bash
   watch -n 1 'curl -s http://localhost:8080/metrics | python3 -m json.tool'
   ```

3. **System Resources**
   ```bash
   # CPU and Memory
   top -pid $(pgrep -f "python3 main.py")
   ```

### Key Metrics

- **Throughput**: Requests per second
- **Latency**: Response time (p50, p95, p99)
- **Error Rate**: Should be < 1%
- **Distribution**: Even across backends
- **Recovery Time**: How fast it detects dead servers

## Expected Performance

On modern hardware, you should see:
- **Throughput**: 1000+ requests/second
- **Latency**: < 10ms per request (p95)
- **Concurrent Connections**: 1000+ handled smoothly
- **Error Rate**: < 0.1% under normal load

## Troubleshooting

### High Error Rate
- Check backend health: `docker-compose ps`
- Check backend logs: `docker-compose logs backend1`
- Verify health monitor is running

### Uneven Distribution
- Check routing algorithm in `config.py`
- Verify all backends are alive
- Check for network issues

### Slow Response Times
- Check system resources (CPU, memory)
- Verify backends can handle load
- Check for network bottlenecks
- Consider building C++ extension for performance

## Advanced: Stress Testing

Push the system to its limits:

```bash
# Find breaking point
python3 load_test.py concurrent 10000 100

# Sustained high load
python3 load_test.py sustained 300 100
```

**Goal:** Find maximum sustainable throughput before errors increase.

## Interpreting Results

### Good Results
- Even distribution across backends
- Low error rate (< 1%)
- Consistent response times
- High throughput
- Automatic recovery from failures

### Warning Signs
- Uneven distribution (one server overloaded)
- Increasing error rate under load
- Response times degrading
- Health monitor not detecting failures
- Memory/CPU usage climbing

## Next Steps

After load testing:
1. Document your findings
2. Identify bottlenecks
3. Optimize if needed (C++ extension)
4. Test different routing algorithms
5. Test with different backend configurations

