FROM python:3.12-slim-bookworm

LABEL maintainer="ThalynnX" \
      org.opencontainers.image.title="QwenPaw" \
      org.opencontainers.image.description="QwenPaw 本地优先个人 AI 助手（多架构镜像，由 ThalynnX 编译发布）" \
      org.opencontainers.image.vendor="ThalynnX" \
      org.opencontainers.image.source="https://github.com/ThalynnX/qwenpaw-fpk" \
      org.opencontainers.image.licenses="Apache-2.0"

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    QWENPAW_WORKING_DIR=/data/.qwenpaw \
    QWENPAW_AUTH_ENABLED=true \
    TZ=Asia/Shanghai

WORKDIR /opt/qwenpaw
COPY code/ /opt/qwenpaw/
COPY docker-entrypoint.sh /opt/qwenpaw/docker-entrypoint.sh
RUN chmod +x /opt/qwenpaw/docker-entrypoint.sh \
 && pip install --no-cache-dir . \
 && rm -rf /root/.cache/pip

EXPOSE 19091
VOLUME ["/data"]
ENTRYPOINT ["/opt/qwenpaw/docker-entrypoint.sh"]
CMD ["python3", "-m", "qwenpaw", "app", "--host", "0.0.0.0", "--port", "19091"]
