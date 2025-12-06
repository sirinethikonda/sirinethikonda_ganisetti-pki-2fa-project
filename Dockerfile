FROM python:3.11-slim AS builder
WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --prefix=/install -r requirements.txt

FROM python:3.11-slim
WORKDIR /app
ENV TZ=UTC

RUN apt-get update && apt-get install -y cron tzdata

COPY --from=builder /install /usr/local

COPY app /app/app
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY docker-entrypoint.sh /app/docker-entrypoint.sh
COPY app/cron/2fa-cron /etc/cron.d/2fa-cron

RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron
RUN mkdir -p /data /cron

EXPOSE 8080
ENTRYPOINT ["/app/docker-entrypoint.sh"]
