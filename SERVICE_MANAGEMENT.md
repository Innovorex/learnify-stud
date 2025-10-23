# Learnify Student Services Management

## Services Running 24/7

- **Backend**: Port 3003 (FastAPI/Uvicorn)
- **Frontend**: Port 3004 (Vite/React)

## Service Control Scripts

All scripts are located in `/home/learnify/learnify-stud/`

### Start/Stop Commands

```bash
# Start all services
./start-all.sh

# Stop all services
./stop-backend.sh
./stop-frontend.sh

# Start individual services
./start-backend.sh
./start-frontend.sh

# Check status
./status.sh
```

## Automatic Management

✓ **Auto-restart on reboot**: Services automatically start when server restarts
✓ **Auto-recovery**: Services are monitored every 5 minutes and restarted if down
✓ **Persistent**: Services run with `nohup` and continue even after SSH disconnect

## Monitoring

- **Monitor script**: Runs every 5 minutes via cron
- **Monitor log**: `/home/learnify/learnify-stud/monitor.log`
- **Backend log**: `/home/learnify/learnify-stud/backend/backend.log`
- **Frontend log**: `/home/learnify/learnify-stud/frontend/frontend.log`

## Cron Jobs

View cron configuration:
```bash
crontab -l
```

Current setup:
- `@reboot`: Starts services on server boot
- `*/5 * * * *`: Monitors and restarts services every 5 minutes if needed

## Manual Checks

```bash
# Check if ports are listening
lsof -i :3003 -i :3004

# Check running processes
ps aux | grep -E "(uvicorn|vite)"

# Test endpoints
curl http://localhost:3003/
curl http://localhost:3004/
```

## Service Details

### Backend (Port 3003)
- Framework: FastAPI
- Server: Uvicorn
- Working Dir: `/home/learnify/learnify-stud/backend`
- Virtual Env: `/home/learnify/learnify-stud/backend/venv`

### Frontend (Port 3004)
- Framework: React + Vite
- Working Dir: `/home/learnify/learnify-stud/frontend`
- Dev Server: Vite with HMR

## Notes

- Services will continue running after SSH disconnect (using nohup)
- Services will auto-restart if server reboots
- Services will auto-recover if they crash (checked every 5 minutes)
- Both services are configured for production use on `0.0.0.0`
