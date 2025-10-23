#!/bin/bash
cd /home/learnify/learnify-stud/backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null && echo "Backend stopped" || echo "Backend not running"
    rm -f backend.pid
else
    echo "No backend PID file found"
fi
