#!/bin/bash
echo "========================================="
echo "Learnify Student Services Status"
echo "========================================="
echo ""

# Check Backend
if lsof -i :3003 > /dev/null 2>&1; then
    echo "✓ Backend (Port 3003): RUNNING"
    curl -s http://localhost:3003/ | head -1
    if [ -f /home/learnify/learnify-stud/backend/backend.pid ]; then
        echo "  PID: $(cat /home/learnify/learnify-stud/backend/backend.pid)"
    fi
else
    echo "✗ Backend (Port 3003): NOT RUNNING"
fi

echo ""

# Check Frontend
if lsof -i :3004 > /dev/null 2>&1; then
    echo "✓ Frontend (Port 3004): RUNNING"
    if [ -f /home/learnify/learnify-stud/frontend/frontend.pid ]; then
        echo "  PID: $(cat /home/learnify/learnify-stud/frontend/frontend.pid)"
    fi
else
    echo "✗ Frontend (Port 3004): NOT RUNNING"
fi

echo ""
echo "========================================="
echo "Log Files:"
echo "  Backend: /home/learnify/learnify-stud/backend/backend.log"
echo "  Frontend: /home/learnify/learnify-stud/frontend/frontend.log"
echo "  Monitor: /home/learnify/learnify-stud/monitor.log"
echo "========================================="
