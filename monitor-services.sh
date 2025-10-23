#!/bin/bash
# Monitor and restart services if they're down

check_and_restart_backend() {
    if ! lsof -i :3003 > /dev/null 2>&1; then
        echo "[$(date)] Backend is down, restarting..."
        cd /home/learnify/learnify-stud
        ./start-backend.sh
    fi
}

check_and_restart_frontend() {
    if ! lsof -i :3004 > /dev/null 2>&1; then
        echo "[$(date)] Frontend is down, restarting..."
        cd /home/learnify/learnify-stud
        ./start-frontend.sh
    fi
}

check_and_restart_backend
check_and_restart_frontend
