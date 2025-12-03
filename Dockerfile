# Stage 1: builder
FROM python:3.11-slim AS builder
WORKDIR /app
COPY app/requirements.txt .
RUN apt-get update && apt-get install -y build-essential && \
    python -m pip install --upgrade pip && \
    pip install --prefix=/install -r requirements.txt && \
    apt-get purge -y --auto-remove build-essential && rm -rf /var/lib/apt/lists/*

# Stage 2: runtime
FROM python:3.11-slim
ENV TZ=UTC
WORKDIR /app

# system deps for cron
RUN apt-get update && apt-get install -y cron tzdata && \
    ln -snf /usr/share/zoneinfo/Etc/UTC /etc/localtime && echo UTC > /etc/timezone && \
    rm -rf /var/lib/apt/lists/*

# copy installed packages from builder
COPY --from=builder /install /usr/local

# copy app and scripts
COPY app/ /app
COPY student_private.pem /app/student_private.pem
COPY student_public.pem /app/student_public.pem
COPY instructor_public.pem /app/instructor_public.pem
COPY scripts/ /app/scripts
COPY cron/2fa-cron /etc/cron.d/2fa-cron

# permissions and crontab
RUN chmod 0644 /etc/cron.d/2fa-cron && crontab /etc/cron.d/2fa-cron && \
    mkdir -p /data /cron && chmod 755 /data /cron

EXPOSE 8080

CMD service cron start && uvicorn main:app --host 0.0.0.0 --port 8080
