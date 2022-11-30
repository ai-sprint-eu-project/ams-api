# syntax=docker/dockerfile:1

ARG WORKER_NUM=5

FROM python:3.10-alpine
RUN pip --no-cache-dir install "connexion[flask]>=2,<3" "influxdb-client>=1,<2" "pyuwsgi>=2,<3"
RUN mkdir /app
WORKDIR /app

LABEL org.opencontainers.image.title="AMS REST API" \
    org.opencontainers.image.description="AI-SPRINT Monitoring Subsystem (AMS) RESTful API" \
    org.opencontainers.image.version="1.0" \
    org.opencontainers.image.authors="Michał Soczewka" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/ai-sprint-eu-project/monitoring-subsystem" \
    org.opencontainers.image.documentation="https://github.com/ai-sprint-eu-project/monitoring-subsystem"

ADD api.yaml app.py _constants.py _util.py .
CMD ["uwsgi", "--uid=65534",\
     "--http=0.0.0.0:8000", "--master",\
     "-p", "${WORKER_NUM}",\
     "-w", "app:app"]
