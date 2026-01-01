#!/bin/bash
# Realistic load balancer test scenarios

set -e

LB_URL="http://localhost:8080"

echo "PyBalance Load Balancer Test Scenarios"
echo "========================================"
echo ""

# Check if load balancer is running
if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "ERROR: Load balancer is not running on port 8080"
    echo "Please start it first: python3 -m src.main"
    exit 1
fi

echo "Load balancer is running"
echo ""

# Scenario 1: Basic Round-Robin Verification
echo "Scenario 1: Round-Robin Distribution"
echo "------------------------------------"
echo "Making 15 sequential requests to verify distribution:"
echo ""

for i in {1..15}; do
    response=$(curl -s $LB_URL 2>/dev/null)
    if echo "$response" | grep -q "Backend Server 1"; then
        server="Server 1"
    elif echo "$response" | grep -q "Backend Server 2"; then
        server="Server 2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="Server 3"
    else
        server="Unknown"
    fi
    printf "  Request %2d → %s\n" $i "$server"
    sleep 0.1
done

echo ""

# Scenario 2: Concurrent Requests
echo "Scenario 2: Concurrent Requests (Simulating Multiple Users)"
echo "-----------------------------------------------------------"
echo "Making 30 concurrent requests..."
echo ""

start_time=$(date +%s.%N)

for i in {1..30}; do
    (curl -s $LB_URL > /dev/null 2>&1 && echo "Request $i completed") &
done

wait
end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)

echo "All 30 concurrent requests completed in ${duration} seconds"
echo ""

# Scenario 3: High Volume Test
echo "Scenario 3: High Volume Test"
echo "----------------------------"
echo "Making 100 requests as fast as possible..."
echo ""

start_time=$(date +%s.%N)
success=0
errors=0

for i in {1..100}; do
    if curl -s -o /dev/null -w "%{http_code}" $LB_URL | grep -q "200"; then
        success=$((success + 1))
    else
        errors=$((errors + 1))
    fi
    if [ $((i % 20)) -eq 0 ]; then
        echo "  Progress: $i/100 requests"
    fi
done

end_time=$(date +%s.%N)
duration=$(echo "$end_time - $start_time" | bc)
rps=$(echo "scale=2; 100 / $duration" | bc)

echo "  Completed: 100 requests in ${duration} seconds"
echo "  Success: $success, Errors: $errors"
echo "  Throughput: ${rps} requests/second"
echo ""

# Scenario 4: Check Metrics After Load
echo "Scenario 4: Metrics After Load Test"
echo "-----------------------------------"
echo "Checking metrics endpoint:"
echo ""

curl -s $LB_URL/metrics | python3 -m json.tool | head -30

echo ""

# Scenario 5: Fault Tolerance Test
echo "Scenario 5: Fault Tolerance (Stop a Backend)"
echo "----------------------------------------------"
echo "This test requires manual intervention:"
echo "  1. Stop a backend: docker-compose stop backend1"
echo "  2. Wait 6 seconds for health monitor to detect"
echo "  3. Make requests - should only hit backend2 and backend3"
echo "  4. Restart: docker-compose start backend1"
echo "  5. Wait 6 seconds - backend1 should be back in rotation"
echo ""

echo "All scenarios complete!"
echo ""
echo "For advanced load testing, use:"
echo "  python3 load_test.py concurrent 200 20"
echo "  python3 load_test.py sustained 60 50"
echo "  python3 load_test.py burst 100"

