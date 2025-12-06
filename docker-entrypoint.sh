#!/bin/sh
# start cron and then start the FastAPI server
service cron start 2>/dev/null || true
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
