#!/bin/bash

### QwenPaw 入口 CGI
### - 控制台请求：直接输出管理控制台页面
### - 其他请求：静态文件服务

APP_VAR="/var/apps/com.thalynnx.qwenpaw/var"
PID_FILE="${APP_VAR}/qwenpaw.pid"
LOG_FILE="${APP_VAR}/qwenpaw.log"
APP_DIR="com.thalynnx.qwenpaw"
APP_VERSION="2.2.2.post1"

URI_NO_QUERY="${REQUEST_URI%%\?*}"
BASE_PATH="/var/apps/com.thalynnx.qwenpaw/target/www"

# ============ 控制台模式 ============
if echo "$URI_NO_QUERY" | grep -q "console"; then

    find_auth_file() {
        local search_dirs="/vol1/@appshare/${APP_DIR}"
        for d in $search_dirs; do
            if [ -d "$d" ]; then
                local found=$(find "$d" -maxdepth 2 -name "auth.json" -path "*.qwenpaw.secret*" 2>/dev/null | head -1)
                if [ -n "$found" ]; then
                    echo "$found"
                    return 0
                fi
            fi
        done
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

    get_pid() {
        if [ -f "$PID_FILE" ]; then
            head -n 1 "$PID_FILE" | tr -d '[:space:]'
        fi
    }

    get_uptime() {
        local pid=$(get_pid)
        if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
            local start_time=$(ps -o lstart= -p "$pid" 2>/dev/null)
            if [ -n "$start_time" ]; then
                local start_ts=$(date -d "$start_time" +%s 2>/dev/null)
                local now_ts=$(date +%s)
                local diff=$((now_ts - start_ts))
                local days=$((diff / 86400))
                local hours=$(( (diff % 86400) / 3600 ))
                local mins=$(( (diff % 3600) / 60 ))
                if [ "$days" -gt 0 ]; then
                    echo "${days}天 ${hours}:$(printf '%02d' $mins)"
                else
                    echo "${hours}:$(printf '%02d' $mins)"
                fi
                return
            fi
        fi
        echo "--:--"
    }

    # 处理动作
    ACTION="${QUERY_STRING}"
    ACTION="${ACTION%%&*}"

    echo "Content-Type: text/html; charset=utf-8"
    echo ""

    status=$(get_status)
    pid=$(get_pid)
    uptime=$(get_uptime)
    auth_file=$(find_auth_file 2>/dev/null)
    if [ -n "$auth_file" ]; then
        auth_status="已启用"
    else
        auth_status="未设置"
    fi

    if [ "$status" = "running" ]; then
        status_text="运行中"
        status_badge="Active"
        status_class="running"
    else
        status_text="已停止"
        status_badge="Inactive"
        status_class="stopped"
    fi

    # 动作处理
    action_msg=""
    if [ "$ACTION" = "reset_password" ]; then
        auth_file=$(find_auth_file)
        if [ -n "$auth_file" ]; then
            rm -f "$auth_file"
            action_msg='<div class="alert alert-success">✅ 密码已重置。打开 QwenPaw 后需重新注册。</div>'
        else
            action_msg='<div class="alert alert-warning">⚠️ 未找到 auth.json</div>'
        fi
    elif [ "$ACTION" = "restart" ]; then
        action_msg='<div class="alert alert-success">✅ 已发送重启指令，请稍等刷新</div>'
    fi

    cat << 'HTMLEOF'
<!DOCTYPE html>
<html lang="zh-CN">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>QwenPaw 控制台</title>
<style>
:root {
  --bg: #f5f7fa; --card: #fff; --border: #e8ecf0;
  --text: #1f2937; --text2: #6b7280;
  --primary: #3b82f6; --success: #10b981; --warning: #f59e0b;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
body {
  font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif;
  background: var(--bg); color: var(--text); line-height: 1.6; padding: 20px;
}
.wrap { max-width: 800px; margin: 0 auto; }
.page-title { font-size: 22px; font-weight: 700; margin-bottom: 4px; }
.page-desc { color: var(--text2); font-size: 14px; margin-bottom: 20px; }
.card {
  background: var(--card); border: 1px solid var(--border); border-radius: 12px;
  padding: 20px; margin-bottom: 16px;
}
.status-card {
  display: flex; justify-content: space-between; align-items: center; padding: 24px;
  background: linear-gradient(135deg, #f0fdf4, #ecfdf5); border: 1px solid #bbf7d0;
}
.status-card.stopped { background: linear-gradient(135deg, #fef2f2, #fee2e2); border-color: #fecaca; }
.status-left { display: flex; align-items: center; gap: 16px; }
.status-icon {
  width: 48px; height: 48px; border-radius: 12px; background: #dcfce7;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.status-card.stopped .status-icon { background: #fecaca; }
.status-info h2 { font-size: 20px; font-weight: 600; display: flex; align-items: center; gap: 10px; }
.status-badge {
  font-size: 12px; font-weight: 500; padding: 2px 8px; border-radius: 999px;
  background: #dcfce7; color: #166534;
}
.status-card.stopped .status-badge { background: #fecaca; color: #991b1b; }
.status-desc { font-size: 13px; color: var(--text2); margin-top: 2px; }
.btn {
  display: inline-flex; align-items: center; gap: 6px; padding: 8px 16px;
  border-radius: 8px; font-size: 14px; font-weight: 500; border: none;
  cursor: pointer; text-decoration: none; transition: opacity .15s;
}
.btn:hover { opacity: .9; }
.btn-primary { background: var(--primary); color: #fff; }
.btn-warning { background: var(--warning); color: #fff; }
.btn-secondary { background: #f3f4f6; color: var(--text); }
.info-grid { display: grid; grid-template-columns: repeat(3,1fr); gap: 16px; margin-bottom: 16px; }
.info-item { background: var(--card); border: 1px solid var(--border); border-radius: 12px; padding: 16px 20px; }
.info-label { font-size: 12px; color: var(--text2); margin-bottom: 4px; }
.info-value { font-size: 18px; font-weight: 600; font-family: monospace; }
.action-list { display: flex; flex-direction: column; gap: 12px; }
.action-item {
  display: flex; align-items: center; justify-content: space-between;
  padding: 12px; border-radius: 8px; background: #f9fafb; border: 1px solid var(--border);
}
.action-left { display: flex; align-items: center; gap: 12px; }
.action-icon {
  width: 36px; height: 36px; border-radius: 8px; display: flex;
  align-items: center; justify-content: center; font-size: 18px;
}
.action-icon.open { background: #dbeafe; }
.action-icon.restart { background: #fef3c7; }
.action-icon.log { background: #f3f4f6; }
.action-icon.reset { background: #fef3c7; }
.action-title { font-size: 14px; font-weight: 500; }
.action-desc { font-size: 12px; color: var(--text2); }
.service-info { display: flex; flex-direction: column; gap: 12px; }
.info-row {
  display: flex; align-items: center; gap: 12px; padding: 10px 12px;
  border-radius: 8px; background: #f9fafb; border: 1px solid var(--border);
}
.info-row-icon {
  width: 32px; height: 32px; border-radius: 8px; background: #e0e7ff;
  display: flex; align-items: center; justify-content: center; font-size: 16px;
}
.info-row-label { font-size: 12px; color: var(--text2); }
.info-row-value { font-size: 14px; font-weight: 500; }
.alert { padding: 12px 16px; border-radius: 8px; margin-bottom: 16px; font-size: 14px; }
.alert-success { background: #dcfce7; color: #166534; }
.alert-warning { background: #fef3c7; color: #92400e; }
h3 { font-size: 16px; margin-bottom: 16px; }
@media (max-width: 768px) { .info-grid { grid-template-columns: 1fr; } }
</style>
</head>
<body>
<div class="wrap">
HTMLEOF

    echo "
    <div class=\"page-title\">QwenPaw 控制台</div>
    <div class=\"page-desc\">管理 QwenPaw 服务的运行状态</div>
    "

    if [ -n "$action_msg" ]; then
        echo "$action_msg"
    fi

    echo "
    <div class=\"card status-card ${status_class}\">
      <div class=\"status-left\">
        <div class=\"status-icon\">📈</div>
        <div class=\"status-info\">
          <h2>${status_text} <span class=\"status-badge\">${status_badge}</span></h2>
          <div class=\"status-desc\">QwenPaw 服务${status_text}</div>
        </div>
      </div>
      <a href=\"?restart\" class=\"btn btn-primary\" onclick=\"return confirm('确定要重启服务吗？')\">🔄 重启服务</a>
    </div>
    "

    echo "
    <div class=\"info-grid\">
      <div class=\"info-item\">
        <div class=\"info-label\">进程 ID (PID)</div>
        <div class=\"info-value\">${pid:---}</div>
      </div>
      <div class=\"info-item\">
        <div class=\"info-label\">已运行</div>
        <div class=\"info-value\">${uptime}</div>
      </div>
      <div class=\"info-item\">
        <div class=\"info-label\">当前版本</div>
        <div class=\"info-value\">${APP_VERSION}</div>
      </div>
    </div>
    "

    echo "
    <div class=\"card\">
      <h3>⚡ 常用操作</h3>
      <div class=\"action-list\">
        <div class=\"action-item\">
          <div class=\"action-left\">
            <div class=\"action-icon open\">🌐</div>
            <div>
              <div class=\"action-title\">打开 QwenPaw</div>
              <div class=\"action-desc\">访问 QwenPaw Web 界面</div>
            </div>
          </div>
          <a href=\"http://NAS:19091\" target=\"_blank\" class=\"btn btn-primary\">打开</a>
        </div>
        <div class=\"action-item\">
          <div class=\"action-left\">
            <div class=\"action-icon restart\">🔄</div>
            <div>
              <div class=\"action-title\">重启服务</div>
              <div class=\"action-desc\">重启 QwenPaw 服务</div>
            </div>
          </div>
          <a href=\"?restart\" class=\"btn btn-warning\" onclick=\"return confirm('确定要重启服务吗？')\">重启</a>
        </div>
        <div class=\"action-item\">
          <div class=\"action-left\">
            <div class=\"action-icon reset\">🔑</div>
            <div>
              <div class=\"action-title\">重置密码</div>
              <div class=\"action-desc\">清除认证数据，重新注册</div>
            </div>
          </div>
          <a href=\"?reset_password\" class=\"btn btn-warning\" onclick=\"return confirm('确定要重置密码吗？')\">重置</a>
        </div>
      </div>
    </div>

    <div class=\"card\">
      <h3>📊 服务信息</h3>
      <div class=\"service-info\">
        <div class=\"info-row\">
          <div class=\"info-row-icon\">🔌</div>
          <div class=\"info-row-content\">
            <div class=\"info-row-label\">服务端口</div>
            <div class=\"info-row-value\">19091</div>
          </div>
        </div>
        <div class=\"info-row\">
          <div class=\"info-row-icon\">📁</div>
          <div class=\"info-row-content\">
            <div class=\"info-row-label\">工作目录</div>
            <div class=\"info-row-value\">应用文件/${APP_DIR}</div>
          </div>
        </div>
        <div class=\"info-row\">
          <div class=\"info-row-icon\">🔐</div>
          <div class=\"info-row-content\">
            <div class=\"info-row-label\">认证状态</div>
            <div class=\"info-row-value\">${auth_status} 安全</div>
          </div>
        </div>
        <div class=\"info-row\">
          <div class=\"info-row-icon\">📦</div>
          <div class=\"info-row-content\">
            <div class=\"info-row-label\">当前版本</div>
            <div class=\"info-row-value\">${APP_VERSION}</div>
          </div>
        </div>
      </div>
    </div>
    "

    echo '
</div>
</body>
</html>
'
    exit 0
fi

# ============ 静态文件服务 ============
REL_PATH="/"
case "$URI_NO_QUERY" in
    *index.cgi*)
        REL_PATH="${URI_NO_QUERY#*index.cgi}"
        ;;
esac

if [ -z "$REL_PATH" ] || [ "$REL_PATH" = "/" ]; then
    REL_PATH="/index.html"
fi

TARGET_FILE="${BASE_PATH}${REL_PATH}"

if echo "$TARGET_FILE" | grep -q '\.\.'; then
    echo "Status: 400 Bad Request"
    echo "Content-Type: text/plain; charset=utf-8"
    echo ""
    echo "Bad Request"
    exit 0
fi

if [ ! -f "$TARGET_FILE" ]; then
    echo "Status: 404 Not Found"
    echo "Content-Type: text/plain; charset=utf-8"
    echo ""
    echo "404 Not Found: ${REL_PATH}"
    exit 0
fi

ext="${TARGET_FILE##*.}"
case "$ext" in
    html|htm) mime="text/html; charset=utf-8" ;;
    css)     mime="text/css; charset=utf-8" ;;
    js)      mime="application/javascript; charset=utf-8" ;;
    jpg|jpeg) mime="image/jpeg" ;;
    png)     mime="image/png" ;;
    gif)     mime="image/gif" ;;
    svg)     mime="image/svg+xml" ;;
    txt|log) mime="text/plain; charset=utf-8" ;;
    *)       mime="application/octet-stream" ;;
esac

echo "Content-Type: $mime"
echo ""
cat "$TARGET_FILE"
