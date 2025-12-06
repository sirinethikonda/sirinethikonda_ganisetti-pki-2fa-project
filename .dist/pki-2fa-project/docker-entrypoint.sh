#!/bin/bash
service cron start

uvicorn app.main:app --host 0.0.0.0 --port 8080

COPY docker-entrypoint.sh /app/docker-entrypoint.sh
RUN chmod +x /app/docker-entrypoint.sh
