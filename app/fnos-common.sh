#!/bin/bash
# QwenPaw (ThalynnX/qwenpaw) — 飞牛 fnOS 公共路径解析
# 依赖飞牛 fnOS 注入的环境变量：TRIM_APPDEST / TRIM_PKGETC / TRIM_PKGVAR /
# TRIM_PKGHOME / TRIM_TEMP_LOGFILE / TRIM_SERVICE_PORT

# 规范化路径（解析软链接）
qwenpaw_realpath() {
    local p="${1:-}" r=""
    [ -n "${p}" ] || { printf ''; return 0; }
    if r="$(readlink -f "${p}" 2>/dev/null)" && [ -n "${r}" ]; then
        printf '%s' "${r}"
    else
        printf '%s' "${p}"
    fi
}

QWENPAW_APP_DIR="$(qwenpaw_realpath "${TRIM_APPDEST:-/var/apps/qwenpaw/target}")"
QWENPAW_ETC_DIR="$(qwenpaw_realpath "${TRIM_PKGETC:-/var/apps/qwenpaw/etc}")"
QWENPAW_VAR_DIR="$(qwenpaw_realpath "${TRIM_PKGVAR:-/var/apps/qwenpaw/var}")"
QWENPAW_HOME_DIR="$(qwenpaw_realpath "${TRIM_PKGHOME:-${QWENPAW_VAR_DIR}/home}")"
QWENPAW_VENV="${QWENPAW_VAR_DIR}/venv"
QWENPAW_SOURCE="${QWENPAW_VAR_DIR}/source/qwenpaw"
QWENPAW_BIN="${QWENPAW_VENV}/bin/qwenpaw"
QWENPAW_PIDFILE="${QWENPAW_VAR_DIR}/qwenpaw.pid"
QWENPAW_LOG="${QWENPAW_VAR_DIR}/qwenpaw.log"
QWENPAW_ETC_FILE="${QWENPAW_ETC_DIR}/qwenpaw.env"
QWENPAW_PORT="${TRIM_SERVICE_PORT:-8088}"
export QWENPAW_APP_DIR QWENPAW_ETC_DIR QWENPAW_VAR_DIR QWENPAW_HOME_DIR \
       QWENPAW_VENV QWENPAW_SOURCE QWENPAW_BIN QWENPAW_PIDFILE QWENPAW_LOG \
       QWENPAW_ETC_FILE QWENPAW_PORT

qwenpaw_log() {
    printf '%s %s\n' "$(date '+%F %T')" "$*" >>"${QWENPAW_LOG}" 2>/dev/null
}

qwenpaw_fail() {
    qwenpaw_log "ERROR: $*"
    [ -n "${TRIM_TEMP_LOGFILE:-}" ] && echo "QwenPaw：$*" >>"${TRIM_TEMP_LOGFILE}" 2>/dev/null
    echo "QwenPaw：$*" >&2
}

# 读取安装时保存的配置（日志级别）
qwenpaw_log_level() {
    local lvl="info"
    [ -r "${QWENPAW_ETC_FILE}" ] && lvl="$(grep -E '^LOG_LEVEL=' "${QWENPAW_ETC_FILE}" 2>/dev/null | head -n1 | cut -d= -f2 | tr -d '[:space:]')"
    [ -n "${lvl}" ] || lvl="info"
    printf '%s' "${lvl}"
}
