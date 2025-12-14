#!/bin/sh
# docker-entrypoint.sh
set -e

# Start cron daemon in the foreground, or use a robust background start
# This command starts cron and keeps it running
# Using 'service cron start' is common on Debian/Ubuntu, but 'cron -f' is better for container entrypoint if possible.
# Sticking to your original for consistency, but adding an explicit start.
echo "Starting cron service..."
/usr/sbin/cron -f & # Start cron in the background and keep it running

echo "Starting FastAPI server..."
# exec uvicorn runs uvicorn as the main process, which is good practice.
# app.main:app assumes main.py contains the FastAPI instance named 'app'.
exec uvicorn app.main:app --host 0.0.0.0 --port 8080