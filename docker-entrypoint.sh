#!/bin/sh
set -e

echo "Starting cron service..."
/usr/sbin/cron -f & 

echo "Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8080