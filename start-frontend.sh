#!/bin/bash
cd /home/learnify/learnify-stud/frontend
nohup npm run dev > frontend.log 2>&1 &
echo $! > frontend.pid
echo "Frontend started on port 3004 (PID: $(cat frontend.pid))"
