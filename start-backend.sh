#!/bin/bash
cd /home/learnify/learnify-stud/backend
source venv/bin/activate
nohup uvicorn main:app --host 0.0.0.0 --port 3003 > backend.log 2>&1 &
echo $! > backend.pid
echo "Backend started on port 3003 (PID: $(cat backend.pid))"
