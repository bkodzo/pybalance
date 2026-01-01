#!/bin/bash
# Test different routing algorithms

LB_URL="http://localhost:8080"

echo "Testing Routing Algorithms"
echo "=========================="
echo ""

if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "ERROR: Load balancer is not running"
    echo "Please start it first: python3 -m src.main"
    exit 1
fi

echo "Current algorithm: Check config.py"
echo ""

echo "Test: Making 15 requests to see distribution"
echo "--------------------------------------------"

servers=()
for i in {1..15}; do
    timestamp=$(date +%s%N)
    response=$(curl -s -H "Cache-Control: no-cache" -H "Pragma: no-cache" "$LB_URL?t=$timestamp" 2>&1)
    server="?"
    if echo "$response" | grep -q "Backend Server 1"; then
        server="1"
    elif echo "$response" | grep -q "Backend Server 2"; then
        server="2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="3"
    fi
    servers+=($server)
    printf "Request %2d → Server %s\n" $i "$server"
    sleep 0.2
done

echo ""
echo "Distribution:"
count1=0
count2=0
count3=0
for s in "${servers[@]}"; do
    if [ "$s" = "1" ]; then
        count1=$((count1 + 1))
    elif [ "$s" = "2" ]; then
        count2=$((count2 + 1))
    elif [ "$s" = "3" ]; then
        count3=$((count3 + 1))
    fi
done
echo "  Server 1: $count1"
echo "  Server 2: $count2"
echo "  Server 3: $count3"
echo ""

echo "To test different algorithms:"
echo "  1. Edit config.py"
echo "  2. Change ROUTING_ALGORITHM to:"
echo "     - RoutingAlgorithm.LEAST_CONNECTIONS"
echo "     - RoutingAlgorithm.RANDOM"
echo "     - RoutingAlgorithm.URL_HASH"
echo "     - RoutingAlgorithm.CONSISTENT_HASH"
echo "  3. Restart load balancer"
echo "  4. Run this script again"

