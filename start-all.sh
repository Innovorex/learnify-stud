#!/bin/bash
cd /home/learnify/learnify-stud

# Stop any existing processes
./stop-backend.sh
./stop-frontend.sh

# Wait a moment
sleep 2

# Start services
./start-backend.sh
./start-frontend.sh

echo ""
echo "Services started! Check status with:"
echo "  lsof -i :3003 -i :3004"
