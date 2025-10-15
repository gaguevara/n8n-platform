FROM n8nio/n8n:latest

USER root
RUN apk add --no-cache tzdata wget && \
    cp /usr/share/zoneinfo/America/Bogota /etc/localtime && \
    echo "America/Bogota" > /etc/timezone
USER node
