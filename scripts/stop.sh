#!/bin/bash
# Stop script for PyBalance

echo "Stopping PyBalance..."

# Stop Docker containers
echo "Stopping backend containers..."
docker-compose down

echo ""
echo "All services stopped!"
echo ""
echo "To start again, run: ./start.sh"

