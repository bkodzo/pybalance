#!/bin/bash
# Startup script for PyBalance with Docker

set -e

echo "Starting PyBalance Load Balancer with Docker"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "ERROR: Docker daemon is not running!"
    echo ""
    echo "Please start Docker Desktop:"
    echo "  1. Open Docker Desktop application"
    echo "  2. Wait for it to fully start"
    echo "  3. Run this script again"
    exit 1
fi

echo "Docker is running"
echo ""

# Start backend containers
echo "Starting backend servers..."
docker-compose up -d

# Wait for containers to be ready
echo "Waiting for backends to be ready..."
sleep 3

# Verify backends
echo ""
echo "Verifying backends..."
for port in 5003 5001 5002; do
    if curl -s -o /dev/null -w "%{http_code}" http://localhost:$port | grep -q "200"; then
        echo "  Backend on port $port is ready"
    else
        echo "  WARNING: Backend on port $port not responding"
    fi
done

echo ""
echo "All backends started!"
echo ""
echo "Now start the load balancer in another terminal:"
echo "  python3 main.py"
echo ""
echo "Or test the backends directly:"
echo "  curl http://localhost:5003"
echo "  curl http://localhost:5001"
echo "  curl http://localhost:5002"

