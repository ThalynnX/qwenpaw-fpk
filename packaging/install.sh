#!/usr/bin/env bash
# QwenPaw 通用 Linux 一键安装脚本（Debian/Ubuntu/Armbian/CentOS 通用）
# 由 ThalynnX 打包发布：https://github.com/ThalynnX/qwenpaw-fpk
set -euo pipefail

PREFIX="${PREFIX:-/opt/qwenpaw}"
DATA_DIR="${DATA_DIR:-/var/lib/qwenpaw}"
PORT="${PORT:-19091}"
SERVICE="qwenpaw"
USER_NAME="qwenpaw"

msg() { printf "\033[32m[QWENPAW]\033[0m %s\n" "$*"; }
die() { printf "\033[31m[QWENPAW]\033[0m %s\n" "$*" >&2; exit 1; }

[ "$(id -u)" = "0" ] || die "请用 root 执行：sudo bash install.sh"
command -v python3 >/dev/null 2>&1 || die "缺少 python3，请先安装（apt install -y python3 python3-venv）"

SRC_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
[ -f "$SRC_DIR/code/pyproject.toml" ] || [ -f "$SRC_DIR/code/setup.py" ] || die "安装包内容不完整（缺少 code/）"

msg "目标目录: $PREFIX  数据目录: $DATA_DIR  端口: $PORT"

id "$USER_NAME" >/dev/null 2>&1 || { msg "创建系统用户 $USER_NAME"; useradd --system --home "$DATA_DIR" --shell /usr/sbin/nologin "$USER_NAME" 2>/dev/null || true; }

msg "复制程序文件到 $PREFIX"
mkdir -p "$PREFIX"
cp -a "$SRC_DIR/code/." "$PREFIX/"
[ -d "$SRC_DIR/console" ] && mkdir -p "$PREFIX/console" && cp -a "$SRC_DIR/console/." "$PREFIX/console/" || true
mkdir -p "$DATA_DIR/.qwenpaw"
chown -R "$USER_NAME":"$USER_NAME" "$DATA_DIR" 2>/dev/null || true

msg "创建独立虚拟环境并安装依赖（需要能访问 PyPI）"
python3 -m venv "$PREFIX/venv" 2>/dev/null || die "创建 venv 失败，请先安装 python3-venv"
"$PREFIX/venv/bin/pip" install -q --upgrade pip
if [ -d "$SRC_DIR/wheels" ] && [ -n "$(ls -A "$SRC_DIR/wheels" 2>/dev/null)" ]; then
  msg "使用离线 wheels 目录安装"
  "$PREFIX/venv/bin/pip" install -q --no-cache-dir --no-index --find-links "$SRC_DIR/wheels" "$PREFIX"
else
  "$PREFIX/venv/bin/pip" install -q --no-cache-dir "$PREFIX"
fi

msg "写入 systemd 服务"
cat > "/etc/systemd/system/${SERVICE}.service" <<UNIT
[Unit]
Description=QwenPaw personal AI assistant
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=${USER_NAME}
Group=${USER_NAME}
WorkingDirectory=${PREFIX}
Environment=QWENPAW_WORKING_DIR=${DATA_DIR}/.qwenpaw
Environment=QWENPAW_AUTH_ENABLED=true
Environment=PYTHONUNBUFFERED=1
ExecStart=${PREFIX}/venv/bin/python -m qwenpaw app --host 0.0.0.0 --port ${PORT}
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

systemctl daemon-reload
systemctl enable --now "$SERVICE" >/dev/null 2>&1 || systemctl restart "$SERVICE"
sleep 2
systemctl is-active --quiet "$SERVICE" && msg "服务已启动" || msg "服务未正常运行，查看日志：journalctl -u $SERVICE -n 50"

msg "安装完成"
echo "  访问地址: http://<本机IP>:${PORT}"
echo "  数据目录: ${DATA_DIR}/.qwenpaw"
echo "  服务管理: systemctl {status|restart|stop} ${SERVICE}"
echo "  查看日志: journalctl -u ${SERVICE} -f"
echo "  卸载命令: bash ${PREFIX}/uninstall.sh"
