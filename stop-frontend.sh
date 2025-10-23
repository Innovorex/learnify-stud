#!/bin/bash
cd /home/learnify/learnify-stud/frontend
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null && echo "Frontend stopped" || echo "Frontend not running"
    rm -f frontend.pid
else
    echo "No frontend PID file found"
fi
