#!/usr/bin/env bash
set -euo pipefail
PREFIX="${PREFIX:-/opt/qwenpaw}"
SERVICE=qwenpaw
[ "$(id -u)" = "0" ] || { echo "请用 root 执行"; exit 1; }
systemctl disable --now "$SERVICE" >/dev/null 2>&1 || true
rm -f "/etc/systemd/system/${SERVICE}.service"
systemctl daemon-reload
id qwenpaw >/dev/null 2>&1 && userdel qwenpaw 2>/dev/null || true
echo "已停止并移除服务。程序目录 $PREFIX 与数据 /var/lib/qwenpaw 已保留，需要彻底删除请手动 rm -rf。"
