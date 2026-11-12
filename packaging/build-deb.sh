#!/usr/bin/env bash
# 由 CI 调用：build-deb.sh <VERSION> <ARCH> <SRC_DIR> <OUT_DIR>
set -euo pipefail
VERSION="${1:?}"; ARCH="${2:?}"; SRC="${3:?}"; OUT="${4:?}"
STAGE="${SRC}/deb"
rm -rf "$STAGE"; mkdir -p "$STAGE/DEBIAN" "$STAGE/opt/qwenpaw" "$STAGE/lib/systemd/system" "$STAGE/usr/bin"

cp -a "$SRC/code/." "$STAGE/opt/qwenpaw/"
[ -d "$SRC/console" ] && mkdir -p "$STAGE/opt/qwenpaw/console" && cp -a "$SRC/console/." "$STAGE/opt/qwenpaw/console/"
cp -a "$SRC/install.sh" "$SRC/uninstall.sh" "$STAGE/opt/qwenpaw/"

cat > "$STAGE/lib/systemd/system/qwenpaw.service" <<UNIT
[Unit]
Description=QwenPaw personal AI assistant
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=qwenpaw
Group=qwenpaw
WorkingDirectory=/opt/qwenpaw
Environment=QWENPAW_WORKING_DIR=/var/lib/qwenpaw/.qwenpaw
Environment=QWENPAW_AUTH_ENABLED=true
Environment=PYTHONUNBUFFERED=1
ExecStart=/opt/qwenpaw/venv/bin/python -m qwenpaw app --host 0.0.0.0 --port 19091
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
UNIT

cat > "$STAGE/usr/bin/qwenpaw" <<'WRAP'
#!/bin/sh
exec /opt/qwenpaw/venv/bin/python -m qwenpaw "$@"
WRAP
chmod 755 "$STAGE/usr/bin/qwenpaw"

cat > "$STAGE/DEBIAN/control" <<CTRL
Package: qwenpaw
Version: ${VERSION}
Section: utils
Priority: optional
Architecture: ${ARCH}
Maintainer: ThalynnX <https://github.com/ThalynnX>
Homepage: https://github.com/ThalynnX/qwenpaw-fpk
Description: QwenPaw 本地优先个人 AI 助手（多通道对话、多智能体协作、Skills 扩展）
 由 ThalynnX 编译打包，数据保存在 /var/lib/qwenpaw/.qwenpaw，卸载保留。
CTRL

cat > "$STAGE/DEBIAN/postinst" <<'POST'
#!/bin/sh
set -e
id qwenpaw >/dev/null 2>&1 || useradd --system --home /var/lib/qwenpaw --shell /usr/sbin/nologin qwenpaw || true
mkdir -p /var/lib/qwenpaw/.qwenpaw
chown -R qwenpaw:qwenpaw /var/lib/qwenpaw || true
python3 -m venv /opt/qwenpaw/venv || true
/opt/qwenpaw/venv/bin/pip install -q --upgrade pip || true
/opt/qwenpaw/venv/bin/pip install -q --no-cache-dir /opt/qwenpaw || true
systemctl daemon-reload || true
systemctl enable --now qwenpaw || true
exit 0
POST
chmod 755 "$STAGE/DEBIAN/postinst"

cat > "$STAGE/DEBIAN/prerm" <<'PRE'
#!/bin/sh
set -e
systemctl stop qwenpaw || true
systemctl disable qwenpaw || true
exit 0
PRE
chmod 755 "$STAGE/DEBIAN/prerm"

cat > "$STAGE/DEBIAN/postrm" <<'POSTRM'
#!/bin/sh
set -e
systemctl daemon-reload || true
if [ "$1" = "purge" ]; then
  id qwenpaw >/dev/null 2>&1 && userdel qwenpaw || true
fi
exit 0
POSTRM
chmod 755 "$STAGE/DEBIAN/postrm"

mkdir -p "$OUT"
dpkg-deb --build --root-owner-group "$STAGE" "$OUT/qwenpaw_${VERSION}_${ARCH}.deb"
ls -la "$OUT"
