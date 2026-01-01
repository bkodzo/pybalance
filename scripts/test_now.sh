#!/bin/bash
# Quick test script for PyBalance

echo "PyBalance Quick Test"
echo "======================"
echo ""

# Check if load balancer is running
if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "ERROR: Load balancer is not running on port 8080"
    echo ""
    echo "Please start it first:"
    echo "  python3 -m src.main"
    exit 1
fi

echo "Load balancer is running"
echo ""

# Test 1: Round-robin
echo "Test 1: Round-Robin Distribution"
echo "--------------------------------"
for i in {1..6}; do
    response=$(curl -s -H "Cache-Control: no-cache" http://localhost:8080 2>&1)
    if echo "$response" | grep -q "Backend Server 1"; then
        server="Server 1"
    elif echo "$response" | grep -q "Backend Server 2"; then
        server="Server 2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="Server 3"
    else
        server="Error"
    fi
    printf "  Request %d → %s\n" $i "$server"
    sleep 0.3
done

echo ""
echo "Test 2: Metrics Endpoint"
echo "----------------------"
echo ""
metrics=$(curl -s http://localhost:8080/metrics 2>&1)

if echo "$metrics" | grep -q "requests_total"; then
    echo "$metrics" | python3 -m json.tool 2>/dev/null || echo "$metrics"
else
    echo "ERROR: Metrics endpoint not working"
    echo "Response: $metrics"
fi

echo ""
echo "Test complete!"
echo ""
echo "Try these commands:"
echo "  - View metrics: curl http://localhost:8080/metrics | python3 -m json.tool"
echo "  - Make request: curl http://localhost:8080"
echo "  - Open in browser: http://localhost:8080"

