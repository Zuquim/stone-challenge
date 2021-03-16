FROM python:3.8-alpine
ENV TZ America/Sao_Paulo
WORKDIR /opt/challenge
COPY . ./
RUN apk update && \
    apk add --virtual deps \
            gcc python3-dev linux-headers musl-dev postgresql-dev && \
    apk add --no-cache -U libpq make postgresql-dev tzdata && \
    ln /usr/share/zoneinfo/America/Sao_Paulo /etc/localtime && \
    pip install --no-cache-dir -U pip setuptools wheel && \
    pip install --no-cache-dir -r requirements.txt