#!/bin/sh
set -e
mkdir -p "$QWENPAW_WORKING_DIR"
# 数据目录权限自愈（宿主机挂载场景）
[ -w "$QWENPAW_WORKING_DIR" ] || chown -R "$(id -u):$(id -g)" "$QWENPAW_WORKING_DIR" 2>/dev/null || true
exec "$@"
