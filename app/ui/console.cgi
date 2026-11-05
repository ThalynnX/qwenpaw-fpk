#!/bin/bash

### QwenPaw 独立管理控制台 CGI
### 功能：查看状态、重置密码、重启服务、查看日志

APP_HOME="/var/apps/com.thalynnx.qwenpaw/target"
APP_VAR="/var/apps/com.thalynnx.qwenpaw/var"
APP_ETC="/var/apps/com.thalynnx.qwenpaw/etc"
PID_FILE="${APP_VAR}/qwenpaw.pid"
LOG_FILE="${APP_VAR}/qwenpaw.log"

# 查找数据目录中的 auth.json（.qwenpaw.secret/auth.json）
find_auth_file() {
    local search_dirs="/var/apps/com.thalynnx.qwenpaw/data /var/data /home/$(ls /var/apps/com.thalynnx.qwenpaw/home 2>/dev/null | head -1) 2>/dev/null"
    for d in $search_dirs; do
        if [ -d "$d" ]; then
            local found=$(find "$d" -maxdepth 3 -name "auth.json" -path "*.qwenpaw.secret*" 2>/dev/null | head -1)
            if [ -n "$found" ]; then
                echo "$found"
                return 0
            fi
        fi
    done
    # 兜底：全局搜索
    find /var /home -maxdepth 4 -name "auth.json" -path "*.qwenpaw.secret*" 2>/dev/null | head -1
}

get_status() {
    if [ -f "$PID_FILE" ]; then
        pid=$(head -n 1 "$PID_FILE" | tr -d '[:space:]')
        if kill -0 "$pid" 2>/dev/null; then
            echo "running"
            return
        fi
    fi
    echo "stopped"
}

do_reset_password() {
    local auth_file=$(find_auth_file)
    if [ -z "$auth_file" ]; then
        echo "WARNING: 未找到 auth.json，可能尚未初始化"
        return 1
    fi
    rm -f "$auth_file"
    echo "OK: 已删除 $auth_file"
    # 重启服务使配置生效
    do_restart
}

do_restart() {
    # 通过 fnOS 服务管理重启
    if [ -f "${APP_HOME}/cmd/main" ]; then
        bash "${APP_HOME}/cmd/main" stop 2>/dev/null
        sleep 2
        bash "${APP_HOME}/cmd/main" start 2>/dev/null
        echo "OK: 服务已重启"
    else
        echo "ERROR: 找不到启动脚本"
        return 1
    fi
}

# 处理动作
ACTION="${QUERY_STRING}"
# 简化解析
ACTION="${ACTION%%&*}"

echo "Content-Type: text/html; charset=utf-8"
echo ""

echo '<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QwenPaw 管理控制台</title>
<style>
:root { color-scheme: light dark; }
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: #f5f7fa; color: #1f2329; line-height: 1.7; padding: 2rem 1rem;
}
@media (prefers-color-scheme: dark) {
  body { background: #171a1f; color: #e8eaed; }
  .card { background: #1f242b; border-color: #2b313a; }
  .btn { background: #2b313a; color: #e8eaed; }
  pre { background: #111; color: #aaa; }
}
.wrap { max-width: 720px; margin: 0 auto; }
h1 { font-size: 1.4rem; margin-bottom: .3rem; }
.sub { color: #98a2ad; font-size: .85rem; margin-bottom: 1.5rem; }
.card {
  background: #fff; border: 1px solid #e5e8eb; border-radius: 12px;
  padding: 1.5rem; margin-bottom: 1rem;
}
.status { display: inline-block; padding: .2rem .8rem; border-radius: 999px; font-size: .85rem; font-weight: 600; }
.status.running { background: #d4edda; color: #155724; }
.status.stopped { background: #f8d7da; color: #721c24; }
.btn {
  display: inline-block; padding: .6rem 1.4rem; border: none; border-radius: 8px;
  font-size: .95rem; cursor: pointer; margin-right: .5rem; margin-top: .5rem;
  text-decoration: none; background: #1664ff; color: #fff;
}
.btn.danger { background: #dc3545; }
.btn.secondary { background: #6c757d; }
.btn:hover { opacity: .9; }
.msg { padding: .8rem 1rem; border-radius: 8px; margin: .8rem 0; font-size: .9rem; }
.msg.ok { background: #d4edda; color: #155724; }
.msg.warn { background: #fff3cd; color: #856404; }
.msg.err { background: #f8d7da; color: #721c24; }
pre {
  background: #f0f2f5; padding: 1rem; border-radius: 8px; overflow-x: auto;
  font-size: .82rem; max-height: 300px; overflow-y: auto;
}
.row { display: flex; justify-content: space-between; align-items: center; padding: .4rem 0; }
.label { color: #98a2ad; font-size: .9rem; }
.value { font-weight: 600; }
</style>
</head>
<body>
<div class="wrap">
<h1>QwenPaw 管理控制台</h1>
<p class="sub">独立于 QwenPaw Web 界面 · 密码重置 / 服务管理</p>
'

# 处理动作
if [ "$ACTION" = "reset_password" ]; then
    echo '<div class="card">'
    result=$(do_reset_password 2>&1)
    if echo "$result" | grep -q "^OK:"; then
        echo "<div class=\"msg ok\">$result</div>"
        echo "<p>密码已重置。现在可以打开 <a href=\"http://NAS:19091\" target=\"_blank\">QwenPaw Web 控制台</a> 重新注册账号。</p>"
    else
        echo "<div class=\"msg warn\">$result</div>"
    fi
    echo '</div>'
elif [ "$ACTION" = "restart" ]; then
    echo '<div class="card">'
    result=$(do_restart 2>&1)
    if echo "$result" | grep -q "^OK:"; then
        echo "<div class=\"msg ok\">$result</div>"
    else
        echo "<div class=\"msg err\">$result</div>"
    fi
    echo '</div>'
fi

# 状态卡片
status=$(get_status)
auth_file=$(find_auth_file 2>/dev/null)

echo '<div class="card">'
echo "<div class=\"row\"><span class=\"label\">运行状态</span><span class=\"value\"><span class=\"status $status\">$status</span></span></div>"
echo "<div class=\"row\"><span class=\"label\">认证文件</span><span class=\"value\">"
if [ -n "$auth_file" ]; then
    echo "已注册 (有密码)"
else
    echo "未注册 (无密码)"
fi
echo "</span></div>"
echo '<div class="row"><span class="label">Web 控制台</span><span class="value"><a href="http://NAS:19091" target="_blank">http://NAS:19091</a></span></div>'
echo '</div>'

# 操作卡片
echo '<div class="card">'
echo '<h3 style="margin-bottom:1rem;">操作</h3>'
echo '<a class="btn danger" href="?reset_password" onclick="return confirm(\'确定要重置密码吗？这会删除当前账号并重启服务，打开 Web 控制台后需重新注册。\')">重置密码</a>'
echo '<a class="btn secondary" href="?restart">重启服务</a>'
echo '</div>'

# 日志卡片
echo '<div class="card">'
echo '<h3 style="margin-bottom:1rem;">最近日志</h3>'
if [ -f "$LOG_FILE" ]; then
    echo '<pre>'
    tail -30 "$LOG_FILE" 2>/dev/null | sed 's/</\&lt;/g'
    echo '</pre>'
else
    echo '<p class="label">暂无日志</p>'
fi
echo '</div>'

echo '</div></body></html>'
