# Stage 1: Builder
FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
# Install dependencies into a separate directory
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim
WORKDIR /app
ENV TZ=UTC

# Install system dependencies
RUN apt-get update \
    && apt-get install -y cron tzdata procps \
    && rm -rf /var/lib/apt/lists/*

# Copy installed dependencies from builder
COPY --from=builder /install /usr/local

# Copy application code and keys
COPY app /app/app
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY docker-entrypoint.sh /app/docker-entrypoint.sh

# Setup cron
# CRITICAL: Copy cron file to /etc/cron.d (corrected path based on your folder structure)
COPY app/cron/2fa-cron /etc/cron.d/2fa-cron
RUN chmod 0644 /etc/cron.d/2fa-cron \
    && crontab /etc/cron.d/2fa-cron # Not strictly needed if copied to /etc/cron.d, but harmless

# Create volume mount points
RUN mkdir -p /data /cron \
    && chmod 755 /data /cron

EXPOSE 8080
# CRITICAL: Entrypoint file must be executable
RUN chmod +x /app/docker-entrypoint.sh
ENTRYPOINT ["/app/docker-entrypoint.sh"]