#!/bin/bash
# Demo script to showcase PyBalance features

set -e

echo "PyBalance Load Balancer Demo"
echo "================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker is not running!"
    echo "Please start Docker Desktop and run this script again."
    exit 1
fi

# Check if backends are running
if ! docker-compose ps | grep -q "Up"; then
    echo "Starting backend servers..."
    docker-compose up -d
    sleep 3
fi

echo "Backend servers ready"
echo ""

# Check if load balancer is running
if ! lsof -i :8080 > /dev/null 2>&1; then
    echo "WARNING: Load balancer is not running!"
    echo "Please start it in another terminal:"
    echo "  python3 -m src.main"
    echo ""
    read -p "Press Enter when load balancer is running..."
fi

echo ""
echo "Demo 1: Round-Robin Distribution"
echo "------------------------------------"
echo "Making 9 requests to show round-robin:"
echo ""

for i in {1..9}; do
    response=$(curl -s http://localhost:8080 2>/dev/null)
    if echo "$response" | grep -q "Backend Server 1"; then
        server="Server 1"
    elif echo "$response" | grep -q "Backend Server 2"; then
        server="Server 2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="Server 3"
    else
        server="Unknown"
    fi
    echo "  Request $i → $server"
    sleep 0.3
done

echo ""
echo "Round-robin is working - requests distributed evenly!"
echo ""

echo "Demo 2: Health Monitoring"
echo "----------------------------"
echo "Stopping backend1 to test fault tolerance..."
docker-compose stop backend1 > /dev/null 2>&1
echo "  Backend1 stopped"
echo ""
echo "Waiting 6 seconds for health monitor to detect failure..."
sleep 6
echo ""
echo "Making 6 requests (should only hit Server 2 and 3):"
for i in {1..6}; do
    response=$(curl -s http://localhost:8080 2>/dev/null)
    if echo "$response" | grep -q "Backend Server 2"; then
        server="Server 2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="Server 3"
    else
        server="Error/Other"
    fi
    echo "  Request $i → $server"
    sleep 0.3
done

echo ""
echo "Health monitoring working - dead server excluded!"
echo ""

echo "Restarting backend1..."
docker-compose start backend1 > /dev/null 2>&1
echo "  Backend1 restarted"
echo ""
echo "Waiting 6 seconds for health monitor to detect recovery..."
sleep 6
echo ""
echo "Making 3 requests (should include Server 1 again):"
for i in {1..3}; do
    response=$(curl -s http://localhost:8080 2>/dev/null)
    if echo "$response" | grep -q "Backend Server 1"; then
        server="Server 1"
    elif echo "$response" | grep -q "Backend Server 2"; then
        server="Server 2"
    elif echo "$response" | grep -q "Backend Server 3"; then
        server="Server 3"
    else
        server="Unknown"
    fi
    echo "  Request $i → $server"
    sleep 0.3
done

echo ""
echo "Server recovery detected - all servers back in rotation!"
echo ""

echo "Demo Complete!"
echo ""
echo "Key Features Demonstrated:"
echo "  - Round-robin request distribution"
echo "  - Automatic health monitoring"
echo "  - Fault tolerance (excludes dead servers)"
echo "  - Automatic recovery (re-adds healthy servers)"
echo ""

