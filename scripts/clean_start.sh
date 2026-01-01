#!/bin/bash
# Clean start script - kills all PyBalance processes

echo "Cleaning up all PyBalance processes..."
echo "========================================"
echo ""

# Stop load balancer
echo "1. Stopping load balancer..."
pkill -f "python3 -m src.main" 2>/dev/null
sleep 1

# Stop Python backends
echo "2. Stopping Python backend servers..."
sleep 1

# Stop Docker containers
echo "3. Stopping Docker containers..."
docker-compose down 2>/dev/null
sleep 1

# Kill processes on ports
echo "4. Freeing ports..."
for port in 8080 5000 5001 5002; do
    lsof -ti :$port | xargs kill -9 2>/dev/null
done
sleep 2

# Verify
echo ""
echo "5. Verifying cleanup..."
echo ""
all_clear=true

for port in 8080 5000 5001 5002; do
    if lsof -i :$port > /dev/null 2>&1; then
        echo "   WARNING: Port $port still in use"
        all_clear=false
    else
        echo "   Port $port is free"
    fi
done

if ps aux | grep -E "python3 -m src.main" | grep -v grep > /dev/null; then
    echo "   WARNING: Python processes still running"
    all_clear=false
else
    echo "   No Python processes running"
fi

if docker-compose ps 2>/dev/null | grep -q "Up"; then
    echo "   WARNING: Docker containers still running"
    all_clear=false
else
    echo "   No Docker containers running"
fi

echo ""
if [ "$all_clear" = true ]; then
    echo "CLEAN SLATE ACHIEVED!"
else
    echo "WARNING: Some processes may still be running (check manually)"
fi

echo ""
echo "Ready to start fresh:"
echo "  1. ./start.sh          (start Docker backends)"
echo "  2. python3 -m src.main     (start load balancer in new terminal)"
echo "  3. ./test_now.sh       (test it)"

